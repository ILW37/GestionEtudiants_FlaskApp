from flask import Flask, render_template, request, redirect, flash
import json
import os
from grading import get_mention
  

app = Flask(__name__)
app.secret_key = "votre_cle_secrete_ici"  # Pour les messages flash

# Fichier de persistance (optionnel, pour ne pas perdre les données)
DATA_FILE = "etudiants.json"

# --- BASE DE DONNÉES EN MÉMOIRE ---
etudiants = []

def charger_donnees():
    """Charge les données depuis le fichier JSON si il existe"""
    global etudiants
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                etudiants = json.load(f)
            print(f"✓ {len(etudiants)} étudiants chargés")
            # NOUVEAU : Recalcule mentions si manquantes (pour anciens JSON)
            for etu in etudiants:
                if 'mention' not in etu:
                    etu['mention'] = get_mention(etu['moyenne'])
            print("✓ Mentions recalculées pour les anciens étudiants")
        except Exception as e:
            print(f"Erreur chargement: {e}")
            etudiants = []
    else:
        etudiants = []

def sauvegarder_donnees():
    """Sauvegarde les données dans un fichier JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(etudiants, f, ensure_ascii=False, indent=2)
        print("✓ Données sauvegardées")
    except Exception as e:
        print(f"Erreur sauvegarde: {e}")

def calculer_statistiques():
    """Calcule les statistiques des étudiants"""
    if not etudiants:
        return {
            "total": 0,
            "moyenne_classe": 0,
            "reussis": 0,
            "excellents": 0
        }
    
    total = len(etudiants)
    moyennes = [e["moyenne"] for e in etudiants]
    moyenne_classe = sum(moyennes) / total if total > 0 else 0
    reussis = sum(1 for m in moyennes if m >= 10)
    excellents = sum(1 for m in moyennes if m >= 16)
    
    return {
        "total": total,
        "moyenne_classe": moyenne_classe,
        "reussis": reussis,
        "excellents": excellents
    }

# Configuration fictive pour les templates
config = {
    "CONTRACT_ADDRESS": "0x0000000000000000000000000000000000000000"
}

@app.route("/")
def accueil():
    """Page d'accueil avec statistiques"""
    stats = calculer_statistiques()
    return render_template("index.html", stats=stats, config=config, error=None)

@app.route("/liste")
def liste():
    """Affiche la liste des étudiants"""
    return render_template("liste.html", etudiants=etudiants)

@app.route("/ajouter", methods=["GET", "POST"])
def ajouter():
    """Ajoute un nouvel étudiant"""
    if request.method == "POST":
        try:
            # NOUVEAU : Récupère tous les champs (adresse, date_naissance inclus)
            adresse = request.form.get("adresse", "").strip()
            nom = request.form.get("nom", "").strip()
            prenom = request.form.get("prenom", "").strip()
            date_naissance = request.form.get("date_naissance", "").strip()
            moyenne_str = request.form.get("moyenne", "0")
            
            # Validation
            if not nom or not prenom:
                flash("Le nom et le prénom sont obligatoires", "danger")
                return render_template("ajouter.html")
            
            moyenne = float(moyenne_str)
            
            if moyenne < 0 or moyenne > 20:
                flash("La moyenne doit être entre 0 et 20", "danger")
                return render_template("ajouter.html")
            
            # NOUVEAU : Calcule la mention
            mention = get_mention(moyenne)
            
            # NOUVEAU : Ajout de l'étudiant avec TOUS les champs
            etudiants.append({
                "adresse": adresse,
                "nom": nom,
                "prenom": prenom,
                "date_naissance": date_naissance,
                "moyenne": moyenne,
                "mention": mention
            })
            
            # Sauvegarde
            sauvegarder_donnees()
            
            flash(f"Étudiant {prenom} {nom} ajouté avec succès !", "success")
            return redirect("/liste")
            
        except ValueError:
            flash("Moyenne invalide. Veuillez entrer un nombre.", "danger")
            return render_template("ajouter.html")
        except Exception as e:
            flash(f"Erreur lors de l'ajout: {str(e)}", "danger")
            return render_template("ajouter.html")
    
    return render_template("ajouter.html")

@app.route("/statistiques")
def statistiques():
    """Affiche les statistiques détaillées"""
    stats = calculer_statistiques()
    return render_template("statistiques.html", stats=stats, etudiants=etudiants)

@app.route("/supprimer/<int:index>")
def supprimer(index):
    """Supprime un étudiant par son index"""
    try:
        if 0 <= index < len(etudiants):
            etudiant = etudiants.pop(index)
            sauvegarder_donnees()
            flash(f"Étudiant {etudiant['prenom']} {etudiant['nom']} supprimé", "info")
        else:
            flash("Étudiant introuvable", "danger")
    except Exception as e:
        flash(f"Erreur lors de la suppression: {str(e)}", "danger")
    
    return redirect("/liste")

@app.route("/reinitialiser")
def reinitialiser():
    """Réinitialise toutes les données"""
    global etudiants
    etudiants = []
    sauvegarder_donnees()
    flash("Toutes les données ont été réinitialisées", "warning")
    return redirect("/")

# Charger les données au démarrage
charger_donnees()

if __name__ == "__main__":
    print("=" * 50)
    print("🎓 Application Gestion Étudiants démarrée")
    print(f"📊 {len(etudiants)} étudiant(s) en mémoire")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)