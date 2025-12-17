import sqlite3

db_file = 'students.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Ajoute colonne si absente
cursor.execute("PRAGMA table_info(students);")
columns = [col[1] for col in cursor.fetchall()]
if 'mention' not in columns:
    cursor.execute('ALTER TABLE students ADD COLUMN mention TEXT DEFAULT "Passable"')
    print("Colonne 'mention' ajoutée avec défaut 'Passable'.")
else:
    print("Colonne 'mention' existe déjà.")

conn.commit()
conn.close()
