from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

import time
from utils.logger import get_logger

logger = get_logger(__name__)

## NECESITO OPTIMIZAR ESTA PARTE, YA QUE SELENIUM ES MUY LENTO PARA ESTO AYUDAAAAAAAAAAAAAAA

def set_driver(headless=True):
    options = Options()
    options.binary_location = "/usr/bin/chromium"

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

    return webdriver.Chrome(options=options)


def extract_data(driver, url, wait_time=10):
    """Extrae datos usando Selenium + BeautifulSoup para máximo rendimiento."""
    logger.info(f"Extrayendo datos de: {url}")
    driver.get(url)

    # Esperamos solo hasta que aparezca algo tipo <tr> (dinámico)
    WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tr"))
    )

    # Capturamos el HTML una sola vez
    html = driver.page_source
    return parse_html_data(html)


def parse_html_data(html):
    """Procesa el HTML completo con BeautifulSoup (mucho más rápido que Selenium fila a fila)."""
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.select("tr")
    data = []

    for row in rows:
        # Aquí evitamos caer en errores por filas de encabezado u otras
        name_el = row.select_one(".text-left.hidden.sm\\:block")
        if not name_el:
            continue

        name = name_el.get_text(strip=True)

        percent = row.select("div.text-3xl.font-bold")
        changes = row.select("div.text-sm.font-bold")

        use = percent[0].get_text(strip=True) if len(percent) > 0 else ""
        winrate = percent[1].get_text(strip=True) if len(percent) > 1 else ""
        use_change = changes[0].get_text(strip=True) if len(changes) > 0 else ""
        winrate_change = changes[1].get_text(strip=True) if len(changes) > 1 else ""

        # Tendencias por clase
        use_tendency = (
            "aumento" if changes and "green" in changes[0].get("class", []) else
            "disminución" if changes and "red" in changes[0].get("class", []) else
            "neutral"
        )

        winrate_tendency = (
            "aumento" if changes and "green" in changes[1].get("class", []) else
            "disminución" if changes and "red" in changes[1].get("class", []) else
            "neutral"
        )

        data.append({
            "nombre": name,
            "uso": use,
            "cambio_uso": use_change,
            "tendencia_uso": use_tendency,
            "winrate": winrate,
            "cambio_winrate": winrate_change,
            "tendencia_winrate": winrate_tendency
        })

    return data
