import time
from main import run_collector
from utils.logger import get_logger

logger = get_logger(__name__)

def start_scheduler(interval: int = 600):
    logger.info(f"Iniciando scheduler cada {interval} segundos.")
    while True:
        try:
            run_collector()
        except Exception as e:
            logger.error(f"Error durante la ejecución: {e}")
        time.sleep(interval)
