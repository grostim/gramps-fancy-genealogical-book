# Export AC-20 depuis Gramps Desktop — 2 octobre 2026

## Périmètre

- Gramps Desktop 6.0.8 sur macOS, profil temporaire isolé, paquet construit depuis `21cfb8ceec09bb30392fd212455fa0413bffad5c`.
- Base GEDCOM fictive importée dans Gramps : 122 personnes, 61 familles, 183 événements, 17 notes, 183 citations et 12 médias. Les portraits et paysages sont des images de démonstration ; aucune généalogie personnelle n'a été utilisée.
- Depuis **Rapports → Pages web → Livre généalogique illustré pour Gramps**, famille centrale « Exemple, Alex et Exemple, Camille (F0001) », langue **Auto** sous Gramps français, format **Auto**. La confirmation de confidentialité, décochée à chaque ouverture du rapport, a été cochée pour chacun des deux exports.

## Résultats

| Sortie | Fichier local non suivi par Git | Mesure | SHA-256 |
| --- | --- | --- | --- |
| PDF | [`output/pdf/gramps-fancy-book-ac20-gui-20261002.pdf`](../output/pdf/gramps-fancy-book-ac20-gui-20261002.pdf) | 87 pages A4 ; 5 983 720 octets | `257159d05201c662b6c546ad4b5202363b9f5d1be578f806cefe5a54c25fff92` |
| HTML ZIP | [`output/gramps-fancy-book-ac20-gui-20261002.zip`](../output/gramps-fancy-book-ac20-gui-20261002.zip) | 5 466 042 octets | `1f4712d77b938fe9298e7fe9c67d76c88706121d83acc87f7c0e07cc58bc8c89` |

- Gramps est revenu au tableau de bord de la base de 122 personnes après chaque export, sans erreur affichée. LuaHBTeX 1.24.0 a produit un PDF 2.0 balisé, avec titre « Histoire familiale », langue `fr-FR` et sept sections de navigation.
- Les 1 166 annotations de lien interne PDF sont des actions `GoTo` dont les destinations existent. Le fichier expose 2 075 destinations nommées.
- Le ZIP passe `unzip -t`. Son HTML `lang="fr"` contient 122 ancres de fiche, 61 de notice familiale, 183 d'événement et 183 de citation. Ses 1 108 liens pointent tous vers une ancre locale existante ; les 870 identifiants sont uniques. Les 12 images HTML ont un texte alternatif et réutilisent deux fichiers PNG dédupliqués dans l'archive.
- Les 87 pages PDF ont été rendues à 45 ppp et parcourues sur dix planches de contact. Les pages physiques 33 (portrait), 56 (paysage et fin de fiche), 63 (citations) et 87 (index) ont été examinées à 140 ppp. Aucun chevauchement, texte tronqué ou folio manquant n'est visible dans ces vues.
- Les deux PNG du ZIP sont des photographies fictives en niveaux de gris de 1 024 × 1 536 px (personne) et 1 536 × 1 024 px (maison). Ils sont réutilisés dans 12 placements. Ils sont distincts des images minimales de la petite fixture GUI décrite dans la [validation L7](validation-l7.fr.md).

## Limites de cette recette

Le navigateur intégré de cette session refuse le protocole `file://` pour des raisons de sécurité ; l'ouverture interactive hors ligne de **ce** ZIP GUI n'a donc pas été refaite. L'intégrité de l'archive, les ressources relatives et les ancres ont été contrôlées statiquement. Des archives antérieures AC-20 avaient déjà été ouvertes hors ligne dans Chrome, mais elles ne prouvent pas le comportement interactif de cette sortie précise.

Les images et données sont fictives. La revue à haute résolution couvre quatre pages, pas les 87. Il reste à essayer ce PDF et ce ZIP avec un lecteur d'écran, à comparer complètement les deux rendus et à qualifier le PDF selon les critères d'accessibilité applicables ; aucune conformité PDF/UA n'est revendiquée.

Les [exports GUI anglais de la même base](validation-language.fr.md) sont qualifiés séparément.

## Réexport du paquet à marges de 20 mm — 3 octobre 2026

