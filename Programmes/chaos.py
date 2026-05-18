import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

### ==========================================
### ⚙️ CONFIGURATION DE L'ANALYSE
### ==========================================

DOSSIER_SOURCE = "Outputs/"
DOSSIER_EXPORT = "Programmes/Graphiques/"

# Fichiers de résultats à comparer
FICHIER_STABLE = "3_soleils_stable_S1.csv"
FICHIER_CHAOS = "3_soleils_chaos_S1.csv"

# Mode d'exécution
SAUVEGARDER_IMAGE = False       
NOM_EXPORT = "analyse_chaos.png"

### ==========================================

def calculer_distances(df):
    """Calcule les 3 distances mutuelles (r12, r13, r23) à chaque instant."""
    d12 = np.sqrt((df['Soleil_1_X'] - df['Soleil_2_X'])**2 + (df['Soleil_1_Y'] - df['Soleil_2_Y'])**2)
    d13 = np.sqrt((df['Soleil_1_X'] - df['Soleil_3_X'])**2 + (df['Soleil_1_Y'] - df['Soleil_3_Y'])**2)
    d23 = np.sqrt((df['Soleil_2_X'] - df['Soleil_3_X'])**2 + (df['Soleil_2_Y'] - df['Soleil_3_Y'])**2)
    return d12, d13, d23

def analyser_chaos():
    # --- 1. AUDIT DES FICHIERS (FAIL-FAST) ---
    chemin_st = os.path.join(DOSSIER_SOURCE, FICHIER_STABLE)
    chemin_ch = os.path.join(DOSSIER_SOURCE, FICHIER_CHAOS)

    if not os.path.exists(chemin_st) or not os.path.exists(chemin_ch):
        sys.exit(f"❌ Erreur : Fichiers de simulation introuvables dans {DOSSIER_SOURCE}. Vérifiez les chemins et les noms de fichiers.")

    df_stable = pd.read_csv(chemin_st, comment='#')
    df_chaos = pd.read_csv(chemin_ch, comment='#')

    # --- 2. SYNCHRONISATION DES DONNÉES ---
    # Aligner la taille des données (au cas où une simulation a été arrêtée plus tôt)
    nb_lignes = min(len(df_stable), len(df_chaos))
    df_stable = df_stable.iloc[:nb_lignes]
    df_chaos = df_chaos.iloc[:nb_lignes]

    # Extraction dynamique du temps (lecture de l'intervalle dans les métadonnées)
    with open(chemin_st, 'r') as f:
        ligne_meta = f.readline().strip("# \n")
    intervalle_sec = float(ligne_meta.split("|")[2].split(":")[1])
    
    # Création de l'axe temporel (conversion en années pour le graphique)
    temps_annees = (np.arange(nb_lignes) * intervalle_sec) / (365.25 * 24 * 3600)

    # --- 3. CALCUL DES DÉVIATIONS ---
    d12_st, d13_st, d23_st = calculer_distances(df_stable)
    d12_ch, d13_ch, d23_ch = calculer_distances(df_chaos)

    # Calcul de la déviation relative en pourcentage (Delta r / r * 100)
    dev_12 = ((d12_ch - d12_st) / d12_st) * 100
    dev_13 = ((d13_ch - d13_st) / d13_st) * 100
    dev_23 = ((d23_ch - d23_st) / d23_st) * 100

    # --- 4. ESTHÉTIQUE DU GRAPHIQUE ---
    plt.figure(figsize=(10, 6), facecolor='white')
    
    plt.plot(temps_annees, dev_12, color='#3498db', linewidth=1.5, label='Δr (1 - 2)', alpha=0.9)
    plt.plot(temps_annees, dev_13, color='#e74c3c', linewidth=1.5, label='Δr (1 - 3)', alpha=0.9)
    plt.plot(temps_annees, dev_23, color='#2ecc71', linewidth=1.5, label='Δr (2 - 3)', alpha=0.9)
    
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    
    #plt.title("Sensibilité aux conditions initiales", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Temps (années)", fontsize=11)
    plt.ylabel("Déviation Δr (%)", fontsize=11)
    
    # Limitation volontaire de l'axe Y pour bien identifier le point de rupture
    plt.ylim(-500, 500)
    plt.xlim(0, max(temps_annees))
    
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper left', frameon=True, edgecolor='black')
    plt.tight_layout()

    # --- 5. EXPORT OU AFFICHAGE ---
    if SAUVEGARDER_IMAGE:
        if not os.path.exists(DOSSIER_EXPORT):
            os.makedirs(DOSSIER_EXPORT)
        chemin_export = os.path.join(DOSSIER_EXPORT, NOM_EXPORT)
        plt.savefig(chemin_export, dpi=300, bbox_inches='tight')
        print(f"✅ Analyse sauvegardée : {os.path.join(DOSSIER_EXPORT, NOM_EXPORT)}")
    else:
        plt.show()

if __name__ == "__main__":
    analyser_chaos()