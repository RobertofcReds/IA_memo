# app/utils/itinerary_helpers.py
"""
Fonctions helpers pour les itinéraires
"""
import math
import random

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calcule la distance entre deux points (formule Haversine)
    """
    if not lat1 or not lon1 or not lat2 or not lon2:
        return 100  # Distance par défaut
    
    R = 6371  # Rayon de la Terre en km
    
    try:
        lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    except:
        return 100


def optimize_route(sites):
    """
    Optimise l'ordre des sites pour minimiser les déplacements
    """
    if len(sites) <= 2:
        return sites
    
    ordered = [sites[0]]
    remaining = sites[1:]
    
    while remaining:
        last = ordered[-1]
        
        # Trouver le site le plus proche
        min_dist = float('inf')
        closest = None
        closest_idx = 0
        
        for i, site in enumerate(remaining):
            dist = calculate_distance(
                last.get('latitude', 0), last.get('longitude', 0),
                site.get('latitude', 0), site.get('longitude', 0)
            )
            if dist < min_dist:
                min_dist = dist
                closest = site
                closest_idx = i
        
        ordered.append(closest)
        remaining.pop(closest_idx)
    
    return ordered


def calculate_total_price(sites):
    """Calcule le prix total de l'itinéraire"""
    return sum(s.get('prix', 0) for s in sites)


def get_ambiance(criteria):
    """Détermine l'ambiance selon les critères"""
    travel_type = criteria.get('travel_type', '')
    
    ambiances = {
        'romantic': 'Romantique et intimiste',
        'family': 'Convivial et familial',
        'adventure': 'Sportif et dépaysant',
        'culture': 'Culturel et enrichissant',
        'beach': 'Détente et farniente',
        'luxury': 'Prestige et raffinement'
    }
    
    return ambiances.get(travel_type, 'Découverte et authenticité')


def get_season_advice(region, criteria):
    """Donne des conseils sur la meilleure saison"""
    season = criteria.get('season', '')
    
    season_names = {
        'summer': 'Été (décembre-mars)',
        'winter': 'Hiver (juin-septembre)',
        'spring': 'Printemps (octobre-novembre)',
        'autumn': 'Automne (avril-mai)'
    }
    
    return season_names.get(season, 'Toute l\'année')


def generate_map_url(sites):
    """Génère un lien Google Maps pour l'itinéraire"""
    if not sites or len(sites) < 2:
        return ""
    
    try:
        waypoints = []
        for site in sites[:10]:  # Max 10 sites pour l'URL
            if site.get('latitude') and site.get('longitude'):
                waypoints.append(f"{site['latitude']},{site['longitude']}")
        
        if len(waypoints) < 2:
            return ""
        
        origin = waypoints[0]
        destination = waypoints[-1]
        
        if len(waypoints) > 2:
            waypoints_str = '|'.join(waypoints[1:-1])
            return f"https://www.google.com/maps/dir/{origin}/{destination}/data=!3m1!4b1!4m2!4m1!3e0?waypoints={waypoints_str}"
        else:
            return f"https://www.google.com/maps/dir/{origin}/{destination}"
    except:
        return ""


def generate_daily_schedule(sites, total_days):
    """Génère un planning jour par jour"""
    if not sites:
        return []
    
    days = []
    sites_per_day = max(1, len(sites) // total_days)
    
    for i in range(total_days):
        start = i * sites_per_day
        end = min(start + sites_per_day, len(sites))
        
        if start >= len(sites):
            break
        
        day_sites = sites[start:end]
        days.append({
            'jour': i + 1,
            'titre': f"Jour {i+1} : {day_sites[0]['nom']} et découvertes",
            'sites': [s['nom'] for s in day_sites],
            'description': f"Exploration de {len(day_sites)} sites dans la région",
            'restaurant_midi': random.choice(["Restaurant local", "Pique-nique", "Gargote"]),
            'restaurant_soir': random.choice(["Hôtel", "Restaurant typique", "Marché de nuit"])
        })
    
    return days