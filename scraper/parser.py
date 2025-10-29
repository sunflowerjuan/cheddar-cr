import re
from data.config import CONFIG


class ParserBalance:
    def __init__(self):
        # Lista de cartas
        self.cartas = [
            'Arquero mágico', 'Arqueras', 'Ariete de batalla', 'Bárbaros', 'Bárbaros de élite',
            'Bandida', 'Bandida líder', 'Barril de bárbaro', 'Barril de duendes', 'Barril de esqueletos',
            'Bebé dragón', 'Berserker', 'Bombardero', 'Bruja', 'Bruja madre', 'Bruja nocturna',
            'Cañón', 'Cañón con ruedas', 'Caballero', 'Caballero dorado', 'Cazador', 'Cementerio',
            'Chispitas', 'Choza de bárbaros', 'Choza de duendes', 'Clon', 'Cohete', 'Curandera guerrera',
            'Demoledor duende', 'Descarga', 'Dragón eléctrico', 'Dragón infernal', 'Dragones esqueleto',
            'Duende gigante', 'Duende lanzadardos', 'Duendes', 'Duendes con lanza', 'Duendenstein',
            'Ejército de esqueletos', 'Electrocutadores', 'Emperatriz espiritual', 'Enredadera',
            'Esbirros', 'Esqueleto gigante', 'Esqueletos', 'Espíritu de fuego', 'Espíritu eléctrico',
            'Espíritu de hielo', 'Espíritu sanador', 'Excavadora de duendes', 'Fantasma real',
            'Fénix', 'Flechas', 'Furia', 'Gigante', 'Gigante eléctrico', 'Gigante noble',
            'Gigante real', 'Globo bombástico', 'Gólem', 'Gólem de elixir', 'Gólem de hielo',
            'Gran minero', 'Guardias', 'Hielo', 'Horda de esbirros', 'Horno', 'Jabalí real',
            'Jaula del forzudo', 'Lanzafuegos', 'Lápida', 'Leñador', 'Máquina boladora',
            'Máquina duende', 'Maldición duende', 'Megaesbirro', 'Megacaballero', 'Mini P.E.K.K.A.',
            'Minero', 'Monje', 'Montacarneros', 'Montapuercos', 'Mortero', 'Mosquetera',
            'Murciélagos', 'P.E.K.K.A.', 'Paquete real', 'Pandilla de duendes', 'Pescador',
            'Pillos', 'Príncipe', 'Príncipe oscuro', 'Principito', 'Princesa', 'Puercos reales',
            'Rayo', 'Reclutas reales', 'Recolector de elixir', 'Reina arquera', 'Rey esqueleto',
            'Rompemuros', 'Sabueso de lava', 'Terremoto', 'Tornado', 'Torre bombardera',
            'Torre infernal', 'Torre tesla', 'Trio de mosqueteras', 'Tronco', 'Vacío',
            'Valquiria', 'Verdugo', 'Venero', 'Ballesta', 'Bola de fuego', 'Bola de nieve', 'Espejo'
        ]

        # versiones en minúsculas
        self.cartas_lower = [c.lower() for c in self.cartas]
        self.frag_before = CONFIG.get('fragment_window_before', 300)
        self.frag_after = CONFIG.get('fragment_window_after', 600)
        self.max_detalles = CONFIG.get('max_detalles_por_carta', 3)

        # patrones numéricos
        self.patrones = [
            r'de\s+(\d+\.?\d*)\s+a\s+(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*a\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*→\s*(\d+\.?\d*)',
            r'(\d+)%\s*(?:a|→)\s*(\d+)%'
        ]

    def detectar_cartas(self, texto):
        """Detecta qué cartas se mencionan en el texto."""
        if not texto:
            return []
        texto_lower = texto.lower()
        encontradas = []
        for i, carta in enumerate(self.cartas_lower):
            if carta in texto_lower:
                encontradas.append(self.cartas[i])
        return list(dict.fromkeys(encontradas))

    def _extraer_fragmentos_para_carta(self, texto, carta):
        """Devuelve fragmentos del texto alrededor de la carta."""
        texto_lower = texto.lower()
        nombre_lower = carta.lower()
        start = 0
        fragmentos = []

        while True:
            idx = texto_lower.find(nombre_lower, start)
            if idx == -1:
                break
            frm = max(0, idx - self.frag_before)
            to = min(len(texto), idx + len(carta) + self.frag_after)
            fragmentos.append(texto[frm:to].strip())
            start = idx + len(carta)
        return fragmentos

    def extraer_cambios_inteligentes(self, texto):
        """Versión mejorada: reconoce patrones tipo RoyaleAPI y detecta fortalezas/debilitaciones."""
        if not texto:
            return {}

        texto = texto.replace('\r', '')
        lineas = [l.strip() for l in texto.split('\n') if l.strip()]
        texto_lower = texto.lower()

        cartas_encontradas = self.detectar_cartas(texto)
        cambios = {}

        for carta in cartas_encontradas:
            carta_lower = carta.lower()
            detalles = []

            for i, linea in enumerate(lineas):
                if carta_lower in linea.lower():
                    contexto = ' '.join(lineas[max(0, i-2):min(len(lineas), i+3)])
                    contexto_lower = contexto.lower()

                    tipo = "Ajuste"
                    if any(w in contexto_lower for w in ['reduce', 'disminuye', 'nerf', 'reducción', 'slower', 'decreased']):
                        tipo = "Debilitación"
                    elif any(w in contexto_lower for w in ['aumenta', 'incrementa', 'buff', 'mejora', 'fortalec', 'faster', 'increased']):
                        tipo = "Fortalecimiento"

                    hallazgos = []
                    for patro in self.patrones:
                        for m in re.findall(patro, contexto, flags=re.IGNORECASE):
                            if len(m) >= 2 and m[0] != m[1]:
                                hallazgos.append(f"{m[0]} → {m[1]}")

                    if hallazgos:
                        for h in hallazgos[:self.max_detalles]:
                            detalles.append({"cambio": tipo, "detalle": h})
                    else:
                        detalles.append({"cambio": tipo, "detalle": contexto[:200]})

                    if len(detalles) >= self.max_detalles:
                        break

            if detalles:
                cambios[carta] = detalles
            else:
                cambios[carta] = [{"cambio": "Ajuste", "detalle": "Mencionada sin detalles detectables"}]

        # Caso especial: listas tipo “• Carta: +15%” (formato RoyaleAPI)
        if not cambios or all(not v for v in cambios.values()):
            for linea in lineas:
                m = re.match(r"[-•]\s*([A-Za-zÁÉÍÓÚáéíóúñÑ ]+):\s*([+−\-]?\d+%?)", linea)
                if m:
                    carta, valor = m.groups()
                    tipo = "Fortalecimiento" if "+" in valor else "Debilitación"
                    cambios[carta.strip()] = [{"cambio": tipo, "detalle": valor}]

        return cambios
