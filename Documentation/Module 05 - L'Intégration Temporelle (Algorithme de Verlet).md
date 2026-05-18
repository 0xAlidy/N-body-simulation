## Introduction

Le décor est planté, la configuration est validée (Module 03) et les lois de la physique sont modélisées (Module 04). Il est temps de lancer le temps lui-même.

Ce module constitue le cœur battant de notre simulateur. C'est ici que la physique théorique s'incarne dans une boucle temporelle itérative pour donner vie à l'Univers.

L'objectif n'est pas seulement de calculer l'avenir du système N-Corps, mais de sérialiser et d'archiver son histoire de manière fluide, performante et infaillible.

---
### [5.1] : La Préparation du Fichier (La Stratégie d'I/O et les Métadonnées)

**Contexte :** Avant de calculer le premier mouvement, le programme doit ouvrir le flux de données vers le disque dur, choisir sa stratégie d'écriture, et construire une structure d'accueil capable d'enregistrer un nombre $N$ d'astres de manière standardisée et réutilisable.

> [!info]- Ressources
> 
> - **Héritage :** Les constantes définies au Module 03 (`duree`, `pas`, `intervalle`), le nom du fichier de sortie sécurisé, et la liste dynamique des noms des astres (`names`).
>     
> - **Modules Python :** `csv` pour le formatage, `os` pour la gestion des dossiers, la fonction native `open()` pour la gestion du flux mémoire.
>     

> [!brain]- Le Labo (Les Dilemmes d'Ingénierie)
> 
> **Dilemme 1 : La Stratégie d'Enregistrement (Saturation RAM vs Goulet d'étranglement I/O)**
> 
> Comment sauvegarder des millions de calculs ?
> 
> - _Option A (Tout à la fin) :_ Stocker toutes les positions dans des tableaux NumPy géants en RAM, et créer le CSV tout à la fin. _Risque :_ Saturation de la mémoire pour les longues simulations, et perte totale des données si le programme crashe à 99%.
>     
> - _Option B (Au fil de l'eau) :_ Ouvrir le fichier et écrire sur le disque dur à chaque étape. _Risque :_ L'accès matériel au disque (I/O) est des milliers de fois plus lent que la RAM, cela briderait le processeur.
>     
>     _L'Arbitrage (Le Streaming Bufferisé) :_ Nous choisissons l'écriture progressive (Fail-Safe). Pour éviter le ralentissement matériel, nous faisons confiance au buffer natif de la fonction `open()` de Python : les données sont poussées en continu vers le module `csv`, mais le système d'exploitation les groupe silencieusement en RAM avant de les écrire par "blocs" sur le disque. C'est le compromis parfait entre sécurité et performance.
>     
> 
> **Dilemme 2 : La traçabilité scientifique (Le fichier autoporteur)**
> 
> Dans un an, si un expérimentateur ouvre notre fichier `resultats_S1.csv` contenant 200 000 lignes de nombres, il n'aura aucun moyen de savoir avec quelle précision temporelle ($dt$) cette physique a été générée.
> 
> _L'Arbitrage (Les Métadonnées masquées) :_ Le fichier de sortie doit contenir son propre ADN. Nous choisissons d'écrire une toute première ligne de configuration contenant explicitement les variables clés (Durée, Pas, Intervalle). Pour que cette ligne ne fasse pas crasher l'analyse de données (Pandas) par la suite, nous la préfixons d'un `#`. Le fichier devient un objet scientifique traçable et sécurisé.
> 
> **Dilemme 3 : La dimensionnalité de l'en-tête (Aplatir l'Univers)**
> 
> Le moteur physique gère des matrices (tableaux à plusieurs dimensions), mais un fichier CSV est une structure strictement bidimensionnelle (Lignes = Temps, Colonnes = Valeurs). De plus, l'univers peut contenir 3 astres comme 150. On ne peut pas coder les colonnes en dur.
> 
> _L'Arbitrage (La génération dynamique) :_ Nous construisons l'en-tête du tableau de manière procédurale. Le script boucle sur la liste d'astres identifiée au parsing, et génère automatiquement pour chaque corps quatre colonnes distinctes (`Nom_X`, `Nom_Y`, `Nom_VX`, `Nom_VY`). Le tableau s'élargit mathématiquement en fonction du système initial injecté.

**Décisions Implémentées :**

- **Flux d'écriture (Fail-safe) :** Utilisation de l'instruction `with open(..., 'w')` couplée à `csv.writer` pour initialiser un flux continu et profiter du buffer mémoire de Python au lieu de tout stocker en RAM.
    
- **Vérification d'arborescence :** Création automatique du dossier de sortie via `os.makedirs(OUTPUT_FOLDER, exist_ok=True)` pour prévenir les crashs d'I/O.
    
- **Injection des Métadonnées :** Écriture de la ligne `# DUREE_SEC: {duree} | PAS_SEC: {pas} | INTERVALLE_SAUVEGARDE_SEC: {intervalle}` dès l'ouverture du fichier.
    
