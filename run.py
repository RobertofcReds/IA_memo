#!/usr/bin/env python
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, init_service
from app.services.recommendation_service import RecommendationService

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, 
                       default='data/models/tourism_recommender.pkl',
                       help='Chemin vers le modèle')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                       help='Hôte')
    parser.add_argument('--port', type=int, default=8000,
                       help='Port')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("API DE RECOMMANDATION TOURISTIQUE")
    print("=" * 60)
    
    # Créer l'app d'abord pour voir les routes
    app = create_app()
    
    print("\n📋 ROUTES ENREGISTRÉES:")
    print("-" * 60)
    for rule in app.url_map.iter_rules():
        print(f"   {rule}")
    print("-" * 60)
    
    # Charger le modèle
    print(f"\n📂 Chargement du modèle...")
    model_path = Path(__file__).parent / args.model
    
    if not model_path.exists():
        print(f"❌ Modèle non trouvé: {model_path}")
        return
    
    service = RecommendationService()
    if not service.load_model(str(model_path)):
        print("❌ Erreur: impossible de charger le modèle")
        return
    
    print(f"   ✓ Modèle chargé: {service.recommender.data.shape[0]} sites")
    
    # Initialiser le service dans l'app
    init_service(service)
    
    print(f"\n🚀 Serveur démarré sur http://{args.host}:{args.port}")
    print(f"   Test: http://{args.host}:{args.port}/api/v1/health")
    print("=" * 60)
    
    app.run(host=args.host, port=args.port, debug=True)

if __name__ == "__main__":
    main()