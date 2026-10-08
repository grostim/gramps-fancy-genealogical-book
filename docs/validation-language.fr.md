# Validation de la langue du livre

Compte rendu actualisé le 8 octobre 2026. Cette recette cible l’option de langue ajoutée par la PR #100 et utilise uniquement des bases Gramps fictives.

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

## Date structurée avec jour et mois AC-25 — 4 octobre 2026

La fixture native fictive AC-25 a été importée et exportée avec le rapport Gramps Desktop 6.0.8 en ligne de commande, dans des profils isolés. Pour afficher le nom complet du mois, les profils d’essai règlent `preferences.date-format` à `2` ; le format ISO par défaut (`0`) conserve des chiffres pour le mois et ne permet de vérifier que la traduction du qualificatif.

| Langue du livre | Date affichée | Date normalisée |
| --- | --- | --- |
| Français | `vers 14 mars 1900` | `[1900, 3, 14]` |
| Anglais | `about March 14, 1900` | `[1900, 3, 14]` |

Les deux exports ont le même `raw`, les mêmes bornes de comparaison et le même jour structuré ; seul le texte d’affichage change de langue. Le [PDF français AC-25](../output/pdf/gramps-fancy-book-ac25-month-day-fr-20261004.pdf), généré par le même rapport, compte neuf pages A4 balisées. La page 7 a été examinée : « vers 14 mars 1900 » est lisible dans la fiche et ne déborde pas. Cette recette CLI ne valide pas encore le sélecteur de langue par la boîte de dialogue graphique pour cette fixture.

### Recette GUI AC-25 — 6 octobre 2026

La fixture fictive a été exportée depuis l’interface de Gramps Desktop 6.0.8, dans le profil isolé et l’arbre `AC-25 GUI month-day`. La préférence `date-format=2` est confirmée dans `tmp/ac15-desktop-20261005/profile/gramps/gramps60/gramps.ini`. Les deux exports ont utilisé le sélecteur de langue du rapport et le format « Instantané JSON et rapport de cohérence » :

| Langue du livre | `BOOK_LANGUAGE` | Date affichée pour E0000 | Fichier GUI |
| --- | --- | --- | --- |
| Français | `fr` | `vers 14 mars 1900` | `tmp/ac25-month-day/export/gui-fr-dmy.json` |
| Anglais | `en` | `about March 14, 1900` | `tmp/ac25-month-day/export/gui-en-dmy.json` |

Les deux événements conservent exactement le même `raw` (`[0, 3, 0, [14, 3, 1900, false], "", 2415093, 0]`), `ymd` (`[1900, 3, 14]`), `stop_ymd` (`[0, 0, 0]`) et intervalle de comparaison (`[[1850, 3, 14], [1950, 3, 14]]`). Une comparaison complète ne relève aucune autre différence que `BOOK_LANGUAGE`, les chaînes de date affichées et le préfixe du chemin relatif de l’image exportée (`gui-fr-dmy_media` / `gui-en-dmy_media`). Les deux rapports de cohérence ne contiennent ni constat ni diagnostic. Les JSON et rapports de cohérence restent dans `tmp/`, ignoré par Git.

L’ancien `gui-fr.json`, produit avant la correction avec `date-format=4`, reste conservé comme diagnostic (`vers 14. mars 1900`) et ne valide pas AC-25. Cette recette GUI confirme maintenant le sélecteur de langue pour les dates structurées à mois et jour ; la génération PDF/HTML et le contrôle visuel de cette combinaison restent couverts séparément par la recette CLI ci-dessus.

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

## Comparaison graphique sur la base AC-20 riche — 2 octobre 2026

La même base Gramps fictive de 122 personnes et 61 familles a été exportée depuis la fenêtre Desktop 6.0.8 en français automatique, puis avec l'option **Anglais** sous Gramps français. Chaque export PDF et ZIP a reçu sa propre confirmation de confidentialité. Les deux langues comprennent 183 événements, 183 citations et 12 placements d'image.

