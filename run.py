#!/usr/bin/env python
import sys
import argparse
import os
from pathlib import Path

# Ajouter le dossier courant au path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, init_service
from app.services.recommendation_service import RecommendationService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model',
        type=str,
        default='data/models/tourism_recommender.pkl',
        help='Chemin vers le modèle'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("API DE RECOMMANDATION TOURISTIQUE")
    print("=" * 60)

    # Création de l'application Flask
    app = create_app()

    print("\n📋 ROUTES ENREGISTRÉES:")
    print("-" * 60)
    for rule in app.url_map.iter_rules():
        print(f"   {rule}")
    print("-" * 60)

    # Chargement du modèle
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

    # 🔥 CONFIG RENDER
    port = int(os.environ.get("PORT", 8000))

    print(f"\n🚀 Serveur démarré sur http://0.0.0.0:{port}")
    print(f"   Test: http://0.0.0.0:{port}/api/v1/health")
    print("=" * 60)

    # ⚠️ IMPORTANT : host = 0.0.0.0 pour Render
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()