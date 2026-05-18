## Introduction

L'utilisateur sait désormais quoi créer et comment le faire (via le README), et son fichier CSV source est prêt sur le disque dur. L'objectif de ce module est de **franchir la barrière physique** : extraire les données initiales de la simulation et les transformer en variables au sein de notre programme afin de pouvoir les utiliser et appliquer la simulation.
### 🎯 Objectif du Module

Pour réaliser une transition parfaite entre le stockage externe (texte) et la mémoire vive (calcul), cela implique une double mission :

1. **L'Audit de Sécurité** : Intercepter 100% des erreurs humaines avant le calcul (typage, logique physique, doublons, colonnes manquantes) et informer l'utilisateur avec précision.
    
2. **L'Optimisation Structurelle** : Stocker ces informations dans le format le plus pertinent pour garantir l'efficience des futurs calculs physiques.

---
### [2.1] : Le Ciblage du Fichier (L'Aiguilleur)

**Contexte :** Avant d'ouvrir et de valider le contenu du fichier, le programme doit savoir **où** le chercher sur le disque dur et comment l'indiquer de la manière la plus fluide possible pour l'utilisateur.

> [!abstract]- Ressources
> 
> **Ressources :** Module `sys` de Python pour la gestion des arguments systèmes.

> [!brain]- Le Labo (Réflexions & Arbitrage)
> **Problématique Globale :** Quelle est la méthode la plus ergonomique et robuste pour permettre à l'utilisateur de transmettre le chemin du fichier source au programme ?
> 
> **Analyse des Options :**
> 
> - **Option A (Chemin codé en dur dans le script) :** Oblige l'utilisateur à modifier le code Python ou à renommer continuellement ses fichiers. Inacceptable car on ne veut pas qu'il touche au code source.
>   - **Option B (Prompt `input()` pur) :** L'utilisateur tape le chemin dans la console. C'est fastidieux, propice aux fautes de frappe et surtout, on perd l'auto-complétion (la touche `Tabulation` du terminal). Cependant, cela reste un filet de sécurité indispensable si le programme n'est pas lancé via un terminal.
>   - **Option C (Arguments CLI via `sys.argv`) :** L'approche la plus professionnelle. L'utilisateur lance `python main.py mon_systeme.csv`. C'est rapide, permet l'auto-complétion et l'automatisation. S'il y a plusieurs arguments, on sécurise en ne gardant que le premier.
>     
> **Arbitrage de la "Voie Hybride" :** On combine le meilleur des mondes. Le programme vérifie d'abord s'il y a un argument système (Option C). Si oui, il le prend. Sinon, il déclenche le prompt `input()` (Option B).
> 
> **Le Pare-Feu initial :** Peu importe la méthode de saisie, on valide les 4 derniers caractères pour s'assurer que c'est bien un `.csv` avant de lancer la moindre fonction de lecture.

**Décisions :** 
- Création de la fonction `get_file_path()` appliquant la méthode de sélection hybride (CLI prioritaire ou Prompt ).
- Rejet immédiat avec levée d'erreur (exception) si l'extension n'est pas `.csv`.

