from utils.logger import get_logger

logger = get_logger(__name__)

class PlayerAnalyzer:
    def analyze(self, player_data: dict):
        """Analiza la información completa del jugador para generar un perfil avanzado."""

        name = player_data.get("name")
        level = player_data.get("expLevel")
        trophies = player_data.get("trophies")

        # Arena actual
        arena_info = player_data.get("arena", {})
        arena_name = arena_info.get("name", "Desconocida")

        # Temporada anterior 
        previous_season = player_data.get("previousSeason", {})
        prev_trophies = previous_season.get("trophies")
        prev_best = previous_season.get("bestTrophies")

        # Mazo actual
        current_deck = [
            {"name": card["name"], "level": card["level"]}
            for card in player_data.get("currentDeck", [])
        ]

        # Todas las cartas desbloqueadas
        all_cards = [
            {"name": c["name"], "level": c["level"]}
            for c in player_data.get("cards", [])
        ]

        # desempeño 
        wins = player_data.get("wins", None)
        losses = player_data.get("losses", None)
        battle_count = None
        win_rate = None

        if wins is not None and losses is not None:
            battle_count = player_data.get("battleCount")
            win_rate = round((wins / battle_count) * 100, 2) if battle_count > 0 else 0.0


        summary = {
            "name": name,
            "level": level,
            "arena": arena_name,
            "trophies": trophies,
            "previousSeason": {
                "trophies": prev_trophies,
                "bestTrophies": prev_best
            },
            "cards": {
                "currentDeck": current_deck,
                "allCards": all_cards
            },
            "performance": {
                "wins": wins,
                "losses": losses,
                "battles": battle_count,
                "win_rate": win_rate
            },
        }
        print(summary)

        logger.info(
            f"[Análisis] Jugador: {name} | Arena: {arena_name} | Copas: {trophies} | "
            f"Winrate: {win_rate}% | Mazo: {[c['name'] for c in current_deck]}"
        )

        return summary
