import sqlite3
from utils.grading import get_mention

db_file = 'students.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute('SELECT nom, prenom, moyenne, mention FROM students ORDER BY nom')
rows = cursor.fetchall()

print("Étudiants après correction :")
for row in rows:
    nom, prenom, moyenne, mention = row
    bonne_mention = get_mention(moyenne)
    print(f"{nom} {prenom}: Moyenne {moyenne} -> Mention en DB: '{mention}' (✓ si '{bonne_mention}')")

conn.close()
