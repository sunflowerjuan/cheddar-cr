import os
from dotenv import load_dotenv

load_dotenv()

LLM_BASE_URL = os.getenv("BASE_URL")
PLAYER_API_BASE_URL = "http://cr.localhost/collector"
META_API_BASE_URL = "http://cr.localhost/monitor"
MCP_SERVER_URL = "http://127.0.0.1:8000"

KEY_PROMPT = os.getenv("KEY_PROMPT")

server_config = {
    "default": {
        "url": f"{MCP_SERVER_URL}/sse",
        "transport": "sse",
    }
}


RABBITMQ_HOST = "localhost"
RABBITMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_DEFAULT_PASS")