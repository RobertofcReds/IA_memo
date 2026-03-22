# app/utils/itinerary_suggestions.py
"""
Suggestions d'hébergements, restaurants et transports
"""

def suggest_accommodations(region, criteria):
    """Suggère des hébergements selon le budget et la région"""
    budget = criteria.get('budget', 'mid')
    
    # Base de données d'hébergements par région
    accommodations_db = {
        'Analamanga': {
            'budget': [
                {'nom': 'Auberge de jeunesse Antanimena', 'prix': 15000, 'type': 'Auberge', 'note': 3.8},
                {'nom': 'Hôtel Sakamanga', 'prix': 35000, 'type': 'Économique', 'note': 4.2},
                {'nom': 'Chez Francis', 'prix': 25000, 'type': 'Chambre d\'hôte', 'note': 4.0}
            ],
            'mid': [
                {'nom': 'Hôtel Carlton Madagascar', 'prix': 80000, 'type': 'Confort', 'note': 4.5},
                {'nom': 'La Varangue', 'prix': 65000, 'type': 'Boutique', 'note': 4.7},
                {'nom': 'Hôtel Colbert', 'prix': 75000, 'type': 'Confort', 'note': 4.3}
            ],
            'luxury': [
                {'nom': 'Palace Hôtel Antananarivo', 'prix': 150000, 'type': 'Luxe', 'note': 4.8},
                {'nom': 'Relais des Plateaux', 'prix': 120000, 'type': 'Premium', 'note': 4.6},
                {'nom': 'Hôtel Le Louvre', 'prix': 110000, 'type': 'Luxe', 'note': 4.4}
            ]
        },
        'Diana': {
            'budget': [
                {'nom': 'Bungalow Vanila', 'prix': 25000, 'type': 'Bungalow', 'note': 4.1},
                {'nom': 'Chez Robert', 'prix': 20000, 'type': 'Chambre d\'hôte', 'note': 4.0},
                {'nom': 'Hôtel Manga', 'prix': 30000, 'type': 'Économique', 'note': 3.9}
            ],
            'mid': [
                {'nom': 'Nosy Be Hôtel', 'prix': 70000, 'type': 'Hôtel', 'note': 4.4},
                {'nom': 'Le Grand Bleu', 'prix': 60000, 'type': 'Résort', 'note': 4.5},
                {'nom': 'Andilana Beach Resort', 'prix': 85000, 'type': 'Résort', 'note': 4.6}
            ],
            'luxury': [
                {'nom': 'Constance Tsarabanjina', 'prix': 250000, 'type': 'Luxe', 'note': 4.9},
                {'nom': 'Miavana', 'prix': 300000, 'type': 'Ultra-luxe', 'note': 5.0},
                {'nom': 'Vanila Hotel & Spa', 'prix': 180000, 'type': 'Luxe', 'note': 4.7}
            ]
        },
        'Atsinanana': {
            'budget': [
                {'nom': 'Hôtel de la Gare', 'prix': 18000, 'type': 'Économique', 'note': 3.7},
                {'nom': 'Chez Mami', 'prix': 22000, 'type': 'Chambre d\'hôte', 'note': 4.0}
            ],
            'mid': [
                {'nom': 'Hôtel Joffre', 'prix': 45000, 'type': 'Confort', 'note': 4.2},
                {'nom': 'Le Palmarium', 'prix': 55000, 'type': 'Résort', 'note': 4.3}
            ],
            'luxury': [
                {'nom': 'Hôtel Le Bungalow', 'prix': 95000, 'type': 'Luxe', 'note': 4.5}
            ]
        }
    }
    
    # Région par défaut si non trouvée
    region_data = accommodations_db.get(region, accommodations_db['Analamanga'])
    return region_data.get(budget, region_data['mid'])


