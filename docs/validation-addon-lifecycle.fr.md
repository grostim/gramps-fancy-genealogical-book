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

Cette archive a ensuite été extraite dans un nouveau profil temporaire `GRAMPSHOME` et utilisée avec Gramps Desktop 6.0.8 (Python embarqué 3.13.2) ; le processus d’intégration hôte utilise CPython 3.13.7. Le `PYTHONPATH` du checkout est retiré. La vérification native passe pour le modèle, les exports HTML ZIP et JSON, les cas d’erreur et la génération PDF par l’archive installée. Le PDF français balisé compte 18 pages A4 (159 047 octets). Une page intérieure examinée à 100 ppp ne montre pas de texte coupé et ses marges paraissent cohérentes avec les 15 mm configurés. Le [relevé brut](validation-gramps-clean-install-20261006.json) conserve les versions et limites.

Le test est CLI, dans un profil neuf, pas une installation par le gestionnaire graphique. La langue française a été demandée au rendu du livre ; cette invocation n’exerce pas l’interface traduite du rapport. La revue visuelle complète, le lecteur d’écran, les autres versions Desktop et Gramps Web restent à qualifier. Le workflow CI est maintenant configuré pour répéter l’export PDF natif sous Gramps 6.0.7 et 6.0.8 avec l’image LuaLaTeX épinglée ; le premier run hébergé reste à observer avant de considérer ce chemin qualifié.
