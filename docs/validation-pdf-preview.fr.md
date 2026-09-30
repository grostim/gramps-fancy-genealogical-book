# Revue de l’aperçu PDF synthétique

## Document

- Fichier : `output/pdf/gramps-fancy-book-preview.pdf` (artefact local généré, non suivi dans Git)
- SHA-256 : `a06793d3e69460380cd8304c5b586bc4c132f4def5b351ed0bbcbcf5efdc4d72`
- Taille : 739 729 octets ; 193 pages A4 ; LuaTeX 1.24.0
- Jeu de données fictif : 202 personnes et 101 familles
- Signets PDF : sept sections — ascendance, descendance, liens familiaux, notices familiales, fiches individuelles, annexe documentaire et index des personnes

## Revue visuelle

Les pages PDF 1–4, 10, 27, 55, 100, 121, 130, 187 et 193 ont été rendues à 110 ppp et examinées visuellement. L’échantillon couvre la couverture, le sommaire, les sections généalogiques, les notices familiales, les fiches, un portrait, l’annexe et l’index.

Aucun texte coupé, chevauchement ni folio manquant n’est visible sur les pages examinées. Les titres de sections, entrées du sommaire, renvois, notices de sources et entrées d’index restent dans les marges. Les longues URL se répartissent sur plusieurs lignes ; certaines coupures tombent au milieu d’un nom d’hôte, leur lisibilité doit donc encore être évaluée. Cet échantillon ne prouve pas l’absence de défaut sur toutes les pages.

## Limites et travail restant

- Les portraits de ce benchmark sont générés à partir de pixels aléatoires déterministes dans `scripts/benchmark_book.py` ; ils ne représentent pas de vraies photographies. La page d’image sert uniquement à exercer le placement et le recadrage.
- La couverture et les pages généalogiques clairsemées reflètent le jeu de données fictif ; elles ne valident pas le design final.
- `pdfinfo` indique `Tagged: no` ; l’accessibilité du PDF n’est pas qualifiée.
- Les pages examinées n’ont pas été comparées aux maquettes privées de référence. La revue intégrale, la lisibilité des URL longues, les vérifications lecteur d’écran/accessibilité et la comparaison aux principes de conception de la v1.1 restent à faire.

## Contrôle du 29 septembre 2026 — en-têtes, médias et URL

- Fichier local non suivi : `output/pdf/gramps-fancy-book-url-wrap-preview.pdf` ; SHA-256 `a051ee895f93d641747aaf759ac76b6465fac519adba7270f82509c001645173`.
- Jeu fictif ramifié : 122 personnes, 60 unions descendantes et 12 dérivés de média ; PDF A4 de 118 pages compilé par LuaLaTeX sans avertissement de mise en page.
- Les pages 3 (ascendance), 49 (média `BOOK_FEATURED`) et 75 (annexe documentaire) ont été rendues à 110 ppp. L’en-tête de génération/branche est lisible en ascendance ; la page pleine conserve son en-tête de section et son folio ; les URLs de l’annexe se coupent aux séparateurs visibles sans fragmenter un mot du nom d’hôte. Aucun chevauchement ou contenu tronqué n’a été observé sur ces pages.
- Les images du jeu sont des pixels synthétiques, pas des photographies. Cette inspection ciblée ne qualifie ni l’ensemble des pages, ni l’accessibilité (`pdfinfo` indique toujours `Tagged: no`), ni la comparaison avec les maquettes privées.

## Aperçu AC-20 historique — génération du 29 septembre 2026

- Fichiers locaux non suivis : `output/pdf/gramps-fancy-book-ac20-parity-preview.pdf` et `output/gramps-fancy-book-ac20-parity-preview.zip` ; le PDF conserve le SHA-256 `f0482918f12faaca707d9d421906e0f79c8e7405369a83859b322b66a76047c1`.
- Le PDF (470 833 octets, 118 pages A4, LuaTeX 1.24.0) a été généré depuis l’état antérieur au commit `ac7a706`. Il précède la numérotation éditoriale actuelle des citations et la sortie française AC-20 ci-dessous ; sa revue visuelle ne vaut pas pour l’export actuel.
- À titre d’historique, ses 118 pages avaient été parcourues sur 12 planches de contact à 75 ppp et huit pages à 150 ppp. `pdfinfo` indiquait `Tagged: no` ; l’accessibilité et la comparaison aux maquettes privées restent à faire.

## Aperçu français AC-20 courant — revue du 30 septembre 2026

