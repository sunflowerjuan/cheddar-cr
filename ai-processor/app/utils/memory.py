import json
import redis.asyncio as aioredis
from langchain_core.messages import HumanMessage, AIMessage

class RedisChatHistory:
    def __init__(self, session_id: str, host: str = "localhost", port: int = 6379, max_messages: int = 4):
        self.session_id = session_id
        self.redis_url = f"redis://{host}:{port}"
        self.redis = None
        self.max_messages = max_messages 

    async def connect(self):
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)

    async def add_message(self, role: str, content: str):
        await self.connect()
        message = json.dumps({"role": role, "content": content})
        await self.redis.rpush(self.session_id, message)
        # Mantiene solo los últimos N mensajes
        await self.redis.ltrim(self.session_id, -self.max_messages, -1)

    async def get_history(self):
        await self.connect()
        messages = await self.redis.lrange(self.session_id, 0, -1)
        parsed = [json.loads(m) for m in messages]
        return [
            HumanMessage(content=m["content"]) if m["role"] == "human" else AIMessage(content=m["content"])
            for m in parsed
        ]

    async def clear_history(self):
        await self.connect()
        await self.redis.delete(self.session_id)
