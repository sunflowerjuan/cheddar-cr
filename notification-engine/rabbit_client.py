import asyncio
import json
import aio_pika
from utils.config import RABBITMQ_URL, MCP_IN_QUEUE, MCP_OUT_QUEUE

class RabbitClient:
    def __init__(self, on_response_callback=None):
        self.connection = None
        self.channel = None
        self.on_response_callback = on_response_callback

    async def connect(self):
        print("Conectando a RabbitMQ...")
        self.connection = await aio_pika.connect_robust(RABBITMQ_URL)
        self.channel = await self.connection.channel()
        await self.channel.declare_queue(MCP_IN_QUEUE, durable=True)
        await self.channel.declare_queue(MCP_OUT_QUEUE, durable=True)
        print("Conectado a RabbitMQ")

    async def send_to_mcp(self, chat_id, text):
        message = {"chat_id": chat_id, "text": text}
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=MCP_IN_QUEUE,
        )
        print(f"[→] Enviado a {MCP_IN_QUEUE}: {message}")

    async def consume_responses(self):
        queue = await self.channel.declare_queue(MCP_OUT_QUEUE, durable=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = json.loads(message.body)
                        if self.on_response_callback:
                            await self.on_response_callback(data)
                    except Exception as e:
                        print(f"Error procesando mensaje MCP_OUT: {e}")

    async def close(self):
        if self.connection:
            await self.connection.close()
            print("Conexión RabbitMQ cerrada.")
