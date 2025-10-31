from flask import Blueprint, jsonify
from flasgger import swag_from
from collector.api_connector import CRAPIConnector
from collector.player_analyzer import PlayerAnalyzer
from collector.battle_fetcher import BattleFetcher
from collector import cr_services 

router_bp = Blueprint('router', __name__, url_prefix='/')

@router_bp.route('/player/<player_tag>', methods=['GET'])
@swag_from('docs/player.yaml')
def collect_player(player_tag):
    """Recolecta datos del jugador."""
    api = CRAPIConnector()
    analyzer = PlayerAnalyzer()
    player_tag = f"#{player_tag}"

    if not cr_services.check_player_exists(api, player_tag):
        return jsonify({"error": f"Jugador {player_tag} no encontrado"}), 404

    player_data = cr_services.collect_player_data(api, analyzer, player_tag)
    return jsonify(player_data or {}), 200


@router_bp.route('/battles/<player_tag>', methods=['GET'])
@swag_from('docs/battles.yaml')
def collect_battles(player_tag):
    """Recolecta +datos de batallas."""
    api = CRAPIConnector()
    battles = BattleFetcher()
    player_tag = f"#{player_tag}"

    if not cr_services.check_player_exists(api, player_tag):
        return jsonify({"error": f"Jugador {player_tag} no encontrado"}), 404

    battle_data = cr_services.collect_battle_log(api, battles, player_tag)
    return jsonify(battle_data or {}), 200
