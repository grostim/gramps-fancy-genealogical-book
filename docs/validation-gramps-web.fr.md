# Compatibilité Gramps Web — audit statique — 29 septembre 2026

## Version et sources examinées

La dernière version publiée de l’API au moment de l’audit est Gramps Web API **3.22.3** ([publication officielle](https://github.com/gramps-project/gramps-web-api/releases/tag/v3.22.3)). Les fichiers examinés sont le [`const.py` de v3.22.3](https://github.com/gramps-project/gramps-web-api/blob/v3.22.3/gramps_webapi/const.py) et son [`api/report.py`](https://github.com/gramps-project/gramps-web-api/blob/v3.22.3/gramps_webapi/api/report.py). Le guide officiel indique que le serveur expose les rapports installés et transmet le fichier généré au navigateur ([guide Rapports](https://www.grampsweb.org/user-guide/reports/)).

## Incompatibilités relevées

- `REPORT_DEFAULTS` autorise `CATEGORY_TEXT` et `CATEGORY_DRAW`, ainsi que `CATEGORY_GRAPHVIZ` lorsque Graphviz est disponible ; `CATEGORY_WEB` n’y figure pas. La fonction `get_reports()` masque donc le rapport actuel, qui s’enregistre en `CATEGORY_WEB`. `run_report()` refuse également une catégorie absente de cette table avec HTTP 404.
- Le dictionnaire `MIME_TYPES` ne déclare pas `.zip`. Même si le rapport était listé, le point d’entrée de génération ne peut pas créer une réponse ZIP avec le contrat de type de sortie actuel.
- L’API choisit un chemin `of` sous `REPORT_DIR`, puis attend le fichier correspondant à l’extension et au type MIME retenus. Le module actuel écrit à l’emplacement fourni par son option `destination` ; il n’utilise pas ce chemin serveur.

Ces trois écarts empêchent l’intégration actuelle de satisfaire T-01 et AC-22 dans l’API 3.22.3. Le fait que Gramps Web réutilise le moteur de rapports Desktop ne suffit pas : son API serveur filtre les catégories et les types de fichiers qu’elle expose.

## Environnement et portée

Il s’agit d’un audit des sources officielles versionnées, pas d’une recette Gramps Web en exécution. Le Mac dispose du client Docker, mais pas de démon Docker, Docker Compose, Docker Desktop, Colima ou Podman ; aucune instance Web n’a été lancée. Le dépôt et les maquettes privées n’ont pas été modifiés pour cet audit.

Le module ne doit pas être annoncé compatible Web dans cet état. La suite nécessite une extension prise en charge du contrat Gramps Web pour les rapports `CATEGORY_WEB`, les archives ZIP et les sorties placées sous `REPORT_DIR`, ou une adaptation serveur officiellement maintenue qui offre les mêmes garanties. Il faudra ensuite tester sur une version d’API épinglée la découverte du rapport, les options, le consentement, les téléchargements PDF/ZIP et l’avancement/journal des tâches.
