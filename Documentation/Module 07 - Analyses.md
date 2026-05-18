
## Introduction

La physique a généré ses données (Module 05) et notre moteur graphique a démontré sa capacité à les restituer fidèlement (Module 06). Ce dernier module est consacré à l’exploitation scientifique des simulations produites.

L’objectif n’est plus seulement de calculer des trajectoires, mais de vérifier que notre modèle numérique reproduit correctement les comportements physiques attendus. Les scripts de post-traitement analysent ainsi les données brutes afin d’identifier des propriétés caractéristiques de la dynamique gravitationnelle : stabilité orbitale, conservation des mouvements et apparition du chaos dans le problème à trois corps.

Cette démarche permet de valider indirectement la rigueur de la simulation. Si les phénomènes physiques théoriquement attendus émergent naturellement des données calculées, alors le modèle numérique, l’intégration temporelle de Verlet et l’implémentation vectorielle des forces gravitationnelles peuvent être considérés comme cohérents.

Enfin, la visualisation joue un rôle essentiel d’interprétation : elle permet de confronter directement les trajectoires simulées aux comportements physiques prédits par la théorie, prouvant l'efficacité de notre architecture de résolution séparée (Générateur / Post-Traitement).

---
### [7.1] : Détermination Numérique de la Vitesse de Libération

**Contexte & Objectif :** 
Vérifier si notre intégrateur numérique est capable de faire émerger la limite physique d'évasion gravitationnelle (11.2 km/s pour la Terre) de lui-même, uniquement en calculant des forces pas à pas, sans que la formule théorique ne soit jamais écrite dans le code.

> [!info]- Ressources & Connaissances
> - **Outils :** `pandas` pour l'extraction de données, `matplotlib.pyplot` pour le tracé analytique statique.
> - **Données d'entrée :** Huit fichiers CSV distincts (pré-générés dans le dossier `/Outputs/`) simulant des lancements avec des vitesses initiales $v_0$ allant de $10.0$ à $11.5 \text{ km/s}$ depuis la surface terrestre ($R = 6378 \text{ km}$).
> - **Physique Théorique :** La vitesse de libération ($v_l$) est le point de bascule où l'énergie mécanique totale du système devient positive, transformant une trajectoire fermée (ellipse) en une trajectoire ouverte. Pour la Terre, $v_l = \sqrt{\frac{2GM}{R}} \approx 11.2 \text{ km/s}$.

> [!brain]- Le Labo (Réflexions & Arbitrage)  
>  
> **Le Dilemme de la Comparaison (Le problème des corps multiples) :**  
> L'approche naïve consisterait à placer 8 fusées avec 8 vitesses différentes autour de la Terre dans le même fichier CSV. 
> *L'Arbitrage :* Bien que physiquement possible, lancer les fusées depuis des points différents ruinerait la rigueur de la comparaison orbitale. Pour obtenir une lecture claire de l'ouverture de l'orbite, toutes les trajectoires doivent partager strictement la même origine géométrique. Nous avons donc généré une série de fichiers CSV distincts (un par vitesse) partant du même point à $t=0$. Le script de post-traitement se charge d'extraire et de superposer ces chronologies parallèles.
>  
> **L'Automatisation de la Légende :**  
> Afin d'éviter le code en dur, notre script lit chaque fichier, isole la ligne à $t=0$, et extrait la vitesse initiale ($V_y$) directement depuis la donnée brute. C'est cette valeur qui génère automatiquement la légende du graphique. Afin de ne masquer aucune trajectoire, la légende est déportée géométriquement à l'extérieur de la zone de dessin.

**Décisions Analytiques :**
- Développement d'un script superposant les données de multiples fichiers CSV.
- Tracé de la Terre à l'échelle stricte ($R = 6378 \text{ km}$) à l'origine du repère pour identifier visuellement l'orbite de départ.
- Mise à l'échelle de toutes les distances en "Mégamètres" ($10^6$ mètres) pour éviter d'asphyxier les axes de lecture.

