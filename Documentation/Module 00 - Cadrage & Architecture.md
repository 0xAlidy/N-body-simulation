# Module 00 : Préambule & Structure du Projet

## 👥 Démarche et Accompagnement

Ce projet de simulation d'une dynamique gravitationnelle a été réalisé dans le cadre du TP d'algorithmique. Afin de franchir la barrière entre la physique pure et le développement logiciel, l'équipe a bénéficié de l'accompagnement d'un programmeur. Cet encadrement a servi de passerelle pédagogique : il a aidé les étudiants à appréhender l'informatique sous un angle professionnel, à acquérir la méthode de réflexion d'un ingénieur logiciel (modularité, cycle de vie de la donnée, gestion mémoire) et à structurer proprement leur code.

## 🤖 Usage de l'IA

L'Intelligence Artificielle a été utilisée comme un assistant technique ciblé, uniquement sur deux axes :

- **La Documentation :** Mettre en forme et condenser les choix de conception de l'équipe (format _Le Labo / Arbitrage_).
    
- **L'Habillage Graphique :** Configurer les détails visuels de l'interface sous Matplotlib (HUD de télémétrie, style des grilles), évitant de longs tâtonnements sur l'affichage pour se concentrer sur l'algorithmique.
    

---

## 🗺️ La Structure des Modules (Le Master Plan)

Ce tableau présente le découpage fonctionnel du logiciel et sert de table des matières pour l'ensemble de la documentation technique.

|**Module**|**Mission Critique**|**Défi Technique Résolu**|
|---|---|---|
|**01 : L'Entrée**|Standardiser le format d'échange.|Contrat d'interface strict et générateur de configurations chaotiques.|
|**02 : Le Parsing**|Charger les données en mémoire.|Stratégie de "Double Passe" pour pré-allouer NumPy sans saturer la RAM.|
|**03 : La Config**|Interfacer l'humain et auto-piloter.|Saisies résilientes et calcul autonome du pas de temps ($dt$) via le temps dynamique ($t_{dyn}$).|
|**04 : Le Moteur**|Calculer les forces à l'instant T.|Vectorisation par _broadcasting_ NumPy, neutralisation de la diagonale via `np.inf` et interception des collisions.|
|**05 : Le Temps**|Générer l'avenir du système.|Implémentation de l'intégrateur de Velocity-Verlet (symplectique) et flux d'écriture continu.|
|**06 : Le Visuel**|Restituer la cinématique.|Animation fluide à 60 FPS via la technique du _Blitting_ et caméra adaptative.|
|**07 : L'Analyse**|Extraire la valeur scientifique.|Validation empirique : vitesse de libération, chaos (3 corps) et lois de Kepler.|

---

## Conclusion

Ce plan directeur cartographie la manière dont chaque brique s'assemble pour former un écosystème cohérent et robuste. Les bases architecturales étant posées, analysons le contrat qui régit notre univers virtuel.

👉 **Passe au [[Module 01 - Élaboration du Système d'Entrée]].**