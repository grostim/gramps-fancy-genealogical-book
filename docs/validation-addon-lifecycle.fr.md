# Validation du cycle du paquet — 29 septembre 2026

## Environnement et méthode

- Gramps Desktop 6.0.8, macOS 27.0 arm64, interpréteur embarqué Python 3.13.2.
- Source `main` au commit `106eae276871238b0dd2c373cae5879e7f600119` ; enregistrement du module à la version `0.9.0`.
- Archive reconstruite par `build_addon.py` : SHA-256 `e99fbe4c9c19c5817c95c97f7ada6020c2a66473445095815dc6e186a63de366`.
- Profil `GRAMPSHOME` temporaire, sans arbre personnel. Mistune 3.3.4 a été placé uniquement dans le répertoire de bibliothèques de ce profil. Le GEDCOM et son portrait d’un pixel ont également été copiés dans le répertoire temporaire ; Gramps signale `No errors detected` à l’import.

## Résultats

| Étape | Vérification | Résultat |
| --- | --- | --- |
| Installation | Extraction de l’archive dans le profil, puis export HTML ZIP depuis le CLI | Le rapport est découvert ; le ZIP passe le contrôle d’intégrité et contient `index.html` (2 450 octets). |
| Réinstallation | Remplacement complet du dossier `GrampsFancyBook/` par la même archive reconstruite en version `0.9.0`, puis export PDF | Le rapport est découvert après redémarrage du processus ; le fichier commence par la signature `%PDF-` (27 971 octets). |
| Retrait | Suppression du seul dossier installé, puis nouvel appel du rapport | Gramps répond `Unknown report name` et aucun fichier n’est créé. |

Le profil temporaire, sa dépendance, le ZIP et le PDF ont été supprimés à la fin de l’essai. Les archives construites et les sorties résultantes ne contiennent pas de données familiales réelles.

## Portée et limites

Le remplacement exercé est une réinstallation de la même version `0.9.0`, pas une mise à niveau entre deux versions. L’ancienne source `0.8.0` au commit `a8c3797`, reconstruite pour l’essai, échoue au chargement sous Gramps 6.0.8 : son fichier `.gpr.py` appelle `get_addon_translator(__file__)`, alors que Gramps n’injecte pas `__file__` dans ce contexte d’enregistrement. Elle ne constitue donc pas une base de mise à niveau valide pour cette matrice. Aucune version n’est actuellement publiée dans GitHub Releases.

