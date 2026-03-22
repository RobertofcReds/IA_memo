"""Routes de l'API"""

from flask import Blueprint, request, jsonify
import time

api_bp = Blueprint('api', __name__)

# Instance du service (sera initialisée au démarrage)
recommendation_service = None

def init_service(service):
    """Initialise le service pour l'API"""
    global recommendation_service
    recommendation_service = service

@api_bp.route('/health', methods=['GET'])
def health():
    """Vérification de santé"""
    return jsonify({
        'status': 'ok',
        'message': 'API de recommandation opérationnelle'
    })

@api_bp.route('/sites', methods=['GET'])
def get_sites():
    """Liste tous les sites"""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        result, status = recommendation_service.list_sites(limit, offset)
        return jsonify(result), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sites/<string:site_id>', methods=['GET'])
def get_site(site_id):
    """Détails d'un site"""
    try:
        result, status = recommendation_service.get_site(site_id)
        return jsonify(result), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/recommendations/by-site', methods=['POST'])
def recommend_by_site():
    """Recommandations par site"""
    start = time.time()
    
    try:
        data = request.get_json()
        
        if not data or 'site_id' not in data:
            return jsonify({'error': 'site_id requis'}), 400
        
        site_id = data['site_id']
        n = min(int(data.get('n_recommendations', 10)), 50)
        
        result, status = recommendation_service.recommend_by_site(site_id, n)
        
        if status == 200:
            execution_time = (time.time() - start) * 1000
            return jsonify({
                'recommendations': result,
                'query': site_id,
                'total': len(result),
                'time_ms': round(execution_time, 2)
            }), 200
        else:
            return jsonify(result), status
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/search', methods=['POST'])
def search():
    """Recherche sémantique"""
    start = time.time()
    
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'query requise'}), 400
        
        query = data['query']
        n = min(int(data.get('n_results', 10)), 50)
        filters = data.get('filters', {})
        
        result, status = recommendation_service.search(query, n, filters)
        
        if status == 200:
            execution_time = (time.time() - start) * 1000
            return jsonify({
                'results': result,
                'query': query,
                'total': len(result),
                'time_ms': round(execution_time, 2)
            }), 200
        else:
            return jsonify(result), status
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
def stats():
    """Statistiques"""
    try:
        result, status = recommendation_service.get_stats()
        return jsonify(result), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500