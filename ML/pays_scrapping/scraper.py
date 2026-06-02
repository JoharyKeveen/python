import requests
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0"
}


def search_element(nom_pays, texte_recherche):
    url = "https://fr.wikipedia.org/wiki/" + nom_pays.replace(" ", "_")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.content, "html.parser")

        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                th = row.find("th")
                td = row.find("td")

                if th and td:
                    titre = th.get_text(" ", strip=True)

                    if texte_recherche.lower() in titre.lower():
                        valeur = td.get_text(" ", strip=True)
                        valeur = re.sub(r"\[.*?\]", "", valeur)
                        return valeur

    except:
        return ""

    return ""


def get_population_capitale(nom_ville):
    if not nom_ville:
        return ""

    url = "https://fr.wikipedia.org/wiki/" + nom_ville.replace(" ", "_")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.content, "html.parser")

        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                th = row.find("th")
                td = row.find("td")

                if th and td:
                    titre = th.get_text(" ", strip=True).lower()

                    if "population" in titre:
                        valeur = td.get_text(" ", strip=True)
                        valeur = re.sub(r"\[.*?\]", "", valeur)
                        return valeur

    except:
        return ""

    return ""