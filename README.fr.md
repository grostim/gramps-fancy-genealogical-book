# Gramps Fancy Genealogical Book

[English](README.md) · [Plan d’action](docs/action-plan.fr.md) · [Architecture FR](docs/architecture.fr.md) · [Architecture EN](docs/architecture.md) · [Prototypes L2](prototypes/README.md)

Module complémentaire expérimental pour Gramps 6, destiné à produire un livre généalogique familial. Le jalon actuel exporte un modèle JSON commun et un premier rendu LaTeX comprenant les parties généalogiques, les fiches, les notices familiales, les citations, les renvois de pages et l’index. La mise en page définitive et la compilation multipasse du PDF restent à vérifier visuellement ; le rendu HTML est prévu dans un jalon ultérieur.

## Fonctionnement actuel

- Sélecteur de famille Gramps et destination JSON explicite.
- Modèle JSON v0.7 avec occurrences généalogiques, liens typés et cibles de renvoi, accompagné d’une structure éditoriale ordonnée. Un index alphabétique renvoie à chaque fiche ou à sa première occurrence. Les fiches de personnes éligibles et une notice par famille du périmètre référencent les notes publiables, portraits et légendes, événements, médias et sections familiales.
- Extraction des ascendants et descendants en profondeur illimitée par défaut, ou limitée séparément avec un entier ≥ 0.
- Dates structurées affichées selon le formateur de Gramps, avec sérialisation brute ; chaque lien parent-enfant expose le type de filiation enregistré.
- Conservation des handles, identifiants Gramps, ordre d’origine, régions de recadrage et indicateurs de confidentialité.
- Les notes publiables sont rendues en LaTeX depuis l’AST Mistune ; le HTML brut reste du texte littéral, et les styles sémantiques Gramps priment sur la syntaxe Markdown d’une même note. Voir la [règle de normalisation documentée](docs/decisions/003-note-markup.md).
- JSON Unicode, diagnostics structurés de conversion média et remplacement coordonné du modèle avec son dossier de PNG.
- Conservation des fichiers existants, sauf activation de **Replace an existing file**.
- Premier rendu LaTeX avec couverture A4 automatique, noms du couple et médaillons circulaires pour ses portraits disponibles, puis grandes parties généalogiques, fiches, notices familiales, appels de citations numérotés, renvois de pages cliquables et index des personnes. Les notes éditoriales F0 et la validation visuelle du PDF restent à faire.
- Archive reproductible, tests unitaires et contrôle d’intégration avec Gramps réel.

Le parcours suit les filiations parent–enfant explicitement enregistrées. Les unions, partenaires et fratries sont ajoutés comme contexte sans étendre automatiquement leur propre lignée. Le rendu LaTeX reste expérimental : typographie définitive, convergence PDF et recette visuelle restent à réaliser. Voir le [suivi L3](docs/validation-l3.fr.md), le [démarrage L4](docs/validation-l4.fr.md), la [règle de rendu des notes](docs/decisions/003-note-markup.md) et le [suivi des exigences](docs/requirements.fr.md).

## Construction et installation

```sh
python3 build_addon.py
```

Extraire `gramps60/download/GrampsFancyBook.addon.tgz` dans le dossier des extensions utilisateur de Gramps 6, en conservant le répertoire `GrampsFancyBook/`, puis redémarrer Gramps. Emplacements habituels :

- macOS : `~/Library/Application Support/gramps/gramps60/plugins/`
- Linux : `${XDG_DATA_HOME:-$HOME/.local/share}/gramps/gramps60/plugins/`
- Profil isolé : `$GRAMPSHOME/gramps/gramps60/plugins/`

Le rapport est enregistré dans **Rapports → Pages Web** (le libellé dépend de la traduction de Gramps). Cette catégorie permet au plugin d’écrire ses propres fichiers sans utiliser le moteur PDF/ODT intégré. Ce jalon produit un modèle `.json` et, s’il y a des images convertibles, un dossier voisin nommé `<nom>_media/`. Le JSON référence les PNG dérivés et signale les médias qui n’ont pas pu être préparés. Choisir une famille et une destination `.json` ; **Replace an existing file** remplace aussi les dérivés voisins. Le répertoire de destination doit déjà exister.

Le rendu LaTeX des notes requiert Mistune 3.x. Installez-la dans l’environnement Python utilisé par Gramps Desktop ou le service Gramps Web : `python -m pip install 'mistune>=3,<4'`. L’extension déclare `mistune` comme module requis ; l’installation du paquet Python depuis ce dépôt installe également la dépendance déclarée dans `pyproject.toml`.

Les convertisseurs d’images et de PDF sont facultatifs. Pour le développement, les installer dans l’environnement Python utilisé par Gramps avec `python -m pip install -e '.[media]'`. Tant que leur installation dans les paquets Gramps Desktop/Web n’est pas automatisée, une dépendance absente produit un diagnostic et laisse le modèle JSON exportable.

L’interface utilise des chaînes traduisibles ; les traductions françaises propres au plugin restent à compléter.

## Exemple en ligne de commande

```sh
gramps -i tests/fixtures/reference-family.ged -a report \
  -p "name=gramps_fancy_genealogical_book,reference_family=F0001,max_ancestor_depth=unlimited,max_descendant_depth=unlimited,destination=/chemin/absolu/famille.json"
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

Le [compte rendu L1](docs/validation-l1.fr.md) et le [suivi L3](docs/validation-l3.fr.md) distinguent les contrôles effectués et les limites restantes.

La famille de référence doit avoir deux partenaires connus (AC-02). Exigences intégrales : [spécification originale](docs/reference/Gramps_Fancy_Genealogical_Book_Specification_v1.1.md), avec sa [provenance](docs/reference/README.md).
