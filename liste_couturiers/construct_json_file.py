import json
import os

# Dossier contenant tes fichiers JSON
DOSSIER_JSON = "./listing-couturiers"
json_files = [f for f in os.listdir(DOSSIER_JSON) if f.endswith(".json")]

results = []
seen_sirets = set()

for json_file in json_files:
    path = os.path.join(DOSSIER_JSON, json_file)
    with open(path, "r", encoding="utf-8") as f:
        content = json.load(f)

        units = content.get("etablissements", [])
        for unit in units:
            siret = unit.get("siret", "")
            if siret and siret not in seen_sirets:
                item = {
                    "siret": siret,
                    "uniteLegale": {
                        "denominationUniteLegale": unit.get("uniteLegale", {}).get("denominationUniteLegale", ""),
                        "activitePrincipaleUniteLegale": unit.get("uniteLegale", {}).get("activitePrincipaleUniteLegale", ""),
                        "nomUniteLegale": unit.get("uniteLegale", {}).get("nomUniteLegale", ""),
                        "prenom1UniteLegale": unit.get("uniteLegale", {}).get("prenom1UniteLegale", "")
                    },
                    "adresseEtablissement": {
                        "numeroVoieEtablissement": unit.get("adresseEtablissement", {}).get("numeroVoieEtablissement", ""),
                        "typeVoieEtablissement": unit.get("adresseEtablissement", {}).get("typeVoieEtablissement", ""),
                        "libelleVoieEtablissement": unit.get("adresseEtablissement", {}).get("libelleVoieEtablissement", ""),
                        "codePostalEtablissement": unit.get("adresseEtablissement", {}).get("codePostalEtablissement", ""),
                        "libelleCommuneEtablissement": unit.get("adresseEtablissement", {}).get("libelleCommuneEtablissement", "")
                    }
                }
                results.append(item)
                seen_sirets.add(siret)

# Sauvegarde finale
with open("list_couturiers_bordeaux.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
