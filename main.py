from scraper.extractor import ExtractorWeb
from scraper.parser import ParserBalance
from scraper.sources.supercell_source import FuenteSupercell
from scraper.sources.royaleapi_source import FuenteRoyaleAPI
from data.gestor_json import GestorJSON
from utils.logger import Logger
from datetime import datetime


def procesar_fuente(fuente, parser, gestor_json, logger):
    """
    Procesa una fuente (Supercell o RoyaleAPI):
    - Obtiene artículos del último mes.
    - Extrae cambios de balance por carta.
    - Guarda resultados en JSON si hay información válida.
    """
    logger.info(f"🔍 Revisando: {fuente.URL_BASE}")

    try:
        articulos = fuente.obtener_articulos_balance()
    except Exception as e:
        logger.error(f"Error obteniendo artículos desde {fuente.URL_BASE}: {e}")
        return

    if not articulos:
        logger.warning("⚠️  No se encontraron artículos recientes.")
        return

    logger.info(f"📰 {len(articulos)} artículos encontrados en los últimos 30 días")

    for url in articulos:
        try:
            articulo = fuente.extraer_articulo(url)
            titulo_real = articulo["titulo_real"]
            texto = articulo["texto_completo"].strip()

            if not texto:
                continue  # ignora si el artículo no tiene texto útil

            # Detectar cambios en el texto
            cambios = parser.extraer_cambios_inteligentes(texto)
            if not cambios:
                continue  # ignora si no hay cartas detectadas

            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre = f"balances_{fuente.__class__.__name__.lower()}_{timestamp}.json"
            gestor_json.archivo_salida = f"data/json/{nombre}"

            # Guardar cambios
            resultado = gestor_json.guardar_resultados(titulo_real, cambios, url)

            logger.success(f"✅ {resultado['total_cartas']} cartas guardadas en {nombre}")

        except Exception as e:
            logger.error(f"❌ Error procesando {url}: {e}")


def main():
    """
    Punto de entrada del programa.
    """
    logger = Logger()
    parser = ParserBalance()
    gestor_json = GestorJSON()

    # Fuentes configuradas
    fuentes = [
        FuenteSupercell(),
        FuenteRoyaleAPI()
    ]

    # Procesa cada fuente
    for fuente in fuentes:
        procesar_fuente(fuente, parser, gestor_json, logger)

    # Mostrar resumen final
    archivos = gestor_json.listar_archivos_json()
    if archivos:
        logger.info(f"📦 Archivos JSON generados: {len(archivos)} en data/json/")
    else:
        logger.warning("⚠️  No se generaron archivos JSON.")


if __name__ == "__main__":
    main()
