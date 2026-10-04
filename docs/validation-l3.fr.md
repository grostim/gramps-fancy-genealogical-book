# Validation L3 — extraction et normalisation

Mise à jour du 27 septembre 2026. Cette validation porte sur le premier instantané JSON v0.2 ; elle ne déclare pas L3 entièrement terminé.

## Couverture

- `GrampsDatabaseAdapter` extrait la famille de référence, ses membres et les unions/familles parentales directement référencées par ces personnes.
- Les relations de filiation conservent le type père/mère, l’ordre d’origine, les citations, les notes et le drapeau privé portés par la référence enfant.
- Les événements individuels et familiaux conservent leurs associations et rôles. Les dates gardent texte saisi, composants, qualificatifs, bornes et sérialisation Gramps ; les lieux sont des objets reliés par handle.
- Le modèle inclut noms alternatifs, attributs, associations et adresses des personnes, médias et régions de recadrage, notes, citations, sources, dépôts, URL et étiquettes.
- Le texte d’une note est fourni seulement si elle porte `BOOK_PUBLICATION`. Une note privée portant cette étiquette demeure disponible, conformément à la spécification ; les notes de travail sont référencées sans contenu.
- `BOOK_PROFILE = YES`, `BOOK_EXCLUDE` et `BOOK_FEATURED` sont lus depuis leurs portées Gramps. Une valeur `BOOK_PROFILE` invalide et les références manquantes produisent des diagnostics structurés.
- Les drapeaux privés restent attachés aux objets et relations. `privacy.contains_private_data` indique leur présence dans l’instantané ; aucune donnée accessible n’est filtrée.

## Contrôles exécutés

```sh
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
.venv/bin/python build_addon.py
.venv/bin/python scripts/verify_gramps.py --gramps /Applications/Gramps.app/Contents/MacOS/Gramps
```

Résultats : 12 tests unitaires réussis, Ruff réussi, archive construite, puis intégration réussie avec Gramps macOS 6.0.8 dans un profil temporaire. La fixture GEDCOM fictive exerce naissances, profession, mariage, date approximative, lieux, trois citations, source, dépôt et référence de média. Le script contrôle aussi les erreurs de famille incomplète et de destination, le remplacement explicite et la protection des fichiers existants.

Les tests unitaires couvrent en plus les rectangles de média, plusieurs étiquettes, notes publiables et non publiables, données privées, relations de personnes, adresses, filiations typées (y compris une relation explicitement `None`), références facultatives manquantes et absence de lectures répétées des objets référencés.

## Limites restantes

- L’instantané n’est pas encore le graphe généalogique complet : la traversée ascendante/descendante et les règles de profondeur appartiennent à L4.
- La fixture XML native Gramps porte maintenant le tag `BOOK_PUBLICATION` et des rectangles de région média fictifs. Les originaux, notes et photos sont entièrement synthétiques.
- La recette Gramps native vérifie désormais AC-11 : une note de travail sans étiquette, associée à la personne et à la famille centrales, conserve ses liens source mais son texte est absent du modèle éditorial, du HTML et du PDF. Elle vérifie aussi les six rôles de notes F0, leur association directe à la famille, le tag de publication et les diagnostics pour une note dupliquée, multirôle, non publiable ou vide. La saisie dans l’interface Gramps 6 reste ouverte.
- Les sorties PDF et HTML/ZIP sont réalisées dans L6–L7 avec des recettes partielles ; l’intégration Gramps Web et la vérification du consentement dans cette intégration restent à faire.
