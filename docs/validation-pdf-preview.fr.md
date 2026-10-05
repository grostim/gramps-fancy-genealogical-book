# Revue de l’aperçu PDF synthétique

La recette du [PDF AC-20 exporté depuis la fenêtre Gramps Desktop](validation-gramps-gui-ac20.fr.md) le 2 octobre 2026 est consignée séparément ; elle couvre 87 pages et un ZIP issu du même profil fictif.

## Marges de production — 3 octobre 2026

- Le renderer PDF fixe désormais les quatre marges A4 à 20 mm, comme le prototype LaTeX L2. L'en-tête est inclus dans le calcul de la page, avec une hauteur de 30 pt et une séparation de 12 pt. Avant cette correction, le texte du PDF GUI commençait à environ 44 mm du bord gauche, sous les valeurs implicites de la classe `article`.
- [Aperçu local de 71 pages](../output/pdf/gramps-fancy-book-20mm-long-preview-20261003.pdf), SHA-256 `6b1beba28f2970582001562c660e7d6f181ac1c941e6516d8abb8f1fbfb7a864` : livre fictif ramifié de 122 personnes et 60 unions descendantes, avec portraits synthétiques. LuaHBTeX 1.24.0 a produit un PDF A4 balisé de 613 542 octets ; les renvois ont convergé sans avertissement de débordement.
- Les pages physiques 1, 3, 33, 55 et 71 ont été rendues et examinées. Le texte commence à 56,693 pt (20 mm) du bord gauche ; l'en-tête, les fiches, l'annexe et l'index restent lisibles dans cet échantillon. La couverture est clairsemée parce que ce jeu ne fournit ni titre éditorial ni portraits du couple de référence.
- Cet aperçu vient du moteur direct et d'un jeu fictif en anglais. L'export GUI avec la nouvelle marge, les photographies représentatives et la revue visuelle complète restent à qualifier.

## Sections unitaires des fiches — 1er octobre 2026

- Aperçu local : `output/pdf/gramps-fancy-book-single-event-profile-preview-20261001.pdf` ; SHA-256 `6ae26746fcc1588982c7be0786226f6ad8de146636280bc5e9846cafc698c3ac`.
- La fixture ramifiée fictive contient 202 personnes, 101 familles, 303 événements, 20 portraits et 303 citations. LuaHBTeX 1.24.0 a produit un PDF A4 balisé de 177 pages et 1 470 734 octets. Les données et portraits sont fictifs.
- Les pages physiques 57–58 ont été rendues à 130 ppp et examinées. Les événements uniques et renvois de source apparaissent en lignes compactes sous leurs titres. Le portrait et sa légende restent centrés ; aucune coupure ni superposition n’a été observée sur ces pages.
- Le candidat conserve exactement les 1 805 cibles nommées du livre, les 3 073 annotations de liens et les 2 669 éléments structurels `Link` de l’aperçu précédent. Il contient 292 `L` et 1 174 `LI`, soit 404 de moins chacun.
- Cette revue ciblée ne couvre pas toutes les pages en haute résolution, des données Gramps réelles, un lecteur d’écran, l’export depuis Desktop ou la conformité PDF/UA. Aucune conformité PDF/UA n’est revendiquée.

## Renvoi direct pour une citation — 1er octobre 2026

- Aperçu local : `output/pdf/gramps-fancy-book-single-call-citation-preview-20261001.pdf` ; SHA-256 `3cf5f9b8025258db353f71d2292875c5bc0e5d244d5bbbda47f9cd143dfc2578`.
- La fixture ramifiée fictive contient 202 personnes, 101 familles, 303 événements, 20 portraits et 303 citations. LuaHBTeX 1.24.0 a produit un PDF A4 balisé de 193 pages et 1 583 991 octets. Les données et portraits sont fictifs.
- La page physique 123 a été rendue à 130 ppp et examinée. Les citations utilisées une fois affichent un renvoi localisé « Voir » vers la fiche ou la notice familiale associée ; les citations ayant plusieurs appels gardent une liste à puces. Aucun chevauchement ni texte coupé n’a été observé sur cette page.
- Les 1 805 cibles nommées du livre sont conservées. L’arbre compte 696 éléments `L`, 1 578 `LI` et 2 669 `Link`, contre respectivement 972, 1 854 et 2 669 dans l’aperçu précédent.
- Cette revue ciblée ne couvre pas toutes les pages en haute résolution, des données Gramps réelles, un lecteur d’écran, l’export depuis Desktop ou la conformité PDF/UA. Aucune conformité PDF/UA n’est revendiquée.

## Filiation regroupée — 1er octobre 2026

- Aperçu local non suivi : `output/pdf/gramps-fancy-book-parentage-grouping-preview-20261001.pdf` ; SHA-256 `69da39763be7ff34901663cdddf89fa81db178b0741f467b78050b6e4a0642d2`.
- La fixture ramifiée contient 202 personnes, 101 familles, 303 événements, 20 portraits synthétiques et 101 sections familiales. LuaHBTeX 1.24.0 a produit un PDF A4 balisé de 195 pages (1 628 695 octets). Les données et les portraits sont fictifs.
- Les pages physiques 12–13, qui montrent les liens familiaux regroupés, ont été rendues à 130 ppp puis examinées. Chaque enfant est affiché une fois ; les parents et types de relation correspondants restent visibles. Certains libellés de relation passent seuls sur la ligne suivante ; aucun chevauchement ni texte coupé n’a été observé sur ces pages.
- Cette inspection ciblée ne couvre pas les autres pages en haute résolution, les données Gramps réelles, l’essai avec lecteur d’écran, l’export depuis Desktop ou la conformité PDF/UA. Aucune conformité PDF/UA n’est revendiquée.

## Aperçu courant — 1er octobre 2026

