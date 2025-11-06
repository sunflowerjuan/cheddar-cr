# DATA COLLECTOR

## DESCRIPCION

Este modulo de **CHEDAR CR** se encarga de recolectar la informacion publicada en el API oficial de clash Royale y la procesa para generar un perfil del jugador (nivel, mazos, winrate, cartas desbloqueadas) y la cual alimenta al modelon RAG para dar un contexto del jugador expuesto como un API mediante Traefik.

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
│   ├── cr_services.py       # Servicio expuesto al endpoint
│   └── battle_fetcher.py    # Obtiene
│
├── utils/
│   ├── __init__.py
│   ├── config.py            # Carga TOKEN y configuración
│   └── logger.py            # Configuración del logger
│
├── routes/
│   └── cr_router.py
│
├── requirements.txt
└── DockerFile
```

Entrada (API CR) → Procesamiento → HTTP

### COLLECTOR

| Archivo                | Rol principal                                                                                   |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| **api_connector.py**   | Se encarga de conectarse con la API oficial de Clash Royale y obtener datos.                    |
| **player_analyzer.py** | Procesa la información cruda del jugador (nivel, mazo, trofeos, etc.) y genera un resumen útil. |
| **battle_fetcher.py**  | Extrae y resume las últimas batallas del jugador (ganadas, perdidas, mazos usados).             |

## ENDPOINTS

Nuestra API se enruta mediante el reverse proxy de Traefik con el prefijo `/collector` con los siguientes endpoints:

- `/player/{player_tag}` - Recolecta y procesa los datos de un jugador a partir de su Tag
- `/battles/{player_tag}` - Recolecta y procesa el historial de partidas de un jugador a partir de su Tag

Si desea documentacion mas exaustiva una vez ejecutado todo el proyecto acceda a http://cr.localhost/collector/apidocs/ en donde se especifican y se ejemplifican los endpoints de la api
