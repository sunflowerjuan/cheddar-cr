from datetime import datetime, timedelta
import re
from scraper.extractor import ExtractorWeb

class FuenteSupercell:
    """
    Clase encargada de extraer artículos recientes (últimos 30 días)
    del blog oficial de Clash Royale en Supercell.
    """
    URL_BASE = "https://supercell.com/en/games/clashroyale/es/blog/"

    def __init__(self):
        # Crea un extractor web (ya definido en tu scraper)
        self.extractor = ExtractorWeb()
        # Fecha actual
        self.hoy = datetime.now()
        # Límite de antigüedad: solo artículos de los últimos 30 días
        self.limite = self.hoy - timedelta(days=30)

    def obtener_articulos_balance(self):
        """
        Busca artículos recientes relacionados con balance o ajustes
        dentro del blog de Supercell.
        Retorna una lista de URLs válidas.
        """
        # Descarga el HTML del blog principal
        soup = self.extractor.obtener_contenido_pagina(self.URL_BASE)
        if not soup:
            return []

        # Busca todos los enlaces que contengan palabras clave de interés
        candidatos = []
        for a in soup.select("a[href]"):
            href = a.get("href") or ""
            texto = (a.get_text() or "").lower()

            # Detecta enlaces relevantes a temas de balance o notas
            if any(k in href.lower() or k in texto for k in ["ajustes", "balance", "ajustes-de-equilibrio", "release-notes"]):
                if href.startswith("/"):
                    href = "https://supercell.com" + href
                candidatos.append(href)

        # Elimina duplicados manteniendo el orden
        candidatos = list(dict.fromkeys(candidatos))

        # Filtra artículos antiguos verificando la fecha real dentro del contenido
        validos = []
        for url in candidatos:
            soup_art = self.extractor.obtener_contenido_pagina(url)
            if not soup_art:
                continue

            # Intenta obtener la fecha desde distintas partes del HTML
            fecha = self._extraer_fecha_de_soup(soup_art)

            # Solo guarda los artículos que estén dentro del rango de 30 días
            if fecha and self.limite.date() <= fecha.date() <= self.hoy.date():
                validos.append((url, fecha))

        # Devuelve solo las URLs válidas
        return [u for u, f in validos]

    def _extraer_fecha_de_soup(self, soup):
        """
        Intenta detectar la fecha del artículo desde:
        - Meta tags
        - Etiquetas <time>
        - Texto del contenido
        """
        # 1️⃣ Intenta leer la fecha desde un meta tag estándar
        meta = soup.find("meta", {"property": "article:published_time"})
        if meta and meta.get("content"):
            fecha = self._parse_fecha(meta.get("content"))
            if fecha:
                return fecha

        # 2️⃣ Si no hay meta, busca etiqueta <time>
        time_tag = soup.find("time")
        if time_tag:
            dt = time_tag.get("datetime") or time_tag.get_text()
            fecha = self._parse_fecha(dt)
            if fecha:
                return fecha

        # 3️⃣ Si no hay ninguna etiqueta clara, busca texto con posible fecha
        texto = ""
        if soup.find("h1"):
            texto += soup.find("h1").get_text() + " "
            for sib in soup.find("h1").find_next_siblings(limit=6):
                texto += sib.get_text() + " "
        for p in soup.select("article p")[:8]:
            texto += p.get_text() + " "
        return self._buscar_fecha_en_texto(texto)

    def _parse_fecha(self, s):
        """Convierte una cadena a objeto datetime, probando varios formatos."""
        if not s:
            return None
        s = s.strip()

        # Formato ISO estándar: YYYY-MM-DD
        m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
        if m:
            y, mth, d = map(int, m.groups())
            return datetime(y, mth, d)

        # Formatos de texto comunes
        formatos = ["%B %d, %Y", "%d %B %Y", "%d %b %Y", "%b %d, %Y"]
        for fmt in formatos:
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        return None

    def _buscar_fecha_en_texto(self, texto):
        """Busca patrones de fecha en inglés dentro de un texto."""
        meses = [
            ("january",1),("february",2),("march",3),("april",4),("may",5),("june",6),
            ("july",7),("august",8),("september",9),("october",10),("november",11),("december",12),
            ("jan",1),("feb",2),("mar",3),("apr",4),("jun",6),("jul",7),("aug",8),("sep",9),("oct",10),("nov",11),("dec",12)
        ]

        # Busca coincidencias tipo "August 12, 2025" o "12 August 2025"
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
        Descarga el contenido y devuelve un diccionario con título y texto principal.
        """
        soup = self.extractor.obtener_contenido_pagina(url)
        if not soup:
            return {"titulo_real": "Sin título", "texto_completo": ""}
        return {
            "titulo_real": self.extractor.obtener_titulo_pagina(soup),
            "texto_completo": self.extractor.extraer_texto_principal(soup)
        }
