# 🪐 Simulateur de Dynamique Gravitationnelle (N-Corps)

## 📖 Présentation

Ce programme est un moteur de simulation physique permettant de calculer les trajectoires d'objets célestes (planètes, étoiles, satellites) soumis à leur attraction mutuelle. Il utilise l'algorithme d'intégration numérique de **Verlet**, plus stable que la méthode d'Euler, pour garantir la précision des orbites sur de longues durées.

**Note importante :** Ce programme est un **générateur de données**. Il calcule la physique et exporte les résultats dans un fichier CSV destiné à être analysé ou animé par des outils de post-traitement (fournis dans ce projet).

---

## 🛠️ Installation

Le projet nécessite Python 3.x et quelques bibliothèques scientifiques standards.

```bash
pip install numpy pandas matplotlib
python simulation.py
```

---

## ⚙️ Configuration du Système Initial (CSV)

Pour lancer la simulation, vous devez fournir un fichier `.csv` décrivant l'état de l'univers à $t = 0$.

### 1. Structure du fichier

Le fichier doit impérativement comporter l'en-tête (header) suivant sur la première ligne :

```csv
Name,Mass,Position X,Position Y,Velocity X,Velocity Y
```

### 2. Unités et Précision (Système International)

Le moteur physique utilise strictement les unités SI. Toute autre unité (UA, km, jours) faussera les calculs.

| Colonne        | Grandeur    | Unité   | Remarque                      |
| :------------- | :---------- | :------ | :---------------------------- |
| **name**       | Identifiant | Texte   |                               |
| **mass**       | Masse       | **kg**  | Valeur positive uniquement.   |
| **Position X** | Position    | **m**   | Coordonnée X dans le plan 2D. |
| **Position Y** | Position    | **m**   | Coordonnée Y dans le plan 2D. |
| **Velocity X** | Vitesse     | **m/s** | Vitesse initiale sur X.       |
| **Velocity Y** | Vitesse     | **m/s** | Vitesse initiale sur Y.       |

### 3. Règles d'écriture

- **Séparateur de colonnes** : Virgule (`,`).
- **Séparateur décimal** : Point (`.`). _Exemple : 1.503 (et non 1,503)._
- **Pas d'unités dans les cellules** : N'écrivez pas "kg" ou "m" dans les cases, seulement le nombre.

### Exemple de données (Terre-Soleil)

```csv
Name,Mass,Position X,Position Y,Velocity X,Velocity Y
Soleil,1.989e30,0,0,0,0
Terre,5.972e24,149.6e9,0,0,29780
```

---

## 🌌 Le Générateur de Chaos (Création d'Univers Aléatoire)

Vous n'avez pas envie d'écrire un fichier CSV à la main ? Vous voulez tester les limites de votre processeur ou observer des frondes gravitationnelles imprévisibles ?

Un programme générateur est inclus dans le projet. Il crée un système de **$N$ corps célestes** avec une distribution de masse réaliste (échelle logarithmique : beaucoup de petits corps, et seulement quelques étoiles supermassives pour éviter un effondrement global trop uniforme) et les place aléatoirement dans l'espace.

#### ⚙️ Configuration du générateur

Avant de lancer la génération, vous pouvez ouvrir le fichier `Programmes/generateur_chaos.py` pour y modifier les règles de l'univers :

- `NOM_FICHIER` : Par défaut `"univers_chaos.csv"`. Changez ce nom si vous voulez générer plusieurs univers sans écraser les précédents.
- `TAILLE_BOITE` : La dimension du carré d'apparition des planètes (par défaut $40 \text{ UA}$).
- `VITESSE_MAX` : La vitesse maximale initiale pouvant être attribuée à un astre.

#### Lancement de la Génération

Le programme enregistrera le fichier généré directement dans le dossier `/Inputs/`, prêt à être lu par la simulation. Vous pouvez l'exécuter de deux manières :

**1. Mode direct (recommandé) :** Passez le nombre d'astres en argument dans la console.

```bash
python Programmes/generateur_chaos.py 150
```

---

## 🚀 Guide de Configuration Interactif

L'interface interactive de `simulation.py` vous permet de régler précisément le compromis entre précision, vitesse de calcul et poids des données. Elle est "résiliente" : en cas d'erreur de frappe ou d'entrée vide, des valeurs par défaut optimisées s'appliquent.

### 0. Choix du fichier de données (Chargement)

