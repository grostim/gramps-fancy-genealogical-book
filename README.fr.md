# Gramps Fancy Genealogical Book

[English](README.md) · [Plan d’action](docs/action-plan.fr.md) · [Architecture FR](docs/architecture.fr.md) · [Architecture EN](docs/architecture.md) · [Contribution](CONTRIBUTING.fr.md) · [Dépannage](docs/troubleshooting.fr.md) · [Prototypes L2](prototypes/README.md) · [Validation des médias](docs/validation-media.fr.md)

Module complémentaire expérimental pour Gramps 6, destiné à produire un livre généalogique familial. Le rapport Gramps génère par défaut un livre HTML autonome en archive ZIP, peut compiler un PDF avec LuaLaTeX et conserve un export JSON de diagnostic. Les PDF ont fait l’objet de revues ciblées sur des fixtures fictives avec des marges de 15 mm. Un essai graphique du paquet 0.9.0 sous Gramps Desktop 6.0.8-1 a produit un PDF de référence A4 balisé de neuf pages, toutes relues. Le rendu PDF reste expérimental ; les autres versions Desktop, la conformité PDF/UA et la revue au lecteur d’écran restent à qualifier ([compte rendu](docs/validation-addon-lifecycle.fr.md)).

## Fonctionnement actuel

- Sélecteur de famille Gramps, archive HTML ZIP par défaut et export JSON de diagnostic.
- Modèle JSON v0.8 avec occurrences généalogiques, liens typés et cibles de renvoi, accompagné d’une structure éditoriale ordonnée. Un index alphabétique renvoie à chaque fiche ou à sa première occurrence. Les fiches de personnes éligibles et une notice par famille du périmètre référencent les notes publiables, portraits et légendes, événements, médias et sections familiales.
- Extraction des ascendants et descendants en profondeur illimitée par défaut, ou limitée séparément avec un entier ≥ 0.
- Les titres et libellés générés suivent la langue configurée dans Gramps, avec choix manuel français/anglais et repli en anglais pour les langues non prises en charge. Les noms, notes, dates et textes des sources ne sont pas traduits.
- Dates structurées affichées selon le formateur de Gramps, avec sérialisation brute ; chaque lien parent-enfant expose le type de filiation enregistré.
- Conservation des handles, identifiants Gramps, ordre d’origine, régions de recadrage et indicateurs de confidentialité.
- Les notes publiables sont rendues en HTML et en LaTeX depuis l’AST Mistune ; le HTML brut reste du texte littéral, et les styles sémantiques Gramps priment sur la syntaxe Markdown d’une même note. Voir la [règle de normalisation documentée](docs/decisions/003-note-markup.md).
- JSON Unicode, diagnostics structurés de conversion média, rapport séparé de cohérence des faits et remplacement coordonné du modèle, du rapport et des médias.
- Conservation des fichiers existants, sauf activation de **Replace an existing file**.
- La sortie PDF utilise le rendu LaTeX préliminaire : couverture A4 automatique, titres et textes éditoriaux F0, noms du couple et médaillons circulaires pour ses portraits disponibles, puis parties généalogiques, fiches, notices familiales, notes de bas de page par appel de citation avec référence abrégée et lien vers la page définitive de l’annexe, et index des personnes. La validation visuelle et d’accessibilité reste à faire.
- Archive reproductible, tests unitaires et contrôle d’intégration avec Gramps réel.

## Notes éditoriales de la famille F0

Pour personnaliser la couverture et les préliminaires du livre :

1. Dans Gramps, créez ou réutilisez les étiquettes natives `BOOK_PUBLICATION` et les six étiquettes de rôle ci-dessous. Elles servent à identifier les notes ; ce ne sont pas des types de note intégrés à Gramps.
2. Créez une note par rôle, avec son texte, puis attribuez-lui `BOOK_PUBLICATION` et exactement une étiquette de rôle.
3. Dans l’éditeur de la famille choisie comme F0, onglet **Notes**, rattachez directement ces notes à cette famille. Des étiquettes identiques apposées à des notes d’une autre famille ne sont pas prises en compte.

| Étiquette | Contenu affiché |
| --- | --- |
| `BOOK_TITLE` | Titre de couverture ; remplace le titre par défaut |
| `BOOK_SUBTITLE` | Sous-titre de couverture ; les noms du couple restent affichés |
| `BOOK_AUTHOR` | Auteur sur la couverture |
| `BOOK_PUBLICATION_DATE` | Date de publication sur la couverture, saisie comme texte de la note |
| `BOOK_DEDICATION` | Dédicace dans les préliminaires |
| `BOOK_INTRODUCTION` | Introduction, après la dédicace |

Une note de rôle sans `BOOK_PUBLICATION`, sans texte ou portant plusieurs étiquettes de rôle est omise avec un diagnostic. Si plusieurs notes valides portent le même rôle, la première dans l’ordre des notes rattachées à F0 est retenue ; les suivantes sont signalées. Les notes de rôle ne sont pas répétées dans la notice familiale de F0. Les titres et le texte de publication ne sont pas déduits d’autres données généalogiques.

