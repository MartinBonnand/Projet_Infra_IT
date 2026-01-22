import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Optionnel : Ajoute une tâche de test pour vérifier que ça marche
cur.execute("INSERT INTO taches (titre, description, date_echeance, terminee) VALUES (?, ?, ?, ?)",
            ('Première Tâche', 'Réussir mon projet IT', '2026-01-30', 0)
            )

connection.commit()
connection.close()
print("Base de données initialisée avec succès !")
