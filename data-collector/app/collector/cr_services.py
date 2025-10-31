from utils.logger import get_logger


logger = get_logger(__name__)

def check_player_exists(api, player_tag):
    player_data = api.get_player_data(player_tag)
    return player_data is not None

def collect_player_data(api, analyzer,player_tag):
    player_data = api.get_player_data(player_tag)
    if not player_data:
        return None
    summary = analyzer.analyze(player_data)
    return summary

def collect_battle_log(api, battles,player_tag):
    battle_log = api.get_battle_log(player_tag)
    if not battle_log:
        return None
    summary = battles.process_battlelog(battle_log)
    return summary
