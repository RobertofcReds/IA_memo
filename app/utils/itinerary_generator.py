# app/utils/itinerary_generator.py
"""
Génération d'itinéraires intelligents
"""
from .itinerary_helpers import (
    optimize_route, calculate_total_price, get_ambiance,
    get_season_advice, generate_map_url, generate_daily_schedule
)

def generate_smart_itineraries(sites, criteria):
    """
    Génère des itinéraires intelligents selon les critères
    """
    itineraries = []
    
    # Adapter le nombre de sites selon la durée
    duration = criteria.get('duration', 'week')
    duration_sites = {
        'weekend': 4,      # 2 jours × 2 sites
        'week': 10,        # 7 jours × ~1.5 sites
        'two-weeks': 20,   # 14 jours × ~1.5 sites
        'month': 30        # 30 jours × 1 site
    }
    
    max_sites = duration_sites.get(duration, 10)
    top_sites = sites[:max_sites]
    print(f"Sites sélectionnés pour génération d'itinéraire (max {max_sites} selon durée {duration}): {len(top_sites)}")
    if not top_sites:
        return []
    
    # Grouper par région pour des itinéraires cohérents
    sites_by_region = {}
    for site in top_sites:
        region = site.get('region', 'Inconnue')
        if region not in sites_by_region:
            sites_by_region[region] = []
        sites_by_region[region].append(site)
    print(f"Sites regroupés par région: {sites_by_region} ")
    # Créer un itinéraire par région
    for region, region_sites in sites_by_region.items():
        print(f"Traitement de la région {region} avec {len(region_sites)} sites")
        if len(region_sites) < 2:
            continue
        
        # Optimiser l'ordre
        ordered_sites = optimize_route(region_sites)
        
        # Calculer le nombre de jours pour cette région
        region_days = min(len(region_sites), duration_sites.get(duration, 7) // max(1, len(sites_by_region)))
        
        # Créer l'itinéraire
        itinerary = {
            'id': f"itinerary_{region}_{len(itineraries)}",
            'nom': generate_itinerary_name(region, criteria),
            'description': generate_description(region, ordered_sites, criteria),
            'region': region,
            'duree_jours': max(1, region_days),
            'prix_total': calculate_total_price(ordered_sites),
            'nb_sites': len(ordered_sites),
            'score': calculate_score(ordered_sites, criteria),
            'types': list(set(s.get('type', 'Inconnu') for s in ordered_sites)),
            'ambiance': get_ambiance(criteria),
            'saison_ideale': get_season_advice(region, criteria),
            'sites_principaux': [
                {
                    'nom': s['nom'],
                    'description_courte': s.get('description', '')[:100] + '...' if len(s.get('description', '')) > 100 else s.get('description', ''),
                    'duree_visite': s.get('duree', 2),
                    'prix': s.get('prix', 0),
                    'incontournable': s.get('note', 0) > 4.5
                }
                for s in ordered_sites[:5]  # Top 5 sites
            ],
            'itineraire_journalier': generate_daily_schedule(ordered_sites, max(1, region_days)),
            'carte_url': generate_map_url(ordered_sites),
            'conseils': generate_travel_tips(criteria, region)
        }
        
        itineraries.append(itinerary)
    print(f"Itinéraires générés: {len(itineraries)}")
    # Trier par score
    itineraries.sort(key=lambda x: x['score'], reverse=True)
    
    return itineraries[:3]  # Top 3 itinéraires


def generate_itinerary_name(region, criteria):
    """Génère un nom attractif pour l'itinéraire"""
    travel_type = criteria.get('travel_type', '')
    
    names = {
        'romantic': f"❤️ Évasion Romantique à {region}",
        'family': f"👨‍👩‍👧‍👦 Aventure Familiale à {region}",
        'adventure': f"⛰️ Expédition Aventure à {region}",
        'culture': f"🏛️ Découverte Culturelle de {region}",
        'beach': f"🏖️ Paradis Balnéaire à {region}",
        'luxury': f"👑 Séjour Prestige à {region}"
    }
    
    return names.get(travel_type, f"✨ Découverte Authentique de {region}")


def generate_description(region, sites, criteria):
    """Génère une description personnalisée"""
    travel_type = criteria.get('travel_type', '')
    
    base_desc = f"Explorez les merveilles de {region} à travers {len(sites)} sites exceptionnels"
    
    if travel_type == 'romantic':
        return f"{base_desc}. Un voyage conçu pour les couples en quête de moments magiques et de souvenirs inoubliables."
    elif travel_type == 'family':
        return f"{base_desc}. Des activités adaptées à toute la famille pour des vacances réussies petits et grands."
    elif travel_type == 'adventure':
        return f"{base_desc}. Repoussez vos limites avec ce circuit sportif et dépaysant au cœur de la nature."
    elif travel_type == 'culture':
        return f"{base_desc}. Plongez dans l'histoire et les traditions malgaches à travers ce voyage culturel."
    elif travel_type == 'beach':
        return f"{base_desc}. Farniente, baignade et sports nautiques vous attendent sur les plus belles plages."
    elif travel_type == 'luxury':
        return f"{base_desc}. Un voyage d'exception avec des hébergements de prestige et des services haut de gamme."
    
    return f"{base_desc}. Une expérience unique pour découvrir la richesse de Madagascar."


def calculate_score(sites, criteria):
    """Calcule un score personnalisé pour l'itinéraire"""
    if not sites:
        return 0
    
    base_score = sum(s.get('note', 0) for s in sites) / len(sites)
    
    # Bonus selon la pertinence avec les critères
    bonus = 0
    travel_type = criteria.get('travel_type')
    
    if travel_type == 'romantic' and any('Plage' in s.get('type', '') for s in sites):
        bonus += 0.3
    if travel_type == 'adventure' and any('Randonnée' in s.get('type', '') for s in sites):
        bonus += 0.3
    
    interests = criteria.get('interests', [])
    if 'photography' in interests and any('Point de vue' in s.get('description', '') for s in sites):
        bonus += 0.2
    if 'wildlife' in interests and any('Parc National' in s.get('type', '') for s in sites):
        bonus += 0.2
    
    return min(5, base_score + bonus)


def generate_travel_tips(criteria, region):
    """Génère des conseils personnalisés"""
    tips = []
    
    # Conseils selon le type de voyage
    travel_type = criteria.get('travel_type')
    if travel_type == 'romantic':
        tips.append("🌹 Réservez un dîner aux chandelles sur la plage")
        tips.append("📸 Prévoyez un pique-nique au coucher du soleil")
        tips.append("💑 Choisissez un hébergement avec vue panoramique")
    elif travel_type == 'family':
        tips.append("👶 Prévoyez des jeux et activités pour les enfants")
        tips.append("🍼 Vérifiez les services de garde d'enfants")
        tips.append("🚗 Optez pour un véhicule spacieux")
    elif travel_type == 'adventure':
        tips.append("🥾 Emportez de bonnes chaussures de randonnée")
        tips.append("💧 Prévoyez assez d'eau et de snacks")
        tips.append("🆘 Souscrivez une assurance voyage")
    
    # Conseils selon la saison
    season = criteria.get('season')
    if season == 'summer':
        tips.append("☀️ Protection solaire indispensable (crème, chapeau)")
        tips.append("🌡️ Réservez à l'avance (haute saison touristique)")
        tips.append("💦 Buvez beaucoup d'eau, restez hydraté")
    elif season == 'winter':
        tips.append("🧥 Prévoyez des vêtements chauds pour le soir")
        tips.append("🐋 Juillet-septembre : observez les baleines")
        tips.append("📷 Luminosité idéale pour la photo")
    
    # Conseils selon le budget
    budget = criteria.get('budget')
    if budget == 'budget':
        tips.append("💰 Privilégiez les taxis-brousse pour les transports")
        tips.append("🍛 Mangez dans les gargotes locales (économique et authentique)")
        tips.append("🏠 Optez pour les chambres d'hôtes")
    elif budget == 'luxury':
        tips.append("💆 Réservez vos spa et soins à l'avance")
        tips.append("🍷 Goûtez aux vins et gastronomie locale")
        tips.append("🚁 Envisagez des excursions privées")
    
    # Conseils généraux
    tips.append(f"📍 {region} : vérifiez les formalités d'entrée")
    tips.append("📱 Téléchargez une carte hors-ligne")
    tips.append("💳 Prévenez votre banque de votre voyage")
    
    return tips[:5]  # Retourne 5 conseils max