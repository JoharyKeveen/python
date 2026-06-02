# import sqlite3

# # Création / ouverture de la base (fichier database.db)
# conn = sqlite3.connect("database.db")
# cursor = conn.cursor()

# # Création de la table pays
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS pays (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     nom TEXT NOT NULL UNIQUE
# )
# """)

# conn.commit()
# conn.close()

# print("Base de données créée avec succès")

















# import sqlite3

# conn = sqlite3.connect("database.db")
# cursor = conn.cursor()

# cursor.execute("SELECT * FROM pays ORDER BY nom")
# rows = cursor.fetchall()

# for r in rows:
#     print(r)

# conn.close()