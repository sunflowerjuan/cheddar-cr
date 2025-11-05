import os
import json
from finder import obtener_links_balance
from extractor import extraer_datos_articulo

def main():
    links = obtener_links_balance()
    print(f"🔗 Se encontraron {len(links)} posibles artículos de balance.")

    if not os.path.exists("ajustes"):
        os.mkdir("ajustes")

    for url in links:
        datos = extraer_datos_articulo(url)
        if datos:
            nombre_archivo = f"ajustes/{datos['title'].replace(' ', '_').replace('/', '_')}.json"
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
            print(f"✅ Guardado: {nombre_archivo}")

if __name__ == "__main__":
    main()
