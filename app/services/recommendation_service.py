"""Service de recommandation - Interface entre l'API et les modèles"""

from app.models.recommender import TourismRecommender

class RecommendationService:
    """Service qui encapsule la logique métier"""
    
    def __init__(self, model_path=None):
        self.recommender = None
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path):
        """Charge le modèle entraîné"""
        self.recommender = TourismRecommender.load(model_path)
        return self.recommender is not None
    
    def recommend_by_site(self, site_id, n=10):
        """Recommandations basées sur un site"""
        if not self.recommender:
            return {'error': 'Modèle non chargé'}, 503
        
        recommendations = self.recommender.get_similar_sites(site_id, n)
        
        if not recommendations:
            return {'error': 'Site non trouvé'}, 404
        
        return recommendations, 200
    
    def search(self, query, n=10, filters=None):
        """Recherche sémantique"""
        if not self.recommender:
            return {'error': 'Modèle non chargé'}, 503
        
        results = self.recommender.semantic_search(query, n, filters)
        return results, 200
    
    def get_site(self, site_id):
        """Détails d'un site"""
        if not self.recommender:
            return {'error': 'Modèle non chargé'}, 503
        
        site = self.recommender.get_site_details(site_id)
        
        if not site:
            return {'error': 'Site non trouvé'}, 404
        
        return site, 200
    
    def list_sites(self, limit=100, offset=0):
        """Liste des sites"""
        if not self.recommender:
            return {'error': 'Modèle non chargé'}, 503
        
        return self.recommender.get_all_sites(limit, offset), 200
    
    def get_stats(self):
        """Statistiques"""
        if not self.recommender:
            return {'error': 'Modèle non chargé'}, 503
        
        return {
            'total_sites': len(self.recommender.data),
            'types': self.recommender.data['type_activite'].value_counts().to_dict() if 'type_activite' in self.recommender.data.columns else {},
            'note_moyenne': float(self.recommender.data['note_moyenne'].mean()) if 'note_moyenne' in self.recommender.data.columns else None
        }, 200