| Langue du livre | PDF A4 balisé | HTML ZIP |
| --- | --- | --- |
| Français automatique | [87 pages, 5 983 720 octets](../output/pdf/gramps-fancy-book-ac20-gui-20261002.pdf) ; SHA-256 `257159d05201c662b6c546ad4b5202363b9f5d1be578f806cefe5a54c25fff92` | [5 466 042 octets](../output/gramps-fancy-book-ac20-gui-20261002.zip) ; SHA-256 `1f4712d77b938fe9298e7fe9c67d76c88706121d83acc87f7c0e07cc58bc8c89` |
| Anglais forcé | [87 pages, 5 981 269 octets](../output/pdf/gramps-fancy-book-ac20-gui-en-20261002.pdf) ; SHA-256 `1d199d6ece768b241af4400c711889183157d3fc740eee5fd05aa824210e676d` | [5 465 869 octets](../output/gramps-fancy-book-ac20-gui-en-20261002.zip) ; SHA-256 `d701b3ac359ba94ec309ec1dfcaa4548710f4bda26f5f206d53ba0a989a3f757` |

- Les PDF portent respectivement `fr-FR` / `en-US`, les titres « Histoire familiale » / « Family history » et sept signets traduits. Chacun conserve 2 075 destinations nommées et 1 166 liens internes résolus.
- Les ZIP portent `lang="fr"` / `lang="en"`. Leurs ensembles de 870 identifiants et 1 108 liens internes sont exactement identiques ; aucune cible ne manque. Les 12 placements d'image et les deux fichiers PNG inclus sont les mêmes dans les deux archives. Les ancres représentent notamment 122 fiches individuelles, 61 notices familiales, 183 événements et 183 citations.
- Sur la fiche physique 33, `Naissance` et `Principal` deviennent `Birth` et `Primary` ; la date structurée à l'année `1660`, le nom fictif et le portrait restent présents. Les quatre pages anglaises 1, 33, 63 et 87 ont été examinées à 110 ppp : aucun chevauchement ni texte tronqué n'est visible dans ces vues.

Cette fixture ne comporte que des dates structurées à l'année : elle confirme la conservation des années, sans exercer le format des mois et jours dans l'interface graphique. L'ouverture interactive hors ligne de ces ZIP précis, la revue complète du PDF anglais et l'essai au lecteur d'écran restent à faire. Les fichiers liés dans le tableau sont locaux et ignorés par Git ; voir aussi la [recette AC-20 GUI](validation-gramps-gui-ac20.fr.md).

## Contrôle de l’interface française et du catalogue — 8 octobre 2026

Dans Gramps Desktop affiché en français, le rapport est accessible par **Rapports → Pages web → Livre généalogique illustré pour Gramps**. La boîte de dialogue présente en français les options de langue du livre (« Utiliser la langue de Gramps », « Français », « Anglais »), les formats de sortie (mode automatique, HTML ZIP, PDF LuaLaTeX et instantané JSON avec rapport de cohérence), ainsi que l’avertissement de confidentialité. La case de consentement est décochée à l’ouverture. La boîte a été fermée avec **Annuler** : aucun export n’a été lancé et cette vérification ne valide donc pas un parcours de génération graphique.

Le catalogue `fr-local.po` passe `msgfmt --check --check-format --statistics` avec 63 messages traduits, et `msgcmp` le confirme synchronisé au modèle `template.pot`. La comparaison aux chaînes extraites des sources Python se termine sans chaîne manquante ; elle signale huit chaînes non utilisées parce que les messages d’erreur de compilation PDF sont sélectionnés dynamiquement. Les guides de contribution demandent de conserver ces entrées.

Cette recette qualifie l’accès au rapport et les libellés visibles de la boîte française, ainsi que la cohérence statique du catalogue. Elle ne vérifie ni l’affichage effectif des huit erreurs dynamiques, ni l’export par cette boîte, ni Gramps Web.

## Limites

- Les dix essais PDF et HTML ZIP initiaux invoquent le binaire Gramps Desktop en ligne de commande avec des profils isolés ; les exports graphiques complémentaires couvrent le JSON de la petite base et les PDF/ZIP FR/EN de la base AC-20 riche. Le contrôle d’interface du 8 octobre a été annulé avant export.
- La recette ne compare pas toutes les chaînes de notes et d’événements ; elle confirme la conservation du nom saisi. Les données de la fixture sont fictives.
- Les dates structurées sont formatées par Gramps dans la langue du livre et la date libre de la fixture CLI reste intacte ; la base graphique AC-20 ne contient que des années, sans mois ni jour.
- Le PDF de démonstration utilise un petit arbre et des portraits synthétiques ; sa mise en page finale, l’accessibilité PDF et la comparaison avec les maquettes privées ne sont pas qualifiées par cette recette.
