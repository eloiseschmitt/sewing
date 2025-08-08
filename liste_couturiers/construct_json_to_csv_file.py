import json
import csv

# Input / Output files
input_file = "list_couturiers_bordeaux_lat_lng.json"
output_file = "couturiers.csv"

# Load JSON
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Open CSV writer
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)

    # CSV headers
    headers = [
        "siret",
        "denomination",
        "activite_ape",
        "nom",
        "prenom",
        "adresse",
        "code_postal",
        "ville",
        "latitude",
        "longitude"
    ]
    writer.writerow(headers)

    # Loop through JSON entries
    for entry in data:
        row = [
            entry.get("siret", ""),
            entry.get("uniteLegale", {}).get("denominationUniteLegale", ""),
            entry.get("uniteLegale", {}).get("activitePrincipaleUniteLegale", ""),
            entry.get("uniteLegale", {}).get("nomUniteLegale", ""),
            entry.get("uniteLegale", {}).get("prenom1UniteLegale", ""),
            " ".join(filter(None, [
                entry.get("adresseEtablissement", {}).get("numeroVoieEtablissement", ""),
                entry.get("adresseEtablissement", {}).get("typeVoieEtablissement", ""),
                entry.get("adresseEtablissement", {}).get("libelleVoieEtablissement", "")
            ])).strip(),
            entry.get("adresseEtablissement", {}).get("codePostalEtablissement", ""),
            entry.get("adresseEtablissement", {}).get("libelleCommuneEtablissement", ""),
            entry.get("latitude", ""),
            entry.get("longitude", "")
        ]
        writer.writerow(row)

print(f"✅ Export terminé : {output_file}")