- Fichier local non suivi par Git : `output/pdf/gramps-fancy-book-preview.pdf` ; SHA-256 `1196e8e97c80033c20a97ae34ef36a515b2f244d5fc8a1331a723c93f27bc2c2`.
- Le PDF fait 647 443 octets et 55 pages A4. LuaHBTeX 1.24.0 l’a compilé ; `pdfinfo` indique un PDF 2.0 balisé (`Tagged: yes`). Le jeu fictif contient 202 personnes et 101 familles.
- Les 55 pages ont été rendues à 100 ppp et parcourues sur trois planches de contact. Les pages physiques 11, 12, 18, 25, 33 et 49 ont aussi été inspectées à cette résolution. Aucun chevauchement, texte coupé ou folio manquant n’a été observé, y compris dans les liens familiaux et l’index.
- Pour permettre ce volume de liens familiaux imbriqués, le renderer ferme puis rouvre la sous-liste toutes les 20 filiations. Cela évite l’erreur de hooks `tagpdf` déséquilibrés constatée pendant la compilation tout en gardant la structure de liste. La compilation finale s’est achevée sans avertissement de mise en page.
- Les enregistrements et visuels sont synthétiques. Le PDF balisé n’a pas été qualifié avec un lecteur d’écran et aucune conformité PDF/UA n’est revendiquée. La comparaison aux maquettes privées et l’essai avec des photographies représentatives restent à faire.

## Aperçu précédent de 193 pages — historique

- Ancien artefact local, désormais remplacé au même chemin par l’aperçu courant ci-dessus ; son ancien SHA-256 était `a06793d3e69460380cd8304c5b586bc4c132f4def5b351ed0bbcbcf5efdc4d72`.
- Taille : 739 729 octets ; 193 pages A4 ; LuaTeX 1.24.0
- Jeu de données fictif : 202 personnes et 101 familles
- Signets PDF : sept sections — ascendance, descendance, liens familiaux, notices familiales, fiches individuelles, annexe documentaire et index des personnes

## Revue visuelle

Les pages PDF 1–4, 10, 27, 55, 100, 121, 130, 187 et 193 ont été rendues à 110 ppp et examinées visuellement. L’échantillon couvre la couverture, le sommaire, les sections généalogiques, les notices familiales, les fiches, un portrait, l’annexe et l’index.

Aucun texte coupé, chevauchement ni folio manquant n’était visible sur les pages alors examinées. Les titres de sections, entrées du sommaire, renvois, notices de sources et entrées d’index restaient dans les marges. Les longues URL se répartissaient sur plusieurs lignes ; certaines coupures tombaient au milieu d’un nom d’hôte. Cette ancienne revue ne prouvait pas l’absence de défaut sur toutes les pages ; le fichier a depuis été remplacé par l’aperçu courant.

## Limites et travail restant

- Les portraits de ce benchmark sont générés à partir de pixels aléatoires déterministes dans `scripts/benchmark_book.py` ; ils ne représentent pas de vraies photographies. La page d’image sert uniquement à exercer le placement et le recadrage.
- La couverture et les pages généalogiques clairsemées reflètent le jeu de données fictif ; elles ne valident pas le design final.
- `pdfinfo` indiquait alors `Tagged: no` ; l’accessibilité de cet ancien PDF n’était pas qualifiée.
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

## Aperçu français AC-20 précédent — revue du 30 septembre 2026

- Fichiers locaux non suivis, produits depuis `main` au commit `ac7a706` : `output/pdf/gramps-fancy-book-ac20-current-preview.pdf` (SHA-256 `ede8c2c5ed3aa88cadcd09ce397d73971f7fc7f3b2b43fd62bb21ea93aded38a`) et `output/gramps-fancy-book-ac20-current-preview.zip` (SHA-256 `3f474d1a067f169d819438e0fd5664cd62063514f0664a5b041fbaa21f974bf1`).
- Même jeu ramifié synthétique pour les deux formats : 122 personnes, 61 familles, 183 événements, 17 notes, 183 citations et 12 médias dérivés. Le PDF fait 459 319 octets et 97 pages A4 ; LuaHBTeX 1.24.0 l’a produit. Les données et les portraits en pixels sont fictifs.
- Les 97 pages ont été parcourues sur dix planches de contact à 75 ppp. Les pages physiques 2, 13, 28, 48, 63, 80, 94 et 97 ont aussi été inspectées à 150 ppp. Aucun chevauchement ni texte tronqué n’a été observé ; les URL longues restent lisibles dans les pages examinées.
- `pdfinfo` indique `Tagged: no` : l’accessibilité PDF reste à qualifier. La comparaison aux maquettes privées et aux principes de conception de la v1.1 reste à faire.

## Aperçu AC-20 avec navigation PDF par génération — 30 septembre 2026

- Fichiers locaux non suivis, compilés avec les changements de cette branche : output/pdf/gramps-fancy-book-ac20-generation-navigation-preview-20260930.pdf (SHA-256 acd9dc0d1d84c6026775fa38c861405d52befa94e5e9abbfb20992f8f1057ea2) et output/gramps-fancy-book-ac20-generation-navigation-preview-20260930.zip (SHA-256 3f474d1a067f169d819438e0fd5664cd62063514f0664a5b041fbaa21f974bf1). Le ZIP est identique octet par octet à l’archive de l’aperçu précédent.
- Le modèle contient 122 personnes, 61 familles, 183 événements, 17 notes, 183 citations et 12 médias dérivés. Le PDF fait 1 186 027 octets et 118 pages A4 ; LuaHBTeX 1.24.0 l’a compilé. pdfinfo indique Tagged: yes.
- Les 118 pages ont été parcourues sur dix planches de contact à 60 ppp. Les pages physiques 3 et 4, qui présentent la navigation d’ascendance et de descendance, ont été rendues à 110 ppp ; les pages 75 (annexe documentaire) et 118 (index) ont ensuite été inspectées à 150 ppp. Aucun chevauchement ni texte tronqué n’a été observé dans ces vues. Certaines URL longues se coupent au milieu d’un nom d’hôte ; leur lisibilité reste à examiner. Les 2 421 liens internes PDF sont résolus et les sept cibles de génération correspondent aux ancres HTML.
- Au moment de cette première revue ciblée, la comparaison aux maquettes privées n’avait pas encore été faite. La comparaison côte à côte ultérieure de six pages est décrite ci-dessous ; une comparaison complète en haute résolution reste à faire. Cette revue ne remplace pas non plus un export depuis l’interface Gramps ni la qualification d’accessibilité PDF. À la génération de cet aperçu, six fragments HTML de premier niveau n’avaient pas de destination PDF stable. La PR #147 a aligné les cinq ancres de contenu ; `main-content` reste un lien d’évitement propre au HTML. Le contrôle courant des fragments est décrit ci-dessous.

