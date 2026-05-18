import csv
import sys
import math
import numpy as np
import time
import os

###
#
# Configuration et constantes
#
###

VALID_COLUMNS = ['name', 'mass', 'position x', 'position y', 'velocity x', 'velocity y']

ERROR_MESSAGES = { # 
    "empty_path": "Le chemin du fichier ne peut pas être vide.",
    "file_not_found": "le fichier '{file_name}' est introuvable.",
    "invalid_file_format": "format de fichier invalide. Veuillez fournir un fichier CSV.",
    "missing_columns": "L'en-tête du fichier est invalide. La toute première ligne du CSV DOIT être exactement structurée avec ces colonnes : 'Name', 'Mass', 'Position X', 'Position Y', 'Velocity X', 'Velocity Y'.",
    "duplicate_name": "Ligne {index}: le nom '{name}' est dupliqué.",
    "invalid_mass": "Ligne {index}: la masse du corps '{name}' doit être un entier positif.",
    "invalid_position": "Ligne {index}: les positions du corps '{name}' sont invalides.",
    "invalid_velocity": "Ligne {index}: les vitesses du corps '{name}' sont invalides.",
    "collision": "Arrêt de la simulation, collision à t = {t}s"
}

OUTPUT_FOLDER = "Outputs" # Dossier de sortie pour les fichiers CSV générés
G = 6.67408e-11 # m^3 kg^-1 s^-2 (constante gravitationnelle universelle)
DENSITY = 5500  # kg/m^3 (densité moyenne type planète rocheuse)

###
#
# Récupération du chemin relatif fichier CSV
#
###

def get_file_path():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Veuillez entrer le chemin du fichier CSV : ").strip()

    if file_path == "":
        raise ValueError(ERROR_MESSAGES["empty_path"])
        
    if not file_path.lower().endswith('.csv'):
        raise ValueError(ERROR_MESSAGES["invalid_file_format"])
        
    if not os.path.exists(file_path):
       raise FileNotFoundError(ERROR_MESSAGES["file_not_found"].format(file_name=file_path))
        
    return file_path

def afficher_barre_progression(t, duree, longueur=40):
    fraction = min(t / duree, 1.0)
    nb_blocs = int(longueur * fraction)
    barre = '█' * nb_blocs + '-' * (longueur - nb_blocs)
    pourcentage = fraction * 100
    # \r permet de revenir au début de la ligne actuelle dans la console
    print(f"\r⏳ Progression : |{barre}| {pourcentage:.1f}%", end="")

###
# Validation des données (Optimisée : Cast + Validation en une étape)
###

def validate_row(index, row, names):
    """
    Vérifie la validité d'une ligne et retourne les valeurs castées.
    L'en-tête est déjà mis en minuscule par le DictReader.
    """
    name = row['name'] # On utilise les clés en minuscules ici

    if name in names:
        raise ValueError(ERROR_MESSAGES["duplicate_name"].format(index=index, name=name))

    try:
        # Cast unique : on stocke le résultat pour ne pas le recalculer plus tard
        m = float(row['mass'])
        if m <= 0:
            raise ValueError()
    except (ValueError, TypeError, KeyError):
        raise ValueError(ERROR_MESSAGES["invalid_mass"].format(index=index, name=name))

    try:
        px = float(row['position x'])
        py = float(row['position y'])
    except (ValueError, TypeError, KeyError):
        raise ValueError(ERROR_MESSAGES["invalid_position"].format(index=index, name=name))

    try:
        vx = float(row['velocity x'])
        vy = float(row['velocity y'])
    except (ValueError, TypeError, KeyError):
        raise ValueError(ERROR_MESSAGES["invalid_velocity"].format(index=index, name=name))

    return name, m, px, py, vx, vy


###
# Parsing du CSV (Optimisé : Double Passe & Case Insensitive)
###

