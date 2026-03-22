#!/usr/bin/env python
"""Script d'entraînement du modèle"""

import sys
import os
from pathlib import Path

# Ajouter le chemin parent
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from app.models.preprocessor import DataPreprocessor
from app.models.recommender import TourismRecommender

def main():
    """Fonction principale"""
    
    # Configuration
    data_path = "data/raw/sites_touristiques.xlsx"  # À modifier
    model_path = "data/models/tourism_recommender.pkl"
    preprocessor_path = "data/models/preprocessor.pkl"
    
    print("=" * 50)
    print("ENTRAÎNEMENT DU SYSTÈME DE RECOMMANDATION")
    print("=" * 50)
    
    # 1. Chargement des données
    print(f"\n1. Chargement des données: {data_path}")
    df = pd.read_excel(data_path)
    print(f"   {len(df)} sites chargés")
    
    # 2. Prétraitement
    print("\n2. Prétraitement des données...")
    preprocessor = DataPreprocessor()
    df_clean, X = preprocessor.fit_transform(df)
    print(f"   Dimensions: {X.shape}")
    
    # 3. Sauvegarde du préprocesseur
    print(f"\n3. Sauvegarde du préprocesseur...")
    preprocessor.save(preprocessor_path)
    
    # 4. Entraînement du recommender
    print("\n4. Entraînement du moteur de recommandation...")
    recommender = TourismRecommender()
    recommender.fit(df_clean, preprocessor)
    
    # 5. Sauvegarde
    print(f"\n5. Sauvegarde du modèle...")
    recommender.save(model_path)
    
    print("\n" + "=" * 50)
    print("✅ ENTRAÎNEMENT TERMINÉ!")
    print("=" * 50)
    
    # Petit test
    print("\nTest rapide:")
    test = recommender.get_similar_sites(0, 3)
    if test:
        print(f"Site de référence: {df_clean.iloc[0]['nom']}")
        print("Recommandations:")
        for i, rec in enumerate(test, 1):
            print(f"  {i}. {rec['nom']} (score: {rec['score']})")

if __name__ == "__main__":
    main()