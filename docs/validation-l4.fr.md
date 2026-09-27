# Avancement L4 — parcours généalogiques

Premier incrément préparé le 27 septembre 2026. L4 reste en cours ; cette note décrit le contrat implémenté, sans déclarer les scénarios d’acceptation entièrement qualifiés.

## Parcours disponibles

- La famille F0 doit comporter deux partenaires connus, qui deviennent P0 et P1 en génération 0.
- L’ascendance et la descendance ont chacune une limite indépendante. `unlimited` est la valeur par défaut ; une limite entière positive ou zéro peut être saisie.
- L’extraction Gramps charge récursivement les familles et personnes reliées dans ces deux directions, puis conserve les unions et la fratrie comme contexte. Elle n’ouvre pas l’ascendance du conjoint d’un descendant.
- Le moteur indépendant de Gramps produit les générations négatives et positives, les sections familiales, les rôles d’occurrence, les racines de branche et les chemins de filiation.
- F0 est une section unique au début de l’ascendance ; la descendance conserve les occurrences centrales comme renvois. Les enfants des autres unions des ancêtres figurent comme contexte, sans développement de leur descendance.
- Les relations enfant-parent explicitement « None » ne sont pas parcourues. Les familles monoparentales restent admises dans le graphe.
- Un chemin qui revisite une personne est conservé comme occurrence visible, signalé par un diagnostic et arrêté avant de développer la boucle.
- L’éligibilité de fiche applique `BOOK_PROFILE = YES` ou un événement individuel/familial substantiel autre que naissance et décès. Une seule occurrence reçoit l’ancre principale de fiche ; les autres conservent leur renvoi.
- L’ordre des générations est déterministe ; les dates de naissance complètes et exactes sont ordonnées chronologiquement, puis les dates absentes ou incertaines par identifiant stable.

## Limites avant la sortie de L4

- Les scénarios complexes AC-03 à AC-09 (autres unions, filiations multiples, implexes, collatéraux, événements familiaux et profondeur frontière) restent à qualifier sur un graphe fictif de référence.
- Les rendus HTML et LaTeX ne consomment pas encore le modèle `genealogy`; ils restent des démonstrations de contrat.
- Le modèle ne construit pas encore les fiches, chronologies, index ou positions éditoriales de L5.
- Les six notes éditoriales de F0 et leurs conventions Gramps 6 restent à valider séparément.

Le détail des tâches et critères de sortie figure dans le [plan d’action](action-plan.fr.md#l4--parcours-généalogiques-et-sélection) et dans les [exigences](requirements.fr.md).
