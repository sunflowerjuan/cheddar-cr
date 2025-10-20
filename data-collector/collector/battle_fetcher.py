# collectors/battle_fetcher.py
import os
import json
from datetime import datetime, timezone
import requests
from utils.logger import get_logger

logger = get_logger(__name__)

class BattleFetcher:
    def __init__(self, api_client, output_dir="data-collector"):
        self.api_client = api_client
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def fetch_battlelog(self, player_tag: str):
        """Descarga y guarda el historial de batallas de un jugador."""
        endpoint = f"/players/{player_tag.replace('#', '%23')}/battlelog"
        data = self.api_client.get(endpoint)

        if not data:
            logger.warning(f"No se pudo obtener el battlelog de {player_tag}")
            return None

        formatted_battles = []
        for battle in data:
            try:
                battle_time = datetime.strptime(
                    battle["battleTime"], "%Y%m%dT%H%M%S.%fZ"
                ).replace(tzinfo=timezone.utc)

                trophy_change = battle.get("team", [{}])[0].get("trophyChange", 0)
                result = "win" if trophy_change > 0 else "loss" if trophy_change < 0 else "draw"

                opponent_info = battle.get("opponent", [{}])[0]
                player_info = battle.get("team", [{}])[0]

                formatted_battles.append({
                    "battle_time": battle_time.isoformat(),
                    "result": result,
                    "trophy_change": trophy_change,
                    "player": {
                        "name": player_info.get("name"),
                        "starting_trophies": player_info.get("startingTrophies"),
                        "deck": [c["name"] for c in player_info.get("cards", [])]
                    },
                    "opponent": {
                        "name": opponent_info.get("name"),
                        "clan": opponent_info.get("clan", {}).get("name"),
                        "deck": [c["name"] for c in opponent_info.get("cards", [])],
                        "starting_trophies": opponent_info.get("startingTrophies"),
                        "trophy_change": opponent_info.get("trophyChange")
                    }
                })
            except Exception as e:
                logger.error(f"Error procesando batalla: {e}")

        output_path = os.path.join(self.output_dir, f"battlelog_{player_tag.strip('#')}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(formatted_battles, f, indent=4, ensure_ascii=False)

        logger.info(f"Battlelog guardado en {output_path}")
        return formatted_battles
