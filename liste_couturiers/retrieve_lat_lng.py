from dotenv import load_dotenv
import json
import os
import time
import requests

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAP_API_KEY")


def geocoder_google(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": API_KEY
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if data["status"] == "OK":
        loc = data["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    else:
        print(f"[!] Erreur géocodage {address} → {data['status']}")
        return None, None


with open("list_couturiers_bordeaux.json", "r", encoding="utf-8") as f:
    data = json.load(f)

results = []

for e in data:
    nom = e.get("uniteLegale", {}).get("denominationUniteLegale", "")
    if not nom:
        continue

    a = e.get("adresseEtablissement", {})
    address = f"{a.get('numeroVoieEtablissement', '')} {a.get('typeVoieEtablissement', '')} {a.get('libelleVoieEtablissement', '')}, {a.get('codePostalEtablissement', '')} {a.get('libelleCommuneEtablissement', '')}"

    lat, lon = geocoder_google(address)
    if lat is not None:
        e["latitude"] = lat
        e["longitude"] = lon
        results.append(e)

    time.sleep(0.2)  # pour éviter de dépasser les quotas (5 requêtes/sec)

with open("list_couturiers_bordeaux_lat_lng.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"✅ Géocodage terminé : {len(results)} établissements avec coordonnées.")
