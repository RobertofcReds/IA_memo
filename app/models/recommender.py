import numpy as np
import pandas as pd
import joblib
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity

class TourismRecommender:
    """Moteur de recommandation principal"""
    
    def __init__(self):
        self.data = None
        self.preprocessor = None
        self.nn_model = None
        self.features_matrix = None
        self.popularity_scores = None
        
    def fit(self, df, preprocessor):
        """Entraîne le système"""
        self.data = df.reset_index(drop=True)
        self.preprocessor = preprocessor
        
        # Matrice de features
        print("Création de la matrice de features...")
        self.features_matrix = preprocessor.transform(df)
        
        # Scores de popularité
        if 'log_avis' in df.columns and 'note_moyenne' in df.columns:
            self.popularity_scores = (
                df['log_avis'] / df['log_avis'].max() * 0.5 +
                df['note_moyenne'] / 5 * 0.5
            )
        else:
            self.popularity_scores = pd.Series([0.5] * len(df))
        
        # Modèle de similarité
        print("Entraînement du modèle de similarité...")
        X_dense = self.features_matrix.toarray() if hasattr(self.features_matrix, 'toarray') else self.features_matrix
        
        self.nn_model = NearestNeighbors(
            n_neighbors=min(20, len(df)),
            metric='cosine',
            algorithm='brute'
        )
        self.nn_model.fit(X_dense)
        
        print("Système prêt!")
        return self
    
    def _find_site_index(self, site_id):
        """Trouve l'index d'un site"""
    
        if isinstance(site_id, int):
            return site_id if site_id < len(self.data) else None
        
        
        if isinstance(site_id, str):
            # Recherche par nom
            mask = self.data['nom'].str.contains(site_id, case=False, na=False)
            if mask.any():
                return self.data[mask].index[0]
        print(len(self.data))
        print(f"check instance {isinstance(site_id,int)}")
        return None
    
    def get_similar_sites(self, site_id, n_recommendations=10):
        """Recommande des sites similaires"""
        # Trouver l'index
        idx = self._find_site_index(site_id)
        if idx is None:
            return []

        print(f"Recherche de sites similaires pour site_id={site_id} (index={idx})")
        
        # Préparer les données
        X_dense = self.features_matrix.toarray() if hasattr(self.features_matrix, 'toarray') else self.features_matrix
        
        # Trouver les voisins
        site_vector = X_dense[idx].reshape(1, -1)
        distances, indices = self.nn_model.kneighbors(
            site_vector,
            n_neighbors=min(n_recommendations + 1, len(self.data))
        )
        
        # Calculer les scores
        recommendations = []
        for i, (dist, neighbor_idx) in enumerate(zip(distances[0][1:], indices[0][1:])):
            similarity = 1 - dist
            popularity = self.popularity_scores.iloc[neighbor_idx]
            final_score = similarity * (1 + 0.2 * popularity)
            
            site = self.data.iloc[neighbor_idx]
            recommendations.append({
                'id': int(neighbor_idx),
                'nom': site['nom'],
                'type': site.get('type_activite', 'Inconnu'),
                'note': float(site.get('note_moyenne', 0)),
                'prix': float(site.get('prix_approximatif_ar', 0)) if pd.notna(site.get('prix_approximatif_ar')) else None,
                'score': round(float(final_score), 3)
            })
        
        return recommendations
    
    def semantic_search(self, query, n_recommendations=10, filters=None):
        """Recherche par texte"""
        # Créer une requête factice
        fake_data = pd.DataFrame({
            'description_courte': [query],
            'nom': [query],
            'type_activite': [''],
            'region': ['']
        })
        
        # Ajouter les colonnes nécessaires
        for col in self.data.columns:
            if col not in fake_data.columns and self.data[col].dtype in ['int64', 'float64']:
                fake_data[col] = self.data[col].median()
        
        # Transformer la requête
        query_vector = self.preprocessor.transform(fake_data)
        query_dense = query_vector.toarray() if hasattr(query_vector, 'toarray') else query_vector
        features_dense = self.features_matrix.toarray() if hasattr(self.features_matrix, 'toarray') else self.features_matrix
        
        # Calculer les similarités
        similarities = cosine_similarity(query_dense, features_dense)[0]
        
        # Appliquer les filtres
        indices = list(range(len(self.data)))
        if filters:
            filtered = []
            for i in indices:
                site = self.data.iloc[i]
                valid = True
                
                if 'type' in filters and site.get('type_activite') != filters['type']:
                    valid = False
                if 'max_price' in filters and site.get('prix_approximatif_ar', 0) > filters['max_price']:
                    valid = False
                if 'min_rating' in filters and site.get('note_moyenne', 0) < filters['min_rating']:
                    valid = False
                    
                if valid:
                    filtered.append(i)
            indices = filtered
        
        # Calculer les scores finaux
        scores = []
        for i in indices:
            score = similarities[i] * (1 + 0.3 * self.popularity_scores.iloc[i])
            scores.append((i, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Formater les résultats
        results = []
        for i, score in scores[:n_recommendations]:
            site = self.data.iloc[i]
            results.append({
                'id': int(i),
                'nom': site['nom'],
                'type': site.get('type_activite', 'Inconnu'),
                'note': float(site.get('note_moyenne', 0)),
                'prix': float(site.get('prix_approximatif_ar', 0)) if pd.notna(site.get('prix_approximatif_ar')) else None,
                'similarite': round(float(similarities[i]), 3),
                'score': round(float(score), 3)
            })
        
        return results
    
    def get_site_details(self, site_id):
        """Détails d'un site"""
        idx = self._find_site_index(site_id)
        if idx is None:
            return None
        
        site = self.data.iloc[idx]
        return {
            'id': int(idx),
            'nom': site['nom'],
            'region': site.get('region', 'Inconnue'),
            'type': site.get('type_activite', 'Inconnu'),
            'note': float(site.get('note_moyenne', 0)),
            'prix': float(site.get('prix_approximatif_ar', 0)) if pd.notna(site.get('prix_approximatif_ar')) else None,
            'description': site.get('description_courte', ''),
            'tags': site.get('sous_types_tags', '')
        }
    
    def get_all_sites(self, limit=100, offset=0):
        """Liste tous les sites"""
        sites = []
        end = min(offset + limit, len(self.data))
        
        for i in range(offset, end):
            site = self.get_site_details(i)
            if site:
                sites.append(site)
        
        return {
            'total': len(self.data),
            'offset': offset,
            'limit': limit,
            'sites': sites
        }
    
    def save(self, path):
        """Sauvegarde le modèle"""
        joblib.dump(self, path)
    
    @staticmethod
    def load(path):
        """Charge le modèle"""
        return joblib.load(path)
    
    def recommend_by_criteria(self, criteria, n_recommendations=10):
        """
        Recommande des sites basés sur des critères + similarité ML
        
        Parameters:
        -----------
        criteria : dict
            Critères de recherche : type, prix_max, note_min, region, duree_max, etc.
        n_recommendations : int
            Nombre de recommandations souhaité
        """
        import pandas as pd
        import numpy as np
        
        print(f"\n🔍 Recherche avec critères: {criteria}")
        
        # 1. FILTRAGE : trouver les sites qui correspondent aux critères
        mask = pd.Series([True] * len(self.data))
        
        # Filtre par type d'activité
        if criteria.get('type'):
            if isinstance(criteria['type'], list):
                mask &= self.data['type_activite'].isin(criteria['type'])
            else:
                mask &= self.data['type_activite'] == criteria['type']
            print(f"   - Filtre type: {criteria['type']}")
        
        # Filtre par prix maximum
        if criteria.get('prix_max'):
            mask &= self.data['prix_approximatif_ar'] <= criteria['prix_max']
            print(f"   - Filtre prix_max: {criteria['prix_max']} Ar")
        
        # Filtre par prix minimum
        if criteria.get('prix_min'):
            mask &= self.data['prix_approximatif_ar'] >= criteria['prix_min']
            print(f"   - Filtre prix_min: {criteria['prix_min']} Ar")
        
        # Filtre par note minimum
        if criteria.get('note_min'):
            mask &= self.data['note_moyenne'] >= criteria['note_min']
            print(f"   - Filtre note_min: {criteria['note_min']}")
        
        # Filtre par région
        if criteria.get('region'):
            mask &= self.data['region'].str.contains(criteria['region'], case=False, na=False)
            print(f"   - Filtre region: {criteria['region']}")
        
        # Filtre par difficulté
        if criteria.get('difficulte'):
            mask &= self.data['difficulte'] == criteria['difficulte']
            print(f"   - Filtre difficulte: {criteria['difficulte']}")
        
        # Filtre par durée maximum (en heures)
        if criteria.get('duree_max') and 'duree_heures' in self.data.columns:
            mask &= self.data['duree_heures'] <= criteria['duree_max']
            print(f"   - Filtre duree_max: {criteria['duree_max']}h")
        
        # Récupérer les sites correspondant aux critères
        sites_filtres = self.data[mask].copy()
        print(f"   ✓ {len(sites_filtres)} sites correspondent aux critères")
        
        # Si aucun site ne correspond
        if len(sites_filtres) == 0:
            print("   ⚠ Aucun site trouvé avec ces critères")
            return []
        
        # 2. Si l'utilisateur a fourni un site de référence explicite
        if criteria.get('site_reference'):
            site_ref_idx = self._find_site_index(criteria['site_reference'])
            if site_ref_idx is not None:
                print(f"   ✓ Site de référence: {self.data.iloc[site_ref_idx]['nom']}")
                # Utiliser ce site comme référence pour la similarité
                reference_idx = site_ref_idx
            else:
                # Sinon prendre le meilleur site des filtres comme référence
                reference_idx = sites_filtres.sort_values('note_moyenne', ascending=False).index[0]
        else:
            # Prendre le meilleur site des filtres comme référence
            reference_idx = sites_filtres.sort_values('note_moyenne', ascending=False).index[0]
        
        site_reference = self.data.iloc[reference_idx]
        print(f"   📍 Site de référence: {site_reference['nom']}")
        
        # 3. Utiliser le MODÈLE ML pour trouver des sites similaires à la référence
        print("   🤖 Utilisation du modèle ML pour trouver des sites similaires...")
        
        # Obtenir plus de recommandations que nécessaire pour pouvoir filtrer
        try:
            reference_idx = int(reference_idx)
        except ValueError:
            reference_idx = reference_idx
            
        similarites = self.get_similar_sites(int(reference_idx), n_recommendations=n_recommendations * 3)
        
        # 4. Filtrer pour ne garder que ceux qui respectent aussi les critères
        recommandations_finales = []
        for rec in similarites:
            site = self.data.iloc[rec['id']]
            
            # Vérifier que le site respecte les critères
            respecte_criteres = True
            
            if criteria.get('prix_max') and site['prix_approximatif_ar'] > criteria['prix_max']:
                respecte_criteres = False
            if criteria.get('prix_min') and site['prix_approximatif_ar'] < criteria['prix_min']:
                respecte_criteres = False
            if criteria.get('note_min') and site['note_moyenne'] < criteria['note_min']:
                respecte_criteres = False
            
            if respecte_criteres:
                recommandations_finales.append(rec)
                
                if len(recommandations_finales) >= n_recommendations:
                    break
        
        print(f"   ✓ {len(recommandations_finales)} recommandations finales")
        
        return recommandations_finales[:n_recommendations]