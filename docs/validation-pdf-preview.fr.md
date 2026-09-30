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