def suggest_restaurants(region, criteria):
    """Suggère des restaurants selon la région et le type de voyage"""
    
    restaurants_db = {
        'Analamanga': [
            {'nom': 'La Table Malagasy', 'specialite': 'Cuisine locale', 'prix': 15000, 'note': 4.3},
            {'nom': 'Le Continental', 'specialite': 'International', 'prix': 25000, 'note': 4.5},
            {'nom': 'Grill du Rova', 'specialite': 'Grillades', 'prix': 20000, 'note': 4.2},
            {'nom': 'La Varangue', 'specialite': 'Gastronomique', 'prix': 35000, 'note': 4.7},
            {'nom': 'Chez Lala', 'specialite': 'Malgache traditionnel', 'prix': 12000, 'note': 4.1}
        ],
        'Diana': [
            {'nom': 'Le Lagon', 'specialite': 'Fruits de mer', 'prix': 30000, 'note': 4.6},
            {'nom': 'La Pirogue', 'specialite': 'Créole', 'prix': 20000, 'note': 4.4},
            {'nom': 'Chez Tantine', 'specialite': 'Locale', 'prix': 10000, 'note': 4.2},
            {'nom': 'Le Boucanier', 'specialite': 'Poissons', 'prix': 25000, 'note': 4.3}
        ],
        'Menabe': [
            {'nom': 'Baobab Café', 'specialite': 'International', 'prix': 18000, 'note': 4.2},
            {'nom': 'Chez Fred', 'specialite': 'Fruits de mer', 'prix': 22000, 'note': 4.1}
        ]
    }
    
    travel_type = criteria.get('travel_type')
    restaurants = restaurants_db.get(region, restaurants_db['Analamanga'])
    
    # Adapter selon le type de voyage
    if travel_type == 'romantic':
        restaurants = [r for r in restaurants if 'Gastronomique' in r['specialite'] or r['prix'] > 20000]
    elif travel_type == 'family':
        restaurants = [r for r in restaurants if r['prix'] < 25000]
    elif travel_type == 'budget' in criteria.get('budget', ''):
        restaurants = [r for r in restaurants if r['prix'] < 15000]
    
    return restaurants[:3]  # Top 3 restaurants


def suggest_transport(region, criteria):
    """Suggère des moyens de transport selon la région"""
    
    transport_options = {
        'Analamanga': {
            'principal': 'Taxi ou voiture de location',
            'options': ['Taxi-be', 'Voiture avec chauffeur', 'Bus'],
            'prix_journalier': 50000,
            'conseil': 'Privilégiez la location de voiture pour plus de liberté'
        },
        'Diana': {
            'principal': 'Taxi-brousse + bateau pour les îles',
            'options': ['Bateau', 'Quad', 'Moto'],
            'prix_journalier': 40000,
            'conseil': 'Réservez vos traversées en bateau à l\'avance'
        },
        'Atsinanana': {
            'principal': 'Voiture recommandée',
            'options': ['Taxi-brousse', 'Train (parcours pittoresque)'],
            'prix_journalier': 45000,
            'conseil': 'Le train FCE est une expérience unique'
        },
        'default': {
            'principal': 'Taxi-brousse ou voiture de location',
            'options': ['Taxi-be', 'Bus'],
            'prix_journalier': 35000,
            'conseil': 'Comparez les prix avant de réserver'
        }
    }
    
    return transport_options.get(region, transport_options['default'])


