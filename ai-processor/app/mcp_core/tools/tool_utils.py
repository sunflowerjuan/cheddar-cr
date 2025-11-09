import requests
from app.utils.config import PLAYER_API_BASE_URL, META_API_BASE_URL
from app.utils.logger import get_logger

logger = get_logger(__name__)

class APIConnector:
    """Clase para conectar y obtener datos de la API del data-collector."""
    def __init__(self):
        self.player_base_url = PLAYER_API_BASE_URL.rstrip("/")  
        self.meta_base_url = META_API_BASE_URL.rstrip("/")  

    def normalize_tag(self, tag: str) -> str:
        """ Normaliza el tag removiendo '#' si el usuario lo incluye. """
        return tag.replace("#", "").strip()

    def get_player_data(self, tag: str):
        tag = self.normalize_tag(tag)
        url = f"{self.player_base_url}/player/{tag}"
        response = requests.get(url)

        if response.status_code == 200:
            logger.info(f"Datos del jugador {tag} obtenidos correctamente.")
            return response.json()

        logger.error(f"Error {response.status_code} obteniendo jugador {tag}: {response.text}")
        return {"error": f"No se encontró el jugador {tag}."}

    def get_battle_log(self, tag: str):
        tag = self.normalize_tag(tag)
        url = f"{self.player_base_url}/battles/{tag}"
        response = requests.get(url)

        if response.status_code == 200:
            logger.info(f"Battle log de {tag} obtenido correctamente.")
            return response.json()

        logger.error(f"Error {response.status_code} obteniendo battle log: {response.text}")
        return {"error": f"No se encontró el battle log de {tag}."} 

    def get_balance_changes(self):
        url = f"{self.meta_base_url}/meta"
        response = requests.get(url)

        if response.status_code == 200:
            logger.info("Cambios de balance obtenidos correctamente.")
            return response.json()

        logger.error(f"Error {response.status_code} obteniendo cambios de balance: {response.text}")
        return {"error": "No se encontraron cambios de balance."}

    def get_card_stats(self):
        url = f"{self.meta_base_url}/stats"
        response = requests.get(url)

        if response.status_code == 200:
            logger.info("Estadísticas de cartas obtenidas correctamente.")
            return response.json()

        logger.error(f"Error {response.status_code} obteniendo estadísticas de cartas: {response.text}")
        return {"error": "No se encontraron estadísticas de cartas."}
