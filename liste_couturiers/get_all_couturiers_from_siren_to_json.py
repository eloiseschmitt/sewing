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
BATCH_SIZE = 100
OUTPUT_FILE = "resultats_complets_insee.json"
STATE_FILE = "insee_cursor_state.json"
SAUVEGARDE_INTERVALLE = 20
SLEEP_SECS = 2.1
SAVE_EVERY = 20


def get_headers():
    return {
        "X-INSEE-Api-Key-Integration": API_KEY,
        "Accept": "application/json"
    }


def fetch_batch_cursor(cursor):
    params = {"q": QUERY, "nombre": BATCH_SIZE, "curseur": cursor}
    r = requests.get(BASE_URL, headers=get_headers(), params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ JSON file corrupted, starting fresh:", path)
    return default


def save_state(cursor, total_results, batches_done):
    state = {"cursor": cursor, "total_results": total_results, "batches_done": batches_done}
    save_json(state, STATE_FILE)


def load_state():
    return load_json(STATE_FILE, {"cursor": None, "total_results": None, "batches_done": 0})


def map_record(item):
    return {
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


def main():
    # Load previous results and state (for resume)
    results = load_json(OUTPUT_FILE, [])
    state = load_state()

    cursor = state["cursor"] or "*"
    total_results = state["total_results"]

    print("=== Start ===")
    print(f"Already collected: {len(results)} results")
    print(f"Starting cursor: {cursor}")

    # First call to get total if unknown
    if total_results is None:
        print("Fetching first batch to get total count…")
        data = fetch_batch_cursor(cursor)
        header = data.get("header", {})
        total_results = header.get("total", 0)
        establishments = data.get("etablissements", [])
        for item in establishments:
            results.append(map_record(item))

        # Save initial state
        batches_done = 1
        cursor_next = header.get("curseurSuivant")
        cursor_curr = header.get("curseur")
        save_json(results, OUTPUT_FILE)
        save_state(cursor_next, total_results, batches_done)

        # Init progress bar
        total_batches = math.ceil(total_results / BATCH_SIZE) if total_results else None
        pbar = tqdm(total=total_batches, desc="Downloading (cursor mode)", unit="batch")
        pbar.update(1)

        # Early exit if finished in one batch
        if not cursor_next or cursor_next == cursor_curr:
            pbar.close()
            print(f"✅ Done: {len(results)} results saved to {OUTPUT_FILE}")
            return
        cursor = cursor_next
        time.sleep(SLEEP_SECS)
    else:
        # We already know the total → init progress bar from state
        total_batches = math.ceil(total_results / BATCH_SIZE) if total_results else None
        pbar = tqdm(total=total_batches, desc="Downloading (cursor mode)", unit="batch", initial=state["batches_done"])

        batches_done = state["batches_done"]

    # Loop over remaining cursor pages
    while True:
        data = fetch_batch_cursor(cursor)
        header = data.get("header", {})
        establishments = data.get("etablissements", [])
        for item in establishments:
            results.append(map_record(item))

        batches_done += 1
        pbar.update(1)

        # Intermediate save
        if batches_done % SAVE_EVERY == 0:
            save_json(results, OUTPUT_FILE)
            save_state(header.get("curseurSuivant"), total_results, batches_done)
            print(f"💾 Saved after {batches_done} batches ({len(results)} results)")

        cursor_next = header.get("curseurSuivant")
        cursor_curr = header.get("curseur")

        # End condition
        if not cursor_next or cursor_next == cursor_curr:
            break

        cursor = cursor_next
        time.sleep(SLEEP_SECS)  # respect 30 req/min

    # Final save
    pbar.close()
    save_json(results, OUTPUT_FILE)
    save_state(None, total_results, batches_done)
    print(f"✅ Done: {len(results)} results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
