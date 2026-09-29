# Avancement L4 — parcours généalogiques

Compte rendu actualisé le 28 septembre 2026. L4 reste en cours ; les scénarios AC-01 et AC-03 à AC-09 sont exercés sur le modèle et sur le contrat textuel du rendu LaTeX. La pagination visuelle du PDF reste à valider en L6.

## Parcours disponibles

- La famille F0 doit comporter deux partenaires connus, qui deviennent P0 et P1 en génération 0.
- L’ascendance et la descendance ont chacune une limite indépendante. `unlimited` est la valeur par défaut ; une limite entière positive ou zéro peut être saisie.
- L’extraction Gramps charge récursivement les familles et personnes reliées dans ces deux directions, puis conserve les unions et la fratrie comme contexte. Elle n’ouvre pas l’ascendance du conjoint d’un descendant.
- Le moteur indépendant de Gramps produit les générations négatives et positives, les sections familiales, les rôles d’occurrence, les racines de branche et les chemins de filiation.
- F0 est une section unique au début de l’ascendance ; la descendance conserve les occurrences centrales comme renvois. Les enfants des autres unions des ancêtres figurent comme contexte, sans développement de leur descendance.
- Les relations enfant-parent explicitement « None » ne sont pas parcourues. Les familles monoparentales restent admises dans le graphe.
- Un chemin qui revisite une personne est conservé comme occurrence visible, signalé par un diagnostic et arrêté avant de développer la boucle.
- L’éligibilité de fiche applique `BOOK_PROFILE = YES` ou un événement individuel/familial substantiel autre que naissance et décès.
- Chaque occurrence renseigne `primary_occurrence_id` pour renvoyer à la première apparition de la personne, même sans fiche complète. Pour une personne éligible, `profile_anchor` et `is_primary_profile` désignent toujours sa fiche unique et son occurrence principale.
- L’ordre des générations est déterministe ; les dates de naissance complètes et exactes sont ordonnées chronologiquement, puis les dates absentes ou incertaines par identifiant stable.
- Les sections familiales suivent d’abord l’ordre des générations et des occurrences de branche, puis l’ordre source des unions dans les listes Gramps du partenaire ou de l’enfant concerné. L’identifiant familial ne sert que de départage déterministe.
- Chaque section familiale a un identifiant stable, référence les occurrences de ses partenaires et enfants dans le périmètre, et expose les liens parent-enfant avec la valeur du type de filiation normalisée depuis Gramps pour chaque parent, lorsqu’elle est disponible. Chaque occurrence conserve les identifiants de ses sections ; génération, branche, chemin et ancre de fiche fournissent les données du repère.

## Limites avant la sortie de L4

- `tests/test_genealogy_acceptance.py` qualifie AC-01 et AC-03 à AC-09 sur des graphes fictifs et vérifie aussi leur traduction en sorties LaTeX : couple central en tête de l’ascendance, renvois depuis la descendance et contexte des autres unions, types de filiation, fiche unique et renvois, collatéraux, événements familiaux, familles monoparentales et profondeur frontière.
- Le rendu LaTeX consomme le modèle `genealogy` et dispose maintenant d’assertions de contrat pour ces scénarios. Le rendu HTML complet reste planifié en L7 ; la pagination, les renvois multipasses et l’apparence du PDF restent à contrôler visuellement en L6.
- Le modèle éditorial fournit déjà profils, notices familiales, index et cibles de navigation au rendu LaTeX. La validation porte ici sur leur structure textuelle, pas sur la composition paginée finale.
- Les six notes éditoriales de F0 et leurs conventions Gramps 6 restent à valider séparément.

Le détail des tâches et critères de sortie figure dans le [plan d’action](action-plan.fr.md#l4--parcours-généalogiques-et-sélection) et dans les [exigences](requirements.fr.md).

## Essai PDF en CLI — 29 septembre 2026

Gramps 6.0.8 sur macOS a produit un PDF A4 de 9 pages depuis la base native fictive avec LuaHBTeX 1.24.0. La fixture comprenait un dérivé de portrait, visible sur la couverture et dans la fiche de la personne. Cet essai confirme l’intégration Gramps–PDF sur un livre synthétique réduit ; il ne qualifie ni la pagination d’un livre long, ni tous les cas de médias/URL, ni l’accessibilité ou l’acceptation visuelle finale, qui restent à traiter en L6.
