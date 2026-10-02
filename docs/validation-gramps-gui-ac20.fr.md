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

## Limites de cette recette

Le navigateur intégré de cette session refuse le protocole `file://` pour des raisons de sécurité ; l'ouverture interactive hors ligne de **ce** ZIP GUI n'a donc pas été refaite. L'intégrité de l'archive, les ressources relatives et les ancres ont été contrôlées statiquement. Des archives antérieures AC-20 avaient déjà été ouvertes hors ligne dans Chrome, mais elles ne prouvent pas le comportement interactif de cette sortie précise.

Les images et données sont fictives. La revue à haute résolution couvre quatre pages, pas les 87. Il reste à essayer ce PDF et ce ZIP avec un lecteur d'écran, à comparer complètement les deux rendus et à qualifier le PDF selon les critères d'accessibilité applicables ; aucune conformité PDF/UA n'est revendiquée.

Les [exports GUI anglais de la même base](validation-language.fr.md) sont qualifiés séparément.
