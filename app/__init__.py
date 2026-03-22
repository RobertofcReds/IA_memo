from flask import Flask, jsonify, request
from flask_cors import CORS  # Ajoute cette ligne
import time

# Service global
recommendation_service = None

def init_service(service):
    """Initialise le service pour l'API"""
    global recommendation_service
    recommendation_service = service

def create_app():
    """Crée l'application Flask avec toutes les routes"""
    app = Flask(__name__)

    CORS(app, origins=['https://memo-frontend-bw86kwry0-robertofcreds-projects.vercel.app/'])  # Permet les requêtes depuis le frontend React
    
    # ============================================
    # ROUTE DE TEST
    # ============================================
    @app.route('/test', methods=['GET'])
    def test():
        return jsonify({"message": "Route test OK"})
    
    # ============================================
    # ROUTES API
    # ============================================
    @app.route('/api/v1/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'ok',
            'message': 'API fonctionne!'
        })
    
    @app.route('/api/v1/sites', methods=['GET'])
    def get_sites():
        try:
            if not recommendation_service or not recommendation_service.recommender:
                return jsonify({'error': 'Service non initialisé'}), 503
            
            limit = int(request.args.get('limit', 100))
            offset = int(request.args.get('offset', 0))
            
            result = recommendation_service.recommender.get_all_sites(limit, offset)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/sites/<string:site_id>', methods=['GET'])
    def get_site(site_id):
        try:
            if not recommendation_service or not recommendation_service.recommender:
                return jsonify({'error': 'Service non initialisé'}), 503
            
            site = recommendation_service.recommender.get_site_details(site_id)
            
            if not site:
                return jsonify({'error': 'Site non trouvé'}), 404
            
            return jsonify(site)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/recommendations/by-site', methods=['POST'])
    def recommend_by_site():
        start = time.time()
        
        try:
            if not recommendation_service or not recommendation_service.recommender:
                return jsonify({'error': 'Service non initialisé'}), 503
            
            data = request.get_json()
            
            if not data or 'site_id' not in data:
                return jsonify({'error': 'site_id requis'}), 400
            
            site_id = data['site_id']
            n = min(int(data.get('n_recommendations', 10)), 50)
            
            recommendations = recommendation_service.recommender.get_similar_sites(site_id, n)
            
            if not recommendations:
                return jsonify({'error': 'Site non trouvé'}), 404
            
            execution_time = (time.time() - start) * 1000
            
            return jsonify({
                'recommendations': recommendations,
                'query': site_id,
                'total': len(recommendations),
                'time_ms': round(execution_time, 2)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/search', methods=['POST'])
    def search():
        start = time.time()
        
        try:
            if not recommendation_service or not recommendation_service.recommender:
                return jsonify({'error': 'Service non initialisé'}), 503
            
            data = request.get_json()
            
            if not data or 'query' not in data:
                return jsonify({'error': 'query requise'}), 400
            
            query = data['query']
            n = min(int(data.get('n_results', 10)), 50)
            filters = data.get('filters', {})
            
            results = recommendation_service.recommender.semantic_search(query, n, filters)
            
            execution_time = (time.time() - start) * 1000
            
            return jsonify({
                'results': results,
                'query': query,
                'total': len(results),
                'time_ms': round(execution_time, 2)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/stats', methods=['GET'])
    def stats():
        try:
            if not recommendation_service or not recommendation_service.recommender:
                return jsonify({'error': 'Service non initialisé'}), 503
            
            recommender = recommendation_service.recommender
            
            stats_data = {
                'total_sites': len(recommender.data),
            }
            
            if 'note_moyenne' in recommender.data.columns:
                stats_data['note_moyenne'] = float(recommender.data['note_moyenne'].mean())
            
            if 'type_activite' in recommender.data.columns:
                stats_data['types_populaires'] = recommender.data['type_activite'].value_counts().head(5).to_dict()
            
            return jsonify(stats_data)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/recommendations/by-criteria', methods=['POST'])
    def recommend_by_criteria():
        """
        Recommandation basée sur des critères multiples
        """
        import time
        start = time.time()
        
        try:
            # Vérifier que le service est initialisé
            if not recommendation_service or not recommendation_service.recommender:
                return jsonify({'error': 'Service non initialisé'}), 503
            
            # Récupérer les données de la requête
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Données requises'}), 400
            
            # Extraire les critères
            criteria = {}
            
            # Critères de filtrage
            if 'type' in data:
                criteria['type'] = data['type']
            if 'prix_max' in data:
                criteria['prix_max'] = float(data['prix_max'])
            if 'prix_min' in data:
                criteria['prix_min'] = float(data['prix_min'])
            if 'note_min' in data:
                criteria['note_min'] = float(data['note_min'])
            if 'region' in data:
                criteria['region'] = data['region']
            if 'difficulte' in data:
                criteria['difficulte'] = data['difficulte']
            if 'duree_max' in data:
                criteria['duree_max'] = float(data['duree_max'])
            if 'site_reference' in data:
                criteria['site_reference'] = data['site_reference']
            
            # Nombre de recommandations
            n = min(int(data.get('n_recommendations', 10)), 50)
            
            # Appeler la méthode du modèle
            recommendations = recommendation_service.recommender.recommend_by_criteria(
                criteria, 
                n_recommendations=n
            )
            
            execution_time = (time.time() - start) * 1000
            
            return jsonify({
                'success': True,
                'criteria': criteria,
                'recommendations': recommendations,
                'total': len(recommendations),
                'time_ms': round(execution_time, 2)
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/itineraries/generate', methods=['POST'])
    def generate_itinerary():
        """
        Génère un itinéraire basé sur les critères du frontend
        """
        try:
            data = request.get_json()
            print(f"Data reçue pour génération d'itinéraire: {data}")
            
            if not data:
                return jsonify({'error': 'Données requises'}), 400
            
            # Mapper les critères frontend
            criteria = {
                'travel_type': data['userPreferences'].get('travelType'),
                'interests': data['userPreferences'].get('interests', []),
                'budget': data['userPreferences'].get('budget'),
                'duration': data['userPreferences'].get('duration'),
                'season': data['userPreferences'].get('season'),
                'region': data['userPreferences'].get('region'),
                'accommodation': data['userPreferences'].get('accommodation')
            }
            
            # Filtrer les valeurs nulles
            criteria = {k: v for k, v in criteria.items() if v is not None and v != []}
            
            # Utiliser le service d'itinéraires
            from app.services.itinerary_service import ItineraryService
            
            # Récupérer le recommender depuis le service global
            recommender = None
            if hasattr(recommendation_service, 'recommender'):
                recommender = recommendation_service.recommender
            
            itinerary_service = ItineraryService(recommender)
            itineraries, error = itinerary_service.generate_itinerary(criteria)
            
            if error:
                # Suggestions en cas d'échec
                suggestions = itinerary_service.get_suggestions(criteria)
                return jsonify({
                    'success': False,
                    'message': error,
                    'suggestions': suggestions
                }), 404
            
            return jsonify({
                'success': True,
                'itineraries': itineraries,
                'count': len(itineraries),
                'criteria_used': criteria
            })
            
        except Exception as e:
            print(f"❌ Erreur génération itinéraire: {str(e)}")
            return jsonify({'error': str(e)}), 500


    @app.route('/api/v1/itineraries/suggestions', methods=['POST'])
    def get_itinerary_suggestions():
        """
        Retourne des suggestions basées sur des critères partiels
        """
        try:
            data = request.get_json()
            
            criteria = {
                'travel_type': data.get('travelType'),
                'interests': data.get('interests', []),
                'budget': data.get('budget'),
                'season': data.get('season')
            }
            
            criteria = {k: v for k, v in criteria.items() if v is not None and v != []}
            
            from app.services.itinerary_service import ItineraryService
            itinerary_service = ItineraryService()
            suggestions = itinerary_service.get_suggestions(criteria)
            
            return jsonify({
                'success': True,
                'suggestions': suggestions
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


    @app.route('/api/v1/itineraries/regions', methods=['GET'])
    def get_itinerary_regions():
        """
        Retourne la liste des régions disponibles pour les itinéraires
        """
        try:
            from app.services.itinerary_service import ItineraryService
            
            recommender = None
            if hasattr(recommendation_service, 'recommender'):
                recommender = recommendation_service.recommender
            
            itinerary_service = ItineraryService(recommender)
            regions = itinerary_service.get_available_regions()
            
            return jsonify({
                'success': True,
                'regions': regions,
                'count': len(regions)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


    @app.route('/api/v1/itineraries/save', methods=['POST'])
    def save_itinerary():
        """
        Sauvegarde un itinéraire pour un utilisateur
        """
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            itinerary = data.get('itinerary')
            
            if not user_id or not itinerary:
                return jsonify({'error': 'user_id et itinerary requis'}), 400
            
            # TODO: Sauvegarder dans ta BDD
            # save_to_database('user_itineraries', {
            #     'user_id': user_id,
            #     'itinerary': itinerary,
            #     'saved_at': datetime.now()
            # })
            
            return jsonify({
                'success': True,
                'message': 'Itinéraire sauvegardé avec succès'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return app

    