> [!success] Bilan Analytique (Confirmation Théorique)
> Le tracé graphique obtenu démontre visuellement la transition géométrique : les courbes correspondant aux vitesses $< 11.2$ km/s se referment (retour sur Terre), tandis que celles $\ge 11.2$ km/s se courbent sans jamais revenir (trajectoire ouverte). L'émergence naturelle de cette limite physique valide formellement la conservation et la distribution énergétique opérée par notre moteur N-Corps.

> **💡 Perspective d'amélioration (Évolutivité) :**  
> Dans le cadre de ce projet, le script a été ciblé textuellement sur les colonnes `Fusee` et `Terre`. Dans une version ultérieure, ce script d'analyse pourrait être rendu totalement générique : le code scannerait l'en-tête du CSV pour identifier lui-même l'attracteur central et le projectile, permettant l'analyse de trajectoires d'évasion sur n'importe quel système planétaire.

---

### [7.2] : L'Étude du Chaos (Le Problème à 3 Corps)

**Contexte & Objectif :**
Démontrer l'instabilité fondamentale de la gravitation pour un système à plus de deux corps, et mettre en évidence la sensibilité extrême aux conditions initiales (l'effet papillon). L'objectif n'est pas de mesurer la longévité orbitale absolue, mais de prouver mathématiquement qu'une erreur infinitésimale grandit de manière exponentielle au fil du temps.

> [!info]- Ressources & Connaissances
> - **Outils :** Script `chaos.py` (`pandas`, `numpy`, `matplotlib`).
> - **Données d'entrée :** Deux fichiers CSV contenant 3 étoiles de masse solaire ($1.989 \times 10^{30} \text{ kg}$) placées en triangle équilatéral. Dans le second fichier, la vitesse initiale d'une étoile est modifiée (ajout de $0.0002$ m/s).
> - **Physique Théorique :** La prévisibilité d'un système à plus de deux corps est impossible sur le long terme en raison de sa nature chaotique. Nous utilisons l'écart relatif ($\Delta r$) entre deux univers jumeaux pour isoler ce comportement.

> [!brain]- Le Labo (Réflexions & Arbitrage)  
>  
> **Le placement des astres (La méthode scientifique) :**  
> Obtenir un système où 3 corps tournent sur une orbite circulaire exige que l'attraction gravitationnelle compense exactement la force centrifuge. Nous les avons placées aux sommets d'un triangle équilatéral parfait. Les vecteurs vitesses ont été orientés tangentiellement au cercle circonscrit, avec une précision absolue de 10 décimales pour garantir la symétrie à $t=0$.
> 
> **Le Paradoxe du système "Stable" :**  
> Malgré cette perfection initiale, notre simulation de référence finit par se disloquer.
>  
> *Le Diagnostic :* La solution en triangle équilatéral pour trois masses égales est une configuration de Lagrange. Le critère de Gascheau démontre qu'elle n'est stable que si un corps est largement plus massif que les autres. Pour trois masses égales ($\mu = 3$), le mouvement est linéairement instable par nature. L'algorithme de Verlet n'invente pas le chaos, mais il introduit inévitablement des erreurs de discrétisation spatiale et d'arrondi des flottants. Ce "bruit numérique" casse la symétrie, et l'instabilité naturelle du système amplifie cette erreur jusqu'à la dislocation.
>  
> **La Comparaison des Univers :**  
> Notre script aligne les deux fichiers de résultats temporellement, calcule la distance mutuelle entre chaque paire d'étoiles, et applique le calcul d'écart relatif en pourcentage : $\Delta r = \frac{r_{chaos} - r_{stable}}{r_{stable}} \times 100$.

**Décisions Analytiques :**
- Calcul de la configuration initiale de Lagrange.
- Développement du script d'analyse isolant l'écart relatif ($\Delta r$) avec synchronisation temporelle automatique des deux simulations (pour pallier l'arrêt d'une des simulations par le système anticollision).
- Double approche de validation : l'analyse visuelle de la déviation exponentielle croisée avec l'audit direct des données brutes (CSV) pour dater avec précision la rupture des systèmes.

