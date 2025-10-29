import json
import os
from datetime import datetime

class GestorJSON:
    def __init__(self, archivo_salida='balances_reales.json', carpeta_json='data/json', guardar_historico=True):
        self.carpeta_json = carpeta_json
        os.makedirs(self.carpeta_json, exist_ok=True)
        self.guardar_historico = guardar_historico
        self.archivo_base = archivo_salida
        self.archivo_salida = os.path.join(self.carpeta_json, self.archivo_base)

    def _archivo_con_timestamp(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre, ext = os.path.splitext(self.archivo_base)
        return os.path.join(self.carpeta_json, f"{nombre}_{ts}{ext or '.json'}")

    def guardar_resultados(self, titulo_real, cambios_por_carta, url):
        """Guarda los resultados en un archivo JSON. Si guardar_historico=True crea archivo con timestamp."""
        resultado = {
            'titulo_real': titulo_real,
            'enlace': url,
            'cambios_por_carta': cambios_por_carta,
            'total_cartas': len(cambios_por_carta),
            'timestamp_extraccion': datetime.now().isoformat()
        }

        ruta = self._archivo_con_timestamp() if self.guardar_historico else self.archivo_salida

        try:
            # Si no es histórico y ya hay contenido y es lista, lo manejamos
            if not self.guardar_historico and os.path.exists(ruta):
                # intentar cargar y convertir a lista si necesario
                with open(ruta, 'r', encoding='utf-8') as f:
                    contenido = json.load(f)
                if isinstance(contenido, list):
                    contenido.append(resultado)
                    with open(ruta, 'w', encoding='utf-8') as f:
                        json.dump(contenido, f, indent=2, ensure_ascii=False)
                    return resultado
            # Escritura normal (nuevo archivo o histórico)
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            self.archivo_salida = ruta
            return resultado
        except Exception as e:
            raise

    def cargar_resultados_anteriores(self, archivo=None):
        """Carga resultados anteriores si existen. Por defecto usa archivo_salida."""
        ruta = archivo or self.archivo_salida
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return None

    def listar_archivos_json(self):
        """Lista todos los archivos JSON en la carpeta"""
        try:
            archivos = [f for f in os.listdir(self.carpeta_json) if f.endswith('.json')]
            return archivos
        except FileNotFoundError:
            return []
