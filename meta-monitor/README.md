# META MONITOR

Servicio encargado de recopilar y procesar información relacionada con el **meta de Clash Royale**, incluyendo:

- Cambios de balance publicados en el blog oficial de Supercell.
- Tendencias de estadísticas de cartas (uso, winrate y variación) obtenidas desde plataformas públicas de análisis.

Este servicio forma parte del ecosistema **Cheddar-CR**, orientado al análisis competitivo y monitoreo del entorno del juego.

## ESTRUCTURA

```
meta-monitor/
│── app/
│   ├── routes/
│   │   └── monitor_router.py
│   ├── monitor/
│   │   ├── meta_services.py
│   │   ├── card_statistics.py
│   │   ├── utils.py
│   │   └── balance_changes.py
│   └── utils/
│       ├── config.py
│       └── logger.py
│── Dockerfile
│── requirements.txt
│── README.md

```

## Endpoints

### `GET /monitor/meta`

Obtiene información del **artículo oficial de cambios de balance**

### `GET /monitor/meta`

Extrae estadísticas de cartas desde fuentes como StatsRoyale (vía scraping optimizado sin Selenium cuando es posible).

Si desea documentacion mas exaustiva una vez ejecutado todo el proyecto acceda a http://cr.localhost/monitor/apidocs/ en donde se especifican y se ejemplifican los endpoints de la api
