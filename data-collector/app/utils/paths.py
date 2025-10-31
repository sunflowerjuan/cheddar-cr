import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "players")

os.makedirs(DATA_DIR, exist_ok=True)

def get_json_path(player_tag: str, file_type: str):
    clean_tag = player_tag.replace("#", "")
    filename = f"{file_type}_{clean_tag}.json"
    return os.path.join(DATA_DIR, filename)