Le contrôle a utilisé le binaire CLI fourni dans l’application Desktop ; il ne qualifie pas l’interface graphique du gestionnaire d’extensions, une migration interversion, ni Gramps Web. Les étapes manuelles FR/EN sont décrites dans les [instructions d’installation](../README.fr.md#construction-et-installation) et [Build and install](../README.md#build-and-install).

## Requalification de l’archive actuelle — 6 octobre 2026

Deux constructions avec `build_addon.py` donnent la même archive `0.9.0` : SHA-256 `357ce674720f914a4788d99956680b42df5bc84991cee6b7589b85a8a362852c`, 88 346 octets et 29 membres. Le paquet contient le renderer PDF et `locale/fr/LC_MESSAGES/addon.mo`, sans fichiers cache Python.

L’archive locale `gramps60/download/GrampsFancyBook.addon.tgz`, ignorée par Git et datée du 5 octobre avant cette reconstruction, est régénérée avec ces octets. Deux nouvelles constructions locales produisent les mêmes octets et le même SHA-256. Le constructeur refuse maintenant une divergence de version entre `pyproject.toml`, l’enregistrement Gramps et les en-têtes `Project-Id-Version` des catalogues PO/POT. Les README français et anglais indiquent comment fabriquer l’archive ; aucune version GitHub Release n’est publiée.

Cette archive a ensuite été extraite dans un nouveau profil temporaire `GRAMPSHOME` et utilisée avec Gramps Desktop 6.0.8 (Python embarqué 3.13.2) ; le processus d’intégration hôte utilise CPython 3.13.7. Le `PYTHONPATH` du checkout est retiré. La vérification native passe pour le modèle, les exports HTML ZIP et JSON, les cas d’erreur et la génération PDF par l’archive installée. Le PDF français balisé compte 18 pages A4 (159 047 octets). Une page intérieure examinée à 100 ppp ne montre pas de texte coupé et ses marges paraissent cohérentes avec les 15 mm configurés. Le [relevé brut](validation-gramps-clean-install-20261006.json) conserve les versions et limites.

Le test local ci-dessus utilise le CLI dans un profil neuf, pas une installation par le gestionnaire graphique. La langue française a été demandée au rendu du livre ; cette invocation n’exerce pas l’interface traduite du rapport ni une revue visuelle complète. La recette graphique distincte ci-dessous couvre un export de référence. Le lecteur d’écran, les autres versions Desktop et Gramps Web restent à qualifier.

Le premier run hébergé de la CI, associé à la [PR #294](https://github.com/grostim/gramps-fancy-genealogical-book/pull/294), a réussi sous Gramps 6.0.7 et 6.0.8 avec l’image LuaLaTeX épinglée. Les deux jobs ont installé l’archive dans un environnement temporaire, exécuté les contrôles natifs, puis produit un PDF balisé A4 de 16 pages : 151 136 octets pour 6.0.7 et 151 180 octets pour 6.0.8. Les artefacts `GrampsFancyBook-PDF-Gramps-6.0.7` et `GrampsFancyBook-PDF-Gramps-6.0.8` sont conservés 14 jours dans le [run CI](https://github.com/grostim/gramps-fancy-genealogical-book/actions/runs/37515424979). Les matrices Python 3.10–3.13, Windows 3.10–3.13, macOS, la canary Gramps 6.1 et le prototype LaTeX ont également réussi. Cela qualifie l’export CLI depuis l’archive sous ces versions ; cela ne remplace pas la recette graphique ni une revue visuelle complète.

## Qualification graphique de la référence du renderer — 6 octobre 2026

Le test a utilisé Gramps Desktop 6.0.8-1 sous macOS dans le profil temporaire `tmp/l8-4-gui-example-20261006/profile`, lancé avec `GRAMPSHOME` explicite. Ce profil ne contenait aucun arbre au départ. L’arbre `L8_4 GUI reference family 20261006` a été créé dans ce profil et alimenté avec `reference-family.gramps`, une fixture fictive que Gramps a reconnue comme 4 individus, 2 familles, 1 source, 3 événements, 3 citations, 2 lieux et 1 dépôt. Aucun arbre personnel n’a été ouvert.

Le rapport apparaît dans **Rapports → Pages web → Livre généalogique illustré pour Gramps**. L’interface était en français ; les options ont explicitement demandé **Français** et **Livre PDF (LuaLaTeX)**, et l’accusé de confidentialité a été coché. Le dossier de sortie était `output/pdf/`. Le dossier installé dans ce profil provient de l’archive `0.9.0` ; les SHA-256 de `GrampsFancyBook.py`, `gramps_fancy_book/report.py` et `gramps_fancy_book/renderers/latex.py` correspondent aux sources du commit `b8141bc`.

L’export produit [le PDF GUI de référence](../output/pdf/gramps-fancy-book-reference-family-gui-20261006.pdf) : 9 pages A4, balisage PDF actif, 53 135 octets, SHA-256 `79fa54bdd13df112c3e5b57688f64e9f330b2c07edb3f82f9fefabf1a9849fd6`. Les neuf pages ont été rendues à 110 ppp et examinées. Les pages intérieures gardent des marges d’environ 15 mm, sans texte coupé ni chevauchement. La couverture centrée et certaines rubriques courtes sont naturellement aérées avec cette petite fixture ; cet espace n’est pas dû à un élargissement des marges. Cette recette qualifie le chargement du rapport et l’export PDF GUI sous Gramps 6.0.8-1 avec LuaHBTeX 1.24.0 (TeX Live 2026) pour cet état du code. Quatre commits ultérieurs ont modifié le renderer PDF (`2a14b4f`, `7e02043`, `03bcda1`, `7598042`) : ce PDF historique ne qualifie pas le renderer actuel. Il faut réexporter et relire un PDF GUI depuis le renderer courant avant publication. Les autres versions Desktop, Gramps Web, le lecteur d’écran et des médias de taille réaliste restent aussi à qualifier.
