import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

### ==========================================
### ⚙️ CONFIGURATION DE L'ANALYSE
### ==========================================

DOSSIER_SOURCE = "Outputs/"
DOSSIER_EXPORT = "Programmes/Graphiques/"

FICHIERS_CIBLES = [
    "fusee_10000_S1.csv", "fusee_10330_S1.csv", "fusee_10500_S1.csv",
    "fusee_10670_S1.csv", "fusee_11000_S1.csv", "fusee_11170_S1.csv",
    "fusee_11330_S1.csv", "fusee_11500_S1.csv"
]

SAUVEGARDER_IMAGE = True      
NOM_EXPORT = "vitesse_liberation_Terre.png" 
FACTEUR_ECHELLE = 1e6           

### ==========================================

def analyser_vitesse_liberation(liste_fichiers):
    fig, ax = plt.subplots(figsize=(9, 9))
    
    # 1. TRACER LA TERRE (À L'ÉCHELLE)
    rayon_terre = 6378000 / FACTEUR_ECHELLE
    terre = plt.Circle((0, 0), rayon_terre, color='#2c7fb8', label='Terre', zorder=3)
    ax.add_patch(terre)

    nb_astres = len(liste_fichiers)
    couleurs = plt.cm.get_cmap('Set1', nb_astres)

    # 2. DÉTECTION ET TRACÉ DES FUSÉES
    for i, fichier in enumerate(liste_fichiers):
        chemin = os.path.join(DOSSIER_SOURCE, fichier)
        if not os.path.exists(chemin):
            sys.exit(f"❌ Erreur : Fichier {fichier} introuvable dans {DOSSIER_SOURCE}. Vérifiez les chemins et les noms de fichiers.")

        df = pd.read_csv(chemin, comment='#')
        
        # Extraction de la vitesse initiale sur Y pour la légende
        vitesse_initiale_kms = df['Fusee_VY'][0] / 1000
        
        ax.plot(
            df['Fusee_X'] / FACTEUR_ECHELLE, 
            df['Fusee_Y'] / FACTEUR_ECHELLE, 
            color=couleurs(i), alpha=0.8, linewidth=1.5, 
            label=f"$v_0$ = {vitesse_initiale_kms:.1f} km/s"
        )
        
    # 3. ESTHÉTIQUE DU GRAPHIQUE
    ax.set_xlim(-250, 50)
    ax.set_ylim(-50, 250)
    ax.set_aspect('equal')
    
    plt.xlabel(f"Position X (x $10^6$ m)")
    plt.ylabel(f"Position Y (x $10^6$ m)")
    plt.title("Détermination Numérique de la Vitesse de Libération", fontweight='bold', pad=15)
    
    plt.grid(True, linestyle=':', alpha=0.6)
    
    # Légende à l'extérieur du graphique pour ne pas masquer les orbites
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True, edgecolor='black', title="Vitesses initiales")
    plt.tight_layout()

    # 4. EXPORT OU AFFICHAGE
    if SAUVEGARDER_IMAGE:
        if not os.path.exists(DOSSIER_EXPORT):
            os.makedirs(DOSSIER_EXPORT)
        plt.savefig(os.path.join(DOSSIER_EXPORT, NOM_EXPORT), dpi=300, bbox_inches='tight')
        print(f"✅ Analyse sauvegardée : {os.path.join(DOSSIER_EXPORT, NOM_EXPORT)}")
    else:
        plt.show()

if __name__ == "__main__":
    analyser_vitesse_liberation(FICHIERS_CIBLES)