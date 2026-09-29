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

## Libellés standard Gramps — 29 septembre 2026

Une recette complémentaire utilise une base Gramps native fictive avec les événements standard `Birth` et `Marriage`, un type personnalisé `Profession`, une filiation et un rôle `Primary`.

| Langue du livre | Locale Gramps | Sorties inspectées | Résultat |
| --- | --- | --- | --- |
| Français | Anglais | PDF et HTML ZIP | `Naissance`, `Mariage`, `Principal` et la filiation `Naissance` sont traduits ; `Profession` reste tel que saisi |
| Anglais | Français | HTML ZIP | `Birth`, `Marriage`, `Primary` et la filiation `Birth` restent en anglais ; `Profession` reste tel que saisi |

La description d’événement saisie dans la fixture reste intacte. Le PDF français comprend 10 pages A4. La couverture, le sommaire, les parcours familiaux, les notices, les fiches, l’annexe et l’index ont été examinés par échantillon ; la page 3 et l’accessibilité n’ont pas été qualifiées. Le PDF n’est pas balisé (`Tagged: no`). Son SHA-256 est `f01792f5b5b85cd6fcb3f5502ec26b1419dce452d4885402ad2fe5c3a946bcfa`.

## Affichage des dates selon la langue du livre — 30 septembre 2026

La vérification d’intégration native Gramps 6.0.8 compare les mêmes événements exportés avec le livre en anglais puis en français, alors que la locale du profil Gramps reste anglaise. Pour `Birth`, le texte affiché contient l’année 1900 dans les deux cas et diffère selon la langue sélectionnée ; les valeurs brutes et normalisées restent identiques. La date textuelle du mariage, « Entre l’hiver 1924 et le printemps 1925 », reste exactement telle qu’elle a été saisie dans les deux langues, et sa valeur brute est identique.

## Limites

- Ces essais invoquent le binaire Gramps Desktop en ligne de commande avec des profils isolés. Ils ne vérifient pas encore l’affichage graphique de l’option ni son choix dans la boîte de dialogue du rapport.
- La recette ne compare pas toutes les chaînes de notes et d’événements ; elle confirme la conservation du nom saisi. Les données de la fixture sont fictives.
- Les dates structurées sont formatées par Gramps dans la langue du livre et la date libre de cette fixture reste intacte ; la sélection graphique de la langue n’est pas encore couverte.
- Le PDF de démonstration utilise un petit arbre et des portraits synthétiques ; sa mise en page finale, l’accessibilité PDF et la comparaison avec les maquettes privées ne sont pas qualifiées par cette recette.
