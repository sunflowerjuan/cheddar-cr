import requests
from bs4 import BeautifulSoup

class ExtractorWeb:
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.0.1 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
    }

    def obtener_contenido_pagina(self, url):
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"[⚠️ ] Error HTTP {response.status_code} en {url}")
                return None
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException:
            return None


    def obtener_titulo_pagina(self, soup):
        """Devuelve el título de la página."""
        if soup.title:
            return soup.title.get_text().strip()
        h1 = soup.find("h1")
        return h1.get_text().strip() if h1 else "Sin título"

    def extraer_texto_principal(self, soup):
        """Extrae el contenido principal del artículo."""
        # Intentar con article principal (RoyaleAPI)
        article = soup.find("article")
        if article:
            return article.get_text(separator=" ", strip=True)

        # Si no hay <article>, buscar secciones comunes (Supercell)
        main = soup.find("main") or soup.find("div", {"class": "blog"})
        if main:
            return main.get_text(separator=" ", strip=True)

        # Fallback: cuerpo completo
        return soup.get_text(separator=" ", strip=True)
