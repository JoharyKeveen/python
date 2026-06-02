from flask import Flask, render_template, request
from scraper import search_element, get_population_capitale
import sqlite3
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def get_pays():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom FROM pays ORDER BY id ASC")
    data = cursor.fetchall()
    conn.close()
    return data


def get_infos_pays(nom_pays):
    url = "https://fr.wikipedia.org/wiki/" + nom_pays.replace(" ", "_")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    infobox = soup.find("table", class_="infobox")

    if not infobox:
        return {}

    infos = {}
    for row in infobox.find_all("tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            key = th.get_text(" ", strip=True).lower()
            value = td.get_text(" ", strip=True)
            value = re.sub(r"\[.*?\]", "", value)
            if "capitale" in key:
                infos["capitale"] = value
            if "langue" in key:
                infos["langue"] = value
            if "superficie" in key:
                infos["superficie"] = value
    return infos

def dms_to_decimal(dms):
    try:
        match = re.match(r"(\d+)[°]\s*(\d+)?[′']?\s*([NSEW])", dms.strip())

        if not match:
            return None

        deg = float(match.group(1))
        minutes = float(match.group(2)) if match.group(2) else 0
        direction = match.group(3)
        decimal = deg + minutes / 60
        if direction in ["S", "W"]:
            decimal = -decimal
        return decimal
    except:
        return None


# -------------------
# ROUTE HOME
# -------------------
@app.route("/")
def index():
    pays = get_pays()
    return render_template("index.html", pays=pays)


# -------------------
# ROUTE DETAILS
# -------------------
@app.route("/details")
def details():

    nom_pays = request.args.get("pays")

    capitale = search_element(nom_pays, "Capitale")
    superficie = search_element(nom_pays, "Superficie")
    langue = search_element(nom_pays, "Langues officielles")

    latitude = None
    longitude = None

    if capitale:
        coords = re.findall(r"\d+°\s*\d+['′]?\s*[NSEW]", capitale)

        if len(coords) >= 2:
            latitude = dms_to_decimal(coords[0])
            longitude = dms_to_decimal(coords[1])

        capitale = re.sub(r"\d+°.*", "", capitale).strip()
        capitale = re.sub(r"\[.*?\]", "", capitale)

    population_capitale = get_population_capitale(capitale)

    infos = {
        "capitale": capitale,
        "superficie": superficie,
        "langue": langue,
        "latitude": latitude,
        "longitude": longitude,
        "population_capitale": population_capitale
    }

    return render_template(
        "details.html",
        pays=nom_pays,
        infos=infos
    )

if __name__ == "__main__":
    app.run(debug=True)