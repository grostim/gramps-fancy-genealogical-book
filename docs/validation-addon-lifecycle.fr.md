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

## Installateur natif du gestionnaire de greffons — 9 octobre 2026

Le script `scripts/verify_addon_installer.py` appelle `gramps.gen.plug.utils.load_addon_file`, le backend utilisé par le gestionnaire de greffons, dans un nouveau profil temporaire. Le contrôle local a utilisé le Python embarqué 3.13.2 de Gramps Desktop 6.0.8-1. Deux constructions du commit `a5448614948a6c796dfa9fe82721de62f80a3392` produisent les mêmes octets : SHA-256 `f11cca39c47bd6beed9f189feefec4a268b0ee0bf722c791a3e0010038e596d5`, 29 fichiers.

L’installateur accepte l’archive et les 29 fichiers installés correspondent exactement à leurs octets archivés. Une réinstallation restaure le fichier `MANIFEST` volontairement altéré dans ce seul profil temporaire. Une archive diagnostique ciblant Gramps `99.0` est refusée et ne change aucun fichier installé. Le [relevé brut](validation-native-addon-installer-20261009.json) consigne ces résultats. Les étapes de ce contrôle réussissent aussi sous Gramps 6.0.7 et 6.0.8 dans le [run CI 37926760961](https://github.com/grostim/gramps-fancy-genealogical-book/actions/runs/37926760961), avant les exports. La CI conserve chaque relevé JSON comme artefact distinct à côté de l’archive.

Cela qualifie le backend d’installation, pas la manipulation de l’interface graphique, une mise à niveau interversion ni le nettoyage de fichiers obsolètes par le gestionnaire. Le parcours graphique reste à effectuer ; l’accès au Mac était verrouillé pendant cette recette.

## Qualification graphique de la référence du renderer — 6 octobre 2026

Le test a utilisé Gramps Desktop 6.0.8-1 sous macOS dans le profil temporaire `tmp/l8-4-gui-example-20261006/profile`, lancé avec `GRAMPSHOME` explicite. Ce profil ne contenait aucun arbre au départ. L’arbre `L8_4 GUI reference family 20261006` a été créé dans ce profil et alimenté avec `reference-family.gramps`, une fixture fictive que Gramps a reconnue comme 4 individus, 2 familles, 1 source, 3 événements, 3 citations, 2 lieux et 1 dépôt. Aucun arbre personnel n’a été ouvert.

Le rapport apparaît dans **Rapports → Pages web → Livre généalogique illustré pour Gramps**. L’interface était en français ; les options ont explicitement demandé **Français** et **Livre PDF (LuaLaTeX)**, et l’accusé de confidentialité a été coché. Le dossier de sortie était `output/pdf/`. Le dossier installé dans ce profil provient de l’archive `0.9.0` ; les SHA-256 de `GrampsFancyBook.py`, `gramps_fancy_book/report.py` et `gramps_fancy_book/renderers/latex.py` correspondent aux sources du commit `b8141bc`.

L’export produit [le PDF GUI de référence](../output/pdf/gramps-fancy-book-reference-family-gui-20261006.pdf) : 9 pages A4, balisage PDF actif, 53 135 octets, SHA-256 `79fa54bdd13df112c3e5b57688f64e9f330b2c07edb3f82f9fefabf1a9849fd6`. Les neuf pages ont été rendues à 110 ppp et examinées. Les pages intérieures gardent des marges d’environ 15 mm, sans texte coupé ni chevauchement. La couverture centrée et certaines rubriques courtes sont naturellement aérées avec cette petite fixture ; cet espace n’est pas dû à un élargissement des marges. Cette recette qualifie le chargement du rapport et l’export PDF GUI sous Gramps 6.0.8-1 avec LuaHBTeX 1.24.0 (TeX Live 2026) pour cet état du code. Quatre commits ultérieurs ont modifié le renderer PDF (`2a14b4f`, `7e02043`, `03bcda1`, `7598042`) : cette qualification historique ne vaut donc pas pour le renderer courant. La requalification graphique de l’archive actuelle, avec un jeu de portraits, est consignée ci-dessous. Les autres versions Desktop, Gramps Web, le lecteur d’écran et PDF/UA restent à qualifier.

## Requalification graphique avec photographies dans Gramps Desktop — 9 octobre 2026

La recette a utilisé Gramps Desktop 6.0.8-1, macOS 27.0 arm64, Python embarqué 3.13.2 et LuaHBTeX 1.24.0 (TeX Live 2026). L’application a été lancée avec un `GRAMPSHOME` temporaire neuf ; aucun arbre personnel n’a été ouvert. L’archive `0.9.0` a été reconstruite depuis le commit `35b57038889626a6d97af89a307fbd64374913a4` : SHA-256 `c1d4a107f15856a7b55bd10f4f9b5af63fc70bd1390407c5a601930840376df3`. Les sources du rapport et du renderer LaTeX ont respectivement les SHA-256 `55ef2aa9501d3aed4df1282a10fecb01213b426de177c04af31a71e99084a8d6` et `2120b2a6030531251fe52f0df96017147c3e4f392cabfb8ba973a3cf5d41a16b`.

Un GEDCOM synthétique généré pour la recette a été importé sans erreur dans un arbre dédié. Il contient 202 individus, 101 familles fictives et vingt portraits historiques de la Wellcome Collection, sous licence CC BY 4.0. Les fichiers JPEG source totalisent 13 741 822 octets ; le manifeste de licence et de provenance est [wellcome-open-portraits-cc-by.json](fixtures/wellcome-open-portraits-cc-by.json). L’interface Gramps est en français ; l’accusé de confidentialité a été confirmé pour cet export fictif.

Le premier PDF produit fait 103 pages A4, 77 489 999 octets, et `pdfinfo` confirme `Tagged: yes` (PDF 2.0). Son SHA-256 est `e8077819a51dff84387679db903716067f3cb18737ac489484d75ddabafb6e9c`. L’export GUI a duré environ 70,1 secondes. Les vingt images conservées dans le PDF mesurent de 1 600 × 1 540 à 1 601 × 2 700 pixels, à une résolution effective de 301 à 418 ppp. Les 103 pages ont été rendues et relues page par page sur neuf planches (12 pages par planche, sauf la dernière qui en contient 7) ; les pages physiques 22, 35, 49, 70, 96, 98 et 103 ont aussi été examinées séparément à 120 ppp. Cette première revue a révélé une coupure réelle : la dernière ligne de la citation [299] était seule en tête de la page suivante.

Le renderer regroupe désormais sur une page les entrées de citation sans média ayant au plus trois renvois. Le nouvel export GUI depuis le même arbre fictif reste un PDF A4 balisé de 103 pages, de 77 489 335 octets ; son SHA-256 est `c2778863a1237840d248a1a4d9cb9cc83e1b41a0a76b3c55b3bbe829c0b1d871`. Le SHA-256 du source `latex.py` utilisé est `5fa4616031656e10ef24154ef7893e04551c7fe53a25d9420277a992a6b07171`. Les pages physiques 96 à 103 de ce nouvel export ont été rendues à 120 ppp et relues. La citation [299] tient maintenant entièrement sur la page physique 97 (folio imprimé 96), sans ligne orpheline ni autre défaut visible sur les pages relues. Les pages hors de cette annexe ne sont pas affectées par le changement et restent couvertes par la revue page par page initiale. Le PDF corrigé est conservé à `/tmp/gfb-l84-gui-renderer-20261009-y59h24x5/wellcome-portraits-n100-gui-recheck.pdf`. Cette revue visuelle ne constitue pas un audit PDF/UA.

L’export HTML ZIP depuis la même base contient `index.html` et les vingt images, soit 21 fichiers. Le ZIP pèse 76 222 817 octets, son intégrité passe `unzip -t`, et son SHA-256 est `4dabfba9430567e16e941da6ee77204ee3d02635537050a0692718a62f4e4d05`. L’index HTML contient les attributions Wellcome Collection et CC BY 4.0. Le PDF et le ZIP sont des sorties locales non versionnées, conservées dans `/tmp/gfb-l84-gui-renderer-20261009-y59h24x5/`.

Cette recette requalifie le chargement du renderer courant et les exports PDF et HTML depuis l’interface Gramps sur une base isolée avec des photographies publiques. La première revue exhaustive du PDF de 103 pages a détecté la coupure de la citation [299] ; le renderer a été corrigé, puis les pages de l’annexe du nouvel export ont été relues sans défaut visible. Elle ne teste pas l’installation par le gestionnaire graphique, l’extraction de médias depuis un arbre utilisateur existant, d’autres versions Desktop, Gramps Web, la lecture d’écran ni la conformité PDF/UA.

## Export natif CLI avec le renderer courant — 9 octobre 2026

Une archive reconstruite au commit `6330716` a été installée dans un profil Gramps 6.0.8-1 vierge, avec les dépendances copiées uniquement dans ce profil et sans checkout dans le `PYTHONPATH`. La fixture fictive de 202 personnes, 101 familles et vingt portraits publics produit un modèle sans diagnostic puis un PDF balisé A4 de 103 pages. Les 103 pages sont identiques pixel par pixel au PDF GUI corrigé conservé, lors du rendu PDFium à 108 ppp ; quatre pages ont aussi été examinées directement. Les audits de liens, des vingt figures et des exigences automatiques PDF/UA-2 sont consignés dans le [relevé](validation-native-current-portraits-20261009.json) et la [qualification de l’accessibilité](validation-pdf-accessibility.fr.md#qualification-finale-ci-et-export-natif-courant). Le seul échec veraPDF est le schéma d’identification absent. Cette recette CLI ne ferme pas les étapes GUI, installation par le gestionnaire, autres versions Desktop et lecteur d’écran. Le PDF de 77 489 201 octets dépasse encore 16 Mio.
