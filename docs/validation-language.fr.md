# Validation de la langue du livre

Compte rendu du 29 septembre 2026. Cette recette cible l’option de langue ajoutée par la PR #100 et utilise uniquement une base Gramps fictive.

## Environnement

- macOS 27.0 arm64 ; Gramps Desktop 6.0.8 ; Python embarqué 3.13.2.
- LuaHBTeX 1.24.0 (TeX Live 2026) pour les sorties PDF.
- Archive construite depuis `main` au commit `53e9934` ; SHA-256 `4ada701f62340190952df39780b8faf53b125f97745558aa22136d7739dd8e58`.
- Un profil temporaire Gramps distinct par export. L’application macOS ne fournit pas `mistune` ; la copie Python 3.3.4 de cette dépendance a été ajoutée au seul dossier `plugins/lib` du profil d’essai.
- Fixture synthétique avec famille centrale `F0001`, noms fictifs et portrait synthétique. Aucun arbre personnel n’a été utilisé.

## Scénarios CLI

Chaque ligne a été produite en PDF et en HTML ZIP avec le rapport Gramps réel. Les fichiers ont été inspectés avec `pdftotext` ou extraits du ZIP ; `ZipFile.testzip()` n’a signalé aucun membre corrompu.

| Option du livre | Locale Gramps | Langue attendue | PDF | HTML ZIP |
| --- | --- | --- | --- | --- |
| Automatique | Français | Français | Réussi | Réussi |
| Automatique | Anglais | Anglais | Réussi | Réussi |
| Français | Anglais | Français | Réussi | Réussi |
| Anglais | Français | Anglais | Réussi | Réussi |
| Automatique | Allemand non pris en charge | Repli anglais | Réussi | Réussi |

Les libellés « Ascendance » et « Table des matières » apparaissent dans les sorties françaises ; « Ancestry » et « Contents » apparaissent dans les sorties anglaises. Chaque page HTML contient l’attribut `lang` correspondant. Le nom fictif « Exemple, Émile » reste identique dans les dix sorties malgré le changement de langue des libellés.

## Limites

- Ces essais invoquent le binaire Gramps Desktop en ligne de commande avec des profils isolés. Ils ne vérifient pas encore l’affichage graphique de l’option ni son choix dans la boîte de dialogue du rapport.
- La recette ne compare pas toutes les chaînes de notes et d’événements ; elle confirme la conservation du nom saisi. Les données de la fixture sont fictives.
- Le texte de date formaté par Gramps n’est pas reformaté par le renderer ; son apparence sous une dérogation de langue reste à décider et à vérifier.
- L’accessibilité PDF et la comparaison avec les maquettes privées ne sont pas qualifiées par cette recette.
