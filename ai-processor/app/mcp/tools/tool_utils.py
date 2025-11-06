import requests
from utils.config import PLAYER_API_BASE_URL
from utils.logger import get_logger

logger = get_logger(__name__)

class APIConnector:
    """Clase para conectar y obtener datos de la API del data-collector."""
    def __init__(self):
        self.base_url = PLAYER_API_BASE_URL


    def get_player_data(self, tag: str):
        """Obtiene los datos del jugador dado su tag."""
        url = f"{self.base_url}/players/{tag.replace('#', '%23')}"
        response = requests.get(url)
        if response.status_code == 200:
            logger.info(f"Datos del jugador {tag} obtenidos correctamente.")
            return response.json()
        else:
            logger.error(f"Error {response.status_code} obteniendo jugador {tag}: {response.text}")
            return None

    def get_battle_log(self, tag: str):
        url = f"{self.base_url}/battles/{tag.replace('#', '%23')}"
        response = requests.get(url)
        if response.status_code == 200:
            logger.info(f"Battle log de {tag} obtenido correctamente.")
            return response.json()
        else:
            logger.error(f"Error {response.status_code} obteniendo battle log: {response.text}")
            return None