- **En-tête horizontal :** Utilisation d'une boucle génératrice pour concaténer dynamiquement un vecteur textuel de colonnes proportionnel au nombre d'astres (`len(names) * 4` colonnes).
    

> [!warning]- L'Émergence
> 
> Le flux d'enregistrement est ouvert, protégé contre les crashs, et son en-tête est en place, prêt à recevoir les coordonnées de l'univers à chaque instant clé.
> 
> **👉 La problématique suivante s'enclenche :** L'univers est à $t=0$ et le fichier attend. Il faut maintenant lancer le temps. Comment calculer la position future de nos astres avec suffisamment de précision pour que le système ne s'effondre pas sur lui-même au bout de quelques orbites ? Pourquoi l'approche classique (Euler) n'est-elle pas suffisante pour simuler la gravité sur le long terme ?
> 
> $\rightarrow$ **Passe au Maillon 5.2 : La Précision Temporelle (L'Algorithme de Velocity-Verlet).**
---

---
### [5.2] : Le Moteur d'Intégration (L'Algorithme de Velocity-Verlet)

**Contexte :** Transformer l'accélération instantanée subie par chaque astre en un déplacement spatial fluide et continu. Il s'agit de calculer itérativement la trajectoire du système sur des millions de pas de temps ($dt$) sans que la simulation ne se disloque au fil des années virtuelles.

> [!info]- Ressources
> 
> - **Héritage :** Le calculateur d'accélération (matriciel ou par boucle) développé au Module 04.
>     
> - **Concepts Physiques :** Cinématique (Position, Vitesse, Accélération), Intégrateurs Symplectiques (conservation de l'énergie géométrique).
>     

> [!brain]- Le Labo (Les Dilemmes d'Ingénierie)
> 
> **Dilemme 1 : Le Drift de l'Énergie (Euler vs Verlet)**
> 
> L'approche la plus intuitive pour animer un astre est la méthode d'Euler : à chaque pas, on calcule la nouvelle position avec la vitesse actuelle, et la nouvelle vitesse avec l'accélération actuelle.
> 
> _Le problème :_ Euler fait une approximation linéaire sur une courbe elliptique. À chaque itération, l'algorithme "dépasse" légèrement la trajectoire réelle et ajoute artificiellement de l'énergie au système. Sur une simulation de 10 ans, l'orbite terrestre finirait par former une spirale et la Terre s'échapperait du système solaire.
> 
> _L'Arbitrage (Le choix Symplectique) :_ Nous implémentons la méthode de **Velocity-Verlet**. C'est un algorithme symplectique : l'erreur numérique oscille mais ne s'accumule jamais. L'énergie globale du système est conservée, ce qui nous permet de simuler des trajectoires chaotiques ou des figures parfaites (comme l'orbite en "Huit" du Module 07) sur des décennies sans la moindre dérive.
> 
> **Dilemme 2 : La séquence d'exécution (Le paradoxe temporel)**
> 
> L'algorithme de Verlet est ultra-précis car il calcule la nouvelle vitesse en utilisant la moyenne entre l'accélération présente et l'accélération _future_. Mais pour connaître l'accélération future, il faut d'abord connaître la position future.
> 
> _L'Arbitrage (L'architecture en 3 temps) :_ Nous imposons une séquence stricte et immuable dans la boucle de calcul (`while t <= duree`) :
> 
> 1. _Le Saut spatial :_ On avance toutes les planètes d'un coup grâce à leur accélération et vitesse actuelles.
>     
> 2. _La Mise à jour des Forces :_ On appelle notre moteur (Module 04) pour calculer les **nouvelles** accélérations (`acc_t_next`) sur ces nouvelles positions.
>     
> 3. _La Correction cinématique :_ On met à jour les vitesses en utilisant simultanément l'ancienne et la nouvelle accélération.
>     

**Décisions Implémentées :**

- **Rejet d'Euler :** Utilisation exclusive de l'intégration symplectique de Verlet.
    
- **Étape 1 (Positions) :** Application de l'équation cinématique `pos = pos + vel * pas + 0.5 * acc_t * (pas 2)`.
    
- **Étape 2 (Accélérations) :** Appel au moteur gravitationnel pour générer `acc_t_next` en fonction du mode choisi (matrice ou boucle).
    
- **Étape 3 (Vitesses) :** Application de l'équation de correction `vel = vel + 0.5 * (acc_t + acc_t_next) * pas`.
    
- **Recyclage Mémoire :** Écrasement de l'ancienne accélération par la nouvelle (`acc_t = acc_t_next`) à la fin de la boucle pour éviter de saturer la RAM avec des variables inutiles.
    

> [!warning]- L'Émergence
> 
> Les mathématiques tournent. La Terre avance autour du Soleil avec une précision chirurgicale à chaque pas de calcul ($dt$).
> 
> **👉 La problématique suivante s'enclenche :** Si l'utilisateur a choisi un pas de 1 seconde pour une simulation d'une année (31 millions de secondes), le programme va exécuter 31 millions de boucles mathématiques parfaites. Écrire chaque ligne dans notre fichier CSV générerait un fichier de plusieurs gigaoctets, inexploitable par notre visualiseur.
> 
> Comment dé-corréler le temps mathématique (le $dt$) du temps d'enregistrement (l'intervalle) sans utiliser la fonction modulo `%` qui provoque des erreurs catastrophiques sur les nombres flottants en informatique ?
> 
> $\rightarrow$ **Passe au Maillon 5.3 : La Boucle Temporelle (Le Piège du Modulo et la Sauvegarde).**

