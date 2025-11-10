import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


RABBITMQ_HOST = "rabbitmq"
RABBITMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_DEFAULT_PASS")
RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}/"

MCP_IN_QUEUE = "mcp_in"
MCP_OUT_QUEUE = "mcp_out"