Le paquet construit depuis `main` au commit `4d18a22` a été installé dans une **copie isolée** du profil fictif AC-20 ci-dessus. Le rapport a été lancé par la ligne de commande de Gramps Desktop 6.0.8, avec la même famille F0001, la langue française et le format PDF. Cette exécution exerce la base et l'adaptateur Gramps réels, mais **pas la boîte de dialogue graphique**. Les arbres visibles dans le profil Gramps habituel n'ont pas été modifiés.

| Sortie | Fichier local non suivi par Git | Mesure | SHA-256 |
| --- | --- | --- | --- |
| PDF à marges de 20 mm | [`output/pdf/gramps-fancy-book-ac20-gramps-cli-20mm-20261003.pdf`](../output/pdf/gramps-fancy-book-ac20-gramps-cli-20mm-20261003.pdf) | 75 pages A4 ; 5 960 842 octets | `840f7338b0a3d9518ea7c3919c753d9e916ed62ffa68b3e3fd8e7dea6accc761` |

- Le PDF balisé porte le titre « Histoire familiale » et la langue `fr-FR`. Il compte 12 pages de moins que l'ancien export GUI de 87 pages. Le bord gauche du texte passe d'environ 44 mm à 20 mm ; la différence de pagination est cohérente avec l'espace de composition accru.
- Les 12 placements d'image et les 183 notices de source sont conservés. Les 2 063 destinations nommées du nouveau PDF correspondent à celles de l'ancien, à l'exception de 12 destinations `page.*` liées aux pages disparues. Les 1 048 liens internes de la nouvelle pagination atteignent tous une destination. Les 12 éléments `Figure` du balisage possèdent chacun un texte alternatif.
- Les 75 pages ont été parcourues sur trois planches de contact à basse résolution. Les pages physiques 1, 3, 27 (portrait), 51 (paysage), 56 (annexe) et 75 (index) ont été examinées séparément à 1 200 px. Aucun chevauchement ni texte tronqué n'a été observé dans ces vues ; la photographie de paysage et sa légende restent dans la zone de composition.
- La couverture et les pages généalogiques courtes restent aérées parce que ce jeu fictif n'apporte pas de notes éditoriales ni de portraits du couple central et que les grandes parties commencent sur une nouvelle page. La revue ne constitue pas un essai au lecteur d'écran ni une preuve de conformité PDF/UA. Il reste à qualifier un livre avec des médias familiaux représentatifs.

## Export graphique à marges de 20 mm — 3 octobre 2026

Une copie locale de Gramps Desktop 6.0.8 dotée d'un identifiant d'application distinct a ouvert le profil fictif isolé **FancyBook GUI AC20**, sans passer par l'arbre personnel du Mac. Le paquet de ce profil contient déjà la marge de production de 20 mm. La famille F0001 a été conservée dans la boîte de dialogue ; le format automatique a reconnu une destination `.pdf`, l'option de confidentialité a été cochée et le délai PDF prolongé a été activé. Gramps est revenu au tableau de bord après l'export, sans erreur affichée.

| Sortie | Fichier local non suivi par Git | Mesure | SHA-256 |
| --- | --- | --- | --- |
| PDF graphique à 20 mm | [`output/pdf/gramps-fancy-book-ac20-gui-20mm-20261003.pdf`](../output/pdf/gramps-fancy-book-ac20-gui-20mm-20261003.pdf) | 75 pages A4 ; 5 960 833 octets ; PDF 2.0 balisé | `4722102dcc084781d0b47e669edd107833922c42c8ea660b568c84aab0e1cee3` |

`pdfinfo` donne le titre « Histoire familiale » et `Tagged: yes`. Le PDF comporte 12 images. Le texte extrait des 75 pages avec `pdftotext -layout` est identique, par SHA-256, à celui du PDF obtenu par Gramps CLI ci-dessus (`0b0ba78b3156842db42fc8487015efcfaa05380d5c668cf514845d2daa752668`). Les pages physiques 1 (couverture), 3 (généalogie), 27 (portrait), 51 (photo de maison), 56 (annexe) et 75 (index) ont été rendues à 110 ppp ; les pages 1, 27, 51 et 75 ont été ouvertes séparément et ne montrent pas de débordement visible.

