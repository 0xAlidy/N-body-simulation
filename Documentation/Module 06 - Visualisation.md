## Introduction

Ce module est dédié au programme de post-traitement : un script indépendant dont l'unique objectif est de lire notre fichier CSV d'export, d'en extraire la dynamique et de générer un tableau de bord graphique en deux dimensions.

---
### [6.1] : La Lecture des Données et la Restitution du Temps (Le Parsing)

**Contexte :** Cibler le fichier de simulation sur le disque, en extraire de manière sécurisée les métadonnées de configuration ainsi que les trajectoires des astres, et isoler l'identité des corps présents sans aucune saisie manuelle de l'utilisateur.

> [!info]- Ressources
> 
> - **Héritage :** Le fichier CSV de sortie généré par le moteur au Module 05, contenant la ligne de configuration `# DUREE_SEC:...` et l'en-tête aplati (`Astre_X`, `Astre_Y`).
>     
> - **Modules Python :** `pandas` pour le chargement de la matrice de données, `sys` et `os` pour la gestion des flux systèmes et des chemins d'accès.
>     

> [!brain]- Le Labo (Les Dilemmes d'Ingénierie)
> 
> **Dilemme 1 : L'ergonomie de ciblage (Console CLI vs Fichier par défaut)**
> 
> L'utilisateur doit pouvoir lancer rapidement le visualiseur pour tester un rendu sans retaper un long chemin à chaque fois, tout en conservant la possibilité d'analyser un fichier spécifique via la console.
> 
> _L'Arbitrage :_ Nous implémentons une logique d'aiguillage hybride dans `obtenir_chemin_fichier()`. Si un argument est passé en ligne de commande (`sys.argv`), il est prioritaire. À défaut, le script charge automatiquement le fichier standard défini dans la configuration globale (`FICHIER_PAR_DEFAUT`). Un pare-feu système intercepte immédiatement les extensions incorrectes ou l'absence physique du fichier sur le disque dur.
> 
> **Dilemme 2 : L'extraction d'un fichier à format mixte (Texte + Matrice)**
> 
> Notre fichier CSV contient sur sa toute première ligne des métadonnées scientifiques cruciales (Durée, Pas, Intervalle) précédées du caractère `#`. Charger le fichier directement via Pandas provoquerait une erreur de parsing car la structure n'est pas homogène.
> 
> _L'Arbitrage :_ Nous utilisons une lecture séquentielle. Le script ouvre d'abord le fichier avec un `readline()` natif de Python pour capturer la chaîne de configuration et isoler les variables de timing via un découpage (`split`). Ensuite, nous passons le flux à `pandas.read_csv()` avec le paramètre `comment='#'`. Pandas saute proprement la ligne informative et charge la matrice numérique à la vitesse maximale du processeur.
> 
> **Dilemme 3 : L'identification des N-Corps et la déduction du temps**
> 
> Le visualiseur doit être universel et accepter un nombre $N$ d'astres inconnu à l'avance, sans que les noms ne soient codés en dur dans le script. De plus, stocker une colonne "Temps" à chaque ligne du CSV alourdirait le fichier sur le disque pour rien.
> 
> _L'Arbitrage :_ Pour l'identité des corps, le script scanne dynamiquement les en-têtes de colonnes du DataFrame Pandas et filtre toutes les clés se terminant par `_X` pour reconstruire la liste exacte des astres (`colonne[:-2]`). Pour le temps, aucune donnée n'est stockée sur le disque. Le visualiseur calcule algébriquement le temps physique exact à la volée lors de la lecture d'une ligne en multipliant l'index de l'image par l'intervalle de sauvegarde de la simulation (`frame_index * intervalle_csv`).

**Décisions Implémentées :**
- **Sécurisation du ciblage :** Utilisation de `sys.argv` couplé à un fallback automatique sur `FICHIER_PAR_DEFAUT` avec levée d'erreurs explicites (`.endswith('.csv')`, `os.path.exists`).
- **Double lecture du CSV :** Extraction des constantes de simulation via `f.readline()` puis isolation du tableau numérique pur via `pd.read_csv(..., comment='#')`.
- **Scan dynamique :** Utilisation d'une compréhension de liste pour isoler le nom des astres à partir des suffixes de coordonnées.
- **Restitution temporelle :** Reconstitution mathématique du temps universel à l'écran via le produit `frame_index * intervalle_csv` dans la boucle d'animation.
    
> [!warning]- L'Émergence
> 
> Les données brutes de l'univers sont maintenant chargées en mémoire vive, l'identité des astres est isolée et le chronomètre est étalonné.
> 
> **Le problème suivant s'enclenche :** Si nous injectons directement ces coordonnées brutes dans un repère graphique fixe, les planètes risquent d'être invisibles (soit superposées sur un seul pixel au centre, soit perdues hors de l'écran) en raison des écarts d'échelle gigantesques propres à la gravitation. Comment calibrer automatiquement la fenêtre d'affichage avant le rendu ?
> 
> $\rightarrow$ **Passe au Maillon 6.2 : Le Cadrage Automatique et le Défi de l'Échelle (La Caméra Dynamique).**
---

---
### [6.2] : Le Cadrage Automatique et le Défi de l'Échelle (La Caméra Dynamique)

**Contexte :** Ajuster automatiquement la fenêtre d'affichage (le zoom de la caméra) pour que tous les astres soient visibles à l'écran, peu importe si le système est microscopique (une fusée) ou macroscopique (le système solaire externe).

> [!info]- Ressources
> 
> - **Concept Physique :** L'Unité Astronomique ($1.496 \times 10^{11}$ m), les ordres de grandeur de distance.
> - **Outils Mathématiques :** Fonctions NumPy `abs()`, `max()`, `log10()` et `ceil()`.

> [!brain]- Le Labo (Réflexions & Arbitrage)
> 
> **Pourquoi le choix de la 2D ? (L'arbitrage de clarté) :**
> L'espace possède trois dimensions, mais une visualisation en 3D sur un écran plat implique des projections complexes, des distorsions optiques et une perte de repères.
> 
> _L'arbitrage :_ Conformément aux recommandations de physique numérique, nous travaillons dans le plan orbital bidimensionnel ($X-Y$). Cela simplifie le tracé, garantit une mesure directe des distances et rend immédiate la vérification visuelle des lois de Kepler (trajectoires elliptiques).
> 
> **Le piège du zoom fixe (Dompter le gigantisme) :**
> Si nous bloquons la taille de l'écran sur une valeur fixe (par exemple 35 UA), le visualiseur sera parfait pour Uranus, mais si nous chargeons une simulation de laboratoire à petite échelle, l'écran sera vide car le zoom sera trop lointain. À l'inverse, si nous simulons une comète qui s'éloigne, elle sortira instantanément du cadre.
> 
> _La solution (La caméra adaptative) :_ Au lancement, le script parcourt l'intégralité du fichier de données et cherche la coordonnée la plus grande en valeur absolue parmi tous les astres et sur toute la durée du calcul (`max_pos`). À partir de ce nombre pur en mètres, le code prend une décision d'unité humaine :
> - Si `max_pos` dépasse 1% d'une UA, la caméra bascule en **Unités Astronomiques (UA)**.
> - Si elle dépasse 1000 km, elle passe en **kilomètres (km)**.
> - En dessous, elle reste en **mètres (m)**.
> 
> Pour éviter que les planètes ne collent aux bords du cadre, nous appliquons une marge de sécurité de 10% et arrondissons proprement la limite au demi-ordre de grandeur supérieur grâce à une analyse logarithmique (`10 ** floor(log10(marge))`). La caméra est ainsi parfaitement calibrée avant même la première image.

**Décisions :**
- Calcul du maximum absolu des données pour définir la taille de la boîte d'affichage.
- Graduation automatique et intelligente des axes (Ticks) en notation scientifique adaptée à l'unité choisie.

---
### [6.3] : Le Tableau de Bord et la Fluidité Graphique

**Contexte :** Créer une animation fluide tout en affichant un panneau latéral de statistiques (télémétrie) qui s'actualise en temps réel, sans surcharger l'écran ni le processeur.

> [!info]- Ressources
> 
> - **Héritage :** La variable `intervalle` calculée dans le Module 03 et le DataFrame chargé au Module 6.1.
>     
> - **Modules Graphiques :** `matplotlib.gridspec` pour le découpage de l'écran, `FuncAnimation` pour la boucle d'images.
>     
> - **Concept Informatique :** Le _Blitting_ (mise à jour sélective des pixels en mémoire vidéo).
>     

> [!brain]- Le Labo (Les Dilemmes d'Ingénierie)
> 
> **Dilemme 1 : Le rafraîchissement vs Les limites de Matplotlib** Si Matplotlib doit redessiner à chaque image le décor complet (les axes, le fond, le texte), le processeur s'effondre. _L'Arbitrage (Le Blitting) :_ Nous activons l'option `blit=True`. Matplotlib prend une "photo" du décor fixe au démarrage. À chaque itération, le code ne lui renvoie que les objets qui ont bougé (planètes, chrono).
> 
> **Dilemme 2 : L'Avance Rapide (Le Frame Skipping)** Si le CSV contient 200 000 lignes, lire l'animation prendrait des heures. Relancer le moteur physique pour changer l'intervalle d'origine serait un gâchis de temps CPU. _L'Arbitrage (L'intervalle visuel dynamique) :_ Nous introduisons `SAUT_IMAGES`. En lisant 1 ligne sur 10, on multiplie la vitesse de lecture par 10 au post-traitement, sans toucher à la physique. _La limite physique :_ La boucle de Matplotlib a un temps de traitement incompressible d'environ 10 millisecondes. Pour éviter qu'il ne s'engorge, nous verrouillons la demande avec un plafond strict (`min(60, FPS_CIBLE)`) couplé à ce délai minimum de 10 ms.
> 
> **Dilemme 3 : L'Asphyxie Visuelle (Le cas des N-Corps massifs)** Notre générateur de chaos peut créer des univers à 150 astres. Tracer 150 sillages infinis et afficher 150 noms dans une légende rendrait l'écran illisible et saturerait la RAM graphique. _L'Arbitrage (Le nettoyage conditionnel) :_ Nous imposons des limites visuelles strictes. La légende est désactivée au-delà de 10 corps. Les traînées orbitales sont bridées à une longueur mémoire courte (`TAILLE_TRAINEE`), avec la possibilité de les rendre complètes uniquement sur demande pour des expériences précises. Enfin, pour que l'utilisateur puisse suivre un astre d'un test à l'autre, on attribue les couleurs via une graine aléatoire fixe.

**Décisions :**

- **Fluidité :** Utilisation de `blit=True` dans `FuncAnimation` pour le rendu partiel.
- **Vitesse temporelle :** Implémentation du `SAUT_IMAGES` dans le découpage des `frames` de lecture pour simuler une avance rapide.
- **Sécurité matérielle :** Calcul du délai avec `max(10.0, 1000.0 / min(60, FPS_CIBLE))` pour ne jamais saturer Matplotlib.
- **Ergonomie dynamique :** - Masquage automatique de la légende `if len(noms_astres) > 10`.
    - Fixation des couleurs via `np.random.default_rng(42)`.
    - Maintien d'un historique de points glissant pour alléger les traînées (`frame_index - TAILLE_TRAINEE`).
    
---
## Conclusion

Ce module de post-traitement transforme notre code de calcul brut en un véritable laboratoire virtuel interactif. En assumant le choix d'une architecture séparée (le moteur calcule d'un côté, le visualiseur lit de l'autre), nous avons créé un outil performant et modulable, capable de s'adapter instantanément à toutes les échelles de l'Univers sans jamais brider la physique.

L'univers s'anime désormais de manière fluide à l'écran, les échelles s'adaptent toutes seules, et l'utilisateur garde le contrôle total du temps via la télémétrie.

Cependant, si l'animation est esthétiquement réussie, une question fondamentale demeure : comment prouver que ce que nous voyons à l'écran est **physiquement juste** ? Comment s'assurer que notre intégrateur de Verlet respecte vraiment la théorie, conserve l'énergie et modélise correctement le chaos, prouvant ainsi la validité scientifique de notre code de bout en bout ?

👉 **C'est l'ultime étape du projet : Direction le [[Module 07 - Analyses]]**