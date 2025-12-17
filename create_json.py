import json
from utils.grading import get_mention

# Données des screenshots (adapte si besoin)
etudiants_data = [
    {
        "adresse": "0x9b3b950.6556c7",
        "nom": "Rmidi",
        "prenom": "Mohamed",
        "date_naissance": "2002/06/17",
        "moyenne": 17.0,
        "mention": get_mention(17.0)  # Très Bien
    },
    {
        "adresse": "0x2222222.2222222",
        "nom": "Rmidi",
        "prenom": "Mohamed",
        "date_naissance": "2002/06/17",
        "moyenne": 17.0,
        "mention": get_mention(17.0)  # Très Bien (doublon)
    },
    {
        "adresse": "0x3333333.3333333",
        "nom": "Al Harmazi",
        "prenom": "Omar",
        "date_naissance": "2000/04/11",
        "moyenne": 13.0,
        "mention": get_mention(13.0)  # Assez Bien
    },
    {
        "adresse": "0x444444.4444444",
        "nom": "El Hassouni",
        "prenom": "Ayman",  # Screenshot dit "Aymane" ? J'ai mis Ayman, corrige si besoin
        "date_naissance": "1998/11/25",
        "moyenne": 10.0,
        "mention": get_mention(10.0)  # Passable
    }
]

data_file = 'etudiants.json'

# Écrit le JSON
with open(data_file, 'w', encoding='utf-8') as f:
    json.dump(etudiants_data, f, ensure_ascii=False, indent=2)

print("Fichier etudiants.json créé avec 4 étudiants et mentions correctes !")
for etu in etudiants_data:
    print(f"- {etu['nom']} {etu['prenom']}: {etu['moyenne']} -> {etu['mention']}")
