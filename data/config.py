# Configuraciones del proyecto
CONFIG = {
    'timeout': 15,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'archivo_salida': 'balances_reales.json',
    'url_base': 'https://supercell.com/en/games/clashroyale/es/blog/',
    'carpeta_json': 'data/json',
    # Opciones adicionales
    'guardar_historico': True,   # si True crea archivos con timestamp en lugar de sobrescribir
    'fragment_window_before': 300,
    'fragment_window_after': 600,
    'max_detalles_por_carta': 3,
    'debug_logs': True
}
