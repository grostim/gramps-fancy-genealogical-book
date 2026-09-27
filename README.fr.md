# Gramps Fancy Genealogical Book

[English](README.md) · [Plan d’action](docs/action-plan.fr.md) · [Architecture FR](docs/architecture.fr.md) · [Architecture EN](docs/architecture.md) · [Prototypes L2](prototypes/README.md)

Module complémentaire expérimental pour Gramps 6, destiné à produire un livre généalogique familial. Le jalon actuel sélectionne une famille, extrait son graphe d’ascendance et de descendance selon les profondeurs choisies, puis exporte un modèle JSON commun. Les rendus éditoriaux LaTeX/PDF et HTML viendront ensuite.

## Fonctionnement actuel

- Sélecteur de famille Gramps et destination JSON explicite.
- Modèle JSON v0.3 avec occurrences par branche et génération, unions familiales, chemins de filiation et éligibilité des fiches.
- Extraction des ascendants et descendants en profondeur illimitée par défaut, ou limitée séparément avec un entier ≥ 0.
- Dates structurées affichées selon le formateur de Gramps, avec sérialisation brute et filiations typées préservées.
- Conservation des handles, identifiants Gramps, ordre d’origine, régions de recadrage et indicateurs de confidentialité.
- Texte des notes exporté uniquement si elles portent l’étiquette Gramps `BOOK_PUBLICATION`; les notes de travail restent référencées sans leur contenu.
- JSON Unicode, diagnostic des références indisponibles et publication atomique du fichier.
- Conservation des fichiers existants, sauf activation de **Replace an existing file**.
- Archive reproductible, tests unitaires et contrôle d’intégration avec Gramps réel.

Le parcours suit les filiations parent–enfant explicitement enregistrées. Les unions, partenaires et fratries sont ajoutés comme contexte sans étendre automatiquement leur propre lignée. Le résultat reste un modèle de données : les fonctions HTML et LaTeX sont encore des démonstrations de contrat. Voir le [suivi L3](docs/validation-l3.fr.md), le [démarrage L4](docs/validation-l4.fr.md) et le [suivi des exigences](docs/requirements.fr.md).

## Construction et installation

```sh
python3 build_addon.py
```

Extraire `gramps60/download/GrampsFancyBook.addon.tgz` dans le dossier des extensions utilisateur de Gramps 6, en conservant le répertoire `GrampsFancyBook/`, puis redémarrer Gramps. Emplacements habituels :

- macOS : `~/Library/Application Support/gramps/gramps60/plugins/`
- Linux : `${XDG_DATA_HOME:-$HOME/.local/share}/gramps/gramps60/plugins/`
- Profil isolé : `$GRAMPSHOME/gramps/gramps60/plugins/`

Le rapport est enregistré dans **Rapports → Pages Web** (le libellé dépend de la traduction de Gramps). Cette catégorie permet au plugin d’écrire ses propres fichiers sans utiliser le moteur PDF/ODT intégré. Ce jalon produit uniquement du JSON. Choisir une famille, une destination `.json` et laisser le remplacement désactivé sauf besoin explicite. Le répertoire de destination doit déjà exister.

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
