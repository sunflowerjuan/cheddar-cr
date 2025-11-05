from utils.logger import get_logger
from monitor.balance_changes import api_request,extract_api_data


logger = get_logger(__name__)

def meta_data():
    links = api_request()
    datos=[]
    for url in links:
        datos[url] = extract_api_data(url)
    return datos

def cards_stadistics():
    # Unimplimented
    return None



