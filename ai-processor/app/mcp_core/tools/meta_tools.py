import logging
from .tool_utils import APIConnector as api
from app.utils.logger import get_logger
logger = get_logger(__name__)


def meta_tools(mcp):
    """
    Tools para obtener información del meta de Clash Royale.
    """
    
    # Crear instancia real del conector
    connector = api()
    
    @mcp.tool()
    def meta_data() -> dict:
        """
        Obtiene los cambios de balance más recientes del juego.
        """
        logger.info("Solicitando cambios de balance...")

        result = connector.get_balance_changes()

        if not result:
            logger.warning("No se recibieron datos del balance.")
            return {"error": "No se pudo obtener los cambios de balance recientes."}

        logger.info(f"Balance recibido correctamente: {result.get('title', 'Sin título')}")
        return result
    

    @mcp.tool()
    def card_stats() -> dict:
        """
        Obtiene estadísticas de uso y winrate de cartas.
        """
        logger.info("Solicitando estadísticas del meta...")

        result = connector.get_card_stats()

        if not result:
            logger.warning("No se recibieron estadísticas del meta.")
            return {"error": "No se pudieron obtener estadísticas del meta."}

        logger.info(f"Estadísticas recibidas. Modos disponibles: {list(result.keys())}")
        return result
