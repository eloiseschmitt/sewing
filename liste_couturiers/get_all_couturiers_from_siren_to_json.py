from dotenv import load_dotenv
import requests
import math
import json
import os
from tqdm import tqdm
import time

load_dotenv()

# === CONFIG ===
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.insee.fr/api-sirene/3.11/siret"
QUERY = "activitePrincipaleUniteLegale:14.13Z"
NOMBRE_PAR_PAGE = 100
OUTPUT_FILE = "resultats_complets_insee.json"
SAUVEGARDE_INTERVALLE = 20
SLEEP_SECS = 2.1


def get_headers():
    return {
        "X-INSEE-Api-Key-Integration": API_KEY,
        "Accept": "application/json"
    }


def fetch_page(page, nombre=NOMBRE_PAR_PAGE):
    params = {"q": QUERY, "nombre": nombre, "debut": (page - 1) * nombre}
    response = requests.get(BASE_URL, headers=get_headers(), params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def sauvegarder_json(data, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Sauvegarde dans {output_file} ({len(data)} résultats)")


def charger_json(output_file):
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Fichier JSON corrompu, reprise impossible. Nouveau départ.")
    return []


def main():
    print("=== Vérification de l'état initial ===")
    resultats_existants = charger_json(OUTPUT_FILE)
    deja_recup = len(resultats_existants)
    print(f"Résultats déjà présents : {deja_recup}")

    print("=== Récupération de la première page ===")
    first_page = fetch_page(1)
    total_results = first_page["header"]["total"]
    total_pages = math.ceil(total_results / NOMBRE_PAR_PAGE)
    print(f"Total résultats : {total_results}, pages à parcourir : {total_pages}")

    all_results = resultats_existants
    start_page = deja_recup // NOMBRE_PAR_PAGE + 1

    for page in tqdm(range(start_page, total_pages + 1), desc="Téléchargement des pages", unit="page"):
        data = fetch_page(page)

        for item in data.get("etablissements", []):
            record = {
                "siret": item.get("siret"),
                "uniteLegale": {
                    "denominationUniteLegale": item.get("uniteLegale", {}).get("denominationUniteLegale"),
                    "activitePrincipaleUniteLegale": item.get("uniteLegale", {}).get("activitePrincipaleUniteLegale"),
                    "nomUniteLegale": item.get("uniteLegale", {}).get("nomUniteLegale"),
                    "prenom1UniteLegale": item.get("uniteLegale", {}).get("prenom1UniteLegale"),
                },
                "adresseEtablissement": {
                    "numeroVoieEtablissement": item.get("adresseEtablissement", {}).get("numeroVoieEtablissement"),
                    "typeVoieEtablissement": item.get("adresseEtablissement", {}).get("typeVoieEtablissement"),
                    "libelleVoieEtablissement": item.get("adresseEtablissement", {}).get("libelleVoieEtablissement"),
                    "codePostalEtablissement": item.get("adresseEtablissement", {}).get("codePostalEtablissement"),
                    "libelleCommuneEtablissement": item.get("adresseEtablissement", {}).get("libelleCommuneEtablissement"),
                }
            }
            all_results.append(record)

        if page % SAUVEGARDE_INTERVALLE == 0 or page == total_pages:
            sauvegarder_json(all_results, OUTPUT_FILE)

        time.sleep(SLEEP_SECS)

    print(f"\n✅ Terminé ! {len(all_results)} résultats enregistrés dans {OUTPUT_FILE}")


if __name__ == "__main__":
    main()