# Validation média / Pillow et PDFium

Statut au 28 septembre 2026.

## Périmètre vérifié

La CI installe l’extra `media` pendant la matrice Python 3.10–3.13 et exécute les conversions sur des images synthétiques ainsi que sur des PDF mono- et multipages. Le test Gramps Desktop utilise Ubuntu 24.04, Python 3.12 et Gramps 6.0.8. Il fabrique un portrait fictif dans le répertoire média temporaire, l’importe dans une base isolée, puis vérifie le recadrage PNG, l’écriture du manifeste et le remplacement coordonné du JSON et du dossier média.

L’intégration ne dépend d’aucune donnée familiale réelle. Les fichiers originaux ne sont pas modifiés ; le portrait existe uniquement dans le répertoire temporaire du test.

## Vérification de publication restante

Dans Gramps, appliquer simultanément `BOOK_EXCLUDE` et `BOOK_FEATURED` à un média fictif, puis générer un livre HTML ZIP. Le contrôle d’acceptation ne réussit que si le média exclu est absent de toutes les références `<img>` de `index.html` et de toutes les entrées `media/` du ZIP. Le fichier ne doit pas non plus être ouvert ni converti pendant la génération. Ce scénario manuel n’a pas encore été exécuté.

## Installation

Pour un environnement de développement, installer le projet et les dépendances de test et de conversion :

\`\`\`sh
python -m pip install -e '.[dev,media]'
\`\`\`

Dans un environnement Gramps Desktop qui permet l’installation par pip, exécuter `python -m pip install 'Pillow>=10' 'pypdfium2>=4'` avec le même interpréteur Python que celui qui lance Gramps, puis redémarrer Gramps. Un autre Python peut installer les paquets dans un environnement invisible pour le plugin.

Les convertisseurs restent facultatifs. Le rapport garde l’export JSON et signale les dérivés impossibles par diagnostic. Ils ne sont donc pas déclarés dans `requires_mod` : Gramps 6.0 traite ce champ comme une condition obligatoire de chargement du plugin, et sa forme texte attend un nom de module importable, alors que Pillow s’installe sous le nom de distribution `Pillow` et s’importe comme `PIL`. Transformer cette fonctionnalité facultative en prérequis empêcherait l’export JSON sur une installation qui n’a pas ces paquets.

## Limites

La CI qualifie l’installation de paquets et le traitement média dans Gramps 6.0.8 sous Ubuntu 24.04. Les installateurs macOS et Windows, ainsi que les distributions isolées telles que Flatpak, Snap ou l’application macOS, restent à vérifier sur leurs propres environnements Python.

Gramps Web exécute les rapports côté serveur. L’installation des dépendances doit donc se faire dans l’environnement Python ou l’image serveur, et aucun serveur de test n’a été vérifié ici. Cette validation ne revendique pas la compatibilité Gramps Web. Ajouter une preuve Web exigera une instance jetable avec des données fictives.

Références : [développement de modules complémentaires Gramps](https://www.gramps-project.org/wiki/index.php/Addons_Development), [gestion des dépendances dans Gramps 6.0.8](https://github.com/gramps-project/gramps/tree/v6.0.8/gramps/gen/utils), [rapports dans Gramps Web](https://www.grampsweb.org/user-guide/reports/).
