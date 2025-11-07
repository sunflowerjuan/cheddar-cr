import requests
from utils.config import PLAYER_API_BASE_URL,META_API_BASE_URL
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
    
    def get_balance_changes(self):
        """Obtiene los cambios de balance recientes desde el meta-monitor."""
        url = f"{META_API_BASE_URL}/meta/"
        response = requests.get(url)
        if response.status_code == 200:
            logger.info("Cambios de balance obtenidos correctamente.")
            return response.json()
        else:
            logger.error(f"Error {response.status_code} obteniendo cambios de balance: {response.text}")
            return None
    def get_card_stats(self):
        """Obtiene las estadísticas de las cartas desde el meta-monitor."""
        url = f"{META_API_BASE_URL}/stats/"
        response = requests.get(url)
        if response.status_code == 200:
            logger.info("Estadísticas de cartas obtenidas correctamente.")
            return response.json()
        else:
            logger.error(f"Error {response.status_code} obteniendo estadísticas de cartas: {response.text}")
            return None
