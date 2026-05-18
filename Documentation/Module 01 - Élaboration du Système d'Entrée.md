## Introduction

Pour qu'une simulation gravitationnelle puisse se faire, le programme doit avoir accès à un **système initial** sur lequel appliquer les lois de la physique. C'est le point de départ indispensable : on ne peut pas calculer un mouvement si l'on ne sait pas _qui_ bouge et _d'où_ il part.

---
### [1.1] : La Carte d'Identité des Astres

> [!ressources]-
> 
> **Ref Sujet :** Créer un système de départ composé d'un ensemble de corps célestes (masses, vitesses et positions initiales).
> 
> **Ref Physique :** Loi de la gravitation universelle de Newton :
> $$F_{AB} = \mathcal{G} \frac{m_A m_B}{r_{AB}^2}$$

**Contexte :** Isoler les variables physiques minimales nécessaires pour que l'univers "existe" mathématiquement dans la simulation.

> [!brain]- Le Labo (Réflexions & Arbitrage)
> 
> **Analyse :** La formule de Newton et les principes de la dynamique nous imposent des besoins précis :
> 
> 1. **La Masse ($m$)** : Grandeur scalaire qui génère la force d'attraction.
> 2. **Position ($x, y$)** : Coordonnées nécessaires pour situer les corps dans l'espace.
> 3. **Vitesse ($v_x, v_y$)** : Sans vitesse initiale, deux astres s'effondreraient simplement l'un sur l'autre par pure attraction.
> 4. **Le Nom** : Crucial pour le post-traitement et l'identification des trajectoires (ex: distinguer la Terre de la Lune).
> 
> - **Anticipation :** Pourquoi pas la 3D ? Le sujet conseille de travailler en 2D car la visualisation est plus aisée. On s'arrête donc à deux coordonnées.
>   
> **Analyse de la Durée :** Est-ce une propriété de l'astre ?
> 
> - **Réflexion :** Non. Un astre existe indépendamment du temps qu'on décide de l'observer. La durée est une contrainte imposée par l'expérimentateur.
>   
>  - **Arbitrage :** On exclut la durée de la définition des astres. Elle sera traitée comme une **Variable Globale d'Expérience** saisie lors de l'exécution.

**Décision :**
- Validation d'un profil d'astre composé de 6 variables : `Nom`, `Masse`, `X`, `Y`, `VX`, `VY`.
- Durée de la simulation devra être renseigné au lancement du programme

> [!warning]- L'Émergence
> Nous connaissons maintenant la structure d'un astre isolé. Cependant, pour simuler un système complexe (N-corps), nous devons manipuler une liste arbitraire d'objets. 
> - Comment permettre à l'utilisateur de fournir ces données sans que cela soit une corvée ou une source d'erreurs ?
>  - Comment stocker cette collection de manière persistante ?
>    
>  $\rightarrow$ **Voir 1.2 (Le Support de Données)**.

---
### [1.2] : Le Choix du Support (Format du Fichier)

**Description** : Déterminer le support de transfert de données le plus efficient entre l'utilisateur et le moteur de calcul.

> [!brain]- Le Labo (Réflexions & Arbitrage)
> 
> **Analyse des options :**
> 
> - **Saisie Console :** Inefficace pour plusieurs corps + non persistante. Trop de risques d'erreurs de frappe.
>     
> - **Format JSON / XML :** Très robuste pour le code, mais complexe à rédiger pour un utilisateur non-développeur.
>   
> - **Format CSV (Tableur) :** Permet d'utiliser des logiciels familiers comme Excel. C'est un format "ligne par ligne" qui correspond parfaitement à notre liste d'astres.

**Décision :** Choix exclusif du format **.csv**. C'est le média qui minimise la friction utilisateur tout en restant simple à interpréter (parser).

> [!warning]- L'Émergence
> Le contenant (CSV) est choisi. Mais l'organisation interne du fichier doit être rigoureuse : l'ordinateur doit savoir quel nombre correspond à quelle variable physique
> 
> $\rightarrow$ **Voir 1.3 (Le Contrat d’Interface)**.

