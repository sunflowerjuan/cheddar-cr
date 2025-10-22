# collectors/battle_fetcher.py
from datetime import datetime, timezone
from utils.logger import get_logger

logger = get_logger(__name__)

class BattleFetcher:
    """Procesa batallas y genera un resumen estructurado."""

    def process_battlelog(self, battle_data: list):
        if not battle_data:
            logger.warning("No se recibió información de batallas")
            return None

        formatted_battles = []
        wins, losses, draws = 0, 0, 0

        for battle in battle_data:
            try:
                battle_time = datetime.strptime(
                    battle["battleTime"], "%Y%m%dT%H%M%S.%fZ"
                ).replace(tzinfo=timezone.utc)

                # Datos principales
                player_info = battle.get("team", [{}])[0]
                opponent_info = battle.get("opponent", [{}])[0]

                player_crowns = player_info.get("crowns", 0)
                opponent_crowns = opponent_info.get("crowns", 0)

                # Resultado de partidas
                if player_crowns > opponent_crowns:
                    result = "win"
                    wins += 1
                elif player_crowns < opponent_crowns:
                    result = "loss"
                    losses += 1
                else:
                    result = "draw"
                    draws += 1

                # Elixir filtrado 
                player_elixir_leaked = player_info.get("elixirLeaked", 0)
                opponent_elixir_leaked = opponent_info.get("elixirLeaked", 0)

                # Arena
                arena = battle.get("arena", {}).get("name")

                # Formatear resultado
                formatted_battles.append({
                    "battle_type": battle.get("type"),
                    "game_mode": battle.get("gameMode", {}).get("name"),
                    "result": result,
                    "player": {
                        "name": player_info.get("name"),
                        "elixir_leaked": player_elixir_leaked,
                        "deck": [
                            {
                                "name": c["name"],
                                "level": c.get("level"),
                                "rarity": c.get("rarity"),
                                "elixirCost": c.get("elixirCost")
                            } for c in player_info.get("cards", [])
                        ]
                    },
                    "opponent": {
                        "name": opponent_info.get("name"),
                        "elixir_leaked": opponent_elixir_leaked,
                        "deck": [
                            {
                                "name": c["name"],
                                "level": c.get("level"),
                                "rarity": c.get("rarity"),
                                "elixirCost": c.get("elixirCost")
                            } for c in opponent_info.get("cards", [])
                        ]
                    }
                })

            except Exception as e:
                logger.error(f"Error procesando batalla: {e}")

        total_battles = wins + losses + draws
        win_rate = round((wins / total_battles) * 100, 2) if total_battles > 0 else 0.0

        summary = {
            "summary": {
                "total_battles": total_battles,
                "wins": wins,
                "losses": losses,
                "draws": draws,
                "win_rate": win_rate
            },
            "battles": formatted_battles
        }

        logger.info(
            f"Procesadas {total_battles} batallas: "
            f"{wins}W/{losses}L/{draws}D ({win_rate}% winrate)"
        )

        return summary
