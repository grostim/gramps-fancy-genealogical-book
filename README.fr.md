# Gramps Fancy Genealogical Book

Plugin modulaire pour Gramps 6 destiné à sélectionner une famille de référence et à produire un modèle intermédiaire commun, qui sera ensuite rendu en LaTeX/PDF et en HTML.

Ce dépôt part de la spécification fonctionnelle et technique v1.1 et des maquettes du livret familial définies dans la discussion de conception. Le premier jalon fournit un rapport Gramps 6 qui sélectionne une famille de référence et exporte un modèle intermédiaire JSON testable.

## Jalon actuel

- modèle métier indépendant de Gramps ;
- enregistrement d’un rapport Gramps 6 et option de sélection de la famille ;
- frontière d’adaptation pour l’accès aux données Gramps ;
- sélection et normalisation déterministes ;
- modèle éditorial sérialisable en JSON ;
- rendus HTML et LaTeX partageant le même modèle ;
- point d’entrée de packaging du module complémentaire ;
- documentation bilingue et intégration continue.

La composition complète du livre reste hors périmètre de ce premier jalon.

## Développement

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
```

Les tests unitaires du domaine ne nécessitent pas l’installation de Gramps. Le rapport Gramps se trouve dans `gramps60/GrampsFancyBook` et utilise `GrampsDatabaseAdapter` pour extraire la famille.

Créer une archive installable manuellement :

```bash
python build_addon.py
```

Le fichier `gramps60/download/GrampsFancyBook.addon.tgz` peut être installé depuis le gestionnaire de modules complémentaires de Gramps. La première sortie du rapport est un modèle JSON ; la composition du livre PDF/HTML viendra plus tard.

Voir [docs/architecture.md](docs/architecture.md) et [docs/specification-v1.1.md](docs/specification-v1.1.md).
