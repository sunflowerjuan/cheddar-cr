from config.settings import URLS, DATA_DIR, WAIT_TIME
from core.driver import crear_driver
from core.extractor import extraer_datos
from core.saver import guardar_json

def main():
    driver = crear_driver(headless=True)

    for modo, url in URLS.items():
        datos = extraer_datos(driver, url, WAIT_TIME)
        guardar_json(datos, f"{DATA_DIR}/{modo}.json")

    driver.quit()

if __name__ == "__main__":
    main()
