## Introduction

L’univers est extrait du fichier source, converti et chargé de manière sécurisée en mémoire RAM (Module 02). Cependant, avant de lancer le moteur physique, le programme doit s'ajuster aux intentions de l'expérimentateur.

Ce module constitue la "couche d'interface" : il traduit les besoins humains (durée de l'expérience, fluidité du rendu, méthode de calcul) en paramètres mathématiques stricts exigés par l'algorithme d'intégration. L'objectif est double : offrir une interface souple et ergonomique, tout en blindant le programme avec des garde-fous algorithmiques et des fonctions d'auto-pilotage pour garantir que la simulation restera stable, même si l'utilisateur ne maîtrise pas les mathématiques sous-jacentes.

---
### [3.1] : La Télémétrie et la Saisie (L'Interface Homme-Machine)

**Contexte :** Déployer un terminal interactif permettant à l'utilisateur de configurer les quatre variables globales qui guideront la boucle principale : la Durée, le Pas de temps ($dt$), l'Intervalle de sauvegarde, et le Mode de calcul.

> [!info]- Ressources
> 
> - **Fonctions natives :** `input()` pour la saisie, boucles `while True` pour contraindre les réponses.
>     
> - **Contraintes avales :** L'Accélération (Module 04) a besoin de la variable `mode` ; l'Exportation (Module 05) a besoin de `intervalle`.
>     

> [!brain]- Le Labo (Les Dilemmes d'Ingénierie)
> 
> **Dilemme 1 : L'Incompatibilité des unités (Temps Humain vs Temps Machine)**
> 
> Un expérimentateur réfléchit en "Jours" ou en "Années" (ex: "Je veux simuler le système solaire sur 10 ans"). Mais la physique de Newton et notre moteur mathématique exigent strictement le Système International (les secondes).
> 
> _L'Arbitrage (La Conversion Transparente) :_ Le terminal demande explicitement l'unité souhaitée (`J` `A` `S`). Une fois saisie, le programme convertit silencieusement la valeur humaine en seconde. L'utilisateur garde son confort de pensée, et la machine obtient sa rigueur mathématique.
> 
> **Dilemme 2 : Le Tsunami de Données (Le ratio de l'Intervalle)**
> 
> Si on calcule une simulation sur 10 ans avec un pas d'une seconde, on génère plus de 315 millions de positions. Tout sauvegarder saturerait le disque dur et ferait crasher le visualiseur.
> 
> _L'Arbitrage (Le Rendu Standardisé) :_ Nous proposons un choix. Soit l'utilisateur impose son intervalle. Soit il appuie sur `Entrée` et le programme applique une règle d'ergonomie : il divise la durée totale par 1000 (`intervalle = duree / 1000`). Cela garantit un fichier CSV final de 1000 lignes.
> 
> **Dilemme 3 : Le Choix du Moteur**
> 
> Nous avons développé deux moteurs mathématiques (Module 04). Il faut permettre de basculer de l'un à l'autre sans toucher au code source.
> 
> _L'Arbitrage :_ Intégration d'un sélecteur strict (1=Matrice, 2=Boucles, 3=Benchmark) qui servira d'aiguillage dans le programme principal.

**Décisions Implémentées :**

- **Boucles de validation :** Utilisation de `try/except ValueError` couplé à des `while True` pour forcer l'utilisateur à entrer des nombres valides et empêcher le crash au menu.
    
- **Auto-calcul de l'intervalle :** Implémentation du fallback par défaut `max(duree / 1000, 1.0)` si la saisie de l'intervalle est laissée vide.
    
- **Sélecteur de mode :** Stockage de la décision dans la variable entière `mode`.
    

> [!warning]- L'Émergence
> 
> Les variables générales sont fixées. Le programme sait combien de temps il doit tourner et comment sauvegarder ses données.
> 
> **👉 La problématique suivante s'enclenche :** Le terminal demande le "Pas de temps" (le $dt$, la distance temporelle entre deux calculs). Si l'utilisateur charge un univers chaotique aléatoire (Module 01), il n'a aucune idée de la vitesse des corps. S'il met un $dt$ trop grand, l'algorithme va rater les courbes et les astres vont se télescoper (_Tunneling_). S'il met un $dt$ trop petit, la simulation prendra des jours à calculer.
> 
> Comment le programme peut-il analyser _lui-même_ la géométrie de l'univers pour calculer mathématiquement le pas de temps idéal ?
> 
> $\rightarrow$ **Passe au Maillon 3.2 : L'Intelligence du Paramétrage ).**

---
### [3.2] : L'Intelligence du Paramétrage (La Déduction Physique du $dt$ Universel)

**Contexte :** Si l'utilisateur laisse le champ du pas de temps ($dt$) vide, le système doit basculer en auto-pilote. Il doit analyser instantanément la topologie de l'univers initial ($t=0$) pour en déduire une résolution temporelle capable de garantir la stabilité de l'intégration numérique, peu importe le scénario injecté.

> [!info]- Ressources
> 
> - **Analyse du Sujet (Limites) :** Le fascicule suggère un pas basé sur la vitesse maximale, une approche insuffisante si le système démarre au repos (vitesses nulles) ou subit de fortes accélérations locales.
>     
> - **Concepts Astrophysiques :** Troisième loi de Kepler généralisée, temps de croisement dynamique ($t_{dyn}$), échelle de temps d'un effondrement en chute libre.
>     
> - **Outils Algorithmiques :** Vectorisation par _broadcasting_ NumPy pour croiser simultanément les paires sans aucune boucle `for` (Module 04).
>     

> [!brain]- Le Labo (Les Dilemmes d'Ingénierie)
> 
> **Dilemme : Le Paradoxe Cinétique (Pourquoi rejeter l'analyse des vitesses initiales ?)**
> 
> Pour calibrer le pas de temps $dt$, l'approche recommandée par le sujet est d'analyser la vitesse des astres.
> 
> _Le problème :_ Cette stratégie détruit l'universalité du programme en échouant sur des cas critiques. Si un système démarre au repos (vitesses initiales nulles), l'algorithme génère instantanément une division par zéro. De plus, si un astre est proche d'un corps lourd mais possède une vitesse initiale lente, le code va déduire à tort qu'un grand pas de temps suffit, alors que l'astre va accélérer de façon fulgurante dès la première seconde, ratant sa trajectoire (effet de _tunneling_).
> 
> _L'Arbitrage (L'implémentation autonome du Temps Dynamique) :_ Pour traiter tous les cas possibles de manière agnostique, nous choisissons d'ignorer la cinématique de départ pour nous concentrer sur le potentiel d'accélération maximal de la géométrie, en exploitant le concept astrophysique du temps dynamique d'interaction :
> 
> 1. **L'Échelle de Temps Critique :** Pour chaque paire d'astres $(i, j)$, le programme calcule son temps caractéristique d'interaction ($t_{dyn}$). Cette valeur représente le temps théorique que mettraient ces deux corps à s'effondrer l'un sur l'autre sous l'effet exclusif de leur gravité mutuelle.
>     
>     $$t_{dyn} = \sqrt{\frac{r^3}{\mathcal{G}(m_1 + m_2)}}$$
>     
> 2. **L'Isolation du Danger :** Le script balaie la matrice des interactions et isole la valeur minimale absolue ($t_{min}$). C'est le point le plus instable de l'univers, le couple d'astres qui va subir la plus violente force gravitationnelle.
>     
> 3. **La Règle des 1% ($\eta = 0.01$) :** Pour s'assurer que l'intégrateur de Verlet (Module 05) ne rate aucun virage orbital, nous convertissons ce temps en un pas de calcul verrouillé à 1% de cette crise dynamique :
>     
>     $$dt = 0.01 \times t_{min}$$
>     
> 
> Cet auto-pilotage physique décharge l'utilisateur de calculs complexes et immunise le moteur contre les variations cinétiques de départ.

**Décisions Implémentées :**

- **Automatisation conditionnelle :** Interception de la chaîne vide (`if not pas_input:`) pour déclencher la routine physique.
    
- **Calcul matriciel instantané :** Calcul de la matrice globale des temps dynamiques en réutilisant les masques de distances `r` et les sommes croisées de masses de NumPy : `np.sqrt(r3 / (G * masses_cumulees))`.
    
- **Neutralisation de l'auto-interaction :** Injection de `np.inf` sur la diagonale de la matrice $t_{dyn}$ pour empêcher un corps de calculer son propre temps d'effondrement sur lui-même ($r=0$).
    
- **Application du verrou de sécurité :** Extraction du minimum via `np.min()` et affectation stricte de la variable globale `pas = 0.01 * t_min`.
    
- **Transparence Console :** Impression immédiate de la valeur calculée dans le terminal afin que l'expérimentateur connaisse la résolution temporelle de sa simulation.
    

> [!warning]- L'Émergence
> 
> Les paramètres temporels de calcul sont désormais stabilisés et optimisés de manière autonome par rapport aux suggestions de base du sujet.
> 
> **👉 La problématique suivante s'enclenche :** Le moteur dispose de toutes ses constantes et s'apprête à générer des millions de lignes de coordonnées. Cependant, une contrainte logicielle majeure surgit : si le fichier d'export possède un nom fixe, chaque exécution va écraser les résultats précédents, anéantissant l'historique des tests et empêchant les futures analyses comparatives. Comment automatiser la gestion des fichiers sur le disque dur ?
> 
> $\rightarrow$ **Passe au Maillon 3.3 : La Sécurisation des Données (L'Archiviste).**

---
### [3.3] : La Sécurisation des Données (L'Archiviste)

**Contexte :** Gérer proprement le cycle de vie des données de sortie en concevant un mécanisme d'archivage automatisé capable de générer un fichier d'exportation unique, sans jamais exiger de saisie fastidieuse de la part de l'utilisateur ni risquer d'écraser des calculs antérieurs.

> [!info]- Ressources
> 
> - **Gestion Système :** Le sous-module natif `os.path` de Python pour interagir avec le système de fichiers de manière agnostique (Windows, Mac, Linux).
>     
> - **Contrat d'Interface :** Le nom du fichier CSV source extrait au Module 02 (ex: `Inputs/chaos_3_corps.csv`).
>     

> [!brain]- Le Labo (Les Dilemmes d'Ingénierie)
> 
> **Dilemme : L'Éphémérité destructive vs Le fardeau ergonomique** Comment organiser les fichiers de sortie d'un laboratoire virtuel ?
> 
> - _Option A (Le fichier unique fixe) :_ Écrire toujours dans un fichier standard `Outputs/resultats.csv`. _Défaut :_ Une catastrophe pour la recherche scientifique. L'utilisateur écrase involontairement sa simulation de la veille à chaque fois qu'il lance un nouveau test.
>     
> - _Option B (La saisie manuelle systématique) :_ Demander à l'utilisateur de taper au clavier un nouveau nom de fichier avant chaque calcul. _Défaut :_ Ergonomie désastreuse qui brise les pipelines d'automatisation et augmente le risque d'erreur de frappe.
>     
> 
> _L'Arbitrage (Le Séquençage de Version Non-Destructif) :_ Nous choisissons d'automatiser entièrement la création de versions uniques par isolation sémantique. Le programme prend la racine textuelle du fichier d'entrée comme identifiant d'expérience. Il interroge ensuite le disque dur via une sonde système (`os.path.exists`) au sein d'une boucle incrémentale. Le script teste les suffixes les uns après les autres (`_S1`, `_S2`, `_S3`) jusqu'à heurter un emplacement totalement vierge. L'utilisateur ne tape rien, le programme ne détruit rien : l'historique de recherche est sanctuarisé.

**Décisions Implémentées :**

- **Encapsulation fonctionnelle :** Déploiement de la fonction dédiée `obtenir_nom_fichier_sortie(chemin_entree)`.
    
- **Isolation du radical :** Utilisation conjointe de `os.path.basename` et `os.path.splitext` pour effacer les répertoires parents et l'extension `.csv` d'origine afin de ne conserver que le nom pur de l'expérience.
    
- **Sonde de vérification active :** Implémentation d'une structure `while os.path.exists(...)` qui teste dynamiquement l'arborescence du dossier `Outputs/` avant de valider définitivement le chemin de sortie.

---
## Conclusion

La phase préliminaire d’ingénierie logicielle et d’ergonomie est officiellement close.

Grâce à cette couche d'interface robuste, l'expérimentateur dispose d'un environnement de configuration hautement sécurisé : les unités de temps humaines sont converties, l'encombrement du stockage est anticipé par le découplage de l'intervalle, le pas de temps est auto-généré par l'analyse géométrique du potentiel gravitationnel ($t_{dyn}$), et l'archiviste garantit l'intégrité de l'historique sur le disque dur.

Toutes les variables d'état sont chargées en RAM (Module 02), les garde-fous temporels sont activés, et le protocole d'écriture est prêt. Le programme de calcul scientifique bascule maintenant dans sa phase la plus intensive : la gestion des forces.

Comment notre système va-t-il appliquer les lois de l'attraction universelle sur ces données matricielles, et comment contourner les limites de vitesse de l'interpréteur Python ?

👉 **Aller au [[Module 04 - Le Moteur Physique (Accélération)]].**