# Architecture

Le projet sépare six responsabilités :

1. **Intégration Gramps** — enregistrement du rapport, options, accès à la base et cycle d’exécution.
2. **Extraction et normalisation** — conversion en objets du domaine indépendants de Gramps.
3. **Moteur généalogique** — ascendances, descendances, générations, branches et déduplication.
4. **Modèle éditorial** — structure commune consommée par les rendus.
5. **Rendu LaTeX** — composition imprimable et compilation PDF.
6. **Rendu HTML** — site statique et distribution ZIP.

## Instantané d’extraction

L’adaptateur produit un instantané JSON v0.2 indépendant de Gramps. Il comprend la famille choisie, ses membres, leurs unions et familles parentales directement référencées, les rôles des événements, les champs de dates, lieux, adresses et associations de personnes, notes, citations, sources, références de dépôts, médias, étiquettes et attributs. Les caches indexés par handle évitent de relire un objet dans la même extraction ; les références facultatives manquantes donnent des diagnostics structurés.

Cet instantané ne constitue pas encore un graphe généalogique parcouru ni un livre éditorial. L’extraction ne suit qu’un niveau de familles depuis les membres de la famille centrale ; le lot L4 ajoutera les parcours d’ascendance et de descendance. Les rendus HTML et LaTeX restent des démonstrations.

Le texte des notes n’est exposé que si elles portent l’étiquette Gramps `BOOK_PUBLICATION`. Les drapeaux privés sont préservés sans exclure les données accessibles à la base fournie. Le JSON indique si l’instantané contient des objets ou associations privés ; l’avertissement requis avant la publication d’un livre complet reste à mettre en place.

## Accès aux données

L’adaptateur n’utilise que les accesseurs publics de la base Gramps. Il ne modifie pas la base et ne contourne pas ses contrôles d’accès. Une donnée inaccessible est représentée par un diagnostic, tandis qu’un membre manquant de la famille choisie bloque l’extraction.

Les noms techniques et métadonnées restent en anglais. Les noms réservés incluent `BOOK_PUBLICATION`, `BOOK_PROFILE`, `BOOK_EXCLUDE` et `BOOK_FEATURED`.

Pour l’enregistrement et l’empaquetage de Gramps 6, le projet a consulté [`grostim/gramps-two-way-fan-chart`](https://github.com/grostim/gramps-two-way-fan-chart). Il sert de référence, son moteur généalogique et ses rendus ne sont pas copiés.
