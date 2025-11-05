import requests
from bs4 import BeautifulSoup
from utils.config import BASE_URL, BLOG_URL, KEY_WORDS
from utils.logger import get_logger
import json
import requests
from .utils import normalize_arrows, classify_from_heading, classify_from_text


logger = get_logger(__name__)

def api_request():
    """Hace la peticion a las URL y busca automáticamente los enlaces de artículos de balance."""
    response = requests.get(BLOG_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if any(p in href for p in KEY_WORDS):
            if href.startswith("/"):
                href = BASE_URL + href
            links.append(href)

    return list(set(links))



def extract_api_data(url):
    """Extrae información estructurada en un archivo Json de un artículo de Supercell."""
    logger.info(f"Procesando: {url}")
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    data_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if not data_tag:
        logger.error(f"No se encontró JSON en {url}")
        return None

    data = json.loads(data_tag.string)
    props = data.get("props", {}).get("pageProps", {})
    game_name = props.get("gameName", "Clash Royale")
    title = props.get("title", "Sin título")
    publish_date = props.get("publishDate", "Desconocido")
    body = props.get("bodyCollection", [])

    ajustes = []
    current_category = "otro"

    for item in body:
        tipo = item.get("__typename", "")
        title_item = item.get("title", "")
        nuevo_tipo = classify_from_heading(title_item)
        if nuevo_tipo:
            current_category = nuevo_tipo

        if tipo == "FeatureBlock":
            nombre = item.get("title", "").strip()
            feature_json = item.get("featureText", {}).get("json", {})
            cambio = ""

            if "content" in feature_json:
                for cont in feature_json["content"]:
                    if cont["nodeType"] == "paragraph":
                        cambio = "".join(
                            [x["value"] for x in cont["content"] if x["nodeType"] == "text"]
                        ).strip()

            cambio = normalize_arrows(cambio)
            tipo_detectado = current_category or classify_from_text(cambio)
            if tipo_detectado == "otro":
                tipo_detectado = classify_from_text(cambio)

            if nombre and cambio:
                ajustes.append({
                    "nombre": nombre,
                    "cambio": cambio,
                    "tipo": tipo_detectado
                })

    return {
        "gameName": game_name,
        "title": title,
        "publishDate": publish_date,
        "ajustes": ajustes
    }