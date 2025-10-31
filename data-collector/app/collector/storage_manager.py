import json
from utils.paths import get_json_path
from utils.logger import get_logger

logger = get_logger(__name__)

class StorageManager:
    @staticmethod
    def save_json(player_tag: str, file_type: str, data: dict):
        path = get_json_path(player_tag, file_type)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Archivo guardado: {path}")
        return path
