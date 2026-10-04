# Validation média / Pillow et PDFium

Statut au 30 septembre 2026.

## Périmètre vérifié

La CI installe l’extra `media` pendant la matrice Python 3.10–3.13 et exécute les conversions sur des images synthétiques ainsi que sur des PDF mono- et multipages. La matrice d’intégration Gramps utilise Ubuntu 24.04, Python 3.12 et Gramps 6.0.7 et 6.0.8. L’intégration locale de cette recette utilise Gramps Desktop 6.0.8 sur macOS avec une base isolée.

La recette native Gramps CLI couvre maintenant AC-13 : une image fictive présente sur disque porte à la fois `BOOK_EXCLUDE` et `BOOK_FEATURED`, et sa référence porte une citation dédiée qui n’est utilisée nulle part ailleurs. L’export du modèle confirme que l’objet conserve ses deux étiquettes dans la source, mais qu’il n’a ni placement, ni référence éditoriale, ni dérivé ; sa citation exclusive ne rejoint pas l’annexe. Le ZIP n’inclut que les deux images attendues pour les autres médias, et ne contient ni description ni détail de citation AC-13. Cela qualifie l’import XML natif et l’export CLI ; voir aussi la recette Desktop ci-dessous. La saisie des tags dans les éditeurs graphiques reste à vérifier.

### AC-13 — Export Gramps Desktop — 30 septembre 2026

- Le paquet courant (archive SHA-256 `8227d8b223cecf3e9fb5841f11ac066051dc6fcc4db8492ebe9d4ac19d975965`) a été exécuté dans Gramps Desktop `6.0.8-1`, macOS 27.0 arm64. Un profil temporaire neuf ne contient que l’arbre fictif `FancyBook GUI AC13`.
- Après import, un export natif Gramps vérifie que le média M0006 est présent sur disque, porte les deux tags `BOOK_EXCLUDE` et `BOOK_FEATURED`, et garde la description `AC13_EXCLUDED_FEATURED_MARKER`. La citation C0003 porte `AC13_EXCLUDED_CITATION_MARKER` et sa seule référence vient du média M0006.
- L’export `.zip` depuis **Rapports → Pages web** produit `tmp/gramps-gui-ac13-run-20260930/approved-ac13.zip` (SHA-256 `9b1f8431c8c2285c2a9a1f0cf931257cb66dba2b56455ba7bfc23978749da470`). `unzip -t` passe ; l’archive contient `index.html` et deux PNG attendus. Les 32 identifiants sont uniques, les 33 liens résolus, les deux images locales ont leur texte alternatif, et ni le nom du média exclu ni les marqueurs du média et de sa citation n’apparaissent dans le HTML.
- L’export `.pdf` depuis la même interface produit `output/pdf/gramps-fancy-book-ac13-gui-20260930.pdf` (SHA-256 `aba8e44e2a97b863588d4b3f73a78ecc2ee3177be2e16e892026fe10c9ec21f8`), neuf pages A4, 80 742 octets ; `pdfinfo` indique `Tagged: yes`. Les marqueurs sont absents du texte extrait et l’inventaire des images ne contient pas le PNG AC-13. Les neuf pages ont été rendues à 100 ppp puis examinées, sans coupure ni superposition visible. Le balisage ne constitue pas à lui seul une validation PDF/UA.
- Pour ces deux exports, l’avertissement de confidentialité était décoché par défaut et a été confirmé pour les seules données fictives. Cette recette valide l’export GUI d’une base Gramps native préparée avec les tags ; elle ne vérifie pas encore la saisie des tags dans les éditeurs graphiques.

La recette CLI Gramps crée quatre justificatifs PDF fictifs, les attache à des citations natives puis génère un ZIP HTML. Elle confirme les quatre règles AC-16 : un PDF monopage sans URL produit un PNG à 300 ppp ; un PDF multipage sans URL reste une référence ; les deux PDF avec URL restent des liens, qu’ils soient mono- ou multipages. Le ZIP contient le dérivé du premier document, les quatre notices et l’URL du dépôt associé aux deux citations liées. L’intégrité du ZIP est vérifiée. Le portrait fictif recadré et le remplacement coordonné du JSON et du dossier média restent également couverts.

Le même scénario produit aussi un livre PDF avec `scripts/verify_gramps.py --pdf-output <fichier.pdf> --lualatex /Library/TeX/texbin/lualatex`. Gramps macOS 6.0.8 et LuaHBTeX 1.24.0 ont produit un PDF français A4 de neuf pages, conservé localement dans `output/pdf/gramps-fancy-book-ac16-pdf-cases.pdf` (sortie non versionnée). Les neuf pages ont été examinées à 110 ppp : aucune coupure ni superposition visible ; l’annexe garde le monopage sans URL comme image, les multipages comme références et l’URL du dépôt des deux citations liées. Les documents justificatifs sont des pages PDF synthétiques vides et les portraits sont fictifs ; cette revue ne qualifie pas encore la maquette finale ni l’accessibilité.

### AC-12 — recette native CLI — 4 octobre 2026

