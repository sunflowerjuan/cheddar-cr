import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
BASE_URL = "https://api.clashroyale.com/v1"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/collector/apidocs/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/collector/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/collector/apidocs/",
}


template = {
    "swagger": "2.0",
    "info": {
        "title": "Data-Collector API from Cheddar-CR ",
        "description": "API para recolección de datos de Jugadores de Clash Royale",
        "version": "1.0.0",
    },
    "basePath": "/collector",
}