def load_bodies(file_path):
    d_names = set()

    try: 
        # --- 1. PREMIÈRE PASSE : Compter & Vérifier l'en-tête ---
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            # On force les noms de colonnes en minuscules immédiatement
            reader = csv.DictReader(csvfile)
            reader.fieldnames = [f.lower() for f in reader.fieldnames]
            
            # Vérification du contrat d'interface (Insensible à la casse)
            if not all(col in reader.fieldnames for col in VALID_COLUMNS):
                raise ValueError(ERROR_MESSAGES["missing_columns"])
            
            # Compte rapide (Passe 1)
            n_bodies = sum(1 for row in reader if any(row.values()))

        # --- 2. PRÉ-ALLOCATION ---
        t_names = []
        t_mass = np.empty(n_bodies, dtype=np.float64)
        t_pos = np.empty((n_bodies, 2), dtype=np.float64)
        t_vel = np.empty((n_bodies, 2), dtype=np.float64)
    except FileNotFoundError:
        raise FileNotFoundError(ERROR_MESSAGES["file_not_found"].format(file_name=file_path))

    # --- 3. SECONDE PASSE : Lecture, Validation et Remplissage ---
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        # On remet les minuscules pour cette passe aussi
        reader.fieldnames = [f.lower() for f in reader.fieldnames]
        
        index_array = 0 
        for index_csv, row in enumerate(reader, start=2):
            if not any(row.values()):
                continue

            # validate_row retourne maintenant les valeurs déjà converties en float
            name, m, px, py, vx, vy = validate_row(index_csv, row, d_names)
            
            d_names.add(name)

            # Injection directe des variables déjà castées (Gain CPU important)
            t_names.append(name)
            t_mass[index_array] = m
            t_pos[index_array] = [px, py]
            t_vel[index_array] = [vx, vy]
            
            index_array += 1

    print(f"✅ Fichier '{file_path}' chargé avec succès : {n_bodies} corps détectés.\n")
    return t_names, t_mass, t_pos, t_vel


def calculer_rayons(mass, density=DENSITY):

    return ((3 * mass) / (4 * np.pi * density)) ** (1/3)


def calculer_pas_optimal(pos, mass, eta=0.01):
    # Distances entre toutes les paires
    dr = pos[np.newaxis, :, :] - pos[:, np.newaxis, :]
    r2 = np.sum(dr**2, axis=-1)

    # Ignore les distances i=i
    np.fill_diagonal(r2, np.inf)

    r = np.sqrt(r2)

    # Sommes des masses paire à paire
    m = mass[:, np.newaxis] + mass[np.newaxis, :]

    # Temps dynamique
    t_dyn = np.sqrt(r**3 / (G * m))

    # Plus petite échelle de temps
    t_min = np.min(t_dyn)

    # Pas fixe final
    dt = eta * t_min

    return dt

###
#
# Configuration de la simulation
#
###

def configurer_simulation(pos, vel, mass):
    print("\n========== CONFIGURATION DE LA SIMULATION ==========")

    # --- 1. CHOIX DE LA DURÉE ---
    print("\n[1] DURÉE DE LA SIMULATION")
    unite = input("Unité de durée (J: Jours, A: Années, S: Secondes) [Défaut = J] : ").upper()
    if unite not in ['J', 'A', 'S']:
        print(" ! Unité non reconnue, utilisation du réglage par défaut : Jours")
        unite = 'J'

    try:
        valeur_input = input(f"Entrez la durée totale ({unite}) : ")
        valeur_duree = float(valeur_input)
    except ValueError:
        print(" ! Erreur de saisie (nombre attendu). Valeur par défaut utilisée : 365 Jours")
        valeur_duree = 365.0
        unite = 'J'

    if unite == 'A':
        duree_sec = valeur_duree * 365.25 * 24 * 3600
    elif unite == 'S':
        duree_sec = valeur_duree
    else:
        duree_sec = valeur_duree * 24 * 3600

    # --- 2. CHOIX DU PAS PHYSIQUE (TAU) ---
    print("\n[2] PRÉCISION DU CALCUL (PAS DE TEMPS)")
    user_tau_input = input("Entrez le pas de calcul (s) [Laissez vide pour AUTO] : ")
    
    pas = None
    if user_tau_input.strip() != "":
        try:
            pas = float(user_tau_input)
        except ValueError:
            print(" ! Saisie invalide pour le pas.")

    if pas is None:
        pas = calculer_pas_optimal(pos, mass)
        print(f" > Mode automatique activé : Pas calculé à {pas:.2f} s")

    # --- 3. CHOIX DE LA SAUVEGARDE (INTERVALLE) ---
    print("\n[3] EXPORTATION DES DONNÉES (CSV)")
    print(" (1) Nombre de points total (ex: 1000)")
    print(" (2) Intervalle de temps fixe")
    mode_save = input("Choix (1/2) [Défaut = 1] : ")

    try:
        if mode_save == '2':
            intervalle = float(input("Entrez l'intervalle de sauvegarde (s) : "))
        else:
            nb_input = input("Nombre de lignes souhaitées ? [Défaut = 1000] : ")
            nb_points = int(nb_input) if nb_input.strip() != "" else 1000
            intervalle = duree_sec / nb_points
    except ValueError:
        print(" ! Saisie invalide : Utilisation de la valeur par défaut (1000 points).")
        intervalle = duree_sec / 1000

    if intervalle < pas:
        intervalle = pas

    # --- 4. CHOIX DU MODE D'EXÉCUTION (NOUVEAU) ---
    print("\n[4] MODE D'EXÉCUTION")
    print(" (1) Matrices (Rapide - NumPy)")
    print(" (2) Boucles (Lent - Algorithme pur)")
    print(" (3) Performance (Test de comparaison)")
    
    choix_mode = input("Quel mode souhaitez-vous ? [Défaut = 1] : ")
    try:
        if choix_mode.strip() == "":
            mode = 1
        else:
            mode = int(choix_mode)
    except ValueError:
        mode = 1

    if mode not in [1, 2, 3]:
        print(f" ! Mode invalide : Utilisation des matrices par défaut.")
        mode = 1

    # --- RÉCAPITULATIF FINAL ---
    nom_modes = {1: "Matrices (NumPy)", 2: "Boucles (Action/Réaction)", 3: "Test de Performance"}
    print("\n===================================================")
    print("\n✅ RÉCAPITULATIF DE VOS RÉGLAGES :")
    print(f"⏳ Durée simulée  : {valeur_duree} {unite} ({duree_sec:.0f} s)")
    print(f"⚙️  Pas de calcul : {pas:.2f} s")
    print(f"📊 Intervalle CSV : 1 ligne toutes les {intervalle:.2f} s")
    print(f"🚀 Mode choisi   : {nom_modes[mode]}")
    print("\n===================================================\n")

    return duree_sec, pas, intervalle, mode

