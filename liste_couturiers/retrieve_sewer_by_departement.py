import requests
import time
import json
from dotenv import load_dotenv
import os

load_dotenv()

# --- Configurations ---
client_id = "sewing_api"
client_secret = os.getenv("API_KEY")
departement = "33"
code_ape = "9529Z"
output_file = "etablissements_33.json"

# --- Étape 1 : Récupérer la liste des communes du département 33 ---
print("Récupération des communes...")
resp = requests.get(f"https://geo.api.gouv.fr/departements/{departement}/communes")
communes = resp.json()
codes_communes = [c["code"] for c in communes]
print(f"✓ {len(codes_communes)} communes récupérées.")

# --- Étape 2 : Authentification API Sirene (OAuth2) ---
print("Obtention du token d'accès...")
auth_resp = requests.post(
    "https://api.insee.fr/api-sirene/3.11/token",
    headers={
        "Authorization": f"Basic {requests.auth._basic_auth_str(client_id, client_secret)}",
        "Content-Type": "application/x-www-form-urlencoded"
    },
    data={"grant_type": "client_credentials"}
)

access_token = auth_resp.json()["access_token"]
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
}

# --- Étape 3 : Boucle sur les communes + pagination ---
etablissements_total = []
base_url = "https://api.insee.fr/entreprises/sirene/V3/siret"

for code_commune in codes_communes:
    debut = 0
    taille_page = 100
    while True:
        q = f"activitePrincipaleUniteLegale:{code_ape} AND codeCommuneEtablissement:{code_commune} AND etatAdministratifEtablissement:A"
        params = {
            "q": q,
            "nombre": taille_page,
            "debut": debut
        }

        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"⚠️ Erreur sur commune {code_commune} (code {response.status_code})")
            break

        data = response.json()
        etablissements = data.get("etablissements", [])
        etablissements_total.extend(etablissements)

        if len(etablissements) < taille_page:
            break  # dernière page atteinte
        else:
            debut += taille_page

        time.sleep(0.2)  # évite d'être bloqué pour dépassement de quota

print(f"✓ Total récupéré : {len(etablissements_total)} établissements")

# --- Étape 4 : Sauvegarde JSON ---
with open(output_file, "w", encoding="utf-8") as f:
    json.dump({"etablissements": etablissements_total}, f, ensure_ascii=False, indent=2)

print(f"✓ Données enregistrées dans : {output_file}")