---
### [1.3] : Le Contrat d'Interface (Unités et Standardisation)

> [!ressources]-
> 
> **Ref Sujet :** "Il est indispensable de maîtriser les unités dans ce projet".
> 
> **Ref Système :** Utilisation impérative du Système International (SI) : $kg, m, s$.

**Description** : Établir les règles de "langage" communes entre l'utilisateur et le programme pour garantir la cohérence des calculs physiques.

> [!brain]- Le Labo (Réflexions & Arbitrage)
> 
> **Analyse du Header (En-tête) :** Pour que le programme récupère les informations sans ambiguïté, l'ordre des colonnes doit être fixé une fois pour toutes.
> 
> **Analyse des Risques :**
> 
> - **Unités disparates :** Nous refusons les conversions complexes (UA, km, masses solaires) pour éviter les erreurs d'échelle. Le SI offre un cadre de calcul direct avec la constante $\mathcal{G}$.
>     
> - **Formatage numérique :** Python utilise le point `.` comme séparateur décimal. Puisque le CSV utilise déjà la virgule `,` pour séparer les colonnes, le point est la seule alternative viable.

**Décisions :**
1. Fixer un en-tête obligatoire : `'Name,Mass,Position X,Position Y,Velocity X,Velocity Y'` 
2. Imposer le **Système International (SI)** strict.
3. Imposer le **point `.`** pour les nombres décimaux.

---
### [1.4] : Le Générateur de Chaos Aléatoire

**Contexte :** Permettre la création instantanée d'un univers à $N$ corps totalement aléatoire afin de tester les limites de performance du moteur matriciel (NumPy) et d'observer des dynamiques chaotiques à grande échelle sans dépendre d'une saisie manuelle fastidieuse.

> [!info]- Ressources
> 
> - **Modules Python :** `csv` pour l'export, `random` pour le tirage des variables, `sys` pour la gestion des arguments CLI.
>     
> - **Contrat d'interface :** Respect strict des colonnes attendues par le parseur principal (`Name`, `Mass`, `Position X`, `Position Y`, `Velocity X`, `Velocity Y`).
>     

> [!brain]- Le Labo (Réflexions & Arbitrage)
> 
> **Le piège de la distribution linéaire des masses :**
> 
> Si nous générons des masses de manière purement linéaire (ex: `random.uniform(1e22, 1e30)`), la probabilité mathématique va saturer l'univers d'étoiles supermassives. Les petits corps (type astéroïdes ou planètes) seraient inexistants, car l'écart d'échelle est de 8 ordres de grandeur. Un tel système s'effondrerait sur lui-même de façon trop uniforme.
> 
> _La solution (L'échelle logarithmique) :_ Nous faisons le choix d'un tirage uniforme appliqué à l'exposant de la puissance de 10 (`10**random.uniform(22, 30.5)`). De cette manière, nous assurons une distribution sémantiquement hiérarchique : le système comportera équitablement une multitude de corps légers  et quelques monstres gravitationnels massifs, ce qui est idéal pour observer du chaos pur.
> 
> **L'absence de contraintes orbitales :**
> 
> Contrairement à un système solaire stable nous cherchons ici le déséquilibre. Les positions et les vecteurs vitesses sont injectés de manière purement cartésienne dans un carré de $40 \text{ UA}$ de côté. Cela garantit un système hors-équilibre, propice aux collisions immédiates, aux frondes gravitationnelles sauvages et aux éjections à haute vitesse.

**Décisions :**

- Utilisation de la distribution logarithmique pour le calcul de la masse de chaque astre.
    
- Le script accepte un nombre d'astres en argument (`python generateur.py 150`)

---
## Conclusion

Le média de transfert est prêt. L'utilisateur a ses instructions. Maintenant, le rôle du développeur commence : comment récupérer ce fichier, valider sa robustesse (gérer l'erreur humaine) et l'initialiser dans le programme ?

**👉 Direction : Module 02 - Parsing et Robustesse.**