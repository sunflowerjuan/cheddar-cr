import requests
from bs4 import BeautifulSoup
from config import BASE_URL, BLOG_URL, PALABRAS_CLAVE

def obtener_links_balance():
    """Busca automáticamente los enlaces de artículos de balance."""
    response = requests.get(BLOG_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if any(p in href for p in PALABRAS_CLAVE):
            if href.startswith("/"):
                href = BASE_URL + href
            links.append(href)

    return list(set(links))
