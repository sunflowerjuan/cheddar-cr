import os
from dotenv import load_dotenv

load_dotenv()

LLM_BASE_URL = os.getenv("BASE_URL")
PLAYER_API_BASE_URL = "http://cr.localhost/collector"

