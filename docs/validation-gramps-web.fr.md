# Compatibilité Gramps Web — audit statique — 30 septembre 2026

## Version et sources examinées

La dernière version publiée de l’API au moment de la vérification est Gramps Web API **3.22.3**, publiée le 27 septembre 2026 et toujours marquée « Latest » sur la page des versions le 30 septembre ([publication officielle](https://github.com/gramps-project/gramps-web-api/releases/tag/v3.22.3), [liste des versions](https://github.com/gramps-project/gramps-web-api/releases)). Les sources épinglées examinées sont [`const.py`](https://github.com/gramps-project/gramps-web-api/blob/v3.22.3/gramps_webapi/const.py), [`api/report.py`](https://github.com/gramps-project/gramps-web-api/blob/v3.22.3/gramps_webapi/api/report.py) et [`api/tasks.py`](https://github.com/gramps-project/gramps-web-api/blob/v3.22.3/gramps_webapi/api/tasks.py). Le guide officiel indique que le serveur expose les rapports installés et transmet le fichier généré au navigateur ([guide Rapports](https://www.grampsweb.org/user-guide/reports/)).

Un contrôle complémentaire de la branche publique non versionnée `master` a été fait le 30 septembre sur les mêmes fichiers ([`const.py`](https://github.com/gramps-project/gramps-web-api/blob/master/gramps_webapi/const.py), [`api/report.py`](https://github.com/gramps-project/gramps-web-api/blob/master/gramps_webapi/api/report.py), [`api/tasks.py`](https://github.com/gramps-project/gramps-web-api/blob/master/gramps_webapi/api/tasks.py)). Il confirme les mêmes points de blocage : filtre par `REPORT_DEFAULTS`, contrôle de l’extension par `MIME_TYPES`, chemin imposé via `of` sous `REPORT_DIR`, et tâche `generate_report` sans callback de progression passé à `run_report`. Ce contrôle de `master` est indicatif et ne remplace pas l’audit épinglé sur la version publiée.

## Incompatibilités relevées

- `REPORT_DEFAULTS` dépend des bibliothèques disponibles : avec GTK, il autorise `CATEGORY_TEXT` et `CATEGORY_DRAW`, plus `CATEGORY_GRAPHVIZ` si Graphviz est installé ; sans PyGObject, seul `CATEGORY_TEXT` est configuré. `CATEGORY_WEB` n’y figure dans aucun de ces cas. La fonction `get_reports()` filtre les rapports selon cette liste et `run_report()` refuse les catégories non prises en charge avec HTTP 404.
- Le dictionnaire `MIME_TYPES` comprend `.html`, mais pas `.zip`. La génération de rapports vérifie ce dictionnaire avant de lancer le rapport ; l’API 3.22.3 ne peut donc pas retourner une archive ZIP par ce point d’entrée.
- L’API crée un nom unique sous `REPORT_DIR` et le transmet au rapport dans l’option standard `of`. Le module actuel écrit à l’emplacement reçu dans son option `destination` ; il n’utilise pas cette cible fournie par le serveur.
- `generate_report` est bien une tâche asynchrone, mais sa fonction n’est pas liée à l’instance Celery et ne transmet aucun callback de progression à `run_report`. Elle retourne les métadonnées du fichier une fois terminé. D’autres tâches de l’API savent publier un état `PROGRESS` ; cela ne signifie pas que cette progression est actuellement disponible pour les rapports.

Ces écarts empêchent l’intégration actuelle de satisfaire T-01 et AC-22 dans l’API 3.22.3. Le fait que Gramps Web réutilise le moteur de rapports Desktop ne suffit pas : son API serveur filtre les catégories et les types de fichiers qu’elle expose.

## Environnement et portée

Il s’agit d’un audit des sources officielles versionnées, pas d’une recette Gramps Web en exécution. Le Mac dispose du client Docker, mais pas de démon Docker, Docker Compose, Docker Desktop, Colima ou Podman ; aucune instance Web n’a été lancée.

Le module ne doit pas être annoncé compatible Web dans cet état. La suite nécessite une extension prise en charge du contrat Gramps Web pour les rapports `CATEGORY_WEB`, les archives ZIP et les sorties placées sous `REPORT_DIR`, ou une adaptation serveur officiellement maintenue qui offre les mêmes garanties. Il faudra ensuite tester sur une version d’API épinglée la découverte du rapport, les options, le consentement, les téléchargements PDF/ZIP et l’état des tâches. La progression détaillée doit faire partie de la discussion du contrat : elle n’est pas fournie actuellement par `generate_report`.
