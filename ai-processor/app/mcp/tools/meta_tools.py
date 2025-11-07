import logging
from .tool_utils import APIConnector as api
from utils.logger import get_logger
logger = get_logger(__name__)


def meta_tools(mcp):
    """
    Tools para obtener información del meta de Clash Royale.
    Incluye:
    - Cambios de balance recientes.
    - Estadísticas de uso y winrate de cartas.
    """
    
    api()  # Inicializa conexión con el backend
    
    @mcp.tool()
    def meta_data() -> dict:
        """
        Obtiene los cambios de balance más recientes del juego.

        Returns:
            dict: Contiene:
                - gameName (str)
                - title (str)
                - publishDate (str, ISO)
                - ajustes (list):
                    - nombre (str)
                    - cambio (str)
                    - tipo (mejora | nerf | ajuste | neutro)
        """
        logger.info("Solicitando cambios de balance...")

        try:
            result = api.get_balance_changes()
            logger.info(f"Balance recibido: {result.get('title', 'Sin título')}")
            return result
        
        except Exception as e:
            logger.error(f"Error al obtener balance: {e}")
            raise RuntimeError("No se pudo obtener los cambios de balance recientes.")
    

    @mcp.tool()
    def card_stats() -> dict:
        """
        Obtiene estadísticas de uso y winrate de cartas en modos del juego.

        Returns:
            dict: Mapa donde cada key es un modo (ej: 'global', 'top ladder'):
                [
                    {
                        nombre: str,
                        uso: str,
                        cambio_uso: str,
                        tendencia_uso: aumento | disminución | neutral,
                        winrate: str,
                        cambio_winrate: str,
                        tendencia_winrate: aumento | disminución | neutral
                    }
                ]
        """
        logger.info("Solicitando estadísticas del meta...")

        try:
            result = api.get_card_statistics()
            logger.info(f"Estadísticas recibidas. Modos disponibles: {list(result.keys())}")
            return result
        
        except Exception as e:
            logger.error(f"Error al obtener stats: {e}")
            raise RuntimeError("No se pudieron obtener estadísticas meta.")