###
#
# Calcul des accélérations avec la méthode par boucles (version de base, plus lente)
#
###

def calculer_accelerations_boucles(mass, pos, rayons, time):
    N = len(mass)
    accelerations = np.zeros((N, 2))

    # Boucle externe normale
    for i in range(N):
        for j in range(i + 1, N): 
            
            dx = pos[j, 0] - pos[i, 0]
            dy = pos[j, 1] - pos[i, 1]
            
            r2 = dx**2 + dy**2
            r = math.sqrt(r2)

            # Correction : r est un scalaire (un simple float), pas besoin de np.any()
            if r < rayons[i] + rayons[j]:
                raise ValueError(ERROR_MESSAGES["collision"].format(t=time))

            # 1. Calcul de la FORCE scalaire mutuelle (symétrique)
            # F = G * m1 * m2 / r^2
            force_scalaire = G * mass[i] * mass[j] / r2

            # 2. Projection de cette force sur X et Y
            force_x = force_scalaire * (dx / r)
            force_y = force_scalaire * (dy / r)

            # 3. Application de l'Action / Réaction
            # L'accélération, c'est a = F / m
            
            # L'astre i est tiré vers l'astre j (on ADDITIONNE)
            accelerations[i, 0] += force_x / mass[i]
            accelerations[i, 1] += force_y / mass[i]

            # L'astre j est tiré vers l'astre i (on SOUSTRAIT, sens opposé)
            accelerations[j, 0] -= force_x / mass[j]
            accelerations[j, 1] -= force_y / mass[j]

    return accelerations

###
#
# Calcul des accélérations avec la méthode matricielle
#
###

def calculer_accelerations_matrice(mass, pos, rayons, time):
    diff = pos[np.newaxis, :, :] - pos[:, np.newaxis, :]

    r2 = np.sum(diff**2, axis=-1)
    np.fill_diagonal(r2, np.inf)
    r = np.sqrt(r2)

    rayons_collision = rayons[:, np.newaxis] + rayons[np.newaxis, :]

    if np.any(r < rayons_collision):
        raise ValueError(ERROR_MESSAGES["collision"].format(t=time))
    
    acc_scalaire = (G * mass / r2)[:, :, np.newaxis]
    
    total_acc = np.sum(acc_scalaire * (diff / r[:, :, np.newaxis]), axis=1)
    
    return total_acc


