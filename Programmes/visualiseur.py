import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
from matplotlib.patches import FancyBboxPatch
import numpy as np
import sys
import os

### ==========================================
### ⚙️ CONFIGURATION DU VISUALISEUR
### ==========================================

DOSSIER_SOURCE = "Outputs/"
# Fichier lu par défaut si aucun argument n'est passé dans la console
FICHIER_PAR_DEFAUT = "systeme_solaire_S1.csv"

# --- Réglages de l'animation ---
FPS_CIBLE = 60                    # Vitesse de l'animation (images par seconde), max 60
SAUT_IMAGES = 5                 # 1 = lire toutes les lignes, 5 = accélérer x5

# --- Réglages des Traînées (Orbites) ---
TRAINEE_COMPLETE = False          # True = trace toute la trajectoire depuis le début, Peut ralentir considérablement le programme pour les longues simulations ou avec beaucoup d'astres.
TAILLE_TRAINEE = 200              # Nombre de points mémorisés (Note: la longueur VISUELLE dépendra de la vitesse de la planète)

# --- Exportation Vidéo ---
SAUVEGARDER = True           # Si True, exporte l'animation en gif (peut être long à générer)
DOSSIER_EXPORT = "Programmes/Graphiques/"
NOM_EXPORT = "animation_simulation.gif"

# Constantes physiques
UNITE_ASTRONOMIQUE = 1.496e11     # 1 UA en mètres

### ==========================================


def obtenir_chemin_fichier():
    """Récupère le fichier CSV via argument ou configuration par défaut."""
    if len(sys.argv) > 1:
        nom_fichier = sys.argv[1]
        # Si l'utilisateur passe un chemin complet, on le garde, sinon on le cherche dans DOSSIER_SOURCE
        chemin = nom_fichier if os.path.exists(nom_fichier) else os.path.join(DOSSIER_SOURCE, nom_fichier)
    else:
        chemin = os.path.join(DOSSIER_SOURCE, FICHIER_PAR_DEFAUT)
        
    if not chemin.endswith('.csv'):
        sys.exit("❌ Erreur : Le fichier doit avoir l'extension .csv")
        
    if not os.path.exists(chemin):
        sys.exit(f"❌ Erreur : Le fichier '{chemin}' est introuvable sur le disque.")
        
    return chemin


def formater_duree(secondes):
    """Convertit des secondes en texte court (s, min, h, j, ans)."""
    secondes = abs(secondes)
    if secondes < 60:
        return f"{secondes:.3g} s"
    if secondes < 3600:
        return f"{secondes/60:.3g} min"
    if secondes < 86400:
        return f"{int(secondes//3600)}h{int((secondes%3600)//60):02d}"
    if secondes < 86400 * 365.25:
        return f"{secondes/86400:.3g} j"
    return f"{secondes/(86400*365.25):.3g} ans"


def choisir_meilleure_unite_temps(duree_totale):
    """Choisit l'unité d'affichage la plus logique pour le chronomètre."""
    if duree_totale < 7200:              return "s", 1
    if duree_totale < 86400 * 2:         return "h", 3600
    if duree_totale < 86400 * 730:       return "j", 86400
    return "ans", 86400 * 365.25


