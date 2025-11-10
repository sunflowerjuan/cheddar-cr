import json
import asyncio
import aio_pika

from mcp_core.mcp_client import ClashRoyaleAssistant
from utils.config import RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASS


class MCPWorker:
    def __init__(self):
        self.rabbit_url = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}/"
        self.in_queue_name = "mcp_in"
        self.out_queue_name = "mcp_out"
        self.assistant = None

    async def setup(self):
        print("Conectando a RabbitMQ...")
        self.connection = await aio_pika.connect_robust(self.rabbit_url)
        self.channel = await self.connection.channel()

        # Declarar colas
        self.in_queue = await self.channel.declare_queue(self.in_queue_name, durable=True)
        self.out_queue = await self.channel.declare_queue(self.out_queue_name, durable=True)

        print("Inicializando asistente MCP...")
        self.assistant = ClashRoyaleAssistant()
        await self.assistant.initialize_agent()

        print("MCP Worker Listo. Esperando mensajes...")

    async def run(self):
        await self.setup()

        async with self.in_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():

                    payload = json.loads(message.body.decode())
                    chat_id = payload["chat_id"]
                    text = payload["text"]

                    print(f"[WORKER] Recibido → chat_id={chat_id}: {text}")

                    response_text = await self.assistant.process_message(text)

                    response_payload = json.dumps({
                        "chat_id": chat_id,
                        "response": response_text,
                    })

                    await self.channel.default_exchange.publish(
                        aio_pika.Message(body=response_payload.encode()),
                        routing_key=self.out_queue_name,
                    )

                    print(f"[WORKER] Respondido → chat_id={chat_id}")
