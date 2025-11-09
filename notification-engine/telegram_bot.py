import pika
import threading
import json
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from utils.config import TELEGRAM_TOKEN, RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASS
from utils.logger import get_logger

logger = get_logger(__name__)

# RABBIT SETUP
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    credentials=credentials
))
channel = connection.channel()
channel.queue_declare(queue="telegram_to_mcp", durable=True)
channel.queue_declare(queue="mcp_to_telegram", durable=True)
channel.queue_declare(queue="notifications", durable=True)



# COMMAND /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Comando /start recibido de %s", update.effective_chat.id)
    await update.message.reply_text(
        "¡Hola! Soy Missy, tu asistente de Clash Royale. "
        "Envíame tu tag con /mytag o simplemente escríbeme algo para hablar conmigo."
    )


# COMMAND /setinterval
async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Comando /setinterval recibido de %s con args: %s",
                update.effective_chat.id, context.args)
    if len(context.args) == 0:
        await update.message.reply_text("Uso: /setinterval <minutos>")
        return
    try:
        minutes = int(context.args[0])
        await update.message.reply_text(f"Intervalo de notificaciones establecido a {minutes} minutos.")
    except ValueError:
        logger.warning("Valor inválido para /setinterval: %s", context.args)
        await update.message.reply_text("Por favor, ingresa un número válido de minutos.")


# COMMAND /mytag
async def set_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Comando /mytag recibido de %s", update.effective_chat.id)
    if len(context.args) == 0:
        await update.message.reply_text("Uso: /mytag <#TAG_JUGADOR>")
        return
    player_tag = context.args[0]
    msg = {
        "chat_id": update.effective_chat.id,
        "command": "set_tag",
        "player_tag": player_tag
    }
    try:
        channel.basic_publish(exchange="", routing_key="telegram_to_mcp", body=json.dumps(msg))
        logger.info("Tag enviado a MCP: %s", msg)
        await update.message.reply_text(f"Tag {player_tag} guardado y enviado a Missy.")
    except Exception as e:
        logger.exception("Error al publicar tag en RabbitMQ: %s", e)
        await update.message.reply_text("Hubo un error al enviar tu tag a Missy.")


# PROMPT HANDLER
async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    chat_id = update.effective_chat.id
    if not user_message:
        return

    msg = {
        "chat_id": chat_id,
        "command": "prompt",
        "prompt": user_message
    }

    try:
        channel.basic_publish(exchange="", routing_key="telegram_to_mcp", body=json.dumps(msg))
        logger.info("Prompt enviado a MCP desde chat %s: %s", chat_id, user_message)
        await update.message.reply_text("Enviando tu mensaje a Missy...")
    except Exception as e:
        logger.exception("Error al publicar prompt: %s", e)
        await update.message.reply_text("Hubo un error al enviar tu mensaje a Missy.")


#  CLIENT CONSUMER FROM MCP
def consume_from_mcp(application):
    def callback(ch, method, properties, body):
        try:
            data = json.loads(body)
            chat_id = data.get("chat_id")
            text = data.get("message", "")
            if chat_id and text:
                logger.info("Mensaje recibido desde MCP para chat %s: %s", chat_id, text)
                asyncio.run(application.bot.send_message(chat_id=chat_id, text=text))
        except Exception as e:
            logger.exception("Error al procesar mensaje desde MCP: %s", e)

    logger.info("Esperando mensajes desde MCP...")
    channel.basic_consume(queue="mcp_to_telegram", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()



if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setinterval", set_interval))
    app.add_handler(CommandHandler("mytag", set_tag))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))

    threading.Thread(target=consume_from_mcp, args=(app,), daemon=True).start()

    logger.info("Bot de Telegram iniciado y en ejecución...")
    app.run_polling()
