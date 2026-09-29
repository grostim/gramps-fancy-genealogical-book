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

## Aperçu AC-20 — revue du 29 septembre 2026

- Fichier local non suivi : `gramps-fancy-book-ac20-parity-preview.pdf`, dans le worktree de validation `l85-build-validation` ; SHA-256 `f0482918f12faaca707d9d421906e0f79c8e7405369a83859b322b66a76047c1`.
- Taille : 470 833 octets ; 118 pages A4 ; LuaTeX 1.24.0 ; jeu synthétique de 122 personnes.
- Les pages physiques 1, 2, 4, 19, 40, 49, 75, 90, 115 et 118 ont été examinées à 110 ppp. Aucun chevauchement ni texte tronqué n’a été observé dans cet échantillon ; titres, sommaire, fiches, avis familiaux, annexe et index restent lisibles. La page 49 utilise un portrait synthétique uniquement destiné à la mise en page.
- Ce PDF précède le paramètre de langue du livre et affiche donc les titres en anglais. `pdfinfo` indique `Tagged: no` ; revue complète, accessibilité et comparaison aux maquettes privées restent à faire.

## Aperçu français du paramètre de langue — 29 septembre 2026

- Fichier local non suivi : `output/pdf/gramps-fancy-book-language-preview-fr.pdf` ; SHA-256 `cdcaafe8c417a06e989fa264e4dc14342fbaa38d135cd462b5e43f26cb70756d`.
- PDF A4 de 18 pages physiques, 56 659 octets ; LuaTeX 1.24.0. Le modèle compact est synthétique et couvre la couverture, le sommaire, l’ascendance, la descendance, les liens et notices familiales, les fiches, l’annexe et l’index.
- La version de 18 pages a été compilée avec le paramètre `fr`. Les pages physiques 2, 9, 10 et 18 ont été recontrôlées après la compilation finale : le sommaire et l’index sont lisibles, et la fiche longue se poursuit sur la page suivante sans chevauchement visible. Les autres sections ont été examinées sur le même prototype lors de la revue précédente.
- Les données, noms, dates et descriptions sont fictifs. Cette sortie confirme le rendu des libellés français dans un prototype, pas encore l’intégration complète dans l’interface Gramps avec une base généalogique réelle. `pdfinfo` indique `Tagged: no` ; l’accessibilité et la comparaison aux maquettes privées restent à faire.
