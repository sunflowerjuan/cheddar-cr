from datetime import datetime, timedelta
import re
from scraper.extractor import ExtractorWeb

class FuenteRoyaleAPI:
    """
    Clase encargada de obtener artículos recientes (últimos 30 días)
    del blog de RoyaleAPI relacionados con balances o temporadas.
    """
    URL_BASE = "https://royaleapi.com/blog"

    def __init__(self):
        # Configuración base: extractor, fecha actual y límite de 30 días
        self.extractor = ExtractorWeb()
        self.hoy = datetime.now()
        self.limite = self.hoy - timedelta(days=30)

    def obtener_articulos_balance(self):
        """
        Recolecta enlaces de artículos relacionados con 'balance' o 'season'
        y los filtra para dejar solo los del último mes.
        """
        soup = self.extractor.obtener_contenido_pagina(self.URL_BASE)
        if not soup:
            return []

        # Recolecta candidatos a artículos
        candidatos = []
        for a in soup.select("a[href]"):
            href = a.get("href") or ""
            texto = (a.get_text() or "").lower()

            # Solo interesan enlaces que mencionen "balance" o "season"
            if "balance" in href.lower() or "balance" in texto or "season" in href.lower():
                if href.startswith("/"):
                    href = "https://royaleapi.com" + href
                candidatos.append(href)

        # Elimina duplicados
        candidatos = list(dict.fromkeys(candidatos))

        # Verifica la fecha real dentro de cada candidato
        validos = []
        for url in candidatos:
            soup_art = self.extractor.obtener_contenido_pagina(url)
            if not soup_art:
                continue
            fecha = self._extraer_fecha_de_soup(soup_art)
            if fecha and self.limite.date() <= fecha.date() <= self.hoy.date():
                validos.append((url, fecha))

        return [u for u, f in validos]

    def _extraer_fecha_de_soup(self, soup):
        """
        Busca la fecha en meta tags, etiquetas <time> o texto.
        """
        meta = soup.find("meta", {"property": "article:published_time"})
        if meta and meta.get("content"):
            fecha = self._parse_fecha(meta.get("content"))
            if fecha:
                return fecha

        time_tag = soup.find("time")
        if time_tag:
            dt = time_tag.get("datetime") or time_tag.get_text()
            fecha = self._parse_fecha(dt)
            if fecha:
                return fecha

        texto = ""
        if soup.find("h1"):
            texto += soup.find("h1").get_text() + " "
            for sib in soup.find("h1").find_next_siblings(limit=6):
                texto += sib.get_text() + " "
        for p in soup.select("article p")[:8]:
            texto += p.get_text() + " "
        return self._buscar_fecha_en_texto(texto)

    def _parse_fecha(self, s):
        """Convierte texto en fecha (YYYY-MM-DD o texto con mes)."""
        if not s:
            return None
        s = s.strip()
        m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
        if m:
            y, mth, d = map(int, m.groups())
            return datetime(y, mth, d)

        formatos = ["%B %d, %Y", "%d %B %Y", "%d %b %Y", "%b %d, %Y"]
        for fmt in formatos:
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        return None

    def _buscar_fecha_en_texto(self, texto):
        """Detecta fechas tipo 'August 15, 2025' o '15 August 2025'."""
        meses = [
            ("january",1),("february",2),("march",3),("april",4),("may",5),("june",6),
            ("july",7),("august",8),("september",9),("october",10),("november",11),("december",12),
            ("jan",1),("feb",2),("mar",3),("apr",4),("jun",6),("jul",7),("aug",8),("sep",9),("oct",10),("nov",11),("dec",12)
        ]
        for nombre, num in meses:
            m = re.search(rf"{nombre}\s+(\d{{1,2}}),\s*(\d{{4}})", texto, re.IGNORECASE)
            if m:
                return datetime(int(m.group(2)), num, int(m.group(1)))
            m2 = re.search(rf"(\d{{1,2}})\s+{nombre}\s+(\d{{4}})", texto, re.IGNORECASE)
            if m2:
                return datetime(int(m2.group(2)), num, int(m2.group(1)))
        return None

    def extraer_articulo(self, url):
        """
        Devuelve el título real y contenido de un artículo.
        """
        soup = self.extractor.obtener_contenido_pagina(url)
        if not soup:
            return {"titulo_real": "Sin título", "texto_completo": ""}
        return {
            "titulo_real": self.extractor.obtener_titulo_pagina(soup),
            "texto_completo": self.extractor.extraer_texto_principal(soup)
        }