- Fichiers locaux non suivis, produits depuis `main` au commit `ac7a706` : `output/pdf/gramps-fancy-book-ac20-current-preview.pdf` (SHA-256 `ede8c2c5ed3aa88cadcd09ce397d73971f7fc7f3b2b43fd62bb21ea93aded38a`) et `output/gramps-fancy-book-ac20-current-preview.zip` (SHA-256 `3f474d1a067f169d819438e0fd5664cd62063514f0664a5b041fbaa21f974bf1`).
- Même jeu ramifié synthétique pour les deux formats : 122 personnes, 61 familles, 183 événements, 17 notes, 183 citations et 12 médias dérivés. Le PDF fait 459 319 octets et 97 pages A4 ; LuaHBTeX 1.24.0 l’a produit. Les données et les portraits en pixels sont fictifs.
- Les 97 pages ont été parcourues sur dix planches de contact à 75 ppp. Les pages physiques 2, 13, 28, 48, 63, 80, 94 et 97 ont aussi été inspectées à 150 ppp. Aucun chevauchement ni texte tronqué n’a été observé ; les URL longues restent lisibles dans les pages examinées.
- `pdfinfo` indique `Tagged: no` : l’accessibilité PDF reste à qualifier. La comparaison aux maquettes privées et aux principes de conception de la v1.1 reste à faire.

## Aperçu français du paramètre de langue — 29 septembre 2026

- Fichier local non suivi : `output/pdf/gramps-fancy-book-language-preview-fr.pdf` ; SHA-256 `cdcaafe8c417a06e989fa264e4dc14342fbaa38d135cd462b5e43f26cb70756d`.
- PDF A4 de 18 pages physiques, 56 659 octets ; LuaTeX 1.24.0. Le modèle compact est synthétique et couvre la couverture, le sommaire, l’ascendance, la descendance, les liens et notices familiales, les fiches, l’annexe et l’index.
- La version de 18 pages a été compilée avec le paramètre `fr`. Les pages physiques 2, 9, 10 et 18 ont été recontrôlées après la compilation finale : le sommaire et l’index sont lisibles, et la fiche longue se poursuit sur la page suivante sans chevauchement visible. Les autres sections ont été examinées sur le même prototype lors de la revue précédente.
- Les données, noms, dates et descriptions sont fictifs. Cette sortie confirme le rendu des libellés français dans un prototype, pas encore l’intégration complète dans l’interface Gramps avec une base généalogique réelle. `pdfinfo` indique `Tagged: no` ; l’accessibilité et la comparaison aux maquettes privées restent à faire.

## Aperçu commun après la PR #106 — 29 septembre 2026

- Fichier local non suivi : `output/pdf/gramps-fancy-book-step-preview-fr.pdf`, généré depuis `main` au commit `5fb7bc7` avec les fonctions de rendu du dépôt. SHA-256 `b3d16126c94ebba0c4dcd0c7424017a15153c976241ff430f2588e90880e6b66`.
- Le modèle fictif comprend 22 personnes, 11 familles, 33 événements, 3 notes, 33 citations et deux dérivés PNG ; l’archive HTML associée a été générée depuis le même modèle. Le PDF compte 22 pages A4 (109 106 octets), compilées sous LuaHBTeX 1.24.0.
- Les 22 pages ont été rendues à 90 ppp. Une planche générale et les pages physiques 7, 16, 19 et 22 ont été examinées séparément ; aucun chevauchement ni texte tronqué n’a été observé dans ces vues. L’annexe contient des URL longues et les portraits sont des pixels synthétiques.
- `pdfinfo` indique `Tagged: no`. L’accessibilité, la comparaison avec les maquettes privées et la revue complète à haute résolution restent à faire.

La relecture haute résolution du 30 septembre confirme que ce fichier historique ne représente plus l’en-tête courant : aux pages physiques 16 et 17, le folio touche visuellement le libellé de section. Le fichier a été généré depuis le commit `5fb7bc7`, avant la correction d’en-tête de la PR #114. Le PDF AC-15 courant ci-dessous sert de preuve pour l’en-tête corrigé.

## PDF natif AC-15 — revue complète du 30 septembre 2026

- Fichier local non suivi : `output/pdf/gramps-fancy-book-ac15-shared-media-review.pdf` ; SHA-256 `f1ac11b304668363c92bcd31415b663ddd39c4ca16b56eea502f78ea5e2fe0df`.
- PDF A4 de 9 pages, 45 802 octets, LuaTeX 1.24.0. Fixture Gramps synthétique AC-15/AC-23 avec une reproduction citée deux fois et des chaînes d’injection réservées au contrôle de sécurité.
- Les neuf pages ont été rendues à 160 ppp et inspectées : couverture, sommaire, ascendance, descendance, liens familiaux, notice, fiche, annexe de sources et index. Les lignes d’en-tête et de folio sont séparées ; aucun chevauchement ni texte coupé n’a été observé.
- Les chaînes `<img ... onerror=...>` et `<script>...</script>` apparaissent comme du texte dans la fiche et la notice. L’annexe affiche une seule reproduction partagée ; l’autre citation renvoie vers cette reproduction. Les URL de cette fixture restent lisibles dans la largeur disponible.
- `pdfinfo` indique `Tagged: no`. Cette fixture de sécurité contient des données fictives et ne valide pas le design final, l’accessibilité ni la comparaison avec les maquettes privées.
