# Décision 006 : rapport séparé de cohérence des événements

## Contexte

La spécification demande un rapport de contrôle hors du livre, limité aux contradictions de dates et de lieux d'un même fait. La décision 005 définit l'attribut Gramps `BOOK_FACT_ID` comme seule identité explicite entre plusieurs objets Event.

## Décision

Le plugin écrit un fichier compagnon `<nom>_consistency.json` à côté du modèle `.json`. Les deux fichiers et le dossier média sont installés ou remplacés comme un seul export ; une erreur pendant l'installation restaure les sorties précédentes. Le rapport ne modifie ni les objets Event, ni le modèle du livre, ni ses diagnostics éditoriaux.

Seuls les événements ayant un `BOOK_FACT_ID` non vide sont groupés ; la valeur est comparée après retrait des espaces périphériques, de façon sensible à la casse. Les groupes d'au moins deux événements sont comparés. Les événements avec plusieurs valeurs distinctes sont exclus et signalés comme diagnostics techniques. Aucun rapprochement par type, description, date, lieu, participant ou citation n'est fait.

Une contradiction de date est émise seulement si deux plages de dates Gramps normalisées ne se chevauchent pas. L'adaptateur fournit `Date.get_start_stop_range()`, qui renvoie les bornes minimale et maximale en calendrier grégorien ; les dates textuelles, absentes ou non analysables sont ignorées pour la comparaison, mais leur affichage reste dans le rapport. La plage prend ainsi en compte les dates partielles, composées et modifiées telles que Gramps les interprète.

Des références de lieux distinctes ne suffisent pas à prouver une contradiction géographique : elles sont rapportées avec la classification `review_required`, afin d'attirer l'attention sans affirmer que deux identifiants représentent des lieux incompatibles. Une date ou un lieu divergent n'ajoute jamais d'avertissement dans le livre. [L'API Gramps pour les plages de dates](https://github.com/gramps-project/gramps/blob/maintenance/gramps60/gramps/gen/lib/date.py) décrit leur normalisation et leur usage pour comparer des chevauchements.

## Sortie

Le JSON de contrôle contient une version de schéma, la famille de référence, les groupes comparés, les événements et leurs valeurs affichées, les conclusions et les diagnostics. Un rapport sans conclusion est quand même écrit ; il indique que le contrôle a été exécuté et quels groupes ont été comparés.

## Validation restante

La fixture native Gramps doit encore vérifier la saisie et la lecture de `BOOK_FACT_ID`, les plages calendaires réelles et la gestion des divergences de lieux. Les divergences de lieux demandent une revue humaine tant qu'aucune identité canonique de lieu n'est déclarée dans Gramps.