def get_smart_suggestions(criteria):
    """
    Génère des suggestions intelligentes basées sur les critères
    """
    suggestions = []
    
    travel_type = criteria.get('travel_type')
    interests = criteria.get('interests', [])
    budget = criteria.get('budget')
    season = criteria.get('season')
    
    # Suggestions basées sur le type de voyage
    type_suggestions = {
        'romantic': [
            "🌅 Île Sainte-Marie - Parfait pour les couples, baleines de juillet à septembre",
            "🏝️ Nosy Be - Couchers de soleil romantiques et plages paradisiaques",
            "🌳 Allée des Baobabs - Moment magique en duo au coucher du soleil"
        ],
        'family': [
            "🦜 Parc National Andasibe - Idéal pour les enfants, lémuriens facilement observables",
            "🐢 Île aux Nattes - Plage familiale sans voitures, eaux calmes",
            "🌺 Lemurs Park - Rencontre avec les lémuriens en sécurité"
        ],
        'adventure': [
            "🗻 Tsingy de Bemaraha - Défi sportif, sites UNESCO",
            "⛰️ Massif de l'Andringitra - Trek inoubliable, sommets à gravir",
            "💧 Canyoning dans l'Isalo - Sensations fortes garanties"
        ],
        'culture': [
            "👑 Rova d'Antananarivo - Histoire royale, vue panoramique",
            "🏯 Ambohimanga - Site sacré, patrimoine mondial",
            "📸 Musée de la Photographie - Histoire de Madagascar en images"
        ],
        'beach': [
            "🏖️ Nosy Be - Plages de rêve, eaux turquoise",
            "🤿 Ifaty - Snorkeling, récifs coralliens",
            "🌴 Morondava - Baobabs et plage, couchers de soleil"
        ],
        'luxury': [
            "✨ Constance Tsarabanjina - Hôtel de luxe île privée",
            "👑 Miavana - Resort exclusif, 5 étoiles",
            "💎 Vanila Hotel - Confort absolu, spa de renom"
        ]
    }
    
    if travel_type and travel_type in type_suggestions:
        suggestions.extend(type_suggestions[travel_type])
    
    # Suggestions basées sur les centres d'intérêt
    interest_suggestions = {
        'wildlife': ["🦁 Parc National de l'Isalo - Faune unique", "🐒 Réserve d'Anja - Lémuriens faciles à voir", "🐋 Sainte-Marie - Baleines à bosse"],
        'photography': ["📷 Allée des Baobabs au coucher", "🌄 Tsingy au lever du soleil", "📸 Nosy Komba - Villages typiques"],
        'food': ["🍲 Marché de Toliara - Produits locaux", "🍽️ Restaurant La Varangue - Gastronomie", "🌶️ Cuisine malgache à Antananarivo"],
        'hiking': ["🥾 Massif du Marojejy - Trek difficile", "🏃 Cirque de Boby - Randonnée mythique", "🚶 Parc National de Ranomafana - Sentiers"],
        'diving': ["🤿 Nosy Tanikely - Réserve marine", "🐠 Île Sainte-Marie - Plongée", "🌊 Mitsio - Fonds marins"],
        'history': ["🏛️ Rova de Manjakamiadana - Palais royal", "👑 Palais d'Andafiavaratra - Musée", "🏯 Ambohimanga - Colline sacrée"],
        'relaxation': ["💆 Spa à Nosy Be - Massages", "😌 Plage d'Ifaty - Détente", "🌴 Île aux Nattes - Farniente"],
        'shopping': ["🛍️ Marché d'Analakely - Artisanat", "🎨 Artisanat à Antsirabe - Objets", "🏺 Marché de Zoma - Souvenirs"]
    }
    
    for interest in interests:
        if interest in interest_suggestions:
            suggestions.extend(interest_suggestions[interest][:2])
    
    # Suggestions basées sur la saison
    season_tips = {
        'summer': ["☀️ Prévoyez de la crème solaire indice 50+", "📅 Réservez à l'avance (haute saison)", "💧 Buvez beaucoup d'eau, évitez la chaleur"],
        'winter': ["🧥 Vêtements chauds pour les hauts plateaux", "🐋 Idéal pour les baleines à Sainte-Marie", "🌤️ Températures agréables pour randonner"],
        'spring': ["🌸 Floraison magnifique dans les parcs", "📷 Peu de touristes, photos réussies", "🌡️ Températures douces et agréables"],
        'autumn': ["🍃 Paysages verdoyants après les pluies", "📸 Luminosité parfaite pour la photo", "🌡️ Ni trop chaud, ni trop froid"]
    }
    
    if season and season in season_tips:
        suggestions.append(f"💡 Conseil saison : {season_tips[season][0]}")
    
    # Suggestion budgétaire
    if budget == 'budget':
        suggestions.append("💰 Astuce budget : Les taxis-brousse sont économiques et authentiques")
    elif budget == 'luxury':
        suggestions.append("💎 Astuce luxe : Certains hôtels offrent des excursions privées")
    
    return list(set(suggestions))[:6]  # 6 suggestions uniques