import csv
import random
import sys
import os

### ==========================================
### ⚙️ CONFIGURATION DU GÉNÉRATEUR
### ==========================================

DOSSIER_EXPORT = "Inputs/"
NOM_FICHIER = "univers_chaos.csv"

# Configuration par défaut si aucun argument n'est passé
NB_CORPS_DEFAUT = 50

# Dimensions et paramètres physiques du système généré
UNITE_ASTRONOMIQUE = 1.496e11
TAILLE_BOITE = 40.0 * UNITE_ASTRONOMIQUE
VITESSE_MAX = 15000                       # Vitesse d'éjection max initiale en m/s

### ==========================================

def obtenir_nb_corps():
    """Récupère le nombre d'astres via argument console ou saisie utilisateur."""
    if len(sys.argv) > 1:
        try:
            return int(sys.argv[1])
        except ValueError:
            sys.exit("❌ Erreur : L'argument doit être un nombre entier valide (ex: python generateur_chaos.py 150)")
    else:
        saisie = input(f"Combien d'astres souhaitez-vous générer ? [Entrée = {NB_CORPS_DEFAUT}] : ").strip()
        if saisie == "":
            return NB_CORPS_DEFAUT
        try:
            return int(saisie)
        except ValueError:
            sys.exit("❌ Erreur : Veuillez entrer un nombre entier.")

def generer_chaos():
    nb_corps = obtenir_nb_corps()
    
    if not os.path.exists(DOSSIER_EXPORT):
        os.makedirs(DOSSIER_EXPORT)
        
    chemin_complet = os.path.join(DOSSIER_EXPORT, NOM_FICHIER)
    
    en_tete = ["Name", "Mass", "Position X", "Position Y", "Velocity X", "Velocity Y"]
    
    print(f"⏳ Génération d'un univers chaotique de {nb_corps} corps...")
    
    with open(chemin_complet, mode='w', newline='') as fichier_csv:
        writer = csv.writer(fichier_csv)
        writer.writerow(en_tete)
        
        for i in range(1, nb_corps + 1):
            nom = f"Astre_{i}"
            
            # Génère équitablement beaucoup de petits corps et quelques corps hyper-massifs
            masse = 10 ** random.uniform(22, 30.5)  
            
            # Positions cartésiennes totalement aléatoires dans la limite de la boîte
            pos_x = random.uniform(-TAILLE_BOITE / 2, TAILLE_BOITE / 2)
            pos_y = random.uniform(-TAILLE_BOITE / 2, TAILLE_BOITE / 2)
            
            # Vitesses vectorielles aléatoires
            vel_x = random.uniform(-VITESSE_MAX, VITESSE_MAX)
            vel_y = random.uniform(-VITESSE_MAX, VITESSE_MAX)
            
            writer.writerow([nom, masse, pos_x, pos_y, vel_x, vel_y])
            
    print(f"✅ Génération terminée ! Fichier prêt : {chemin_complet}")

if __name__ == "__main__":
    generer_chaos()