> [!warning]- L'Émergence
> 
> Le programme sait désormais exactement où chercher le fichier sur le disque dur, et il a la garantie que ce fichier se présente comme un CSV.
> 
> **👉 La problématique suivante s'enclenche :** Maintenant que le fichier est localisé, comment l'ouvrir de manière sécurisée et en extraire intelligemment les données ?
> 
> $\rightarrow$ **Passe au Maillon 2.2 (L'Extraction Automatisée - Le Lecteur)**.

---
### [2.2] : L'Extraction Automatisée (Le Lecteur)

**Contexte :** Ouvrir le fichier de manière sécurisée et définir l'outil capable d'en lire les données intelligemment.

> [!info]- Ressources
> 
> - **Héritage :** Fichier `.csv` ciblé au [[#2.1]].
>     
> - **Contrainte technique :** Gestion de la RAM et des flux d'Entrée/Sortie (I/O).
>     

> [!brain]- Le Labo (Réflexions & Arbitrage)
> 
> **Analyse du Problème Matériel :** Si le programme plante à n'importe quel moment de la lecture, le fichier texte risque de rester "ouvert" dans la RAM, causant des problèmes de verrouillage côté système d'exploitation.
> 
> **Solution :** Utiliser le gestionnaire de contexte `with open(...)` pour déléguer la fermeture propre du fichier à Python, quoi qu'il arrive (même en cas d'erreur fatale).
> 
> **L'Outil de Lecture :** L'utilisation de `csv.DictReader` reste la meilleure option mécanique. Il lit automatiquement la première ligne comme en-tête et nous permet d'accéder aux données via des clés littérales (ex: `row['mass']`) plutôt que par des index (ex: `row[1]`). Cela rend le code infiniment plus lisible pour la maintenance.

**Décisions :**
- Utilisation du gestionnaire de contexte `with open(...)` pour l'Entrée/Sortie.
- Utilisation de `csv.DictReader` pour une extraction lisible.


> [!warning]- L'Émergence
> 
> Le fichier est ouvert et le lecteur est prêt. Mais avant de stocker quoi que ce soit, nous devons définir les règles strictes qui sépareront les données valides des erreurs humaines (fautes de frappe, incohérences physiques).
> 
> $\rightarrow$ **[2.3] : Gestion des Erreurs**.

---
### [2.3] : Gestion des erreurs

**Contexte :** Auditer chaque donnée pour protéger l'intégrité de la simulation.

> [!info]- Ressources
> 
> - **Héritage :** Le contrat d'interface issu du [[Module 01 - Élaboration du Système d'Entrée#[1.3] Le Contrat d'Interface (Unités et Standardisation) | Module 01]].
>     
> - **Concept Informatique :** Principe du _Fail Fast_ (Échouer tôt et de manière explicite pour éviter la corruption en aval).
>     

> [!brain]- Le Labo (Réflexions & Arbitrage)
> 
> **Problématique Globale :** Comment s'assurer que les données brutes lues dans le fichier correspondent parfaitement aux attentes mathématiques et physiques de notre programme, sans avoir à imaginer et coder chaque erreur humaine possible ?
> 
> **Analyse de l'Intégrité :** Si nous passons directement les données au moteur de calcul, n'importe quelle anomalie non détectée (une valeur manquante, une donnée non numérique, une aberration physique) provoquera un crash incompréhensible ou, pire, un comportement faussé à un moment indéterminé de la simulation. Essayer de lister tous les cas particuliers est une bataille perdue d'avance.
> 
> **Arbitrage du Filtre Générique :** Plutôt que de chercher des erreurs spécifiques, on applique un tamis strict basé sur nos contraintes :
> 
> 1. **Conformité structurelle :** L'en-tête lu par le `DictReader` doit correspondre exactement à notre standard.
>     
> 2. **Conformité mathématique :** Chaque donnée doit pouvoir être convertie en flottant (`float`). Le simple fait de tenter cette conversion de manière encadrée (via `try/except`) permet d'intercepter n'importe quelle donnée non numérique d'un seul coup.
>     
> 3. **Conformité physique :** Une masse ne peut pas être nulle ou négative.
> 
> 4. **Entité unique :** Chaque astre est identifié par un nom unique
>     
> **Le Choix de l'Information Utilisateur :** Au lieu de planter silencieusement, l'interception de ces anomalies nous permet de renvoyer un message d'erreur clair indiquant le numéro de la ligne fautive, rendant l'outil collaboratif et non frustrant.

**Décisions :**
- Création d'une constante globale définissant le standard absolu : `VALID_HEADER = ['name', 'mass', 'position x', 'position y', 'velocity x', 'velocity y']`.
- Création d'un dictionnaire centralisé `ERROR_MESSAGES`.
- Vérification immédiate de l'en-tête via `reader.fieldnames == VALID_HEADER`.
- Création d'une fonction `validate_row` avec bloc `try/except ValueError` pour le typage, et vérifications logiques (`mass > 0`, noms uniques).

> [!warning]- L'Émergence
> Les règles de validation sont désormais fixées et notre "pare-feu" est prêt. Cependant, avant de lancer concrètement la lecture pour filtrer et extraire ces données, nous devons préparer les réceptacles qui vont les accueillir. Sous quelle forme mathématique précise doit-on allouer la mémoire de l'ordinateur pour stocker cet univers et garantir la rapidité du futur calcul N-Corps ?
> 
> $\rightarrow$ Voir [2.4] : L'Allocation Mémoire Anticipée.
> $\rightarrow$ Voir [2.4] : L'Allocation Mémoire Anticipée.


---
### [2.4] : L'Allocation Mémoire Anticipée

**Contexte :** Le Module 03 (Moteur de calcul) exigera des matrices NumPy pour calculer les forces rapidement en vectoriel. Le défi de ce maillon est de trouver la méthode la plus optimisée pour convertir notre fichier texte en tableaux NumPy, tout en intégrant les règles de notre fonction qui gère les erreurs.

> [!info]- Ressources
> 
> - **Contrainte aval :** Le moteur physique (Module 03) calculera les forces en vectoriel.
>     
> - **Concept Informatique :** 
> 	- Allocation mémoire contiguë (NumPy) vs allocation dynamique (Listes Python).
> 	- Compromis entre temps de calcul (CPU) et espace mémoire (RAM).

> [!brain]- Le Labo (Réflexions & Arbitrage)
> 
> **Analyse de l'Approche Simple (Listes Python) :** La méthode la plus intuitive et pratique serait d'ajouter chaque ligne validée dans une liste classique (`liste.append()`), puis de convertir cette liste globale en tableau NumPy à la toute fin (`np.array(liste)`). Soyons honnêtes : pour un système de 10 ou 100 astres, le temps de calcul perdu avec cette méthode est totalement insignifiant. Le véritable enjeu d'optimisation se situera dans le moteur de forces physiques.
> 
> **Le Dilemme NumPy (Le Piège de la Réallocation) :** Si l'on choisit tout de même d'optimiser cette étape en utilisant NumPy dès le départ pour construire un programme "scalable", on se heurte à une contrainte stricte. Les tableaux NumPy stockent les nombres dans des blocs de mémoire contigus. Si l'on tente d'agrandir ce tableau à chaque nouvelle ligne lue (ce qui équivaut à recréer un tableau plus grand et tout recopier à chaque fois), on détruit littéralement les performances de la RAM. L'optimisation devient alors pire que la méthode simple.
> 
> **Arbitrage de Rigueur (La Double Passe) :** Pour utiliser NumPy correctement sans tomber dans le piège de la réallocation, nous devons connaître la taille exacte des matrices _avant_ de les remplir. Nous utiliserons donc une stratégie de "Double Passe".
> 
> **Dilemme d'Exécution : L'Emplacement du Pare-Feu (CPU vs RAM)** Puisque nous lisons le fichier deux fois, où doit-on exécuter notre validation (conversion en flottants et limites physiques) ?
> 
> - _Option A (Optimisation RAM) :_ Valider dans la Passe 1. On convertit pour tester, on jette la donnée, on compte, puis en Passe 2, on reconvertit pour stocker. _Avantage :_ On n'alloue la RAM que si le fichier est 100% sain. _Défaut :_ On fait travailler le processeur deux fois pour rien.
>     
> - _Option B (Optimisation CPU) :_ La Passe 1 ne fait que compter les lignes aveuglément. On alloue la RAM. La Passe 2 fait la conversion, le test Pare-Feu et l'injection simultanément. _Avantage :_ Le processeur ne convertit le texte qu'une seule fois. _Défaut :_ Si une erreur survient en Passe 2, on a alloué une matrice pour rien avant de crasher.
>     
> 
> **Arbitrage Final :** Allouer temporairement quelques mégaoctets de RAM (qui seront libérés en cas de crash) n'est pas un problème. En revanche, la conversion de texte en Python est coûteuse pour le processeur. Nous choisissons donc l'**Option B (Optimisation CPU)** : Passe 1 aveugle, Passe 2 intelligente.

**Décisions :**
- Séparation des données finales : `names` (Liste Python), `masses` (Vecteur NumPy 1D), `positions` (Matrice NumPy 2D), `vitesses` (Matrice NumPy 2D).
- Implémentation de la "Double Passe" 
- Exécution du Pare-Feu uniquement lors de la Passe 2.
---
## Conclusion 

Le passage de la barrière physique est accompli. L'univers n'est plus un texte, c'est un état mathématique chargé en RAM à $t=0$, validé et sécurisé.

👉 **La problématique suivante est le cœur du projet : comment appliquer les lois de Newton pour calculer le mouvement de ces points vers l'avenir ?**

$\rightarrow$ **Module 03 : Le Moteur Physique.**