## Aperçu AC-20 balisé avec ancres HTML/PDF alignées — 30 septembre 2026

- Fichier local non suivi : [`output/pdf/gramps-fancy-book-ac20-shared-section-anchor-preview-20260930.pdf`](../output/pdf/gramps-fancy-book-ac20-shared-section-anchor-preview-20260930.pdf) ; SHA-256 `237b92ac2b10f6c99ba5d5cabd3b04068da343e0d9b96a0de1f97bcc542beda2`.
- Le PDF fait 1 187 795 octets et 118 pages A4 ; LuaHBTeX 1.24.0 l’a compilé. `pdfinfo` indique `Tagged: yes`, PDF 2.0 et la langue `fr-FR`. Le jeu fictif ramifié contient 122 personnes, 61 familles, 183 événements, 17 notes, 183 citations et 12 médias dérivés.
- Les 118 pages ont été parcourues sur dix planches de contact à 50 ppp ; les pages physiques 3, 4, 75 et 118 ont été examinées à 140 ppp. Aucun chevauchement ni texte tronqué n’a été observé. Sur la page 75, quelques URL d’archive se replient après un point du nom d’hôte ; la revue à 140 ppp confirme qu’elles restent lisibles. L’annotation PDF conserve l’URL complète, dont `https://archives.example.test/item/3` ; l’inspection du document relève 732 liens URI externes.
- L’aperçu expose 2 978 destinations PDF nommées. Les 565 fragments HTML internes pointent vers une cible PDF stable, sauf `main-content`, le lien d’évitement propre à l’HTML. Les cinq ancres de sections de premier niveau correspondent maintenant entre HTML et PDF ; les sept cibles de génération restent alignées.
- Le ZIP HTML du même aperçu a été extrait et ouvert directement dans Chrome avec `file://`. Le document s’affiche ; les 12 PNG figurent dans l’extraction. Le lien du sommaire vers la descendance et un appel de citation ouvrent leurs cibles dans `index.html`. Cette vérification confirme l’ouverture hors ligne et ces renvois sur macOS, mais ne remplace pas la revue complète des pages, la validation depuis l’interface Gramps, les essais petits écrans ou le lecteur d’écran.
- Les portraits restent des pixels synthétiques. La comparaison côte à côte de six pages est décrite dans la section suivante ; elle ne couvre pas les 118 pages en haute résolution. Le contrôle de l’ordre de lecture avec un lecteur d’écran et la qualification PDF/UA restent à faire.

## Revue graphique ciblée selon la v1.1 — 30 septembre 2026

- L’aperçu AC-20 balisé ci-dessus a été comparé aux règles graphiques de la spécification v1.1 (§ 6.3, 7.1, 8, 9.3–9.4) et aux critères consignés dans la [revue des maquettes](reference/mockup-review.md). Les maquettes privées restent non suivies par Git et ne sont pas intégrées à cette fixture.
- Sur les pages physiques 1, 3, 4, 49, 75 et 118, le format A4 et le texte sans empattements sont conformes à la v1.1 ; `pdffonts` confirme les fontes Latin Modern Sans. Les en-têtes courants donnent la section et le folio, et ajoutent génération/branche dans les sections généalogiques. La page 4 laisse cohabiter plusieurs générations, sans saut systématique par génération. Les pages physiques 3, 4, 49, 75 et 118 restent lisibles après rendu en niveaux de gris.
- La comparaison côte à côte a couvert les 22 pages des deux PDF de référence et les six pages AC-20 ci-dessus. Les maquettes montrent un bandeau gris « Où suis-je ? », des panneaux parentaux encadrés, des fratries avec renvois et des liens en pied de page. L’aperçu conserve plusieurs générations sur une page et la composition compacte prévue par la v1.1 ; le bandeau et les liens de pied de page restent différents des références. La spécification décrit un en-tête courant avec section, génération, branche et folio : le contrôle du renderer a révélé que les pages de fiches et de notices familiales perdaient la génération et la branche. Ce contexte est corrigé et vérifié dans l’aperçu représentatif ci-dessous. L’écart du bandeau gris et des liens de pied de page reste à arbitrer avant de conclure sur la fidélité finale.
- L’image `BOOK_FEATURED` générée en pixels aléatoires de l’aperçu 118 pages occupait une page dédiée (page physique 49) ; elle vérifiait le placement et le cadrage, mais pas l’équilibre visuel d’une photo. L’aperçu distinct avec visuels fictifs représentatifs ci-dessous complète ce contrôle pour un portrait et une photographie de paysage. La couverture de la fixture 118 pages reste uniquement typographique, car le couple n’a pas de portraits.
- La page 75 regroupe plusieurs entrées numérotées de l’annexe documentaire avec leurs liens ; la page 118 contient l’index des personnes et leurs renvois de page. Aucun chevauchement ni texte coupé n’a été observé dans ces vues. Le contraste avec les titres à empattements des maquettes suit la règle v1.1, qui impose une typographie sans empattements.
- La comparaison directe reste limitée à ces six pages AC-20 représentatives : les 118 pages n’ont pas toutes été comparées aux maquettes à haute résolution. La vérification avec un lecteur d’écran, l’accessibilité PDF et l’essai avec des photographies représentatives restent à faire ; aucune conformité PDF/UA n’est revendiquée.

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

