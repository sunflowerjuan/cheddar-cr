import os

TOKEN = os.getenv("CR_TOKEN")
BASE_URL = "https://api.clashroyale.com/v1"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