def animer_simulation(fichier_csv):
    nom_simulation = os.path.basename(fichier_csv)

    # --- 1. LECTURE DES MÉTADONNÉES ---
    with open(fichier_csv, 'r') as f:
        premiere_ligne = f.readline()
        
    if not premiere_ligne.startswith("#"):
        sys.exit("❌ Erreur : L'en-tête du fichier CSV n'a pas été trouvée.")
        
    infos = premiere_ligne.strip("# \n").split("|")
    duree_sec = float(infos[0].split(":")[1])
    pas_temps = float(infos[1].split(":")[1])
    intervalle_csv = float(infos[2].split(":")[1])

    # --- 2. LECTURE DES DONNÉES ---
    df = pd.read_csv(fichier_csv, comment='#')
    noms_astres = [colonne[:-2] for colonne in df.columns if colonne.endswith('_X')]
    nb_lignes = len(df)

    # --- 3. CALCULS DE TIMING ---
    fps_limite = min(60, FPS_CIBLE)
    delai_entre_images_ms = max(10.0, 1000.0 / fps_limite)
    fps_reel = 1000.0 / delai_entre_images_ms
    
    nb_images_diffusees = nb_lignes / SAUT_IMAGES
    duree_video_reelle = nb_images_diffusees / fps_reel
    vitesse_ecoulement = (intervalle_csv * SAUT_IMAGES) * fps_reel 

    print(f"✅ {len(noms_astres)} astres trouvés. Vidéo estimée à ~{duree_video_reelle:.1f} secondes.")

    # --- 4. ÉCHELLE SPATIALE DYNAMIQUE ---
    toutes_les_positions = df[[f'{a}_X' for a in noms_astres] + [f'{a}_Y' for a in noms_astres]]
    distance_max_metres = toutes_les_positions.abs().max().max()

    if distance_max_metres > 0.01 * UNITE_ASTRONOMIQUE:
        facteur_echelle, nom_unite = UNITE_ASTRONOMIQUE, "UA"
    elif distance_max_metres > 1e6:
        facteur_echelle, nom_unite = 1000.0, "km"
    else:
        facteur_echelle, nom_unite = 1.0, "m"

    marge = (distance_max_metres / facteur_echelle) * 1.10
    ordre_grandeur = 10 ** np.floor(np.log10(marge))
    limite_affichage = np.ceil(marge / (ordre_grandeur / 2)) * (ordre_grandeur / 2)

    # --- 5. INITIALISATION DE LA FIGURE ---
    generateur = np.random.default_rng(42)
    couleurs_astres = {a: plt.cm.hsv(t) for a, t in zip(noms_astres, generateur.uniform(0, 1, len(noms_astres)))}

    fig = plt.figure(figsize=(12, 8), facecolor='#07080f')
    grille = gridspec.GridSpec(1, 2, width_ratios=[4, 1.15], figure=fig, left=0.07, right=0.97, top=0.92, bottom=0.10, wspace=0.06)
    
    ax_carte = fig.add_subplot(grille[0])
    ax_panneau = fig.add_subplot(grille[1])

    # --- 6. DESSIN DE LA CARTE DE L'ESPACE ---
    ax_carte.set_facecolor('#07080f')
    ax_carte.set_xlim(-limite_affichage * facteur_echelle, limite_affichage * facteur_echelle)
    ax_carte.set_ylim(-limite_affichage * facteur_echelle, limite_affichage * facteur_echelle)
    ax_carte.set_aspect('equal')
    
    valeurs_ticks = np.linspace(-limite_affichage, limite_affichage, 11)
    
    def formater_tick(valeur):
        if valeur == 0: return "0"
        return f"{valeur:.2e}" if (abs(valeur) < 0.01 or abs(valeur) >= 1e5) else f"{valeur:.3g}"

    labels_ticks = [f"{formater_tick(v)} {nom_unite}" for v in valeurs_ticks]
    
    ax_carte.set_xticks(valeurs_ticks * facteur_echelle)
    ax_carte.set_yticks(valeurs_ticks * facteur_echelle)
    ax_carte.set_xticklabels(labels_ticks, color='#445566', fontsize=7, rotation=30, ha='right')
    ax_carte.set_yticklabels(labels_ticks, color='#445566', fontsize=7)
    ax_carte.tick_params(colors='#223344', length=4)
    
    ax_carte.set_xlabel("Position X", color='#6688aa', fontsize=9)
    ax_carte.set_ylabel("Position Y", color='#6688aa', fontsize=9)
    ax_carte.grid(True, color='#111820', linewidth=0.5)
    for bordure in ax_carte.spines.values(): bordure.set_color('#1a2a3a')
        
    fig.suptitle(f"Simulateur Gravitationnel N-Corps | Fichier : {nom_simulation}", color='white', fontsize=12, fontweight='bold', fontfamily='monospace')

    # --- 7. CRÉATION DES OBJETS GRAPHIQUES ---
    lignes_trainees = {}
    points_astres = {}
    
    for astre in noms_astres:
        couleur = couleurs_astres[astre]
        lignes_trainees[astre], = ax_carte.plot([], [], color=couleur, alpha=0.55, linewidth=1.0)
        points_astres[astre], = ax_carte.plot([], [], color=couleur, marker='o', markersize=5, markeredgewidth=0)

    # LÉGENDE (Seulement si peu d'astres pour ne pas polluer l'écran)
    if len(noms_astres) <= 10:
        ax_legende = ax_carte.inset_axes([0.01, 0.01, 0.22, min(0.04 + len(noms_astres) * 0.038, 0.40)])
        ax_legende.set_facecolor((0.04, 0.05, 0.09, 0.75))
        ax_legende.set_xticks([]); ax_legende.set_yticks([])
        for bordure in ax_legende.spines.values(): 
            bordure.set_color('#223344'); bordure.set_linewidth(0.8)
            
        pas_vertical = 1.0 / (len(noms_astres) + 1)
        for i, astre in enumerate(noms_astres):
            y_pos = 1.0 - (i + 0.8) * pas_vertical
            c = couleurs_astres[astre]
            ax_legende.plot([0.06, 0.22], [y_pos, y_pos], color=c, linewidth=2, transform=ax_legende.transAxes)
            ax_legende.plot([0.14], [y_pos], color=c, marker='o', markersize=4, transform=ax_legende.transAxes)
            ax_legende.text(0.28, y_pos, astre, transform=ax_legende.transAxes, color=c, fontsize=7.5, va='center', ha='left', fontfamily='monospace')

    # --- 8. DESSIN DU PANNEAU DE TÉLÉMÉTRIE (HUD) ---
    ax_panneau.set_facecolor('#07080f')
    ax_panneau.axis('off') 

    unite_symbole, unite_diviseur = choisir_meilleure_unite_temps(duree_sec)

    def ecrire_ligne_info(y, titre, valeur):
        """Aligne le texte et retourne l'objet texte de la valeur."""
        ax_panneau.text(0.05, y, titre, transform=ax_panneau.transAxes, color='#556677', fontsize=8, va='top', ha='left', fontfamily='monospace')
        return ax_panneau.text(0.97, y, valeur, transform=ax_panneau.transAxes, color='#ddeeff', fontsize=8, va='top', ha='right', fontfamily='monospace')

    hauteur_y = 0.98
    ecrire_ligne_info(hauteur_y, "Corps", f"{len(noms_astres)}")
    ecrire_ligne_info(hauteur_y - 0.06, "Duree sim.", formater_duree(duree_sec))
    ecrire_ligne_info(hauteur_y - 0.12, "Precision dt", f"{pas_temps:.4g} s")
    ecrire_ligne_info(hauteur_y - 0.18, "1 img =", formater_duree(intervalle_csv))
    ecrire_ligne_info(hauteur_y - 0.24, "FPS", f"{fps_reel:.0f}")
    
    texte_visionnage = ecrire_ligne_info(hauteur_y - 0.30, "Visionnage", f"0.0s / {duree_video_reelle:.1f}s")
    ecrire_ligne_info(hauteur_y - 0.36, "Vitesse", f"{formater_duree(vitesse_ecoulement)}/s")
    ecrire_ligne_info(hauteur_y - 0.42, "Trainee", "Complete" if TRAINEE_COMPLETE else f"~{TAILLE_TRAINEE} pts")

    # Zone du chronomètre animé
    hauteur_y -= 0.52
    ax_panneau.text(0.5, hauteur_y, "TEMPS ECOULE", transform=ax_panneau.transAxes, color='#aabbdd', fontsize=9, ha='center', fontfamily='monospace')
    texte_chronometre = ax_panneau.text(0.5, hauteur_y - 0.06, f"0 {unite_symbole}", transform=ax_panneau.transAxes, color='white', fontsize=12, fontweight='bold', ha='center', fontfamily='monospace')

    # Barre de progression
    hauteur_y -= 0.16
    ax_panneau.add_patch(FancyBboxPatch((0.05, hauteur_y), 0.90, 0.04, boxstyle="round,pad=0.005", facecolor='#0d1520', edgecolor='#223344', transform=ax_panneau.transAxes))
    jauge_progression = FancyBboxPatch((0.05, hauteur_y), 0.001, 0.04, boxstyle="round,pad=0.005", facecolor='#1a66ff', edgecolor='none', transform=ax_panneau.transAxes)
    ax_panneau.add_patch(jauge_progression)
    texte_pourcentage = ax_panneau.text(0.5, hauteur_y + 0.02, "0%", transform=ax_panneau.transAxes, color='white', fontsize=8, fontweight='bold', ha='center', va='center')

    # --- 9. LE MOTEUR DE L'ANIMATION ---
    def mettre_a_jour_image(frame_index):
        if TRAINEE_COMPLETE:
            debut_historique = 0
        else:
            # IMPORTANT: La traînée a toujours mathématiquement le même nombre de points.
            debut_historique = max(0, frame_index - TAILLE_TRAINEE)

        for astre in noms_astres:
            x_historique = df[f'{astre}_X'].iloc[debut_historique : frame_index]
            y_historique = df[f'{astre}_Y'].iloc[debut_historique : frame_index]
            x_actuel = df[f'{astre}_X'].iloc[frame_index]
            y_actuel = df[f'{astre}_Y'].iloc[frame_index]

            lignes_trainees[astre].set_data(x_historique, y_historique)
            points_astres[astre].set_data([x_actuel], [y_actuel])

        progression_ratio = frame_index / max(nb_lignes - 1, 1)
        jauge_progression.set_width(max(0.001, 0.90 * progression_ratio))
        texte_pourcentage.set_text(f"{progression_ratio * 100:.0f}%")
        
        temps_actuel_unite = (frame_index * intervalle_csv) / unite_diviseur
        texte_chronometre.set_text(f"{temps_actuel_unite:.4g} {unite_symbole}")

        temps_reel_ecoule = (frame_index / SAUT_IMAGES) / fps_reel
        texte_visionnage.set_text(f"{temps_reel_ecoule:.1f}s / {duree_video_reelle:.1f}s")

        return list(lignes_trainees.values()) + list(points_astres.values()) + [jauge_progression, texte_pourcentage, texte_chronometre, texte_visionnage]

    # --- 10. LANCEMENT & EXPORT ---
    frames_a_lire = range(0, nb_lignes, SAUT_IMAGES)
    animation = FuncAnimation(fig, mettre_a_jour_image, frames=frames_a_lire, interval=delai_entre_images_ms, blit=True, repeat=False)
    
    if SAUVEGARDER:
        if not os.path.exists(DOSSIER_EXPORT):
            os.makedirs(DOSSIER_EXPORT)
        chemin = os.path.join(DOSSIER_EXPORT, NOM_EXPORT)
        print("⏳ Génération de la vidéo en cours...")
       
        writer = PillowWriter(fps=fps_reel)
        animation.save(chemin, writer=writer, dpi=80)
        print(f"✅ Vidéo sauvegardée avec succès dans : {chemin}")
    else:
        plt.show()


if __name__ == "__main__":
    try:
        chemin_csv = obtenir_chemin_fichier()
        animer_simulation(chemin_csv)
    except Exception as erreur:
        sys.exit(f"❌ Erreur - {erreur}")