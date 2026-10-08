# Validation média / Pillow et PDFium

Actualisé le 8 octobre 2026.

## Périmètre vérifié

La CI installe l’extra `media` pendant la matrice Python 3.10–3.13 et exécute les conversions sur des images synthétiques ainsi que sur des PDF mono- et multipages. La matrice d’intégration Gramps utilise Ubuntu 24.04, Python 3.12 et Gramps 6.0.7 et 6.0.8. L’intégration locale de cette recette utilise Gramps Desktop 6.0.8 sur macOS avec une base isolée.

### L8.3 — portraits d’archives photographiques — 8 octobre 2026

Le banc utilise vingt portraits d’archives de la Wellcome Collection, tous marqués `cc-by` dans le Catalogue API et accessibles via l’API IIIF. Le manifeste [wellcome-open-portraits-cc-by.json](fixtures/wellcome-open-portraits-cc-by.json) conserve titre, crédit, identifiants, URL de l’œuvre, URL IIIF, licence, dimensions, taille et SHA-256. Les JPEG ne sont pas versionnés ; le script les télécharge dans un répertoire temporaire et vérifie leur contenu. La [documentation Catalogue](https://developers.wellcomecollection.org/api/catalogue) expose notamment le filtre de licence et les champs de crédit ; l’[API IIIF](https://developers.wellcomecollection.org/api/iiif) permet de demander une taille et un format d’image. L’URL demandait 1 600 pixels de large au maximum ; une réponse fait 1 601 pixels. Les légendes comprennent le titre, Wellcome Collection et CC BY 4.0, et le relevé indique la transformation IIIF. Voir le [texte de la licence](https://creativecommons.org/licenses/by/4.0/).

Les photos sont des portraits historiques d’archives, principalement du XIXᵉ et du début du XXᵉ siècle ; elles ne représentent pas des photos modernes de téléphone. Le graphe familial reste entièrement fictif. La recette améliore donc la mesure du rendu avec de vraies photographies, mais ne qualifie pas encore les médias extraits d’une base Gramps réelle.

Le premier build a exposé un débordement LaTeX de 14,06 pt : une photo verticale intégrée au profil était limitée par sa largeur seulement et dépassait la hauteur utile de page. `_render_media_image` ajoute maintenant un maximum à `0.65\textheight` avec conservation des proportions. Les trois builds N=100 qui suivent compilent sans avertissement de mise en page. Les pages PDF 71, 72, 76 et 77 ont été examinées visuellement ; les photos restent proportionnelles, leurs crédits tiennent dans les légendes et aucune coupure ni superposition n’est visible. L’audit du PDF conservé confirme 40 figures avec texte alternatif et attribution, une structure balisée et aucune divergence ParentTree/OBJR ; les mesures détaillées figurent dans [validation de performance](validation-performance.fr.md) et le [relevé JSON](validation-latex-open-portraits-n100-20261008.json).

Le même banc a aussi été compilé trois fois avec CPython 3.13.7 sur macOS 27.0 arm64. Le PDF passe le même audit sémantique et ne présente aucun avertissement de mise en page. Cette variante utilise le Python hôte, pas le Python 3.13.2 embarqué par Gramps ; elle ne constitue donc pas une qualification de Gramps Desktop. Les mesures détaillées sont dans [le relevé Python 3.13](validation-latex-open-portraits-py313-n100-20261008.json).

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

Le rendu PDF A4 français produit 18 pages. Les pages physiques 12 et 14 ont été examinées à 130 ppp : la page 12 montre la région familiale choisie en pleine page, sans déformation, et la fiche renvoie à cette reproduction ; la page 15 montre le portrait du second partenaire sans chevauchement. Le scénario vérifie également les deux portraits de couverture et les liens HTML de l’usage secondaire. Il s’agit d’une fixture synthétique et d’un export CLI ; l’export GUI ciblé reste à qualifier. Cette preuve ne valide pas le lecteur d’écran ni la maquette finale.

### AC-12 — revue interactive du ZIP CLI — 4 octobre 2026

Le [ZIP de l’intégration native](../output/gramps-fancy-book-native-integration-20261004.zip), identifié par le SHA-256 `4b57d50081362327a48e60fbac6d369c0dc6ddab4f2abba0349d3746e6e67f76`, a été extrait puis servi au navigateur par un serveur local sur `127.0.0.1`. Le lien de la fiche individuelle a été activé ; il atteint la figure unique placée dans la notice familiale. Le navigateur charge le recadrage AC-12 en 540 × 600 pixels, avec sa légende et le texte alternatif synthétique de la fixture. Les quatre images de cette archive combinée chargent et possèdent un texte alternatif non vide ; les 282 liens internes pointent vers une ancre existante.

Aux largeurs de 320, 375, 768, 1 024 et 1 440 px, la page ne déborde pas horizontalement. Ce contrôle porte sur le ZIP natif CLI extrait et servi localement, pas sur un ZIP exporté depuis la boîte de dialogue Gramps ni sur une ouverture directe par `file://`. Le texte alternatif de démonstration est un marqueur de fixture, pas une description de photographie réelle. L’essai au lecteur d’écran, les médias d’une base Gramps réelle et l’export GUI ciblé restent à faire.

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
