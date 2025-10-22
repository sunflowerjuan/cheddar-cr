# DATA COLLECTOR

## DESCRIPCION

Este modulo de **CHEDAR CR** se encarga de recolectar la informacion publicada en el API oficial de clash Royale y la procesa para generar un perfil del jugador (nivel, mazos, winrate, cartas desbloqueadas) y la cual envia como mensajeria a modelo de IA

## ESTRUCTURA

```
data-collector/
│
├── main.py                  # Punto de entrada
│
├── collector/
│   ├── __init__.py
│   ├── api_connector.py     # Conexión con la API
│   ├── player_analyzer.py   # Análisis de datos
│   ├── battle_fetcher.py    # Obtiene
│   ├── storage_manager.py   # Guarda y registra en DB
│   └── event_publisher.py   # eventos a RabbitMQ
│
├── utils/
│   ├── __init__.py
│   ├── config.py            # Carga TOKEN y configuración
│   ├── logger.py            # Configuración del logger
│   └── paths.py             # Rutas dinámicas para guardar archivos
│
├── data/                    # Datos generados localmente
│   └── players/
│       ├── player_9GQYJJR.json
│       └── battles_9GQYJJR.json
│
├── requirements.txt
└── .env
```

Entrada (API CR) → Procesamiento → Persistencia/Comunicación

### COLLECTOR

| Archivo                | Rol principal                                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------------------------- |
| **api_connector.py**   | Se encarga de conectarse con la API oficial de Clash Royale y obtener datos.                              |
| **player_analyzer.py** | Procesa la información cruda del jugador (nivel, mazo, trofeos, etc.) y genera un resumen útil.           |
| **battle_fetcher.py**  | Extrae y resume las últimas batallas del jugador (ganadas, perdidas, mazos usados).                       |
| **storage_manager.py** | Guarda las respuestas de la API y los análisis en archivos JSON dentro del volumen `/app/data`.           |
| **event_publisher.py** | Publica los resultados a otros servicios.                                                                 |
| **scheduler.py**       | Permite ejecutar el proceso automáticamente cada cierto tiempo si el contenedor está en modo “scheduler”. |