La recette `scripts/verify_gramps.py` a été exécutée contre Gramps macOS 6.0.8 et une base XML native entièrement fictive. Ses deux partenaires ont chacun un portrait de couverture. Une même image `BOOK_FEATURED` est liée à la notice familiale et à une fiche individuelle, avec des régions distinctes (`[0, 0, 60, 100]` pour la notice et `[40, 0, 100, 100]` pour la fiche). Les deux usages et rectangles sont conservés dans le modèle éditorial ; la règle de priorité familiale choisit une seule reproduction principale. Le dérivé PNG correspondant à la région familiale mesure 540 × 600 pixels. Le ZIP HTML contient cette seule image pleine page dans la notice et un renvoi vers elle depuis la fiche.

Le rendu PDF A4 français produit 18 pages. Les pages physiques 11 et 14 ont été examinées à 130 ppp : la première montre la région familiale choisie en pleine page, sans déformation, et la fiche renvoie à cette reproduction ; la page 15 montre le portrait du second partenaire sans chevauchement. Le scénario vérifie également les deux portraits de couverture et les liens HTML de l’usage secondaire. Il s’agit d’une fixture synthétique et d’un export CLI : l’export GUI ciblé et l’ouverture interactive de son ZIP restent à qualifier. Cette preuve ne valide pas le lecteur d’écran ni la maquette finale.

Le [livre synthétique de 127 pages](../output/pdf/gramps-fancy-book-122-person-featured-media-centered-preview-20260930.pdf) contient deux autres médias `BOOK_FEATURED`. Les pages physiques 49–51 et 64–67 ont été examinées séparément ; les images pleine page restent centrées, sans déformation, avec leurs légendes. Les 127 pages ont aussi été parcourues sur planches de contact. Cette revue confirme le rendu PDF sur un volume synthétique ; la recette native ci-dessus couvre désormais la sélection et le partage d’un média dans Gramps.

Pour que Gramps CLI utilise les mêmes dépendances optionnelles que l’environnement de recette, `scripts/verify_gramps.py` copie Pillow et PDFium dans le profil Gramps temporaire. Cette manipulation est isolée au test ; elle ne configure pas l’installation Gramps Desktop de l’utilisateur.

L’intégration ne dépend d’aucune donnée familiale réelle. Les fichiers originaux ne sont pas modifiés ; le portrait et les quatre PDF existent uniquement dans le répertoire temporaire du test.

## Vérifications restantes

Le test `test_excluded_featured_media_is_absent_from_generated_books` construit un instantané Gramps fictif dont un média porte les deux étiquettes. Il vérifie que ses références éditoriales et les citations qui leur sont attachées ne créent ni notice ni dérivé média, que le ZIP contient uniquement `index.html`, et que la description ou une balise `<img>` n’apparaît ni dans le HTML ni dans le LaTeX. Le chemin source fictif n’existe pas : toute tentative de lecture ferait échouer le test.

Pour AC-13, l’export GUI du paquet courant est maintenant confirmé sur une base native fictive avec les deux étiquettes ; la saisie des tags depuis les éditeurs graphiques reste à vérifier. Pour AC-16, la boîte d’options GUI, des justificatifs réalistes et une comparaison aux maquettes restent à vérifier.

## Installation

Pour un environnement de développement, installer le projet et les dépendances de test et de conversion :

\`\`\`sh
python -m pip install -e '.[dev,media]'
\`\`\`

Dans un environnement Gramps Desktop qui permet l’installation par pip, exécuter `python -m pip install 'Pillow>=10' 'pypdfium2>=4'` avec le même interpréteur Python que celui qui lance Gramps, puis redémarrer Gramps. Un autre Python peut installer les paquets dans un environnement invisible pour le plugin.

Les convertisseurs restent facultatifs. Le rapport garde l’export JSON et signale les dérivés impossibles par diagnostic. Ils ne sont donc pas déclarés dans `requires_mod` : Gramps 6.0 traite ce champ comme une condition obligatoire de chargement du plugin, et sa forme texte attend un nom de module importable, alors que Pillow s’installe sous le nom de distribution `Pillow` et s’importe comme `PIL`. Transformer cette fonctionnalité facultative en prérequis empêcherait l’export JSON sur une installation qui n’a pas ces paquets.

## Limites

La CI qualifie l’installation de paquets et le traitement média dans Gramps 6.0.7 et 6.0.8 sous Ubuntu 24.04. La recette AC-16 passe aussi avec l’exécutable Gramps 6.0.8 de l’application macOS quand les dépendances sont ajoutées au profil temporaire. Les installateurs macOS et Windows, ainsi que les distributions isolées telles que Flatpak et Snap, restent à vérifier avec leurs propres environnements Python.

Gramps Web exécute les rapports côté serveur. L’installation des dépendances doit donc se faire dans l’environnement Python ou l’image serveur, et aucun serveur de test n’a été vérifié ici. Cette validation ne revendique pas la compatibilité Gramps Web. Ajouter une preuve Web exigera une instance jetable avec des données fictives.

Références : [développement de modules complémentaires Gramps](https://www.gramps-project.org/wiki/index.php/Addons_Development), [gestion des dépendances dans Gramps 6.0.8](https://github.com/gramps-project/gramps/tree/v6.0.8/gramps/gen/utils), [rapports dans Gramps Web](https://www.grampsweb.org/user-guide/reports/).