La recette d’intégration utilise désormais des notes Gramps natives pour les six rôles et couvre l’absence du tag de publication, les rôles ambigus, le texte vide et les doublons dans l’export CLI. La saisie dans l’interface Gramps 6 et la revue visuelle du résultat PDF restent à qualifier. Voir la [décision sur les notes F0](docs/decisions/004-f0-editorial-notes.md) et le [manuel Gramps 6 sur l’édition des notes et des familles](https://gramps-project.org/wiki/index.php/Gramps_6.0_Wiki_Manual).

Le parcours suit les filiations parent–enfant explicitement enregistrées. Les unions, partenaires et fratries sont ajoutés comme contexte sans étendre automatiquement leur propre lignée. Le rendu LaTeX reste expérimental : typographie définitive, convergence PDF et recette visuelle restent à réaliser. Voir le [suivi L3](docs/validation-l3.fr.md), le [démarrage L4](docs/validation-l4.fr.md), la [règle de rendu des notes](docs/decisions/003-note-markup.md) et le [suivi des exigences](docs/requirements.fr.md).

## Construction et installation

La construction compile le catalogue français du rapport depuis `gramps60/GrampsFancyBook/po/fr-local.po` et l’inclut dans l’archive sous forme de `addon.mo`. Elle vérifie aussi que la version de `pyproject.toml`, de l’enregistrement Gramps et des catalogues POT/PO est cohérente. GNU gettext (`msgfmt`) doit être disponible dans le `PATH` ; installez le paquet `gettext` si nécessaire (par exemple `brew install gettext` sur macOS).

```sh
python3 build_addon.py
```

Cette commande génère l’archive localement ; le fichier est ignoré par Git et n’est pas encore publié comme version GitHub.

Extraire `gramps60/download/GrampsFancyBook.addon.tgz` dans le dossier des extensions utilisateur de Gramps 6, en conservant le répertoire `GrampsFancyBook/`, puis redémarrer Gramps. Emplacements habituels :

- macOS : `~/Library/Application Support/gramps/gramps60/plugins/`
- Linux : `${XDG_DATA_HOME:-$HOME/.local/share}/gramps/gramps60/plugins/`
- Profil isolé : `$GRAMPSHOME/gramps/gramps60/plugins/`

Pour installer une mise à jour manuellement, quittez d’abord Gramps et remplacez le dossier `GrampsFancyBook/` complet par celui de la nouvelle archive ; ne fusionnez pas seulement les fichiers. Relancez Gramps après le remplacement. Pour retirer le module, quittez Gramps, supprimez uniquement ce dossier, puis relancez l’application. Les autres extensions et les arbres Gramps ne sont pas concernés. Le cycle dans un profil temporaire est consigné dans la [validation du paquet](docs/validation-addon-lifecycle.fr.md).

Le rapport est enregistré dans **Rapports → Pages Web** (le libellé dépend de la traduction de Gramps). Cette catégorie permet au plugin d’écrire ses propres fichiers sans utiliser le moteur PDF/ODT intégré. La sortie par défaut du rapport est un livre HTML autonome en `.zip`, à extraire pour le consulter localement. Choisir le format PDF (LuaLaTeX) ou laisser le mode automatique reconnaître une destination `.pdf` ; LuaLaTeX doit être dans le `PATH` du processus Gramps ou, sur macOS, installé au chemin standard `/Library/TeX/texbin/lualatex` de BasicTeX/MacTeX. Le mode JSON reste disponible pour le diagnostic et produit un modèle `.json`, un rapport de contrôle séparé `<nom>_consistency.json` et, s’il y a des images convertibles, un dossier voisin `<nom>_media/`. Le rapport de contrôle compare uniquement les événements portant le même attribut natif Gramps `BOOK_FACT_ID` ; il signale les plages de dates disjointes comme contradictions et les références de lieux différentes comme divergences à examiner. Pour l’obtenir, choisir **Instantané JSON et rapport de cohérence** et une destination `.json` ; **Remplacer un fichier existant** remplace aussi le rapport et les médias dérivés. Le répertoire de destination doit déjà exister. Voir [comment déclarer et lire un même fait](docs/consistency-report.fr.md).

Le PDF utilise normalement un plafond de trois minutes (deux minutes par passe). Pour un livre volumineux, cocher **Autoriser une compilation PDF prolongée (jusqu’à 30 minutes)** dans les options du rapport ; chaque passe est alors limitée à dix minutes. Ce réglage concerne seulement le PDF et ne garantit pas qu’un livre très long respecte le budget de performance visé.

Les rendus HTML et LaTeX des notes requièrent Mistune 3.x. Installez-la dans l’environnement Python utilisé par Gramps Desktop ou le service Gramps Web : `python -m pip install 'mistune>=3,<4'`. L’extension déclare `mistune` comme module requis ; l’installation du paquet Python depuis ce dépôt installe également la dépendance déclarée dans `pyproject.toml`.

Les convertisseurs d’images et de PDF restent facultatifs afin que l’export JSON fonctionne aussi sans eux. Pour le développement, installez le projet et ses dépendances avec `python -m pip install -e '.[dev,media]'`. Dans un environnement Gramps Desktop où pip est pris en charge, installez `Pillow` et `pypdfium2` avec le même interpréteur Python que celui qui lance Gramps, puis redémarrez Gramps : `python -m pip install 'Pillow>=10' 'pypdfium2>=4'`. Une dépendance absente produit un diagnostic et les dérivés concernés sont omis. La sortie PDF nécessite aussi LuaLaTeX (fourni par TeX Live) dans le `PATH` utilisé pour lancer Gramps, ou à l’emplacement standard `/Library/TeX/texbin/lualatex` sur macOS. Le rendu PDF reste expérimental : l’essai GUI 0.9.0 couvre une version de Gramps Desktop et une fixture de référence ; les scénarios plus larges, PDF/UA et le lecteur d’écran restent à qualifier. La CI qualifie Ubuntu 24.04, Python 3.12 et Gramps 6.0.7–6.0.8 ; voir le [compte rendu de validation média](docs/validation-media.fr.md). L’exécution dans Gramps Web reste non qualifiée : les paquets devraient être installés dans l’environnement serveur, et aucune instance de test n’a été validée.

Les libellés du rapport Gramps ont un catalogue français dans `gramps60/GrampsFancyBook/po/fr-local.po` ; la construction le compile et l’inclut dans l’archive. Les nouvelles chaînes du plugin doivent aussi être ajoutées au catalogue.

## Langue du livre

La langue du livre suit par défaut celle configurée dans Gramps. Choisissez le français ou l’anglais dans les options du rapport pour la remplacer ; les autres langues Gramps utilisent l’anglais. Cela concerne les titres, la navigation et les libellés d’accessibilité générés dans le PDF et le HTML. Les noms, notes, descriptions d’événements et textes des sources ne sont pas traduits. Les dates conservent le texte d’affichage déjà formaté par Gramps lors de l’extraction.

## Exemple en ligne de commande

```sh
gramps -i examples/reference-family.ged -a report \
  -p "name=gramps_fancy_genealogical_book,reference_family=F0001,max_ancestor_depth=unlimited,max_descendant_depth=unlimited,book_language=auto,output_format=json_snapshot,privacy_acknowledged=True,destination=/chemin/absolu/famille.json"
```

L’option `privacy_acknowledged=True` est requise pour chaque export en ligne de commande. Dans Desktop et Web, confirmer l’option de confidentialité à chaque export. Le rapport ne filtre ni n’anonymise les données accessibles. Ajouter `overwrite=True` aux options pour autoriser le remplacement. Le fichier [GEDCOM d’exemple](examples/reference-family.ged) contient uniquement des personnes, lieux et références d’archives fictifs, sans média. Le script ci-dessous automatise le test dans un profil Gramps temporaire et importe sa propre fixture depuis `tests/fixtures/`. Sur macOS, l’exécutable est `/Applications/Gramps.app/Contents/MacOS/Gramps`.

Pour essayer le livre lui-même, reprenez la commande ci-dessus avec `output_format=pdf` et une destination finissant par `.pdf`, ou `output_format=html_zip` et une destination finissant par `.zip`. LuaLaTeX doit être accessible à Gramps pour générer le PDF.

## Développement et validation

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev,media]'
.venv/bin/ruff check .
.venv/bin/pytest -q
.venv/bin/python build_addon.py
.venv/bin/python scripts/verify_gramps.py --gramps /chemin/vers/gramps
```

Les tests unitaires ne nécessitent pas Gramps. Le script d’intégration nécessite Python 3.12+ et Gramps 6.0 ; il vérifie les fichiers et diagnostics car Gramps peut renvoyer un code de sortie zéro malgré l’échec d’un rapport. La CI cible Python 3.10 à 3.13 pour le domaine et Gramps 6.0.7 et 6.0.8 pour l’intégration stable. Un canari non bloquant exerce aussi Gramps 6.1.0-beta2 depuis un commit amont épinglé ; il retargete seulement le manifeste du paquet CI temporaire pour sonder les nouvelles API et ne déclare pas de support stable.

Le [compte rendu L1](docs/validation-l1.fr.md), le [suivi L3](docs/validation-l3.fr.md) et la [validation des médias](docs/validation-media.fr.md) distinguent les contrôles effectués et les limites restantes.

La famille de référence doit avoir deux partenaires connus (AC-02). Exigences intégrales : [spécification originale](docs/reference/Gramps_Fancy_Genealogical_Book_Specification_v1.1.md), avec sa [provenance](docs/reference/README.md).

## Licence

Le projet est distribué sous la licence publique générale GNU, version 3 ou toute version ultérieure. Voir [LICENSE](LICENSE).
