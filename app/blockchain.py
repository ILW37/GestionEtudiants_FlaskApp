import os
from dotenv import load_dotenv

load_dotenv()

USE_BLOCKCHAIN = os.getenv('USE_BLOCKCHAIN', 'false').lower() == 'true'

if USE_BLOCKCHAIN:
    from web3 import Web3
    raise NotImplementedError("Blockchain désactivée pour le moment")

else:
    import sqlite3

    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "students.db")

    def init_db():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS students (
                adresse TEXT PRIMARY KEY,
                nom TEXT,
                prenom TEXT,
                dateNaissance TEXT,
                moyenne REAL
            )
        ''')
        conn.commit()
        conn.close()

    init_db()

    class BlockchainManager:
        def get_all_students(self):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT adresse, nom, prenom, dateNaissance, moyenne FROM students")
            rows = c.fetchall()
            conn.close()
            return [
                {"adresse": r[0], "nom": r[1], "prenom": r[2],
                 "dateNaissance": r[3], "moyenneGenerale": float(r[4])}
                for r in rows
            ]

        def add_student(self, adresse, nom, prenom, dateNaissance, moyenne):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            try:
                c.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?)",
                          (adresse, nom, prenom, dateNaissance, float(moyenne)))
                conn.commit()
                print(f"Étudiant {nom} {prenom} ajouté en local !")
            except sqlite3.IntegrityError:
                raise ValueError("Cette adresse existe déjà")
            finally:
                conn.close()
            return type('obj', (object,), {'transactionHash': {'hex': lambda: '0xLOCAL123'}})()

        def get_statistics(self):
            students = self.get_all_students()
            total = len(students)
            if total == 0:
                return {'total': 0, 'moyenne_generale': 0.0, 'reussis': 0, 'excellents': 0,
                        'mentions': {'Passable':0, 'AssezBien':0, 'Bien':0, 'TresBien':0, 'Excellent':0}}

            moyenne = sum(s["moyenneGenerale"] for s in students) / total
            reussis = sum(1 for s in students if s["moyenneGenerale"] >= 10)
            excellents = sum(1 for s in students if s["moyenneGenerale"] >= 16)

            def mention(m):
                if m < 10: return "Passable"
                elif m < 12: return "AssezBien"
                elif m < 14: return "Bien"
                elif m < 16: return "TresBien"
                else: return "Excellent"

            mentions = {"Passable":0, "AssezBien":0, "Bien":0, "TresBien":0, "Excellent":0}
            for s in students:
                mentions[mention(s["moyenneGenerale"])] += 1

            return {
                'total': total,
                'moyenne_generale': round(moyenne, 2),
                'reussis': reussis,
                'excellents': excellents,
                'mentions': mentions
            }

        def get_student(self, adresse):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT * FROM students WHERE adresse = ?", (adresse,))
            row = c.fetchone()
            conn.close()
            if row:
                return {"adresse": row[0], "nom": row[1], "prenom": row[2],
                        "dateNaissance": row[3], "moyenneGenerale": float(row[4])}
            return None
