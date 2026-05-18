## Introduction

L'univers est chargé en mémoire : nous disposons désormais des masses, des positions et des vitesses initiales de chaque corps à l'instant $t=0$. Cependant, cet univers reste figé. L'objectif de ce module est de concevoir le "moteur" de la simulation en modélisant la loi de la Gravitation Universelle de Newton.

Au-delà de la stricte fidélité physique, ce module représente un authentique défi d'optimisation informatique : comment calculer des millions d'interactions gravitationnelles croisées à chaque pas de temps sans mettre le processeur à genoux  et sans effondrer la fluidité du programme ? (temps / mémoire)

---

### [4.1] : L'Approche Classique par Boucles (La Projection et l'Action-Réaction)

**Contexte :** Traduire la loi physique scalaire de Newton en coordonnées cartésiennes bidimensionnelles et implémenter une première version itérative du calcul des forces en optimisant le nombre d'opérations grâce aux symétries de la nature.

> [!info]- Ressources
> 
> - **Lois Physiques :** Loi de la gravitation universelle ($F = \mathcal{G} \frac{m_i m_j}{r^2}$) et Principe Fondamental de la Dynamique ($\vec{a} = \vec{F}/m$).
>     
> - **Outils Mathématiques :** Théorème de Pythagore pour les distances, trigonométrie des triangles semblables pour la projection linéaire.
>     

> [!brain]- Le Labo (Les Dilemmes d'Ingénierie)
> 
> **Dilemme 1 : Le Découpage Géométrique (La Projection Cartésienne)**
> 
> L'ordinateur travaille uniquement sur des axes orthogonaux indépendants ($X$ et $Y$), tandis que la force de gravité agit selon une diagonale directe reliant deux astres. Comment répartir cette intensité ?
> 
> _L'Arbitrage :_ Pour chaque paire d'astres, le code calcule l'écart sur chaque axe ($dx = x_j - x_i$ et $dy = y_j - y_i$), puis l'hypoténuse $r = \sqrt{dx^2 + dy^2}$. Plutôt que de calculer des angles (sinus/cosinus) avec des fonctions trigonométriques extrêmement lourdes pour le processeur, nous utilisons le principe géométrique des triangles semblables. On projette la force en la multipliant simplement par le ratio de distance de l'axe : $F_x = F \times \frac{dx}{r}$ et $F_y = F \times \frac{dy}{r}$.
> 
> **Dilemme 2 : L'Explosion Algorithmique (La redondance en $\mathcal{O}(N^2)$)**
> 
> La méthode la plus naïve consiste à utiliser deux boucles imbriquées complètes pour que chaque astre parcoure tous les autres. Mais si le code calcule l'influence de l'astre $i$ sur l'astre $j$, il recroisera plus tard l'influence de $j$ sur $i$. C'est un gâchis colossal de calculs.
> 
> _L'Arbitrage (L'Action-Réaction) :_ Nous invoquons la 3ème loi de Newton ($\vec{F}_{ij} = -\vec{F}_{ji}$). Nous implémentons une boucle à indexation triangulaire partielle : `for j in range(i + 1, N)`. Cela résout deux problèmes d'un coup : un astre ne se compare jamais avec lui-même (évitant la division par zéro), et la force n'est calculée qu'une seule fois par paire. Elle est directement ajoutée à l'accélération de l'astre $i$ et soustraite à celle de l'astre $j$, divisant le nombre d'itérations par deux : $\frac{N(N-1)}{2}$.

**Décisions Implémentées :**

- **Architecture de calcul :** Création de la fonction de référence `calculer_accelerations_boucles(mass, pos, rayons, time)`.
    
- **Allocation locale :** Initialisation d'une matrice d'accélération vierge via `np.zeros((N, 2))` à chaque pas de temps.
    
- **Symétrie physique :** Application stricte du principe d'action-réaction via les opérateurs cumulatifs `+=` sur l'index $i$ et `-=` sur l'index $j$.
    

> [!warning]- L'Émergence
> 
> L'astuce de l'Action-Réaction soulage l'algorithme, mais l'exécution de boucles `for` imbriquées en Python pur reste dramatiquement lente dès que le nombre de corps $N$ augmente (langage interprété).
> 
> **👉 La problématique suivante s'enclenche :** Comment court-circuiter totalement la lenteur de l'interpréteur Python pour déléguer le calcul de ces millions de paires directement au processeur en langage machine ?
> 
> $\rightarrow$ **Passe au Maillon 4.2 : L'Approche Matricielle et le Broadcasting (NumPy).**

---
### [4.2] : L'Approche Matricielle et le Broadcasting (NumPy)

**Contexte :** Migrer le calcul des forces vers un paradigme vectoriel global pour exploiter la vitesse brute du langage C sous-jacent à la bibliothèque NumPy, éliminant ainsi toute boucle itérative.

> [!info]- Ressources
> 
> - **Héritage :** Les matrices de positions 2D et de masses 1D allouées dynamiquement lors du parsing (Module 02).
>     
> - **Concept Informatique :** Le _Broadcasting_ (extension virtuelle des dimensions matricielles sans duplication en mémoire).
>     

