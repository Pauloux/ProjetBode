# Quel est ce projet ?
Ce projet a été réalisé dans le cadre de l'unité d'enseignement "Instrumentation" en première année du master ÉLISE.
Il vise à apprendre à communiquer avec des instruments afin de réaliser des systèmes de mesure automatique.

Ce projet permet de déterminer le comportement fréquentiel d'un circuit électronique en traçant ses diagrammes de Bode en gain et en phase.
Pour cela, le logiciel commande un générateur basse fréquence (GBF) afin de faire varier la fréquence d'un signal sinusoïdal. Ce signal est l'entrée du circuit à tester.
Le logiciel communique ensuite avec un oscilloscope afin de mesurer l'amplitude du signal de sortie du circuit, ainsi que le déphasage entre le signal d'entrée et de sortie du circuit.

# Dépendances :
- PyVISA

# Comment exécuter le programme ?
Exécuter le fichier "main.py" avec Python.

/!\ Si les ports USB ne sont pas détectés, exécuter le programme en tant que super-utilisateur (sudo) /!\

# Comment utiliser le programme ?
- Dans le panneau de gauche, connecter les instruments et configurer les paramètres d'acquisition.
- Démarrer l'acquisition !
- Les données peuvent être exportées en csv (Enregistrer -> Enregistrer au format csv), et les graphiques peuvent être exportés en tant qu'image (Enregistrer -> Enregistrer au format png ou jpg).

# Comment connecter mes instruments ?
La voie 1 du GBF est divisée en deux avec un té :
- d'une part, le signal est envoyé sur la voie 1 de l'oscilloscope.
- d'autre part, le signal est envoyé sur l'entrée du système à tester.

La sortie du système à tester est reliée à la voie 2 de l'oscilloscope.

# Cela ne fonctionne pas, comment faire ?
Ceci est un projet académique, et c'est d'ailleurs pour cette raison que l'interface et les explications sont en français.
Ma volonté était de le rendre le plus abouti possible, mais des problèmes peuvent toujours survenir. De plus, certains cas limites peuvent ne pas être pris en compte.

## Problèmes connus :
- Les signaux ayant une composante continue ne sont pas pris en charge. Si besoin, configurer les voies de l'oscilloscope en mode AC pour couper la composante continue.
- Les signaux à basses fréquences entraînent un temps d'acquisition erroné. L'acquisition peut donc être trop lente (et perdre du temps) ou trop rapide (et l'oscilloscope n'a pas le temps de faire la mesure). Des propositions de changement pour la formule servant à estimer la durée d'acquisition des mesures sont les bienvenues.
