import time
from .parser import analizar_fila

def extraer_datos(driver, url, wait_time):
    """Extrae las estadísticas de una URL."""
    print(f"🔍 Extrayendo datos de: {url}")
    driver.get(url)
    time.sleep(wait_time)

    filas = driver.find_elements("css selector", "tr")
    datos = [analizar_fila(f) for f in filas if analizar_fila(f) is not None]
    return datos