> [!success] Bilan Analytique (Validation de l'Effet Papillon)
> Le tracé graphique obtenu valide parfaitement le comportement chaotique attendu : 
> 1. **La phase dormante :** La courbe reste plate à 0% pendant plus de 8 ans. Les deux univers évoluent de manière identique, l'anomalie n'ayant pas encore pris le dessus.
> 2. **L'explosion exponentielle :** La courbe s'emballe de manière verticale, prouvant que des conditions initiales quasi identiques mènent irrémédiablement à une perte de corrélation spatiale.
> 
> **Les limites de la courbe (La nécessité de la donnée brute) :**
> Le graphique de déviation relative ne permet pas d'identifier directement la perte de stabilité du système de référence. Une fois le système perturbé devenu erratique, la courbe devient irrégulière et masque le comportement de l'autre univers. 
> Les véritables dates de rupture de stabilité ($t \approx 8,29$ ans pour le système perturbé et $t \approx 13,56$ ans pour le système de référence) ont donc été déterminées exclusivement par notre outil de visualisation et par l'analyse directe des distances mutuelles dans les données brutes (CSV).

---
### [7.3] : Validation à Long Terme (Le Système Solaire sur 165 ans)

**Contexte & Objectif :** 
Prouver la viabilité et la stabilité numérique de notre moteur physique. Pour cela, nous simulons le Système Solaire complet (le Soleil et ses 8 planètes) sur une durée de 165 ans. Ce laps de temps n'est pas choisi au hasard : il correspond exactement à une révolution complète de Neptune, la planète la plus éloignée de notre système.

> [!info]- Ressources & Connaissances
> - **Outils :** Le moteur `simulation.py` et le script d'animation `visualiseur.py` (aucun script d'analyse supplémentaire n'est requis).
> - **Données d'entrée :** Un fichier `systeme_solaire.csv` contenant les masses, positions (sur X) et vitesses initiales (sur Y) réelles de nos 8 planètes.
> - **Physique Théorique :** L'algorithme de Verlet est dit "symplectique". Contrairement à la méthode d'Euler,  l'énergie totale oscille très légèrement mais ne dérive jamais sur le long terme.

> [!brain]- Le Labo (Réflexions & Arbitrage)  
>  
> **L'Épreuve du Temps (Le Crash-Test) :**  
> L'un des plus grands défis de la simulation numérique est la dérive de l'énergie. Si notre intégrateur n'était pas parfait, les erreurs de calcul s'accumuleraient à chaque pas de temps (chaque seconde simulée). Sur 165 ans, les planètes finiraient inévitablement par s'écraser sur le Soleil ou s'échapper dans le vide.
>  
> **Le Paradoxe Visuel des Échelles :**  
> En gravitation, les différences d'échelle sont immenses. Mercure orbite à $\sim 5.79 \times 10^{10}$ mètres du Soleil, tandis que Neptune évolue à $\sim 4.495 \times 10^{12}$ mètres.
> 
> *Le Diagnostic :* Si nous dézoomons la caméra pour voir Neptune, les planètes telluriques (Mercure, Vénus, Terre, Mars) se retrouvent toutes superposées dans un seul pixel au centre de l'écran. 


**Décisions Analytiques :**
- Lancement de la simulation via le moteur vectorisé (Mode Matrices) sur une durée de 165 années (`unite = 'A'`) pour absorber la charge colossale de calculs.
- Injection directe du fichier CSV de sortie dans le `visualiseur.py`.
- Utilisation de la fonction "Caméra Adaptative" du visualiseur pour absorber les écarts d'échelle planétaires.
-  Utilisation du visualiseur pour générer la vidéo de l'évolution, mettant en évidence la stabilité du système ainsi que la clôture de l'orbite de Neptune.

> [!success] Bilan Analytique (Validation Symplectique)
> L'animation graphique produite valide magistralement notre moteur : malgré des milliards d'opérations mathématiques effectuées par le processeur, Neptune clôture parfaitement son ellipse à l'écran après 165 ans, sans aucune dérive apparente (comme le reste du systeme). Ce résultat confirme la nature symplectique de notre intégrateur temporel.

---
### [7.4] : La Stabilité Absolue (L'Orbite en Huit de Moore)

**Contexte & Objectif :**  
Isoler et prouver la perfection géométrique de notre moteur physique (l'intégration symplectique de Verlet). Pour cela, nous devons utiliser une configuration à trois corps de masses égales qui soit mathématiquement capable de résister aux erreurs d'arrondis de l'ordinateur, afin de démontrer que notre algorithme ne dérive pas sur le très long terme.

> [!info]- Ressources & Connaissances
> 
> - **Outils :** Le moteur physique simulation.py et le script d'animation visualiseur.py.
>     
> - **Données d'entrée :** Un fichier 3_soleils_huit.csv contenant trois astres de masse solaire (
>     
>     ```
>     1.989×1030 kg1.989×1030 kg
>     ```
>     
>     ) placés avec des coordonnées et des vecteurs vitesses extrêmement précis.
>     
> - **Physique Théorique :** L'orbite en lemniscate (figure en 8). Découverte numériquement par Cris Moore en 1993 et prouvée mathématiquement par Chenciner et Montgomery en 2000, c'est une chorégraphie gravitationnelle où trois corps se poursuivent indéfiniment sur la même courbe fermée.
>     

> [!brain]- Le Labo (Réflexions & Arbitrage)
> 
> **Le Mythe du Triangle (Le Théorème de Gascheau) :**  
> Nous avons vu (Module 7.2) que la configuration en triangle équilatéral parfait finit systématiquement par exploser au bout de quelques années. Ce n'est pas un défaut de notre code, mais une loi physique (Théorème de Gascheau, 1843) : avec 3 masses égales, cet équilibre est sur le fil du rasoir. La moindre erreur d'arrondi des flottants (la limite matérielle de la machine) suffit à réveiller le chaos.  
> Le Dilemme : Comment prouver alors que notre algorithme est robuste sur le long terme, si la configuration de test de base est elle-même instable par nature ?
> 
> **La Solution en Huit (Le Bassin d'Attraction) :**  
> Pour contourner cette limite théorique, nous avons fait appel à une solution beaucoup plus rare : l'orbite en "Huit". L'avantage majeur et unique de cette solution est que son "bassin d'attraction" est large. Contrairement au triangle, elle tolère les micro-perturbations. Elle s'auto-corrige naturellement et encaisse les erreurs d'arrondis inévitables de l'ordinateur sans se disloquer.
> 
> **L'Épreuve de vérité pour notre Moteur :**  
> Si notre intégrateur mathématique générait la moindre friction numérique ou ajoutait artificiellement de l'énergie (comme le ferait la méthode d'Euler), même l'orbite en Huit finirait par se briser. La tester sur une longue durée est le juge de paix de notre code.

**Décisions Analytiques :**
- Création d'un fichier de configuration spécial (3_soleils_huit.csv) traduisant les constantes mathématiques de Moore adaptées aux échelles de notre système.
- Exécution de la simulation sur une durée de 50 ans via le moteur matriciel, avec un pas de temps de haute précision.
- Utilisation du `visualiseur.py` avec l'option de traînée complète (TRAINEE_COMPLETE = True) pour tracer visuellement le "8" parfait à l'écran et s'assurer que les orbites ne s'épaississent pas au fil du temps.
    

> [!success] Bilan Analytique (La Preuve Symplectique Ultime)  
> En soumettant cette orbite à notre moteur, le résultat visuel est sans appel : la trajectoire reste parfaitement stable, fluide et strictement superposée à elle-même au-delà de 50 ans simulés.  
> Cette démonstration est la preuve ultime que notre algorithme de Velocity-Verlet préserve parfaitement l'énergie géométrique du système. Nous avons atteint une précision et une rigueur satisfisante, sans avoir eu recours à des algorithmes de calcul beaucoup plus lourds en temps d'exécution (comme Runge-Kutta d'ordre 4).
