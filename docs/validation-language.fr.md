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

## Sélection dans l’interface Desktop — 2 octobre 2026

La boîte de rapport de Gramps Desktop 6.0.8 a été ouverte avec l’archive de l’extension construite depuis `891a10b462ec` (SHA-256 `0260be914cf71e3e5be95794f58f7d22df492ef3036bbbe4fd12304e85e6d391`). Le profil Gramps, l’extension et la base de trois personnes fictives ont été placés sous `/tmp/gfb-gui-language-20261002`. La dépendance `mistune` 3.3.4 a été ajoutée au seul profil temporaire. La famille centrale `F0001` a été choisie dans la boîte graphique. Chaque export a reçu un consentement explicite, décoché de nouveau à l’ouverture suivante.

| Locale de Gramps | Option choisie dans la boîte | `BOOK_LANGUAGE` exporté | SHA-256 du JSON |
| --- | --- | --- | --- |
| Français | Utiliser la langue de Gramps | `fr` | `ad2f15318697259a90b260305b627f97ba0ba5c96b224808117358c7baf981d9` |
| Français | Anglais | `en` | `96d24deae3a6efd89efc47a3ee9a64c1c495d927f72cd37fe01bf31abfadb1d9` |
| Français | Français | `fr` | `ad2f15318697259a90b260305b627f97ba0ba5c96b224808117358c7baf981d9` |
| Allemand, non pris en charge par le livre | Utiliser la langue de Gramps | `en` | `96d24deae3a6efd89efc47a3ee9a64c1c495d927f72cd37fe01bf31abfadb1d9` |

Les quatre fichiers contiennent les mêmes trois personnes, une famille et la même référence `BOOK_REFERENCE_FAMILY`. Leur contenu est identique après retrait de `BOOK_LANGUAGE` ; les sorties françaises sont identiques octet pour octet entre elles, tout comme les sorties anglaises. Les libellés de l’extension non traduits en allemand restent en anglais, tandis que la boîte native Gramps est en allemand. Cette recette graphique contrôle la sélection et le modèle JSON ; les sorties PDF et HTML ZIP des combinaisons de langue ont été qualifiées séparément par le CLI ci-dessus.

Un cinquième export graphique, avec Gramps en allemand et le livre forcé en français, a produit un [PDF local de démonstration](../output/pdf/gramps-fancy-book-gramps-gui-fr-demo-20261002.pdf) de sept pages A4, balisé, via LuaHBTeX 1.24.0. Son SHA-256 est `89331f631741dfcc30715cba68d36c4360b4458b7545e65dce1f37bb4411c964`. Le texte extrait commence par « Histoire familiale », « Table des matières » et « Ascendance » ; la couverture et la page d’ascendance ont été examinées visuellement. La petite base ne contient ni photo ni citation ; ce PDF illustre le parcours graphique, sans qualifier une composition riche ou une revue intégrale.

## Limites

- Les essais PDF et HTML ZIP ci-dessus invoquent le binaire Gramps Desktop en ligne de commande avec des profils isolés ; la recette graphique complémentaire porte sur le JSON d’une base fictive plus petite.
- La recette ne compare pas toutes les chaînes de notes et d’événements ; elle confirme la conservation du nom saisi. Les données de la fixture sont fictives.
- Les dates structurées sont formatées par Gramps dans la langue du livre et la date libre de la fixture CLI reste intacte ; la petite fixture graphique ne contient pas ces dates.
- Le PDF de démonstration utilise un petit arbre et des portraits synthétiques ; sa mise en page finale, l’accessibilité PDF et la comparaison avec les maquettes privées ne sont pas qualifiées par cette recette.
