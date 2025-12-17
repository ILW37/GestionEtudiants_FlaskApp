import json
import os
from utils.grading import get_mention

data_file = 'etudiants.json'

if os.path.exists(data_file):
    with open(data_file, 'r', encoding='utf-8') as f:
        etudiants = json.load(f)
    
    updated = 0
    for etu in etudiants:
        if 'mention' not in etu:
            etu['mention'] = get_mention(etu['moyenne'])
            updated += 1
            print(f"Mis à jour {etu['nom']} {etu['prenom']}: {etu['mention']}")
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(etudiants, f, ensure_ascii=False, indent=2)
    
    print(f"{updated} mentions ajoutées au JSON !")
else:
    print("Fichier etudiants.json non trouvé – ajoute un étudiant via l'app pour le créer.")
