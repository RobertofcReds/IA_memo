import requests
import json

# Test 1: Sites culturels pas chers
print("=" * 60)
print("TEST 1: Sites culturels pas chers")
print("=" * 60)

data1 = {
    "type": "Culture et histoire",
    "prix_max": 20000,
    "note_min": 4.0,
    "n_recommendations": 5
}

response = requests.post(
    "http://localhost:5000/api/v1/recommendations/by-criteria",
    json=data1
)

if response.status_code == 200:
    result = response.json()
    print(f"Trouvé: {result['total']} recommandations")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"{i}. {rec['nom']} - {rec['type']} - {rec['prix']} Ar (note: {rec['note']})")
else:
    print(f"Erreur: {response.status_code}")
    print(response.text)

# Test 2: Randonnées à Antananarivo
print("\n" + "=" * 60)
print("TEST 2: Randonnées à Antananarivo")
print("=" * 60)

data2 = {
    "type": "Randonnée",
    "region": "Antananarivo",
    "prix_max": 30000,
    "note_min": 4.0,
    "n_recommendations": 5
}

response = requests.post(
    "http://localhost:5000/api/v1/recommendations/by-criteria",
    json=data2
)

if response.status_code == 200:
    result = response.json()
    print(f"Trouvé: {result['total']} recommandations")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"{i}. {rec['nom']} - {rec['type']} - {rec['prix']} Ar (note: {rec['note']})")
else:
    print(f"Erreur: {response.status_code}")
    print(response.text)