Cette recette confirme le parcours de la boîte de dialogue et la pagination de 75 pages sur ce profil fictif. Elle ne remplace pas la revue de toutes les pages, l'essai au lecteur d'écran ni la qualification PDF/UA. La copie isolée de l'application reste locale, hors Git.

## Revue complète du PDF graphique à marges de 20 mm — 4 octobre 2026

Le PDF graphique de 75 pages identifié ci-dessus (SHA-256 `4722102dcc084781d0b47e669edd107833922c42c8ea660b568c84aab0e1cee3`) a été rendu page par page et parcouru sur dix planches de contact couvrant les 75 pages. Les pages physiques 1, 3, 18, 37 et 75 ont ensuite été examinées séparément à environ 120 ppp ; les pages 9, 15, 29, 47, 56, 57 et 71 à 130 ppp. Cet échantillon couvre la couverture, les parcours généalogiques, les liens familiaux, les notices, les fiches avec portraits, l'annexe documentaire et l'index.

Aucun chevauchement, texte coupé, folio manquant ni rupture de mise en page n'a été relevé sur les planches ou les pages détaillées. Les portraits et la photo de paysage conservent leurs proportions et leurs légendes. Les marges de composition restent régulières ; les pages plus aérées ou partiellement remplies correspondent aux ruptures de section et aux données fictives de cette base, sans contenu manquant visible.

Cette revue complète porte sur le PDF synthétique exporté depuis Gramps Desktop. Elle ne qualifie pas les photos familiales réelles, l'ordre de lecture au lecteur d'écran ni la conformité PDF/UA. L'essai au lecteur d'écran et la comparaison d'accessibilité restent ouverts.

## Texte alternatif des images HTML — 3 octobre 2026

L'ancien ZIP AC-20 attribuait « Portrait de [personne] » aux 12 images principales. Cette formule décrivait à tort les deux placements de la photo de maison. Le renderer HTML donne maintenant priorité à la description enregistrée du média ; en son absence, il conserve le libellé localisé avec le nom de la personne. Le PDF utilisait déjà cette priorité.

Un [nouvel export ZIP par Gramps CLI](../output/gramps-fancy-book-ac20-alt-descriptions-20261003.zip), issu du même profil fictif isolé, contient les mêmes deux PNG octet pour octet. Seuls les 12 attributs `alt` de `index.html` diffèrent de l'ancien export ; ils reprennent ici les titres génériques « Synthetic benchmark image … » de la fixture. L'archive fait 5 466 039 octets, passe le contrôle CRC et porte le SHA-256 `e8ecc81307db16fef16c7e53510a96cc5ef9cd1e3e0935fc1984c70e013fe763`. Des descriptions Gramps plus informatives amélioreraient ces textes ; le plugin ne peut pas déduire qu'une image représente une maison à partir de ses seuls pixels.

Le contrôle CRC et la vérification statique des liens de cette archive sont consignés ici. Le navigateur intégré refuse son ouverture directe sous `file://`; la revue via un serveur local sur `127.0.0.1` du 4 octobre est décrite ci-dessous.

## Revue navigateur de l’export CLI à descriptions corrigées — 4 octobre 2026

L’archive CLI ci-dessus a été extraite puis ouverte via un serveur local sur `127.0.0.1`. À 1 280 × 720 px, le HTML français compte 871 identifiants uniques et 1 108 liens internes, tous résolus. Les 12 placements chargent deux PNG locaux ; tous les textes alternatifs sont non vides, aucun lien n’est sans nom, aucun niveau de titre n’est sauté et aucun débordement horizontal n’apparaît. La couverture et l’annexe ont été examinées visuellement ; le lien du sommaire vers l’annexe atteint sa cible.

Les images de démonstration (portrait 1 024 × 1 536 px et maison 1 536 × 1 024 px) s’affichent sans déformation. Leur texte alternatif reprend la description générique de la fixture (`Synthetic benchmark image …`) ; une description utile doit être renseignée dans Gramps. Cette revue porte sur l’export CLI à 1 280 px : elle ne qualifie ni les petits écrans, ni tout le parcours clavier, ni les annonces d’un lecteur d’écran. Elle ne remplace pas l’export AC-20 depuis la boîte de dialogue avec le paquet courant, qui reste à refaire.
