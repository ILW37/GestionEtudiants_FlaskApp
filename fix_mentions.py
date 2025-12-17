import sqlite3
from utils.grading import get_mention

db_file = 'students.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Récupère TOUS les étudiants (pas d'ID, donc on itère sur tout)
cursor.execute('SELECT nom, prenom, moyenne FROM students')
rows = cursor.fetchall()

updated = 0
for row in rows:
    nom, prenom, moyenne = row
    nouvelle_mention = get_mention(moyenne)
    
    # Update basé sur nom + prenom + moyenne (unique ? ; sinon, adapte si doublons)
    cursor.execute('''
        UPDATE students 
        SET mention = ? 
        WHERE nom = ? AND prenom = ? AND moyenne = ?
    ''', (nouvelle_mention, nom, prenom, moyenne))
    
    if cursor.rowcount > 0:
        updated += 1
        print(f"Mis à jour {nom} {prenom}: '{nouvelle_mention}'")

conn.commit()
conn.close()
print(f"\n{updated} mentions corrigées et stockées en DB !")
