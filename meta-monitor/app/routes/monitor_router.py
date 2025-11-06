from flask import Blueprint, jsonify
from flasgger import swag_from
from monitor.meta_services import meta_data, cards_stadistics
import json

router_bp = Blueprint('router', __name__, url_prefix='/')


@router_bp.route('/meta', methods=['GET'])
@swag_from('docs/meta.yaml')
def balance_endpoint():
    """Recolecta datos asociados a los cambios de balance."""
    data = meta_data()                    
    return jsonify(json.loads(data)), 200  

@router_bp.route('/stadistics', methods=['GET'])
@swag_from('docs/stadistics.yaml')
def statistics_endpoint():
    """Recolecta estadísticas de cartas."""
    data = cards_stadistics()
    return jsonify(data), 200