def obtenir_nom_fichier_sortie(chemin_entree):
    # 1. On extrait juste le nom sans le dossier et sans l'extension
    nom_fichier_complet = os.path.basename(chemin_entree) # 'fusee_crash.csv'
    nom_base = os.path.splitext(nom_fichier_complet)[0]   # 'fusee_crash'

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    # 2. On commence à S1
    compteur = 1
    nom_sortie = f"{nom_base}_S{compteur}.csv"
    
    # 3. On incrémente tant que le fichier existe
    while os.path.exists(f"{OUTPUT_FOLDER}/{nom_sortie}"):
        compteur += 1
        nom_sortie = f"{nom_base}_S{compteur}.csv"

    return nom_sortie

###
#
# Simulation avec la méthode de Verlet
#
###

# pos, vel et acc sont des matrices (N, 2)
# mode 1 = matrices, 2 = boucles, 3 = perf
def simulation_verlet(names, mass, pos, vel, rayons, duree=7, pas=60, intervalle=3600, mode=1, file_out="simulation.csv"):
    t = 0
    prochaine_sauvegarde = 0
    
    colonnes = []
    for name in names:
        colonnes.extend([f"{name}_X", f"{name}_Y", f"{name}_VX", f"{name}_VY"])
        
    print(f"Début de la simulation (Durée: {duree}s, Pas: {pas}s)\n")
    
    with open(f"{OUTPUT_FOLDER}/{file_out}", 'w', newline='') as csvfile:
        # ON GARDE LA DURÉE ET LE PAS ICI
        csvfile.write(f"# DUREE_SEC:{duree:.1f}|PAS:{pas:.4f}|INTERVALLE:{intervalle:.2f}\n")
        writer = csv.writer(csvfile)
        writer.writerow(colonnes)
        writer.writerow(np.hstack((pos, vel)).flatten())

        if (mode == 2):
            acc = calculer_accelerations_boucles(mass, pos, rayons, t)
        else:
            acc = calculer_accelerations_matrice(mass, pos, rayons, t)
            

        while t < duree:
            pos = pos + pas * vel + 0.5 * (pas**2) * acc

            if (mode == 2):
                acc_new = calculer_accelerations_boucles(mass, pos, rayons, t)    
            else:
                acc_new = calculer_accelerations_matrice(mass, pos, rayons, t)
                

            vel = vel + pas * 0.5 * (acc + acc_new)

            acc = acc_new

            if t >= prochaine_sauvegarde:
                writer.writerow(np.hstack((pos, vel)).flatten())
                prochaine_sauvegarde += intervalle
                afficher_barre_progression(t, duree)
                
            t += pas


###
#
# Test de performance entre les deux méthodes
#
###

def test_performance(names, mass, pos, vel, rayons, duree, pas, intervalle, file_out):
    print("Lancement des boucles...")
    debut_boucles = time.perf_counter()
    simulation_verlet(names, mass, pos, vel, rayons, pas=pas, intervalle=intervalle, duree=duree, mode=2, file_out=file_out)
    fin_boucles = time.perf_counter()
    temps_boucles = fin_boucles - debut_boucles
    print(f"⏱️ Temps (Boucles) : {temps_boucles:.5f} secondes\n")

    print("Lancement des matrices...")
    debut_matrice = time.perf_counter()
    simulation_verlet(names, mass, pos, vel, rayons, pas=pas, intervalle=intervalle, duree=duree, mode=1, file_out=file_out)
    fin_matrice = time.perf_counter()
    temps_matrice = fin_matrice - debut_matrice
    print(f"⏱️ Temps (Matrice) : {temps_matrice:.5f} secondes\n")

    # Comparaison des performances
    if temps_matrice > 0:
        ratio = temps_boucles / temps_matrice
        print(f"🏆 VERDICT : La méthode matricielle est {ratio:.1f} fois plus rapide dans cette configuration!\n")

###
#
# Main
#
###

def main():
    try:
        # 1. Parsing
        file_path = get_file_path()
        names, mass, pos, vel = load_bodies(file_path)

        rayons = calculer_rayons(mass)

        # 2. Configuration
        duree, pas, intervalle, mode = configurer_simulation(pos, vel, mass)
        file_out = obtenir_nom_fichier_sortie(file_path)

        if (mode == 3): # Comparaison des deux méthodes 
            test_performance(names, mass, pos, vel, rayons, duree, pas, intervalle, file_out=file_out)
        else:
            simulation_verlet(names, mass, pos, vel, rayons, duree=duree, pas=pas, intervalle=intervalle, mode=mode, file_out=file_out)
        
        print(f"\n✅ Simulation terminée ! Résultats sauvegardés dans '{OUTPUT_FOLDER}/{file_out}'")
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

