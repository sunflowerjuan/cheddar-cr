from utils.logger import get_logger
from monitor.balance_changes import api_request, extract_api_data
from .card_stadistics import set_driver, extract_data
from utils.config import STATICS_URLS as URLS, WAIT_TIME

logger = get_logger(__name__)

def meta_data():
    links = api_request()
    data = {}  
    for url in links:
        try:
            data[url] = extract_api_data(url)
        except Exception as e:
            logger.error(f"Error procesando {url}: {e}")
            data[url] = None
    return data

def cards_stadistics():
    """
    Extrae estadísticas de cartas usando Selenium.
    - urls: lista de URLs a procesar. Si es None, usa api_request() para obtener enlaces.
    Devuelve dict { modo|url: datos } donde datos es la lista devuelta por extract_data o None en caso de error.
    """
    import json
    from pathlib import Path

    results = {}

    if URLS:
        driver = None
        driver = set_driver(headless=True)
        for i, url in URLS.items():
            data = extract_data(driver, url, WAIT_TIME)
            results[i] = data   

    return results



