# Validation média / Pillow et PDFium

Statut au 30 septembre 2026.

## Périmètre vérifié

La CI installe l’extra `media` pendant la matrice Python 3.10–3.13 et exécute les conversions sur des images synthétiques ainsi que sur des PDF mono- et multipages. Le test Gramps utilise Ubuntu 24.04, Python 3.12 et Gramps 6.0.8. L’intégration locale de cette recette utilise Gramps Desktop 6.0.8 sur macOS avec une base isolée.

La recette native Gramps CLI couvre maintenant AC-13 : une image fictive présente sur disque porte à la fois `BOOK_EXCLUDE` et `BOOK_FEATURED`, et sa référence porte une citation dédiée qui n’est utilisée nulle part ailleurs. L’export du modèle confirme que l’objet conserve ses deux étiquettes dans la source, mais qu’il n’a ni placement, ni référence éditoriale, ni dérivé ; sa citation exclusive ne rejoint pas l’annexe. Le ZIP n’inclut que les deux images attendues pour les autres médias, et ne contient ni description ni détail de citation AC-13. Cela qualifie l’import XML natif et l’export CLI, pas encore la saisie ou l’export depuis l’interface graphique.

La recette CLI Gramps crée quatre justificatifs PDF fictifs, les attache à des citations natives puis génère un ZIP HTML. Elle confirme les quatre règles AC-16 : un PDF monopage sans URL produit un PNG à 300 ppp ; un PDF multipage sans URL reste une référence ; les deux PDF avec URL restent des liens, qu’ils soient mono- ou multipages. Le ZIP contient le dérivé du premier document, les quatre notices et l’URL du dépôt associé aux deux citations liées. L’intégrité du ZIP est vérifiée. Le portrait fictif recadré et le remplacement coordonné du JSON et du dossier média restent également couverts.

Le même scénario produit aussi un livre PDF avec `scripts/verify_gramps.py --pdf-output <fichier.pdf> --lualatex /Library/TeX/texbin/lualatex`. Gramps macOS 6.0.8 et LuaHBTeX 1.24.0 ont produit un PDF français A4 de neuf pages, conservé localement dans `output/pdf/gramps-fancy-book-ac16-pdf-cases.pdf` (sortie non versionnée). Les neuf pages ont été examinées à 110 ppp : aucune coupure ni superposition visible ; l’annexe garde le monopage sans URL comme image, les multipages comme références et l’URL du dépôt des deux citations liées. Les documents justificatifs sont des pages PDF synthétiques vides et les portraits sont fictifs ; cette revue ne qualifie pas encore la maquette finale ni l’accessibilité.

Pour que Gramps CLI utilise les mêmes dépendances optionnelles que l’environnement de recette, `scripts/verify_gramps.py` copie Pillow et PDFium dans le profil Gramps temporaire. Cette manipulation est isolée au test ; elle ne configure pas l’installation Gramps Desktop de l’utilisateur.

L’intégration ne dépend d’aucune donnée familiale réelle. Les fichiers originaux ne sont pas modifiés ; le portrait et les quatre PDF existent uniquement dans le répertoire temporaire du test.

## Vérifications restantes

Le test `test_excluded_featured_media_is_absent_from_generated_books` construit un instantané Gramps fictif dont un média porte les deux étiquettes. Il vérifie que ses références éditoriales et les citations qui leur sont attachées ne créent ni notice ni dérivé média, que le ZIP contient uniquement `index.html`, et que la description ou une balise `<img>` n’apparaît ni dans le HTML ni dans le LaTeX. Le chemin source fictif n’existe pas : toute tentative de lecture ferait échouer le test.

Pour AC-13, l’export depuis l’interface Gramps reste à confirmer sur une base native fictive avec les deux étiquettes. Pour AC-16, la boîte d’options GUI, des justificatifs réalistes et une comparaison aux maquettes restent à vérifier.

## Installation

Pour un environnement de développement, installer le projet et les dépendances de test et de conversion :

\`\`\`sh
python -m pip install -e '.[dev,media]'
\`\`\`

Dans un environnement Gramps Desktop qui permet l’installation par pip, exécuter `python -m pip install 'Pillow>=10' 'pypdfium2>=4'` avec le même interpréteur Python que celui qui lance Gramps, puis redémarrer Gramps. Un autre Python peut installer les paquets dans un environnement invisible pour le plugin.

Les convertisseurs restent facultatifs. Le rapport garde l’export JSON et signale les dérivés impossibles par diagnostic. Ils ne sont donc pas déclarés dans `requires_mod` : Gramps 6.0 traite ce champ comme une condition obligatoire de chargement du plugin, et sa forme texte attend un nom de module importable, alors que Pillow s’installe sous le nom de distribution `Pillow` et s’importe comme `PIL`. Transformer cette fonctionnalité facultative en prérequis empêcherait l’export JSON sur une installation qui n’a pas ces paquets.

## Limites

La CI qualifie l’installation de paquets et le traitement média dans Gramps 6.0.8 sous Ubuntu 24.04. La recette AC-16 passe aussi avec l’exécutable Gramps 6.0.8 de l’application macOS quand les dépendances sont ajoutées au profil temporaire. Les installateurs macOS et Windows, ainsi que les distributions isolées telles que Flatpak et Snap, restent à vérifier avec leurs propres environnements Python.

Gramps Web exécute les rapports côté serveur. L’installation des dépendances doit donc se faire dans l’environnement Python ou l’image serveur, et aucun serveur de test n’a été vérifié ici. Cette validation ne revendique pas la compatibilité Gramps Web. Ajouter une preuve Web exigera une instance jetable avec des données fictives.

Références : [développement de modules complémentaires Gramps](https://www.gramps-project.org/wiki/index.php/Addons_Development), [gestion des dépendances dans Gramps 6.0.8](https://github.com/gramps-project/gramps/tree/v6.0.8/gramps/gen/utils), [rapports dans Gramps Web](https://www.grampsweb.org/user-guide/reports/).
