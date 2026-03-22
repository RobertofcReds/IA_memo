# app/services/itinerary_service.py
"""
Service de génération d'itinéraires
"""
import pandas as pd
from app.utils.itinerary_filters import apply_criteria_filters
from app.utils.itinerary_generator import generate_smart_itineraries
from app.utils.itinerary_suggestions import suggest_accommodations, suggest_restaurants, suggest_transport, get_smart_suggestions

class ItineraryService:
    """Service de génération d'itinéraires intelligents"""
    
    def __init__(self, recommender=None):
        self.recommender = recommender
    
    def get_sites_from_recommender(self):
        """Récupère les sites depuis le modèle de recommandation"""
        if self.recommender and hasattr(self.recommender, 'data'):
            sites = []
            data = self.recommender.data
            
            for idx, row in data.iterrows():
                site = {
                    'id': idx,
                    'nom': row.get('nom', ''),
                    'region': row.get('region', ''),
                    'type': row.get('type_activite', ''),
                    'description': row.get('description_courte', ''),
                    'prix': float(row.get('prix_approximatif_ar', 0)) if pd.notna(row.get('prix_approximatif_ar')) else 0,
                    'note': float(row.get('note_moyenne', 0)) if pd.notna(row.get('note_moyenne')) else 0,
                    'duree': float(row.get('duree_typique_visite_heures', 2)) if pd.notna(row.get('duree_typique_visite_heures')) else 2,
                    'difficulte': row.get('difficulte', 'Moyenne'),
                    'latitude': float(row.get('latitude', 0)) if pd.notna(row.get('latitude')) else 0,
                    'longitude': float(row.get('longitude', 0)) if pd.notna(row.get('longitude')) else 0,
                    'tags': row.get('sous_types_tags', ''),
                    'saison_recommandee': row.get('saison_recommandee', '')
                }
                sites.append(site)
            return sites
        return []
    
    def generate_itinerary(self, criteria):
        """Génère un itinéraire complet selon les critères"""
        
        # 1. Récupérer les sites
        sites = self.get_sites_from_recommender()
        if not sites:
            return None, "Aucun site disponible"
        print(f'Critères reçus : {criteria}')
        # 2. Filtrer selon les critères
        filtered_sites = apply_criteria_filters(sites, criteria)
        
        if not filtered_sites:
            return None, "Aucun site correspondant aux critères"
        
        # 3. Générer les itinéraires
        itineraries = generate_smart_itineraries(filtered_sites, criteria)
        
        if not itineraries:
            return None, "Impossible de générer un itinéraire"
        
        # 4. Enrichir avec suggestions
        for it in itineraries:
            it['hebergements'] = suggest_accommodations(it['region'], criteria)
            it['restaurants'] = suggest_restaurants(it['region'], criteria)
            it['transport'] = suggest_transport(it['region'], criteria)
        
        return itineraries, None
    
    def get_suggestions(self, criteria):
        """Retourne des suggestions basées sur des critères partiels"""
        return get_smart_suggestions(criteria)
    
    def get_available_regions(self):
        """Retourne la liste des régions disponibles"""
        sites = self.get_sites_from_recommender()
        
        regions = {}
        for site in sites:
            region = site.get('region')
            if region and region not in regions:
                regions[region] = {
                    'nom': region,
                    'nb_sites': 0,
                    'types': set()
                }
            if region:
                regions[region]['nb_sites'] += 1
                regions[region]['types'].add(site.get('type', 'Inconnu'))
        
        result = []
        for region, data in regions.items():
            result.append({
                'nom': region,
                'nb_sites': data['nb_sites'],
                'types': list(data['types'])[:5]
            })
        
        return sorted(result, key=lambda x: x['nom'])