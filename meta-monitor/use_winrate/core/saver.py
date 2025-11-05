import os
import json

def guardar_json(data, path):
    """Guarda los datos en un archivo JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✅ Guardado {len(data)} registros en {path}")
