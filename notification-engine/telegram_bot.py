import asyncio
import json
import threading
import time
import requests
import aio_pika
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from utils.config import RABBITMQ_URL, MCP_IN_QUEUE, MCP_OUT_QUEUE, TELEGRAM_TOKEN, TELEGRAM_API_URL
from utils.logger import get_logger

logger = get_logger(__name__)


class RabbitConsumerThread(threading.Thread):
    """
    Hilo separado que corre su propio event loop y consume de MCP_OUT.
    Cuando recibe una respuesta publica directamente a Telegram via HTTP API.
    """

    def __init__(self, rabbit_url, out_queue, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.rabbit_url = rabbit_url
        self.out_queue = out_queue
        self._stop_event = stop_event
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._consume_loop())
        except Exception as e:
            logger.exception(f"Excepción en consumer thread: {e}")
        finally:
            pending = asyncio.all_tasks(loop=self.loop)
            for t in pending:
                t.cancel()
            try:
                self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            except Exception:
                pass
            self.loop.close()
            logger.info("Consumer thread finalizado correctamente.")

    async def _consume_loop(self):
        logger.info("[Consumer] Conectando a RabbitMQ (consumer)...")
        conn = await aio_pika.connect_robust(self.rabbit_url)
        channel = await conn.channel()
        queue = await channel.declare_queue(self.out_queue, durable=True)
        logger.info(f"[Consumer] Conectado y escuchando {self.out_queue}")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = json.loads(message.body.decode())
                    except Exception:
                        logger.warning(f"[Consumer] Mensaje no JSON: {message.body}")
                        continue

                    chat_id = data.get("chat_id")
                    response = data.get("response", "").strip()
                    if not chat_id:
                        logger.warning(f"[Consumer] No chat_id en mensaje: {data}")
                        continue
                    if not response:
                        logger.warning(f"[Consumer] Mensaje vacío ignorado: {data}")
                        continue

                    payload = {"chat_id": chat_id, "text": response}
                    try:
                        r = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
                        if r.status_code != 200:
                            logger.error(f"[Consumer] Error al enviar a Telegram: {r.status_code} {r.text}")
                        else:
                            logger.info(f"[Consumer] Enviado a Telegram chat_id={chat_id}")
                    except Exception as e:
                        logger.exception(f"[Consumer] Excepción enviando a Telegram: {e}")

                if self._stop_event.is_set():
                    break

        await channel.close()
        await conn.close()
        logger.info("[Consumer] Cerrada conexión y thread finaliza.")


class TelegramBot:
    def __init__(self):
        self.app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        self._pub_conn = None
        self._pub_channel = None
        self._stop_event = threading.Event()
        self._consumer_thread = RabbitConsumerThread(RABBITMQ_URL, MCP_OUT_QUEUE, self._stop_event)

    async def ensure_publisher(self):
        if self._pub_conn and not self._pub_conn.is_closed:
            return
        logger.info("[Publisher] Conectando a RabbitMQ (publisher)...")
        self._pub_conn = await aio_pika.connect_robust(RABBITMQ_URL)
        self._pub_channel = await self._pub_conn.channel()
        await self._pub_channel.declare_queue(MCP_IN_QUEUE, durable=True)
        logger.info("[Publisher] Conectado (publisher)")

    async def publish_to_mcp(self, chat_id: int, text: str):
        await self.ensure_publisher()
        message = {"chat_id": chat_id, "text": text}
        await self._pub_channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=MCP_IN_QUEUE,
        )
        logger.info(f"[Publisher] Encolado en {MCP_IN_QUEUE}: chat_id={chat_id}")

    async def start_cmd(self, update, context):
        await update.message.reply_text("Hola, soy MissyBot. Envíame algo y lo procesaré.")
        logger.info(f"[Bot] /start usado por chat_id={update.effective_chat.id}")

    async def message_handler(self, update, context):
        text = update.message.text or ""
        chat_id = update.effective_chat.id
        await self.publish_to_mcp(chat_id, text)
        await update.message.reply_text("Procesando tu solicitud...")
        logger.info(f"[Bot] Mensaje recibido de chat_id={chat_id}: {text}")

    def start(self):
        self.app.add_handler(CommandHandler("start", self.start_cmd))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))

        logger.info("[Main] Iniciando consumer thread...")
        self._consumer_thread.start()
        time.sleep(0.1)

        logger.info("[Main] Iniciando Bot (run_polling)...")
        try:
            self.app.run_polling()
        finally:
            self._stop_event.set()
            logger.info("[Main] Bot detenido, esperando consumer thread terminar...")
            self._consumer_thread.join(timeout=5)

            loop = asyncio.get_event_loop()
            if loop and not loop.is_closed():
                loop.run_until_complete(self._close_publisher())
            logger.info("[Main] Shutdown completo.")

    async def _close_publisher(self):
        if self._pub_channel and not self._pub_channel.is_closed:
            await self._pub_channel.close()
        if self._pub_conn and not self._pub_conn.is_closed:
            await self._pub_conn.close()
        logger.info("[Publisher] Conexión cerrada.")


if __name__ == "__main__":
    bot = TelegramBot()
    try:
        bot.start()
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt recibido, cerrando...")
        bot._stop_event.set()
        bot._consumer_thread.join(timeout=5)
        try:
            loop = asyncio.get_event_loop()
            if loop and not loop.is_closed():
                loop.run_until_complete(bot._close_publisher())
        except Exception:
            pass
        logger.info("MissyBot detenido correctamente.")