---
### [5.3] : La Boucle Principale et l'Extraction d'État (Sérialisation)

**Contexte :** Le moteur tourne et calcule les nouvelles positions à chaque pas de temps ($dt$). Il faut maintenant extraire ces données à des intervalles précis pour les écrire dans le fichier CSV, c'est-à-dire transformer un état matriciel 2D en une simple ligne de texte 1D, tout en gardant une synchronisation temporelle parfaite.

> [!info]- Ressources
> 
> - **Héritage :** Les variables `t`, `pas` et `intervalle`.
>     
> - **Modules Mathématiques :** Manipulation de matrices avec NumPy (`np.hstack`, `flatten()`).
>     
> - **Concept Informatique :** La représentation des nombres à virgule flottante (Standard IEEE 754).
>     

> [!brain]- Le Labo (Les Dilemmes d'Ingénierie)
> 
> **Dilemme 1 : La synchronisation temporelle (Le Piège du Modulo sur les flottants)**
> 
> Pour savoir quand sauvegarder une image, l'approche naïve est d'utiliser le modulo : si le reste de la division du temps par l'intervalle est nul (`t % intervalle == 0`), on sauvegarde.
> 
> _Le problème :_ En informatique, les nombres décimaux (flottants) sont imparfaits (ex: $0.1 + 0.2 = 0.30000000000000004$). Sur des millions d'itérations, le temps $t$ ne tombera presque jamais _exactement_ sur un multiple parfait de l'intervalle. Le modulo ratera la condition, et le fichier sera vide.
> 
> _L'Arbitrage (Le Seuil Cumulatif) :_ Nous abandonnons le modulo. Nous créons une variable "cible" (`prochaine_sauvegarde`). À chaque boucle, on vérifie simplement si le temps a dépassé cette cible (`if t >= prochaine_sauvegarde`). Si oui, on écrit la ligne, puis on repousse la cible (`prochaine_sauvegarde += intervalle`). C'est mathématiquement infaillible, peu importe l'imprécision des décimales.
> 
> **Dilemme 2 : L'Aplatissement de l'Univers (La Sérialisation 2D vers 1D)**
> 
> Notre moteur physique stocke les positions et les vitesses sous forme de deux matrices 2D distinctes (Lignes = Astres, Colonnes = Axes X/Y). Mais la fonction `csv.writer` n'accepte qu'une liste simple (un vecteur 1D) pour écrire une ligne dans le fichier.
> 
> _L'Arbitrage :_ Plutôt que de faire des boucles `for` imbriquées très lentes pour extraire chaque coordonnée une par une, nous utilisons la puissance vectorielle de NumPy. Nous collons d'abord horizontalement la matrice des positions et des vitesses (`np.hstack((pos, vel))`), puis nous écrasons le tout en une seule dimension avec `.flatten()`. La conversion est instantanée.

**Décisions Implémentées :**

- **Découplage temporel strict :** Le rythme du moteur physique (calcul) est totalement indépendant de la fréquence d'enregistrement (sauvegarde) grâce au système de seuil cumulatif.
    
- **Sérialisation optimisée :** L'instruction `np.hstack((pos, vel)).flatten()` est utilisée pour fusionner et aplatir les matrices d'état avant l'écriture.
    
- **Avancement du temps :** Le temps est incrémenté strictement de `t += pas` à la toute fin de la boucle d'intégration.
    

---

## Conclusion

Le temps s'est écoulé. Les planètes ont suivi leurs trajectoires selon les lois immuables de Newton et la précision chirurgicale de Verlet. L'univers entier est désormais archivé de manière sécurisée et continue dans un fichier CSV.

La simulation physique est une réussite technique : le processeur a été optimisé grâce au calcul matriciel, la mémoire a été préservée par l'écriture en flux continu (Fail-safe), et l'architecture logicielle garantit des résultats mathématiquement fiables sur le long terme.

Cependant, ces millions de lignes de coordonnées brutes sont illisibles pour un cerveau humain. Pour comprendre ce qu'il s'est passé, repérer d'éventuelles collisions ou observer le chaos gravitationnel, nous devons donner vie à ces chiffres.

👉 **Direction le [[Module 06 - Visualisation]]**