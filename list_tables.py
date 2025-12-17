import sqlite3
import os

db_file = 'students.db'  # Le vrai fichier !

print(f"Vérification DB: {db_file}")
if not os.path.exists(db_file):
    print(f"ERREUR: Fichier {db_file} n'existe pas !")
    exit(1)

try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables trouvées :")
    if tables:
        for table in tables:
            print(f"- {table[0]}")
        
        # Liste colonnes de la table principale (probablement 'student' ou 'students')
        if tables:
            main_table = tables[0][0]  # Prend la première (adapte si plusieurs)
            print(f"\nColonnes de la table '{main_table}' :")
            cursor.execute(f"PRAGMA table_info({main_table});")
            columns = cursor.fetchall()
            for col in columns:
                print(f"- {col[1]} (type: {col[2]})")
    else:
        print("Aucune table trouvée (DB vide ?)")
    
    conn.close()
except Exception as e:
    print(f"ERREUR: {e}")

