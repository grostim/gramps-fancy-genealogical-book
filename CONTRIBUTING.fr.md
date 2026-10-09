# Contribuer

Ce projet est un module complémentaire expérimental pour Gramps 6. Les changements doivent préserver la séparation entre intégration Gramps, données normalisées, parcours généalogique, modèle éditorial et rendus. Voir le [guide d’architecture en français](docs/architecture.fr.md) et le [guide anglais](CONTRIBUTING.md).

## Avant d’ouvrir une pull request

- Partir de la branche `main` à jour et créer une branche dédiée à un changement ciblé.
- Aligner le changement sur la spécification ; si un critère d’acceptation change, mettre à jour `docs/requirements.fr.md` et `docs/action-plan.fr.md`.
- Utiliser Conventional Commits, par exemple `feat(html): add family navigation` ou `docs: clarify installation`.
- Décrire le comportement visible, les vérifications effectuées et les limites dans la pull request.

## Protéger les données familiales

Utiliser les données fictives de `tests/fixtures/reference-family.ged` et des enregistrements synthétiques dans les tests. Ne jamais committer un arbre généalogique réel, des noms, dates, lieux, photographies, scans, JSON exporté ou journaux contenant des données personnelles. Retirer les données personnelles des signalements et exemples de pull request.

## Environnement de développement

Le paquet prend en charge Python 3.10 et versions ultérieures. Depuis la racine du dépôt :

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev,media]'
.venv/bin/ruff check .
.venv/bin/pytest -q
.venv/bin/python build_addon.py
```

La construction du module complémentaire nécessite aussi `msgfmt` de GNU gettext dans le `PATH` lorsqu’elle compile le catalogue français du rapport. Installer le paquet système `gettext` si la commande manque. L’extra `media` installe Pillow et pypdfium2 pour convertir les médias ; la suite de tests importe ces dépendances.

Pour le script d’intégration avec Gramps réel, utiliser Python 3.12 ou ultérieur et Gramps 6.0 :

```sh
.venv/bin/python scripts/verify_gramps.py --gramps /chemin/vers/gramps
```

Le script installe l’archive construite dans un profil Gramps temporaire et importe le GEDCOM fictif de référence. Il ne nécessite pas de base personnelle. La CI couvre Python 3.10 à 3.13 et utilise Gramps 6.0.7 et 6.0.8 pour l’intégration ; un lancement local avec une autre version corrective de Gramps fournit une indication, mais ne remplace aucune de ces cibles CI.

Si Gramps est installé dans l’environnement Python courant, lancer aussi le contrôle de son installateur d’archives dans un processus neuf :

```sh
python scripts/verify_addon_installer.py --addon-archive gramps60/download/GrampsFancyBook.addon.tgz
```

Il exerce le backend du gestionnaire de greffons dans un profil temporaire : installation, réinstallation de la même version et refus d’une cible incompatible. Les fichiers installés doivent correspondre exactement à l’archive. La CI lance ce contrôle sous Gramps 6.0.7 et 6.0.8 et conserve son relevé JSON avec l’archive. Ce contrôle n’exerce ni la manipulation graphique ni une mise à niveau interversion.

## Traduction et fichiers générés

Ajouter ou modifier les libellés du rapport dans `gramps60/GrampsFancyBook/po/fr-local.po` et synchroniser `po/template.pot` avec les chaînes source. Les messages d’échec de compilation PDF sont sélectionnés dynamiquement dans `GrampsFancyBook.py` : les conserver explicitement dans les deux catalogues. La construction compile le catalogue français et inclut `addon.mo` dans l’archive. Ne pas committer les fichiers `.mo` générés ni `gramps60/download/GrampsFancyBook.addon.tgz` : le catalogue est créé temporairement par la construction et l’archive est un artefact généré.

## Liste de contrôle de la pull request

- Expliquer le comportement attendu et indiquer l’exigence ou l’étape du plan concernée.
- Lister les vérifications réellement exécutées et leurs résultats ; ne pas présenter comme réussi un contrôle non effectué.
- N’utiliser que des exemples fictifs qui préservent la vie privée.
- Mettre à jour la documentation destinée aux utilisateurs ou aux développeurs lorsque changent le comportement, l’installation, les environnements pris en charge ou les limites connues.
- Indiquer les vérifications manuelles Gramps Desktop ou Web qui restent à effectuer.
