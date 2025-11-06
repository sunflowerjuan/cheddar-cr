BASE_URL = "https://supercell.com"
BLOG_URL = f"{BASE_URL}/en/games/clashroyale/blog/"
KEY_WORDS = ["balance", "equilibrio", "ajuste", "release-notes", "cambios"]


# URL PARA ESTADISTICAS DE LAS CARTAS
STATICS_URLS = {
    "competitivo": "https://statsroyale.com/es/top/cards?type=path-of-legends",
    "camino_trofeos": "https://statsroyale.com/es/top/cards?type=ladder"
}
WAIT_TIME = 5 

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/monitor/apidocs/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/monitor/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/monitor/apidocs/",
}


template = {
    "swagger": "2.0",
    "info": {
        "title": "Meta-Monitor API from Cheddar-CR ",
        "description": "API para recolección informacion acerca de cambios en el meta de Clash Royale, basado en análisis de blogs oficiales y estadísticas de cartas.",
        "version": "1.0.0",
    },
    "basePath": "/monitor",
}