> [!brain]- Le Labo (Les Dilemmes d'Ingénierie)
> 
> **Dilemme 1 : Le Calcul Vectoriel Simultané**
> 
> Comment forcer le processeur à calculer toutes les distances inter-planétaires d'un seul coup sans utiliser de boucle ?
> 
> _L'Arbitrage :_ Nous utilisons l'extension de dimension `np.newaxis`. En soustrayant la matrice des positions étendue en ligne à elle-même étendue en colonne (`pos[np.newaxis, :, :] - pos[:, np.newaxis, :]`), NumPy génère instantanément une matrice 3D contenant les écarts ($dx, dy$) de toutes les paires possibles de l'univers en une seule opération exécutée en C backend.
> 
> **Dilemme 2 : Le Piège du Branching (L'Auto-interaction matricielle)**
> 
> Le broadcasting croise inévitablement chaque astre avec lui-même. Sur la diagonale de notre matrice de distances, on se retrouve avec des zéros ($r = 0$), provoquant une division par zéro fatale lors du calcul de la force. Ajouter une condition classique (`if i != j`) pour sauter la diagonale forcerait le processeur à s'interrompre à chaque case pour "réfléchir" (rupture de pipeline ou _branching_). Cela briserait la vitesse du calcul vectoriel.
> 
> _L'Arbitrage (La Neutralisation Algébrique) :_ Nous interdisons les conditions algorithmiques. Nous appliquons une ruse mathématique : nous écrasons la diagonale des zéros en y injectant la valeur de l'Infini via `np.fill_diagonal(r2, np.inf)`. On laisse ensuite NumPy appliquer la formule de Newton de manière aveugle sur tout le bloc mémoire. Comme $G \frac{m}{\infty^2} = 0$, l'auto-attraction s'annule mathématiquement d'elle-même à la vitesse maximale du processeur, sans aucune interruption de flux.

**Décisions Implémentées :**

- **Vectorisation totale :** Implémentation de la fonction ultra-rapide `calculer_accelerations_matrice(mass, pos, rayons, time)`.
    
- **Algèbre matricielle :** Réduction de la matrice 3D des deltas par somme quadratique sur le dernier axe (`np.sum(..., axis=-1)`) pour isoler le carré des distances `r2`.
    
- **Verrouillage de la diagonale :** Utilisation exclusive de `np.fill_diagonal(r2, np.inf)` pour immuniser le code contre l'auto-interaction.
    
> [!warning]- L'Émergence
> 
> Le calcul vectoriel est un succès : notre moteur tourne désormais à pleine puissance, libéré des lenteurs de Python.
> 
> **👉 La problématique suivante s'enclenche :** Cette exécution purement mathématique est aveugle. Elle met en lumière un cas limite catastrophique de la formule de Newton : que se passe-t-il si deux astres finissent par se percuter ? La distance qui les sépare devient nulle. La force est divisée par zéro, explose vers l'infini, et corrompt immédiatement toute la simulation. Comment doter notre moteur d'un véritable "sens du toucher" pour détecter un contact physique avant que l'univers mathématique ne s'effondre ?
> 
> $\rightarrow$ **Passe au Maillon 4.3 : La Singularité Gravitationnelle (Gestion et Interception des Collisions).**

---
### [4.3] : La Singularité Gravitationnelle (Gestion et Interception des Collisions)

**Contexte :** Doter le moteur de calcul d'une réalité matérielle. Il s'agit d'empêcher les astres de se traverser comme des fantômes (effet de _Tunneling_) ou de générer des forces infinies, en concevant un système d'arrêt d'urgence capable de s'adapter automatiquement à l'échelle de chaque objet (de la simple sonde spatiale à l'étoile supermassive).

> [!info]- Ressources
> 
> - **Formules Géométriques :** Volume de la sphère ($V = \frac{4}{3}\pi R^3$) et équation de masse par la densité ($M = V \times \rho$).
>     
> - **Constante Physique :** Densité moyenne type planète rocheuse (`DENSITY = 5500 kg/m³`).
>     

> [!brain]- Le Labo (Les Dilemmes d'Ingénierie)
> 
> **Dilemme 1 : L'Événement Post-Impact (Fusion, Rebond ou Arrêt ?)**
> 
> Si deux astres entrent en contact physique, comment le moteur doit-il réagir ? La physique offre deux voies : la collision élastique (les astres rebondissent) ou inélastique (fusion).
> 
> _L'Arbitrage (Le principe de rigueur) :_ Gérer une fusion exigerait de détruire et recréer dynamiquement les matrices NumPy en plein milieu de la boucle de calcul, ce qui anéantirait nos efforts d'optimisation (Module 4.2). Gérer un rebond imposerait une modélisation vectorielle complexe. Plutôt que d'implémenter une mécanique approximative, nous optons pour la sécurité absolue : le **Hard Stop**. Dès qu'un impact est avéré, le programme se gèle et lève une erreur explicite, préservant ainsi la validité scientifique de la simulation au lieu de générer des trajectoires faussées par une force infinie.
> 
> **Dilemme 2 : Le Seuil de Détection (Constante Globale vs Échelle Dynamique)**
> 
> Maintenant que la règle d'arrêt est fixée, il faut déterminer _quand_ elle se déclenche. N'ayant pas le rayon des astres dans le fichier CSV, deux options s'offrent à nous :
> 
> - _Option A (La Constante Arbitraire) :_ Fixer une limite absolue en dur dans le code pour tout l'univers (ex: si l'écart est inférieur à 5000 km, c'est un crash). _Le problème :_ C'est inadapté à un système multi-échelles. Une sonde de 10 mètres s'écraserait virtuellement à des milliers de kilomètres de la Terre, et deux étoiles géantes se traverseraient presque avant que le code ne réagisse.
>     
> - _Option B (Le Rayon Numérique Déduit) :_ Estimer un rayon théorique dynamique basé sur la masse de chaque corps.
>     
>     _L'Arbitrage :_ Nous rejetons la constante globale et optons pour l'Option B. En imposant une densité moyenne universelle (`DENSITY = 5500 kg/m³`), le programme isole mathématiquement le rayon à l'initialisation : $R_i = \left(\frac{3M_i}{4\pi\rho}\right)^{1/3}$. Même si cela lisse les spécificités des géantes gazeuses, la collision devient une frontière géométrique propre à chaque paire : l'impact se déclenche si `r < R[i] + R[j]`.
>     

**Décisions Implémentées :**

- **Déduction Mathématique :** Création de la sous-fonction `calculer_rayons(mass)` exécutée uniquement à l'initialisation pour générer le tableau des seuils.
    
- **Pare-feu d'impact vectorisé :** Génération de la matrice de collision par sommation croisée (`rayons[:, np.newaxis] + rayons[np.newaxis, :]`) permettant une vérification matricielle instantanée via `np.any(r < rayons_collision)`.
    
- **Interception (Hard Stop) :** Levée d'une exception explicite (`ValueError`) figeant la boucle temporelle avant l'effondrement gravitationnel.

> [!warning]- L'Émergence
>Notre moteur physique est désormais mathématiquement complet, performant et protégé contre les collisions accidentelles. Nous disposons de deux moteurs fonctionnels dans le code (le mode Boucles et le mode Matrices).
>
>**👉 La problématique suivante s'enclenche :** L'ingénierie logicielle exige de prouver scientifiquement l'efficacité d'une optimisation par rapport à une autre. Comment mesurer empiriquement le gain de vitesse réel apporté par le calcul matriciel ?
>
>$\rightarrow$ **Passe au Maillon 4.4 : Le Mode Benchmark (La Validation Empirique).**

---
### [4.4] : Le Mode "Benchmark" (La Validation Empirique)

**Contexte :** Déployer un environnement de test scientifique au sein de l'application pour quantifier et comparer objectivement le temps CPU consommé par les deux méthodes de résolution (Boucles vs Matrices).

> [!info]- Ressources
> 
> - **Bibliothèque Système :** Le module natif `time` de Python.
>     
> - **Outil de mesure :** L'horloge haute précision `time.perf_counter()` pour capturer les microsecondes d'exécution du processeur.
>     

> [!brain]- Le Labo (Les Dilemmes d'Ingénierie)
> 
> **Dilemme : L'isolation des mesures de performance** Comment s'assurer que notre chronométrage mesure la pure efficacité mathématique des algorithmes sans être faussé par les lenteurs d'écriture sur le disque dur (I/O) ou par les tâches de fond du système d'exploitation ?
> 
> _L'Arbitrage :_ Nous créons une routine d'exécution isolée (`mode == 3`). Le programme prend le même système d'entrée et lance la simulation complète deux fois consécutives. Les compteurs encadrent de manière chirurgicale les appels à la fonction de Verlet, et le script calcule lui-même le ratio mathématique final (`temps_boucles / temps_matrice`) pour l'afficher à l'utilisateur, apportant une preuve irréfutable de la supériorité vectorielle.

**Décisions Implémentées :**

- **Architecture de test :** Centralisation de la procédure dans la fonction dédiée `test_performance(...)`.
    
- **Chronométrage chirurgical :** Encapsulation des fonctions de simulation entre deux variables de capture temporelle (`debut = time.perf_counter()` ... `fin = time.perf_counter()`).
    
- **Restitution des métriques :** Affichage direct des résultats dans la console avec calcul automatique du vainqueur de performance pour guider les choix futurs de l'expérimentateur.

---
## Conclusion

Notre moteur physique a maintenant deux vitesses (classique et matricielle).
Nous savons maintenant calculer "l'effort" (l'accélération) que subit chaque astre à un instant $T$. Mais une accélération ne crée pas de mouvement toute seule : elle modifie la vitesse, qui elle-même modifie la position au cours du temps.

Comment transformer cette accélération instantanée en un déplacement réel sur une période donnée (ex: 1 jour, 1 an) ?

👉 **Direction : Module 05 - L'Intégration Temporelle (Algorithme de Verlet).**