## Prototype technique de balisage PDF — 30 septembre 2026

- L’ancien PDF français AC-20 de 97 pages, généré avant l’activation du balisage, reste non balisé (`pdfinfo` : `Tagged: no`). L’installation TeX Live 2026 Basic du Mac contient `tagpdf` 0.99y (2026-01-29) ; la version publiée sur CTAN au 30 septembre est 1.0g (2026-09-23), voir [TagPDF sur CTAN](https://ctan.org/pkg/tagpdf?lang=en).
- Un prototype temporaire d’une page a été compilé avec LuaHBTeX 1.24.0, `\DocumentMetadata{lang=en,pdfstandard=ua-2,tagging=on}` et le groupe de paquets actuellement chargé par le renderer (`article`, `babel`, `xurl`, `hyperref`, `graphicx`, `ulem`, `textcomp`, `tikz`, `fancyhdr`). Le résultat est un PDF 2.0 que `pdfinfo` reconnaît comme balisé. L’arbre `/StructTreeRoot`, inspecté avec `pypdf`, contient deux éléments `/Figure` munis des textes `/Alt` fournis pour `\includegraphics` et `tikzpicture`. Le texte barré et le lien restent visibles dans l’extraction ; la page rendue a été examinée visuellement.
- Ce prototype confirme que la configuration minimale compile avec la version locale, pas la conformité PDF/UA-2 du livre. Selon l’[état officiel de compatibilité LaTeX](https://latex3.github.io/tagging-project/tagging-status/), `article`, `fancyhdr`, `graphicx` et `xurl` sont compatibles ; `graphicx` exige une description alternative, TikZ est partiellement compatible et requiert également une description, `ulem` est actuellement incompatible (attributs `TextDecoration` manquants) et `babel` reste non vérifié pour les langues. Dans le prototype initial, avant la PR #132, `ulem` produisait `\sout` pour les notes barrées, les appels `\includegraphics` n’ajoutaient pas d’Alt, et TikZ servait au recadrage circulaire des portraits.
- Les [instructions officielles de balisage](https://latex3.github.io/tagging-project/documentation/usage-instructions) demandent un choix explicite entre texte alternatif et élément décoratif pour chaque graphique. Le renderer ajoute maintenant l’attribut de mise en page `TextDecorationType=LineThrough` au texte barré, sans changer son rendu `ulem`. Il reste à qualifier `babel` en français et en anglais, puis à valider le livre avec `veraPDF` et un lecteur d’écran. À cette étape du prototype, `veraPDF` n’était pas encore installé ; aucune validation complète de conformité n’avait été effectuée.

## Premier branchement du balisage dans le renderer — 30 septembre 2026

- Le renderer LaTeX active maintenant le balisage structurel sans annoncer de profil PDF/UA, et règle la langue PDF sur `fr-FR` ou `en-US` selon la langue du livre.
- Les images utilisent une description fournie (légende, description du média ou nom contextualisé pour un portrait) ; à défaut, le texte de repli localisé signale l’absence de description. Le recadrage circulaire en couverture expose une seule figure, son image interne étant décorative.
- L’aperçu de production ci-dessous confirme la compilation et les textes alternatifs du renderer. `ulem` reste chargé pour préserver l’apparence des notes barrées, alors que sa compatibilité de balisage est signalée comme incomplète par LaTeX ; `babel` doit également être qualifié pour les langues retenues. Aucune déclaration PDF/UA ne doit être faite avant ces contrôles et un essai au lecteur d’écran.

## Premier PDF de production balisé — 30 septembre 2026

- Fichier local non suivi : `output/pdf/gramps-fancy-book-tagged-preview-fr-20260930.pdf`, SHA-256 `54f934e96dd990b4fc83805fe3745d13a177eaee50221fd0d137e19d38e231c9`.
- Le PDF A4 de cinq pages a été compilé par LuaHBTeX 1.24.0 avec TeX Live 2026. `pdfinfo` indique `Tagged: yes`, PDF 2.0 et la langue `fr-FR`. L’arbre `/StructTreeRoot` a été inspecté avec `pypdf` : les trois éléments `/Figure` portent respectivement les textes alternatifs « Portrait de Jeanne Exemple », « Acte de naissance de Jeanne Exemple, extrait de recette fictive. » et « Portrait de Jeanne Exemple ». Le portrait circulaire ne crée pas de doublon de figure.
- Les cinq pages ont été rendues à 90 ppp et examinées ; la légende de la reproduction pleine page se place désormais sous l’image. Le nom, les actes et les images sont fictifs, et les visuels sont des dégradés synthétiques. Cette preuve vérifie la compilation, la langue PDF, quelques textes alternatifs et le rendu de cette fixture ; elle ne qualifie pas les données réelles, l’arbre complet de lecture ni la conformité PDF/UA.
- `ulem` reste utilisé pour les passages barrés. La compatibilité de `babel` en français et en anglais, l’ordre de lecture réel et l’essai avec un lecteur d’écran restent à vérifier. À cette étape, `veraPDF` n’était pas encore installé. Le PDF peut être consulté à l’emplacement local indiqué ci-dessus.

## Attribut sémantique des notes barrées — 30 septembre 2026

- Le renderer déclare un attribut PDF de mise en page `/O /Layout /TextDecorationType /LineThrough` et l’attache à un élément `/Span` autour de chaque `\sout`. Le texte reste une seule séquence extractible et `ulem` dessine toujours le trait.
- Le renderer a produit [un aperçu local de trois pages](../output/pdf/gramps-fancy-book-strikethrough-preview-fr-20260930.pdf), SHA-256 `b5e308af5ff81278af5aa8ce9d9adc6a6edf03c81f3f86ac66b9e46584bae208`. `pdfinfo` indique un PDF 2.0 balisé en `fr-FR`. `pdfinfo -struct` expose le `Span` et son attribut `TextDecorationType /LineThrough` ; `pdftotext` conserve le texte ; la page d’introduction montre toujours le trait de barrage.
- Cette compilation française a aussi révélé un avertissement Babel : avec le balisage activé, Babel-French désactive ses réglages de listes, qu’il signale incompatibles avec la nouvelle implémentation balisée. Le premier aperçu ne contenait pas de liste à contrôler. Un essai ciblé est documenté ci-dessous ; le registre officiel de [compatibilité LaTeX](https://latex3.github.io/tagging-project/tagging-status/) indique `french` comme non vérifié et la fiche CTAN de [Babel-French](https://ctan.org/pkg/babel-french?lang=en) signale l’incompatibilité avec les PDF balisés.
- Le registre LaTeX classe toujours le paquet `ulem` comme actuellement incompatible en raison de cet attribut manquant ; notre wrapper fournit cet attribut pour l’usage `\sout` du projet, mais cela ne qualifie pas toutes les commandes de `ulem`. L’arbre complet, les langues `babel`, la règle d’identification PDF/UA relevée par veraPDF et le lecteur d’écran restent à qualifier ; aucune conformité PDF/UA n’est revendiquée.

## Libellé français des listes balisées — 30 septembre 2026

- Fichier local non suivi : `output/pdf/gramps-fancy-book-french-list-preview-fr-20260930.pdf` ; SHA-256 `a290a17e620e5a55d3f7d3deb960611373c87aaf799cbdfc01498e72f58fabd5`.
- La fixture synthétique de quatre pages a été compilée avec LuaHBTeX 1.24.0 et TeX Live 2026. `pdfinfo` indique PDF 2.0 balisé en `fr-FR`. `pdfinfo -struct` montre les éléments `L` et `LI` ; `pdftotext -layout` conserve les tirets cadratins avant les deux noms de l’index. Les quatre pages ont été rendues et examinées ; la couverture, le trait de barrage, le sommaire et l’index sont lisibles.
- Pour les listes françaises générées, le renderer redéfinit les commandes de libellé `\labelitemi` à `\labelitemiv` avec `\textemdash`, car Babel-French désactive ses réglages lorsque le balisage est actif. Ces commandes standard du noyau conservent le tiret cadratin dans les éléments balisés ; la CI de la PR #136 a confirmé la compatibilité avec son image TeX Live épinglée. Poppler 24.04.0 émet `Syntax Warning: Attribute ListNumbering value is of wrong type (name)` lors de l’inspection de l’arbre, alors que le ClassMap du PDF contient `/ListNumbering /Unordered`. La référence PDF 2.0 de la [PDF Association](https://pdfa.org/download-area/cheat-sheets/StructureAttributes.pdf) répertorie `Unordered` comme valeur autorisée ; cet avertissement ne prouve donc pas que le fichier est mal formé. Cette fixture ne démontre pas la conformité PDF/UA.

## Aperçu français complet avec listes balisées — 30 septembre 2026

- Fichier local non suivi : [`output/pdf/gramps-fancy-book-french-tagged-renderer-preview-20260930.pdf`](../output/pdf/gramps-fancy-book-french-tagged-renderer-preview-20260930.pdf) ; SHA-256 `4f7f306a48acb5f45561f667d887638814b37932b11f83a225c43280c4963de7`.
- Le PDF fictif compte 19 pages A4 et a été compilé avec LuaHBTeX 1.24.0 / TeX Live 2026. Il couvre la couverture, le sommaire, les sections généalogiques, une image synthétique, une fiche longue avec notes, l’annexe documentaire et l’index. `pdfinfo` confirme PDF 2.0 balisé et la langue `fr-FR`.
- Le contrôle local de structure trouve neuf listes `L` et 90 éléments `LI`, avec `ListNumbering /Unordered` ; l’extraction conserve les tirets cadratins devant les noms de l’index. Les 19 pages ont été rendues en planche générale ; les pages physiques 1, 2, 8, 17, 18 et 19 ont aussi été examinées en détail. Aucun défaut visuel n’a été relevé.
- Les données et visuels sont fictifs. Cette revue et le contrôle ajouté à la CI vérifient cette fixture, pas la compatibilité complète de Babel ni la conformité PDF/UA ; aucun profil PDF/UA n’est revendiqué.

## Contrôle veraPDF et métadonnées du titre — 30 septembre 2026

- Le CLI officiel veraPDF 1.30.2 a été téléchargé depuis le site du projet, vérifié par signature GPG avec l’empreinte publiée par veraPDF, puis installé temporairement dans `/tmp` avec le seul composant CLI. Il n’a pas été ajouté au dépôt ni installé globalement.
- Sur l’aperçu français balisé de 19 pages ci-dessus, le profil PDF/UA-2 a signalé trois règles : l’absence de l’identification PDF/UA dans XMP, l’absence de `/ViewerPreferences /DisplayDocTitle true` et l’absence de `dc:title`. L’identification formelle reste volontairement absente : le projet ne revendique pas PDF/UA tant que l’ordre de lecture, les paquets et le lecteur d’écran ne sont pas qualifiés.
- Le renderer renseigne `dc:title` à partir de la note éditoriale `BOOK_TITLE` (ou du titre de couverture localisé par défaut) et demande aux lecteurs d’afficher ce titre. Le vérificateur structurel confirme ces deux métadonnées, neuf listes `L`, 90 éléments `LI`, les marqueurs cadratins de l’index, quatre titres `H3` et aucun titre `H4`.
- L’audit statique de l’arbre a montré que les sous-titres produits par `\paragraph` étaient balisés `H4`, sans aucun `H3`. La correction en cours remappe ce rôle en `H3` avec `role/new-tag`, sans modifier la présentation. L’aperçu mis à jour, [`output/pdf/gramps-fancy-book-french-tagged-renderer-reading-order-preview-20260930.pdf`](../output/pdf/gramps-fancy-book-french-tagged-renderer-reading-order-preview-20260930.pdf), est un PDF A4 de 19 pages (SHA-256 `e90d35095f48af1fe16e1a5ad2a6ad7469f15c27966e36cb8709384013fde6ef`). Les 19 pages ont été rendues en planche et examinées ; aucun défaut visuel n’a été relevé.
- Avec veraPDF 1.30.2, l’aperçu mis à jour passe 1 726 règles et échoue à une seule : l’absence d’identification PDF/UA (règle 5-1). Ce contrôle machine ne certifie pas la conformité PDF/UA, que le projet ne revendique pas.
- Un PDF français de deux pages, [`output/pdf/gramps-fancy-book-title-metadata-preview-fr-20260930.pdf`](../output/pdf/gramps-fancy-book-title-metadata-preview-fr-20260930.pdf), vérifie en plus une note de titre avec accents, esperluette, croisillon et mise en gras. Son titre XMP obtenu est « Histoire d’Élise & Louis #2 » ; SHA-256 `7486adba99d7190374d63ef5f92154c0d3d9df18a5018ace91440dcb31e399a1`. Les deux pages ont également été examinées visuellement.
- La traversée statique de l’arbre balisé suit l’ordre général de publication : couverture, sommaire, sections généalogiques et familiales, fiches individuelles, annexe, puis index. Elle dénombre huit H1, quatre H2, quatre H3, neuf listes et 90 éléments de liste. Les quatre éléments `/Figure` ont tous un `/Alt` non vide ; le vérificateur CI impose maintenant cette règle.
- La fixture anglaise riche a également été compilée localement : 18 pages A4, langue `en-US`, titre « Family history », huit H1, quatre H2, quatre H3, neuf listes, 90 éléments et quatre figures avec texte alternatif. La CI applique le même contrôle structurel aux versions anglaise et française. Le préambule anglais utilise l’option Babel `american`, cohérente avec les métadonnées `en-US`, ce qui évite l’avertissement lié à l’option générique `english` ; cela ne valide pas la compatibilité générale de Babel. Les noms, événements et descriptions de la fixture restent fictifs et plusieurs descriptions de données sont en français.
- Ces contrôles statiques ne garantissent pas la narration effective ni l’ordre de lecture complet à l’écran.
- Un essai avec lecteur d’écran reste nécessaire, de même que la compatibilité générale de `babel` et `ulem`. La référence veraPDF documente les profils et l’option `-f ua2` ([validation CLI](https://docs.verapdf.org/cli/validation/)) ; son installation et la vérification de signature sont décrites dans le [guide officiel](https://docs.verapdf.org/install/). La documentation LaTeX décrit le remappage des rôles via [`role/new-tag`](https://latex3.github.io/tagging-project/documentation/usage-instructions).

## Aperçu PDF avec médias fictifs représentatifs et contexte courant — 30 septembre 2026

- Fichier local non suivi : `output/pdf/gramps-fancy-book-ac20-representative-media-context-preview-20260930.pdf` ; SHA-256 `a8e61932932a6eeadd6f9be6b33f9eb3d66e962a1d2a6e2bbdc25f092e6d2bc2`.
- La fixture de 30 pages A4 comprend 26 personnes, un portrait vertical fictif et une photographie paysagère fictive marquée `BOOK_FEATURED`. Les deux images ont été générées pour cette revue ; elles ne proviennent pas des maquettes privées. `pdfinfo` confirme `Tagged: yes`, le format A4 et 3 862 577 octets.
- Les pages physiques 9, 14, 15, 18 et 27 ont été rendues à 110 ppp et examinées. Les fiches individuelles affichent maintenant section, folio, génération et branche, y compris sur la page dédiée à la photo mise en avant ; les notices familiales affichent également leur génération et leur branche. La photo paysagère apparaît dans la fiche puis sur une page dédiée avec légende ; le portrait recadré reste lisible dans la fiche et dans l’annexe. Aucun chevauchement ni texte tronqué n’a été observé sur ces pages.
- Cette fixture confirme le rendu avec des formats portrait et paysage et le contexte d’en-tête des pages de fiches/notices. Elle ne remplace pas la revue haute résolution des 118 pages, une photo fournie par l’utilisateur, l’export AC-20 depuis Gramps Desktop, l’essai lecteur d’écran ou la qualification PDF/UA.

## Aperçu long avec photos mises en avant équilibrées — 30 septembre 2026

- Fichier local non suivi : `output/pdf/gramps-fancy-book-122-person-featured-media-centered-preview-20260930.pdf` ; SHA-256 `26efdb78e33e24bbe8240bafd83ae0cc805168dff34565ef9c002f9e3346e2fd`.
- La fixture de branchement comprend 122 personnes, 61 familles, 183 événements, 17 notes, 183 citations et 12 médias, dont deux images `BOOK_FEATURED`. Les portraits et les fermes sont des visuels fictifs générés pour la revue. Le PDF fait 127 pages A4, 21 191 010 octets, PDF 2.0 balisé ; LuaHBTeX 1.24.0 a convergé sans avertissement de mise en page.
- Les pages physiques 38, 50, 51, 65 et 66 ont été rendues à 110 ppp et examinées. Les portraits restent nets ; les deux photos paysagères conservent leurs proportions et leur légende, et sont centrées verticalement sur leurs pages dédiées. Les en-têtes de fiches gardent la section, le folio, la génération et la branche, y compris sur les pages des photos mises en avant. Aucun chevauchement ni texte coupé n’a été observé sur ces pages.
- Cette revue confirme le placement des photos et l’équilibre des pages dédiées sur un livre long. Elle ne couvre pas les 127 pages en haute résolution, les vraies photos Gramps, l’export AC-20 depuis Desktop, l’essai lecteur d’écran ni la conformité PDF/UA.

## Revue visuelle complète du volume long — 30 septembre 2026

- Aperçu local non suivi : `output/pdf/gramps-fancy-book-122-person-featured-media-centered-preview-20260930.pdf`, SHA-256 `26efdb78e33e24bbe8240bafd83ae0cc805168dff34565ef9c002f9e3346e2fd`. `pdfinfo` confirme un PDF A4 de 127 pages, balisé, version 2.0, de 21 191 010 octets.
- Les 127 pages ont été rendues à 110 ppp et examinées intégralement sur 32 planches de quatre pages couvrant la couverture, le sommaire, les parcours généalogiques, les fiches, l’annexe documentaire et l’index. Les pages physiques 49–51 et 64–67, qui contiennent les deux médias `BOOK_FEATURED`, ont aussi été examinées individuellement à 160 ppp. Les proportions et légendes des images sont conservées ; les pages dédiées sont centrées.
- Aucun chevauchement, texte coupé ou page vide n’a été relevé. L’extraction contient 127 pages non vides ; les pages généalogiques physiques 3–78 portent toutes le contexte génération/branche, et chaque page après la couverture et le sommaire porte un en-tête de section. Le premier contrôle visuel avait fait croire que deux en-têtes perdaient leur contexte ; le rendu à 160 ppp et l’extraction texte ont confirmé qu’il est présent.
- Le contrôle statique de l’arbre avec `pdfinfo -enc UTF-8 -struct-text` extrait huit titres `H1` : le titre du sommaire, puis les sept sections indiquées dans le sommaire (ascendance, descendance, liens familiaux, notices, fiches, annexe et index), 190 titres `H2`, 383 titres `H3` et sept entrées de sommaire. Les 24 figures ont un texte alternatif non vide (`/Alt`). Cela vérifie la hiérarchie et l’ordre déclarés dans le PDF synthétique ; cela ne remplace pas un essai de navigation avec un lecteur d’écran.
- La comparaison aux maquettes sur les 22 pages de référence et un échantillon représentatif du PDF long est consignée ci-dessous. Elle ne remplace pas l’essai avec des photos réelles de Gramps, l’export complet AC-20 depuis Desktop, la vérification au lecteur d’écran ni la qualification PDF/UA. Aucune conformité PDF/UA n’est revendiquée.

## Comparaison visuelle aux maquettes — 30 septembre 2026

- Les 12 pages de la maquette structurelle et les 10 pages de la maquette « événements et sources » ont été examinées à 72 ppp. La comparaison avec le livre long courant a couvert les pages physiques 1–4 (couverture, sommaire, ascendance et descendance), 19 (notices familiales), 36–38 (fiches et portrait), 49–51 (média `BOOK_FEATURED`), 80 et 94 (annexe), et 124 (index), rendues à 110 ppp.
- Le PDF courant suit les exigences graphiques de la v1.1 : A4, niveaux de gris, typographie sans empattements, mise en page compacte, en-têtes adaptés au contexte, plusieurs éléments éditoriaux par page, reproduction `BOOK_FEATURED` pleine page et index alphabétique. Aucun défaut de mise en page bloquant n’a été relevé dans cet échantillon.
- Les bandeaux « Où suis-je ? », les titres à empattements et les liens de navigation en pied visibles dans les maquettes ne sont pas reproduits à l’identique. Les deux premiers divergent volontairement des exigences de la v1.1 (présentation minimaliste, typographie sans empattements, en-tête compact). Les liens en pied restent une piste de confort facultative, à évaluer sans en faire un critère d’acceptation.
- Cette comparaison vérifie la cohérence visuelle sur des pages représentatives, pas l’équivalence fonctionnelle complète des deux rendus. Les médias restent fictifs ; l’export AC-20 depuis Desktop, les tailles d’écran, l’essai lecteur d’écran et la qualification PDF/UA restent à faire.

## Qualification ciblée de Babel et des notes barrées — 30 septembre 2026

- La fixture complète du renderer a été compilée en anglais avec `american` (18 pages) et en français avec `french` (19 pages), sur trois passes LuaLaTeX. Les deux PDF sont balisés ; leurs métadonnées XMP portent respectivement `en-US` et `fr-FR`. Les fichiers temporaires de ces essais ont été supprimés après inspection visuelle.
- Une phrase `\sout` longue, avec accents en français, a été ajoutée à chaque fixture. Le trait reste visible même lorsque la phrase se poursuit sur la ligne suivante ; le texte reste extractible et l’arbre contient un `Span` avec `/TextDecorationType /LineThrough`, fourni par le wrapper du renderer. Aucune erreur fatale, référence non résolue ou boîte `Overfull` ne subsiste après la troisième passe. La fixture longue conserve des avertissements `Underfull` attendus pour ses paragraphes synthétiques.
- La version installée sur ce Mac est Babel-French 4.0e (15 août 2025), avec le noyau LaTeX2e du 1er novembre 2025, et `ulem` 2019/11/18. En mode balisé, Babel-French avertit que sa personnalisation des listes est désactivée ; le renderer redéfinit les quatre commandes de libellé de liste avec `\textemdash`, et les tirets restent visibles dans la sortie. Ce contrôle confirme le chemin réellement utilisé sur ce Mac, pas Babel-French 4.1a.
- Le manuel officiel de Babel-French 4.1a (révisé le 6 juin 2026) décrit un chemin fondé sur les nouveaux modèles LaTeX publiés le 1er juin 2026, absents du noyau installé ici. Le registre officiel marque encore Babel comme « unchecked » par langue et `ulem` comme incompatible en raison des attributs `TextDecoration` manquants. Notre wrapper et cet essai couvrent seulement `\sout` dans le renderer, pas l’ensemble des commandes de `ulem` ni toutes les langues Babel. Voir le [registre de compatibilité du projet LaTeX](https://latex3.github.io/tagging-project/tagging-status/), le [manuel officiel Babel-French](https://tug.ctan.org/macros/latex/required/babel/contrib/frenchb/frenchb.pdf) et la [fiche CTAN de ulem](https://ctan.org/pkg/ulem?lang=en).
- Le run CI [36754589844](https://github.com/grostim/gramps-fancy-genealogical-book/actions/runs/36754589844), issu de la PR #166, utilise LaTeX2e 2026-06-01, Babel-French 4.1a et `ulem` 2019/11/18. Les fixtures `french` et `american` contiennent chacune une phrase longue barrée ; la compilation et les vérificateurs passent. L’extraction conserve le texte et `pdfinfo -struct` montre le `Span` avec `/TextDecorationType /LineThrough`.
- Le lecteur d’écran, les autres moteurs et versions de TeX, les autres commandes de `ulem`, les autres langues Babel et toute conformité PDF/UA restent à qualifier.

## Export AC-20 de la base synthétique par Gramps CLI — 30 septembre 2026

- Fichier local non suivi : `output/pdf/gramps-fancy-book-ac20-gramps-cli-synthetic-20260930.pdf` ; SHA-256 `9e9729567d55c2ef541a9e50a5581080cbf39b3ec359953e3ef33d1af5c2f53e`.
- La GEDCOM synthétique a été importée dans un profil Gramps 6.0.8 isolé sans erreur. L’arbre contient 122 personnes, 61 familles, 183 événements, 183 citations, 17 notes et 12 médias ; aucune donnée de l’arbre personnel n’a été utilisée. L’export PDF a été lancé avec le rapport du paquet courant par l’interface en ligne de commande, pas depuis la fenêtre Gramps.
- LuaHBTeX 1.24.0 a produit un PDF 2.0 balisé de 107 pages A4 (6 381 203 octets), avec le titre « Histoire familiale » et la langue `fr-FR`. Les 107 pages ont été rendues et examinées sur 14 planches de contact ; les pages physiques 1, 2, 66, 67 et 107 ont aussi été inspectées à 160 ppp. Aucun débordement ou texte coupé n’a été observé. La couverture reste très épurée et les contenus, noms, lieux et images sont fictifs.
- L’arbre expose huit titres principaux, 190 sous-titres de niveau 2, 366 de niveau 3, sept entrées de sommaire et 12 figures dotées chacune d’un `/Alt` non vide. `pdfinfo -struct-text` produit 591 avertissements `ListNumbering value is of wrong type (name)` pour les listes `/Unordered`. La [fiche officielle PDF Association des attributs de structure](https://pdfa.org/download-area/cheat-sheets/StructureAttributes.pdf) donne bien `Unordered` comme nom valide pour PDF 2.0 ; ces avertissements reflètent donc la limite de cet inspecteur face à cet attribut PDF 2.0, et ne constituent pas à eux seuls un échec de syntaxe. Une validation indépendante d’accessibilité demeure nécessaire ; aucune conformité PDF/UA n’est revendiquée.
- Cet aperçu permet de juger le rendu du rapport sur un jeu AC-20 complet et fictif. Il ne qualifie pas encore l’export depuis la fenêtre Gramps, l’essai au lecteur d’écran, les données ou médias réels, ni l’acceptation visuelle finale.

## Aperçu N=100 après compaction des notices familiales — 1er octobre 2026

- Aperçu local : [`output/pdf/gramps-fancy-book-single-event-notice-preview-20261001.pdf`](../output/pdf/gramps-fancy-book-single-event-notice-preview-20261001.pdf), SHA-256 `0b3b395928504f2ad8a1b6412d878443a64200be5fe533892f080a2804db00b0`.
- Le PDF balisé fait 169 pages A4 et 1 409 982 octets. Il est issu de la fixture ramifiée fictive de 202 personnes, 101 familles, 303 événements/citations, 101 notices, 202 fiches et 20 portraits de 96 × 72 pixels.
- Les pages physiques 29 et 31 ont été rendues à 130 ppp et inspectées. Elles montrent notamment une notice familiale ; aucune coupure de texte ni superposition n’a été observée. Les 1 805 destinations nommées et les 3 073 annotations PDF sont conservées par rapport à l’aperçu précédent.
- L’aperçu permet de comparer les notices familiales à entrée unique avec les notices en listes. Les objets généalogiques et portraits sont fictifs ; cela ne constitue pas une revue intégrale de toutes les pages ni une qualification de PDF/UA.

## Export AC-15 depuis Gramps CLI avec les marges à 15 mm — 5 octobre 2026

- PDF local non suivi : [`output/pdf/gramps-fancy-book-ac15-shared-media-15mm-20261005.pdf`](../output/pdf/gramps-fancy-book-ac15-shared-media-15mm-20261005.pdf), SHA-256 `20931cecc9fa69c90f619b3e94037c84920d026bcc07ea798607d9420900b600`.
- L’archive courante du module complémentaire a été installée dans un profil Gramps temporaire isolé. Le rapport Gramps 6.0.8 a importé la fixture AC-15 fictive et produit un PDF en français avec LuaHBTeX 1.24.0 / TeX Live 2026. Ce parcours utilise Gramps CLI, pas la boîte de dialogue Desktop.
- Le PDF compte neuf pages A4 (66 423 octets), porte le balisage PDF 2.0 et la langue `fr-FR`. Les 81 destinations nommées sont présentes ; les 32 liens internes sont résolus. Les trois figures ont un texte alternatif non vide.
- L’annexe, à la page physique 8 (folio 7), affiche une seule reproduction partagée et les entrées de citation [2] et [3] y renvoient. Les pages physiques 7 et 8 ont été rendues à 120 ppp et examinées ; aucun chevauchement ni texte coupé n’a été observé.
- Cette recette confirme la marge actuelle de 15 mm et le chemin PDF du rapport Gramps sur la fixture AC-15. L’export depuis la fenêtre Desktop avec ce média partagé, une revue complète des neuf pages, les médias réels et le lecteur d’écran restent à faire. Aucune conformité PDF/UA n’est revendiquée. Les mesures détaillées figurent dans [le relevé JSON](validation-gramps-ac15-margins15-20261005.json).
