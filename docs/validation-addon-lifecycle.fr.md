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
