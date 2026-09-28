# Gramps Fancy Genealogical Book

[English](README.md) · [Plan d’action](docs/action-plan.fr.md) · [Architecture FR](docs/architecture.fr.md) · [Architecture EN](docs/architecture.md) · [Contribution](CONTRIBUTING.fr.md) · [Dépannage](docs/troubleshooting.fr.md) · [Prototypes L2](prototypes/README.md) · [Validation des médias](docs/validation-media.fr.md)

Module complémentaire expérimental pour Gramps 6, destiné à produire un livre généalogique familial. Le rapport Gramps génère désormais par défaut un livre HTML autonome en archive ZIP, tout en conservant un mode d’export JSON de diagnostic et un premier rendu LaTeX. Les améliorations de navigation clavier et de mise en page sur petit écran sont intégrées ; leur revue manuelle d’accessibilité et la validation visuelle du PDF restent à faire.

## Fonctionnement actuel

- Sélecteur de famille Gramps, archive HTML ZIP par défaut et export JSON de diagnostic.
- Modèle JSON v0.8 avec occurrences généalogiques, liens typés et cibles de renvoi, accompagné d’une structure éditoriale ordonnée. Un index alphabétique renvoie à chaque fiche ou à sa première occurrence. Les fiches de personnes éligibles et une notice par famille du périmètre référencent les notes publiables, portraits et légendes, événements, médias et sections familiales.
- Extraction des ascendants et descendants en profondeur illimitée par défaut, ou limitée séparément avec un entier ≥ 0.
- Dates structurées affichées selon le formateur de Gramps, avec sérialisation brute ; chaque lien parent-enfant expose le type de filiation enregistré.
- Conservation des handles, identifiants Gramps, ordre d’origine, régions de recadrage et indicateurs de confidentialité.
- Les notes publiables sont rendues en HTML et en LaTeX depuis l’AST Mistune ; le HTML brut reste du texte littéral, et les styles sémantiques Gramps priment sur la syntaxe Markdown d’une même note. Voir la [règle de normalisation documentée](docs/decisions/003-note-markup.md).
- JSON Unicode, diagnostics structurés de conversion média, rapport séparé de cohérence des faits et remplacement coordonné du modèle, du rapport et des médias.
- Conservation des fichiers existants, sauf activation de **Replace an existing file**.
- Premier rendu LaTeX avec couverture A4 automatique, titres et textes éditoriaux F0, noms du couple et médaillons circulaires pour ses portraits disponibles, puis grandes parties généalogiques, fiches, notices familiales, appels de citations numérotés, renvois de pages cliquables et index des personnes. La validation visuelle du PDF reste à faire.
- Archive reproductible, tests unitaires et contrôle d’intégration avec Gramps réel.

## Notes éditoriales de la famille F0

Pour personnaliser les préliminaires, créez une note Gramps par rôle et associez-lui l’étiquette native `BOOK_PUBLICATION` ainsi qu’une seule étiquette de rôle : `BOOK_TITLE`, `BOOK_SUBTITLE`, `BOOK_INTRODUCTION`, `BOOK_DEDICATION`, `BOOK_AUTHOR` ou `BOOK_PUBLICATION_DATE`. Rattachez chaque note directement à la famille sélectionnée. Les doublons sont départagés selon l’ordre des notes dans Gramps ; une note portant plusieurs rôles est ignorée avec un diagnostic. Le parcours dans l’interface Gramps 6 et la compilation visuelle du PDF restent à valider.

Le parcours suit les filiations parent–enfant explicitement enregistrées. Les unions, partenaires et fratries sont ajoutés comme contexte sans étendre automatiquement leur propre lignée. Le rendu LaTeX reste expérimental : typographie définitive, convergence PDF et recette visuelle restent à réaliser. Voir le [suivi L3](docs/validation-l3.fr.md), le [démarrage L4](docs/validation-l4.fr.md), la [règle de rendu des notes](docs/decisions/003-note-markup.md) et le [suivi des exigences](docs/requirements.fr.md).

## Construction et installation

La construction compile le catalogue français du rapport depuis `gramps60/GrampsFancyBook/po/fr-local.po` et l’inclut dans l’archive sous forme de `addon.mo`. GNU gettext (`msgfmt`) doit être disponible dans le `PATH` ; installez le paquet `gettext` si nécessaire (par exemple `brew install gettext` sur macOS).

```sh
python3 build_addon.py
```

Extraire `gramps60/download/GrampsFancyBook.addon.tgz` dans le dossier des extensions utilisateur de Gramps 6, en conservant le répertoire `GrampsFancyBook/`, puis redémarrer Gramps. Emplacements habituels :

