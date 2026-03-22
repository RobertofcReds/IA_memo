# app/utils/itinerary_filters.py
"""
Fonctions de filtrage pour les itinéraires
"""

def apply_criteria_filters(sites, criteria):
    """
    Applique les filtres basés sur les critères frontend
    """
    filtered = sites.copy()
    
    # 1. FILTRE PAR TYPE DE VOYAGE
    travel_type = criteria.get('travel_type')
    if travel_type:
        filtered = filter_by_travel_type(filtered, travel_type)
    
    # 2. FILTRE PAR CENTRES D'INTÉRÊT
    interests = criteria.get('interests', [])
    if interests:
        filtered = filter_by_interests(filtered, interests)
    
    # 3. FILTRE PAR BUDGET
    budget = criteria.get('budget')
    if budget:
        filtered = filter_by_budget(filtered, budget)
    
    # 4. FILTRE PAR DURÉE
    duration = criteria.get('duration')
    if duration:
        filtered = filter_by_duration(filtered, duration)
    
    # 5. FILTRE PAR SAISON
    season = criteria.get('season')
    if season:
        filtered = filter_by_season(filtered, season)
    
    # 6. FILTRE PAR RÉGION (si spécifié)
    region = criteria.get('region')
    if region:
        filtered = [s for s in filtered if s.get('region', '').lower() == region.lower()]
    
    # 7. FILTRE PAR HÉBERGEMENT
    accommodation = criteria.get('accommodation')
    if accommodation:
        filtered = filter_by_accommodation(filtered, accommodation)
    
    # Trier par note
    filtered.sort(key=lambda x: x.get('note', 0), reverse=True)

    print(f"Nombre de sites après application de tous les filtres : {len(filtered)}")
    
    return filtered


def filter_by_travel_type(sites, travel_type):
    """Filtre les sites selon le type de voyage"""
    type_mapping = {
        'romantic': ['Plage', 'Détente', 'Coucher de soleil', 'Romantique', 'Île'],
        'family': ['Parc National', 'Plage', 'Facile', 'Famille', 'Animaux'],
        'adventure': ['Aventure', 'Randonnée', 'Difficile', 'Sport', 'Trek'],
        'culture': ['Culture', 'Histoire', 'Patrimoine', 'UNESCO', 'Musée'],
        'beach': ['Plage', 'Mer', 'Océan', 'Île', 'Snorkeling'],
        'luxury': ['Luxe', 'Hôtel', 'Spa', 'Gastronomie', 'Premium']
    }
    
    keywords = type_mapping.get(travel_type, [])
    sites = [s for s in sites if any(
        kw.lower() in str(s.get('type', '')).lower() or
        kw.lower() in str(s.get('description', '')).lower() or
        kw.lower() in str(s.get('tags', '')).lower()
        for kw in keywords
    )]
    print(f"Sites après filtrage par type de voyage ({travel_type}): {len(sites)}")
    return sites



def filter_by_interests(sites, interests):
    """Filtre les sites selon les centres d'intérêt"""
    interest_mapping = {
        'wildlife': ['Parc National', 'Réserve', 'Animaux', 'Lémuriens', 'Oiseaux', 'Faune'],
        'photography': ['Point de vue', 'Coucher de soleil', 'Paysage', 'Photo', 'Panorama'],
        'food': ['Gastronomie', 'Restaurant', 'Cuisine', 'Marché', 'Dégustation'],
        'hiking': ['Randonnée', 'Montagne', 'Sentier', 'Trek', 'Massif'],
        'diving': ['Plongée', 'Snorkeling', 'Mer', 'Corail', 'Baleines', 'Océan'],
        'history': ['Histoire', 'Patrimoine', 'Culture', 'Musée', 'Royal', 'Palais'],
        'relaxation': ['Plage', 'Spa', 'Détente', 'Bien-être', 'Lagon'],
        'shopping': ['Marché', 'Artisanat', 'Shopping', 'Souvenirs', 'Boutique']
    }
    
    filtered = sites.copy()
    for interest in interests:
        keywords = interest_mapping.get(interest, [])
        filtered = [s for s in filtered if any(
            kw.lower() in str(s.get('type', '')).lower() or
            kw.lower() in str(s.get('description', '')).lower() or
            kw.lower() in str(s.get('sous_types_tags', '')).lower()
            for kw in keywords
        )]
    print(f"Sites après filtrage par centres d'intérêt ({interests}): {len(filtered)}")
    return filtered


def filter_by_budget(sites, budget):
    """Filtre les sites selon le budget"""
    budget_ranges = {
        'budget': (0, 20000),      # Économique
        'mid': (20000, 50000),      # Moyen
        'luxury': (50000, 1000000)  # Luxe
    }
    
    if budget in budget_ranges:
        min_price, max_price = budget_ranges[budget]
        sites_budget_filtered = [s for s in sites if min_price <= s.get('prix', 0) <= max_price]
        print(f'sites après filtrage par budget ({budget}): {len(sites_budget_filtered)}')
        return sites_budget_filtered
    print(f'sites après filtrage par budget ({budget}): {len(sites)}')
    return sites


def filter_by_duration(sites, duration):
    """Adapte le nombre de sites selon la durée"""
    duration_hours = {
        'weekend': 2,      # 2 jours
        'week': 7,         # 1 semaine
        'two-weeks': 14,   # 2 semaines
        'month': 30        # 1 mois
    }
    
    max_sites = duration_hours.get(duration, 7) * 2  # ~2 sites par jour
    print(f"sites[:max_sites] après filtrage par durée ({duration}): {len(sites[:max_sites])}")
    return sites[:max_sites]


def filter_by_season(sites, season):
    """
    Filtre les sites selon la saison
    Gère les cas "Toute l'année" qui sont valables pour toutes les saisons
    """
    season_mapping = {
        'summer': ['décembre', 'janvier', 'février', 'mars', 'été', 'déc', 'jan', 'fév', 'mar'],
        'winter': ['juin', 'juillet', 'août', 'septembre', 'hiver', 'jun', 'jul', 'aoû', 'sep'],
        'spring': ['octobre', 'novembre', 'printemps', 'oct', 'nov'],
        'autumn': ['avril', 'mai', 'automne', 'avr', 'mai']
    }
    
    # Expressions pour "toute l'année"
    all_year_expressions = ['toute l\'année', 'toute année', 'toutes saisons', 
                            'toute saison', 'toute l annee', 'toute annee',
                            'tous les mois', 'tous mois', 'toute l’année']
    
    months = season_mapping.get(season, [])
    
    print(f"Sites avant filtrage par saison ({season}): {len(sites)}")
    
    def is_valid_for_season(site):
        saison = str(site.get('saison_recommandee', '')).lower().strip()
        
        # Si c'est vide, on considère que c'est valable toute l'année (par défaut)
        if not saison:
            return True
        
        # Vérifier si c'est valable toute l'année
        if any(expr in saison for expr in all_year_expressions):
            return True
        
        # Vérifier si la saison correspond
        return any(month in saison for month in months)
    
    filtered_sites = [s for s in sites if is_valid_for_season(s)]
    
    print(f"Sites après filtrage par saison ({season}): {len(filtered_sites)}")
    
    # Debug: afficher quelques exemples de ce qui a été filtré
    if len(filtered_sites) < len(sites):
        print(f"  - {len(sites) - len(filtered_sites)} sites exclus (saison non correspondante)")
    
    return filtered_sites

def filter_by_accommodation(sites, accommodation):
    """Filtre selon le type d'hébergement préféré"""
    # À implémenter selon tes données d'hébergement
    return sites