from collector.api_connector import CRAPIConnector
from collector.player_analyzer import PlayerAnalyzer
from collector.battle_fetcher import BattleFetcher
from collector.storage_manager import StorageManager
from collector.event_publisher import EventPublisher
from utils.logger import get_logger

logger = get_logger(__name__)

def run_collector():
    player_tag = "#Y9LJQ8GYC"

    api = CRAPIConnector()
    analyzer = PlayerAnalyzer()
    battles = BattleFetcher()
    storage = StorageManager()
    publisher = EventPublisher()

    logger.info("Iniciando recolección de datos...")

    #Player Data
    player_data = api.get_player_data(player_tag)
    if player_data:
        summary = analyzer.analyze(player_data)
        storage.save_json(player_tag, "player", summary)
        publisher.publish("player_update", summary)

    #Battle Log
    battle_log = api.get_battle_log(player_tag)
    if battle_log:
        battle_summary = battles.process_battlelog(battle_log)
        storage.save_json(player_tag, "battles", battle_summary)
        publisher.publish("battle_update", battle_summary)

def main():
    import os
    mode = os.getenv("MODE", "single")

    if mode == "scheduler":
        from collector.scheduler import start_scheduler
        interval = int(os.getenv("INTERVAL", 600))
        start_scheduler(interval)
    else:
        run_collector()

if __name__ == "__main__":
    main()