- macOS : `~/Library/Application Support/gramps/gramps60/plugins/`
- Linux : `${XDG_DATA_HOME:-$HOME/.local/share}/gramps/gramps60/plugins/`
- Profil isolé : `$GRAMPSHOME/gramps/gramps60/plugins/`

Le rapport est enregistré dans **Rapports → Pages Web** (le libellé dépend de la traduction de Gramps). Cette catégorie permet au plugin d’écrire ses propres fichiers sans utiliser le moteur PDF/ODT intégré. La sortie par défaut du rapport est un livre HTML autonome en `.zip`, à extraire pour le consulter localement. Le mode JSON reste disponible pour le diagnostic et produit un modèle `.json`, un rapport de contrôle séparé `<nom>_consistency.json` et, s’il y a des images convertibles, un dossier voisin `<nom>_media/`. Le rapport de contrôle compare uniquement les événements portant le même attribut natif Gramps `BOOK_FACT_ID` ; il signale les plages de dates disjointes comme contradictions et les références de lieux différentes comme divergences à examiner. Pour un instantané de diagnostic, choisir le format JSON et une destination `.json` ; **Replace an existing file** remplace aussi le rapport et les médias dérivés. Le répertoire de destination doit déjà exister.

Les rendus HTML et LaTeX des notes requièrent Mistune 3.x. Installez-la dans l’environnement Python utilisé par Gramps Desktop ou le service Gramps Web : `python -m pip install 'mistune>=3,<4'`. L’extension déclare `mistune` comme module requis ; l’installation du paquet Python depuis ce dépôt installe également la dépendance déclarée dans `pyproject.toml`.

Les convertisseurs d’images et de PDF restent facultatifs afin que l’export JSON fonctionne aussi sans eux. Pour le développement, installez le projet et ses dépendances avec `python -m pip install -e '.[dev,media]'`. Dans un environnement Gramps Desktop où pip est pris en charge, installez `Pillow` et `pypdfium2` avec le même interpréteur Python que celui qui lance Gramps, puis redémarrez Gramps : `python -m pip install 'Pillow>=10' 'pypdfium2>=4'`. Une dépendance absente produit un diagnostic et les dérivés concernés sont omis. La CI qualifie actuellement Ubuntu 24.04, Python 3.12 et Gramps 6.0.8 ; voir le [compte rendu de validation média](docs/validation-media.fr.md). L’exécution dans Gramps Web reste non qualifiée : les paquets devraient être installés dans l’environnement serveur, et aucune instance de test n’a été validée.

Les libellés du rapport Gramps ont un catalogue français dans `gramps60/GrampsFancyBook/po/fr-local.po` ; la construction le compile et l’inclut dans l’archive. Les nouvelles chaînes du plugin doivent aussi être ajoutées au catalogue.

## Exemple en ligne de commande

```sh
gramps -i tests/fixtures/reference-family.ged -a report \
  -p "name=gramps_fancy_genealogical_book,reference_family=F0001,max_ancestor_depth=unlimited,max_descendant_depth=unlimited,output_format=json_snapshot,destination=/chemin/absolu/famille.json"
```

Ajouter `overwrite=True` aux options pour autoriser le remplacement. Le GEDCOM fourni ne contient que des personnes fictives. Le script ci-dessous automatise le test dans un profil Gramps temporaire et installe uniquement l’archive construite. Sur macOS, l’exécutable est `/Applications/Gramps.app/Contents/MacOS/Gramps`.

## Développement et validation

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/ruff check .
.venv/bin/pytest -q
.venv/bin/python build_addon.py
.venv/bin/python scripts/verify_gramps.py --gramps /chemin/vers/gramps
```

Les tests unitaires ne nécessitent pas Gramps. Le script d’intégration nécessite Python 3.12+ et Gramps 6.0 ; il vérifie les fichiers et diagnostics car Gramps peut renvoyer un code de sortie zéro malgré l’échec d’un rapport. La CI cible Python 3.10 à 3.13 pour le domaine et Gramps 6.0.8 pour l’intégration.

Le [compte rendu L1](docs/validation-l1.fr.md), le [suivi L3](docs/validation-l3.fr.md) et la [validation des médias](docs/validation-media.fr.md) distinguent les contrôles effectués et les limites restantes.

La famille de référence doit avoir deux partenaires connus (AC-02). Exigences intégrales : [spécification originale](docs/reference/Gramps_Fancy_Genealogical_Book_Specification_v1.1.md), avec sa [provenance](docs/reference/README.md).