- **Argument direct :** `python simulation.py ./Inputs/systeme_solaire.csv` (saute l'étape de saisie).
- **Saisie interactive :** Chemin relatif (ex: `./Inputs/collision.csv`).

### 1. La Durée de la Simulation

Fenêtre temporelle totale observée (Jours, Années ou Secondes). Le programme convertit tout en secondes.

### 2. Le Pas Physique

Définit la fréquence de calcul de la physique de Verlet.

- **Mode AUTO :** Le programme calcule le pas idéal selon le temps dynamique du système pour éviter les "sauts".
- **Mode MANUEL :** Vous forcez un pas en secondes. Attention, un pas trop grand détruit la physique, un pas trop fin allonge le temps de calcul.

### 3. L'Exportation (Intervalle de Sauvegarde)

Gère le poids du fichier de sortie sans impacter la précision des calculs.

- **Nombre de points :** (ex: 1000). Le fichier fera 1000 lignes, peu importe la durée de la simulation. Idéal pour la visualisation et éviter des CSV de plusieurs Go.
- **Intervalle fixe :** Sauvegarde toutes les X secondes. Idéal pour des analyses scientifiques ciblées.

### 4. Le Mode d'Exécution

- **(1) Matrices (NumPy) :** Utilise le calcul vectoriel (C) pour traiter toutes les planètes simultanément. _À privilégier absolument._
- **(2) Boucles :** Optimisé par la 3ème loi de Newton (Action/Réaction), mais reste lent en Python pur.
- **(3) Performance :** Lance les deux modes successivement pour comparer les chronos.

---

## 📊 Programmes de Post-Traitement & Analyses

Une fois que `simulation.py` a généré vos données physiques dans le dossier `/Outputs`, vous disposez d'une suite d'outils indépendants (situés dans le dossier `/Programmes`) pour animer et analyser scientifiquement ces résultats.

### 1. 🎬 Animation & Tableau de Bord (`visualiseur.py`)

**Description & Objectif :**
Ce script est dédié à la visualisation spatiale de vos données. Conçu comme un tableau de bord scientifique de laboratoire, il intègre :

- **Une Caméra Adaptative :** Scanne les données et ajuste automatiquement l'échelle (Mètres, Kilomètres ou Unités Astronomiques) pour que tous les astres restent visibles.
- **Une Télémétrie en temps réel (HUD) :** Affiche le chronomètre physique (avec unité adaptative), la progression de lecture et les ratios de vitesse temporelle.
- **Des Performances Graphiques (Blitting) :** Ne redessine que les pixels modifiés, garantissant une animation fluide à 60 FPS.

#### ⚙️ Configuration du script

En ouvrant le fichier `Programmes/visualiseur.py`, un bloc de configuration au sommet vous permet de modifier le comportement du moteur graphique :

- `DOSSIER_SOURCE` & `FICHIER_PAR_DEFAUT` : Définit le fichier qui sera lu automatiquement si vous ne spécifiez rien dans la console.
- `FPS_CIBLE` & `SAUT_IMAGES` : Contrôle la fluidité. L'option Saut d'images permet de lire 1 ligne sur X (ex: 5) pour accélérer visuellement une simulation très longue.
- `TRAINEE_COMPLETE` & `TAILLE_TRAINEE` : Gère le sillage orbital.

- `SAUVEGARDER_GIF` & `DOSSIER_EXPORT` : Passez à `True` pour que Matplotlib génère un fichier vidéo `.gif` de l'animation.

#### Lancement de l'Animation

Vous pouvez lancer le visualiseur de deux manières depuis la racine du projet :
**En ciblant un fichier de sortie précis :**

```bash
python Programmes/visualiseur.py Outputs/systeme_solaire_S1.csv
```

**En utilisant la configuration par défaut du fichier :**

```bash
python Programmes/visualiseur.py
```

---

## 📊 Analyses Scientifiques & Post-Traitement

Outre l'outil d'animation général (`visualiseur.py`), ce projet inclut des scripts de post-traitement spécifiques situés dans le dossier `/Programmes/`. Leur but est d'extraire des comportements physiques fondamentaux en croisant et en analysant les données générées par notre moteur.

### 1. Analyse Numérique de la Vitesse de Libération (`evasion.py`)

**Description & Objectif :**
Ce programme de post-traitement permet de déterminer numériquement la vitesse de libération de la Terre ($v_l \approx 11.2 \text{ km/s}$). Le script superpose sur un même graphique les trajectoires d'une fusée lancée avec différentes vitesses initiales. Cela permet d'observer visuellement le seuil exact où la trajectoire passe d'une orbite fermée (la fusée retombe) à une orbite ouverte (la fusée s'échappe définitivement de l'attraction terrestre).

#### Les Données de Test (Fichiers Fournis)

Pour faciliter le test et éviter de devoir recalculer 8 simulations manuellement, 8 fichiers (vitesses de $10.0$ à $11.5$ km/s) ont déjà été générés par notre moteur et sont disponibles dans le dossier `/Outputs/`.
_Note de format :_ Le script attend spécifiquement un fichier CSV contenant deux astres nommés "Terre" et "Fusee" (ex: `Terre_X, Terre_Y, Fusee_X, ...`).

#### ⚙️ Configuration du script

En ouvrant le fichier `Programmes/liberation.py`, vous trouverez un bloc de variables globales au sommet du script vous permettant de paramétrer totalement l'analyse :

- `DOSSIER_SOURCE` : Le dossier où le script va chercher les fichiers de simulation (par défaut `"Outputs/"`).
- `DOSSIER_EXPORT` : Le dossier de destination si vous choisissez de sauvegarder le graphique.
- `FICHIERS_CIBLES` : La liste exacte des fichiers CSV à superposer. Vous pouvez en ajouter ou en retirer.
- `SAUVEGARDER_IMAGE` : Si réglé sur `False`, le graphique s'affiche à l'écran. Si réglé sur `True`, le graphique est exporté en haute résolution sans bloquer le terminal.
- `NOM_EXPORT` : Le nom du fichier image généré (ex: `"vitesse_liberation.png"`).
- `FACTEUR_ECHELLE` : Permet de convertir les axes. `1e6` convertit les mètres de la simulation en Mégamètres (milliers de kilomètres) pour une meilleure lisibilité visuelle.

#### Lancement de l'Analyse

Une fois vos fichiers cibles renseignés, exécutez simplement la commande suivante depuis la racine du projet :

```bash
python Programmes/liberation.py
```

### 2. Étude du Chaos et de l'Effet Papillon (`chaos.py`)

**Description & Objectif :**
Ce script d'analyse démontre l'instabilité mathématique fondamentale d'un système à plus de deux corps. Il compare ligne par ligne le résultat de deux univers "jumeaux". Dans le premier, trois étoiles forment un triangle équilatéral parfait. Dans le second, la vitesse initiale d'une étoile a été modifiée de `0.00002 m/s` (une fraction infinitésimale par rapport à sa vitesse spatiale). Le script trace la courbe de l'écart relatif ($\Delta r$) entre les deux univers pour mettre en évidence le point de rupture exponentiel où la perturbation disloque le système (le Chaos).

#### Les Données de Test (Fichiers Fournis)

Deux simulations mathématiquement ajustées sont fournies dans le dossier `/Outputs/` pour observer l'expérience :

- Le système de référence : `3_soleils_stable_S1.csv`
- Le système perturbé : `3_soleils_chaos_S1.csv`

_Note de format :_ Le script attend spécifiquement des fichiers contenant trois astres nommés "Soleil_1", "Soleil_2" et "Soleil_3".

#### ⚙️ Configuration du script

En ouvrant le fichier `Programmes/chaos.py`, vous trouverez un bloc de configuration au sommet vous permettant d'ajuster l'analyse :

- `DOSSIER_SOURCE` : Le dossier de lecture des fichiers (par défaut `"Outputs/"`).
- `DOSSIER_EXPORT` : Le dossier de destination si vous exportez le graphique (par défaut `"Programmes/Graphiques/"`).
- `FICHIER_STABLE` & `FICHIER_CHAOS` : Les noms exacts des deux fichiers à comparer.
- `SAUVEGARDER_IMAGE` : Si défini sur `True`, exporte le graphique en haute résolution sans bloquer le terminal. Sinon, affiche le graphique à l'écran.
- `NOM_EXPORT` : Le nom du fichier image généré (ex: `"analyse_chaos.png"`).

#### Lancement de l'Analyse

Assurez-vous que vos fichiers cibles sont corrects, puis lancez la commande depuis la racine du projet :

```bash
python Programmes/chaos.py
```

---

### 3. La Stabilité Absolue (L'Orbite en Huit de Moore)

**Description & Objectif :**
Cette dernière expérience est le test de robustesse ultime de notre moteur physique. Contrairement au triangle équilatéral parfait qui finit systématiquement par être disloqué par le chaos (voir expérience précédente), l'orbite en "Huit" (découverte par Cris Moore en 1993) possède un bassin d'attraction qui tolère les micro-erreurs d'arrondis de l'ordinateur.
L'objectif est de simuler cette chorégraphie gravitationnelle sur une très longue durée pour prouver la nature "symplectique" de l'algorithme de Verlet : le système ne dérive pas, ne gagne pas et ne perd pas d'énergie au fil des décennies.

#### Les Données de Test (Fichiers Fournis)

Pour observer ce phénomène, un fichier de configuration initial traduisant les constantes mathématiques de Moore est fourni :

- Fichier source : `Inputs/3_soleils_huit.csv`
- Simulation pré-calculée sur 50 ans avec un pas precis de 1000 : `Outputs/3_soleils_huit_S1.csv`

#### ⚙️ Configuration du visualiseur

Contrairement aux programmes de post-traitement précédents, cette démonstration est **purement visuelle**. Elle tire parti du système de traînée orbitale de notre visualiseur.

Avant de lancer le programme, ouvrez le fichier `Programmes/visualiseur.py` avec votre éditeur de texte et modifiez la configuration en haut du fichier pour activer la traînée persistante :

```python
TRAINEE_COMPLETE = True
```

#### Lancement de la Démonstration

Exécutez le visualiseur en ciblant directement le fichier pré-généré :

```bash
python Programmes/visualiseur.py Outputs/3_soleils_huit_S1.csv
```

**Résultat attendu :** Vous verrez les trois étoiles se pourchasser indéfiniment sur une trajectoire en lemniscate (figure en 8). Malgré les années qui défilent à l'écran, le tracé de la courbe reste mathématiquement parfait et d'une épaisseur constante, prouvant que notre intégrateur de Verlet conserve l'énergie du système.
