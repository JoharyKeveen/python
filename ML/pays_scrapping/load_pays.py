# import requests
# from bs4 import BeautifulSoup
# import sqlite3
# import re

# headers = {
#     "User-Agent": "MonProjetPython/1.0"
# }

# url = "https://fr.wikipedia.org/wiki/Liste_des_pays_par_population"

# response = requests.get(url, headers=headers)
# soup = BeautifulSoup(response.text, "html.parser")

# table = soup.find("table", class_="wikitable")
# rows = table.find_all("tr")

# # 🗄️ connexion base SQLite
# conn = sqlite3.connect("database.db")
# cursor = conn.cursor()

# for row in rows[1:]:
#     cols = row.find_all("td")

#     if len(cols) < 2:
#         continue

#     pays = re.sub(r"\[.*?\]", "", cols[1].get_text(strip=True))

#     if pays.lower() == "monde":
#         continue

#     cursor.execute(
#         "INSERT OR IGNORE INTO pays(nom) VALUES (?)",
#         (pays,)
#     )

# conn.commit()
# conn.close()

# print("✔ Liste des pays insérée dans la base")