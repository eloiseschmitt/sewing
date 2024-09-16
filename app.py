from flask import Flask, render_template
import pandas as pd


app = Flask(__name__)


class SewingCompany:
    def __init__(self, siren: int, main_activity: str, denomination: str, activite_principale: str, siege):
        self.siren = siren
        self.main_activity = main_activity
        self.denomination = denomination
        self.activite_principale = activite_principale
        self.siege = siege


@app.route('/')
def index():
    csv_data = pd.read_csv(filepath_or_buffer="data_sources/etablissements_romain.csv", sep=",")
    sewing_companies = []
    for _, row in csv_data.iterrows():
        if row["activitePrincipaleUniteLegale"] == "95.29Z":
            sewing_company = SewingCompany(siren=row["siren"],
                                           main_activity=row["activitePrincipaleUniteLegale"],
                                           denomination=row["denominationUniteLegale"],
                                           activite_principale=row["activitePrincipaleRegistreMetiersEtablissement"],
                                           siege=row["etablissementSiege"])
            sewing_companies.append(sewing_company)
    return render_template('couturiers.html', couturiers=sewing_companies)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
