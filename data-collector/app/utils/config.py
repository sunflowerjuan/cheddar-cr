import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
BASE_URL = "https://api.clashroyale.com/v1"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

