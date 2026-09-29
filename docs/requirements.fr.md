# Suivi des références et exigences

État au 29 septembre 2026. Les identifiants ci-dessous sont propres à ce suivi et ne remplacent pas ceux des 27 scénarios retrouvés dans la spécification originale.

## Sources

- S1 : discussion « Spécification plugin Gramps », conversation `6ab6271b-2764-83eb-bee1-104a02c02d59`.
- S2 : discussion « Concevoir un livre généalogique », conversation `6ab57872-e2e4-83eb-b0b9-1c0081b338b0`.
- S3 : [synthèse locale](specification-v1.1.md), établie à partir de S1.

- S4 : [transcription intégrale de la v1.1](reference/specification-v1.1.visible.txt), extraite de l’aperçu ChatGPT le 27 septembre 2026 ; voir la [provenance](reference/README.md). Elle contient AC-01 à AC-27. Le [Markdown original](reference/Gramps_Fancy_Genealogical_Book_Specification_v1.1.md) et les quatre maquettes ont ensuite été retrouvés dans le ZIP téléchargé. L’original prime ; les maquettes sont conservées localement hors Git.

## Matrice de suivi

| ID local | Exigence retrouvée | Source | Lot | Preuve ou état |
| --- | --- | --- | --- | --- |
| REF-01 | Plugin Gramps 6 installable et sélection d’une famille | S1 | L1 | Archive extraite dans un profil isolé ; export CLI Gramps 6.0.8 validé |
| REF-02 | Modèle intermédiaire indépendant et testable | S1 | L1–L3 | Tests unitaires ; JSON avec identifiants et relations |
| REF-03 | Documentation FR/EN, code et métadonnées anglais | S1 | Tous | README et guides complets FR/EN ; catalogue français compilé et inclus à la construction ; affichage dans Gramps et CI reproductible à valider |
| REF-04 | Architecture en six responsabilités | S1 | L2–L7 | Architecture en six responsabilités décrite dans les guides ; extraction, parcours, modèle éditorial et rendus HTML/LaTeX présents. Recettes Desktop/Web et visuelles restantes |
| REF-05 | Ascendance par générations et descendance par branches | S2 | L4 | Parcours et occurrences implémentés ; PR #43–44 qualifient les principaux graphes et le contrat LaTeX. Recette complète et revue HTML/graphique restantes |
| REF-06 | Repères généalogiques en haut de page et renvois | S2 | L4–L7 | Ancres, navigation par génération/branche et renvois HTML/PDF implémentés ; ZIP hors ligne et apparence restent à vérifier |
| REF-07 | Événements de vie, portraits et photos complémentaires | S2 | L3, L5–L7 | Événements, portraits et médias consommés par les rendus ; comportement complet avec base Gramps et revue visuelle restant à qualifier |
| REF-08 | Citations partagées entre faits, annexes compactes | S2 | L3, L5–L7 | Appels réutilisés, numérotation, renvois et annexe présents en HTML/LaTeX ; validation des scénarios de bout en bout restante |
| REF-09 | URL complètes et régions de médias Gramps | S2 | L2, L5–L7 | URL, régions et règles de conversion raster/PDF implémentées ; recette avec les quatre cas Gramps et revue visuelle restantes |
| REF-10 | BOOK_PUBLICATION, BOOK_PROFILE, BOOK_EXCLUDE, BOOK_FEATURED | S1 | L3–L5 | Règles BOOK_* implémentées dans l’extraction, le modèle et les rendus ; recette native complète restante |
| REF-11 | Respect des droits, objets privés lisibles selon Gramps et avertissement avant export | S1 | L2–L3, L8 | L’adaptateur utilise les accesseurs Gramps, préserve les indicateurs privés accessibles et exige une confirmation avant chaque export ; le comportement Desktop/Web reste à qualifier |
| REF-12 | LaTeX/PDF, HTML et ZIP ; faisabilité Gramps Web | S1 | L2, L6–L8 | Rapport Gramps avec PDF LuaLaTeX, HTML ZIP et JSON ; compilation dans Gramps, revue visuelle et compatibilité Gramps Web restent à qualifier |

## Décision d’intégration du premier jalon

Le rapport emploie `CATEGORY_WEB`, mécanisme natif pour les rapports qui génèrent leurs propres fichiers. Il conserve le sélecteur de famille et le cycle Gramps, sans utiliser le moteur PDF/ODT intégré : le plugin compile lui-même un PDF via LuaLaTeX, ou écrit une archive HTML ZIP ou un instantané JSON. En mode automatique, `.pdf` sélectionne le PDF, `.zip` le livre HTML et `.json` conserve la compatibilité historique de l’instantané ; les formats peuvent aussi être choisis explicitement. LuaLaTeX est facultatif et requis seulement pour le PDF. Cette intégration n’est pas encore qualifiée dans Gramps Desktop et ne constitue pas une validation de Gramps Web.

Le statut d’enregistrement est `EXPERIMENTAL` : le statut `UNSTABLE` utilisé initialement est masqué par les versions publiques de Gramps. Ce choix est fondé sur le code installé et sur un essai de découverte réel.

## Points ouverts

- Exécuter les recettes de bout en bout des 27 scénarios sur les versions Desktop/Web réellement prises en charge et conserver leur environnement comme preuve.
- Qualifier dans Gramps Desktop et Gramps Web la confirmation préalable à chaque export, y compris l’arrêt sans écriture lorsque la case n’est pas cochée ; conserver l’inclusion prévue par la spécification.
- Rétablir les exécutions GitHub Actions : les derniers workflows ont été bloqués avant les jobs par un message de paiement ou de plafond de dépenses.
- Réaliser les revues visuelles PDF/HTML, l’essai du ZIP hors ligne, les vérifications clavier/lecteur d’écran et les mesures de performance.
- Qualifier Gramps Web ainsi que l’installation de Pillow et pypdfium2 dans les paquets Desktop/Web.
- Vérifier le chargement du catalogue français dans Gramps et le maintenir synchronisé aux chaînes ; obtenir une CI reproductible pour la matrice annoncée.
- Confirmer la licence de distribution déclarée GPL dans les métadonnées avant une version distribuée. Le dépôt reste privé ; la visibilité des distributions publiques doit être décidée.
- Conserver les références et maquettes originales hors du dépôt public et organiser leur transmission privée aux intervenants qui en ont besoin.

## Règles désormais établies

- F0 doit comporter deux partenaires connus (AC-02). Les familles monoparentales rencontrées dans le parcours restent valides (AC-09). Le rapport minimal rejette désormais F0 incomplète ; l’adaptateur reste capable de représenter une famille monoparentale.
- Descendance : union des descendants de P0 et P1, y compris les autres unions. Tous les liens de filiation explicites sont conservés, avec leur type retourné par Gramps dans le parcours, sans transformer « aucun » en filiation. Les collatéraux ne déclenchent pas leur propre descendance.
- Fiche : événement individuel ou familial substantiel hors naissance/décès, ou attribut BOOK_PROFILE=YES. Une seule fiche par personne, à la première occurrence déterministe. Toute autre apparition renvoie vers cette occurrence ou vers la fiche, même lorsqu’aucune fiche n’est créée.
- Notes : étiquette native BOOK_PUBLICATION obligatoire ; une note partagée est publiée dans chaque contexte. Les six rôles éditoriaux de F0 sont reconnus par l’extraction et le rendu ; leur recette dans l’interface Gramps 6 reste à faire.
- Médias : BOOK_EXCLUDE prime sur BOOK_FEATURED ; reproduction principale unique. PDF multipages jamais reproduit ; PDF monopage reproduit seulement sans URL externe.
- Livre : couverture, préliminaires, sommaire, ascendance, descendance, annexe documentaire unique et index des personnes. Notes de bas de page et renvois vers la pagination définitive du PDF.
- Gramps Web est une exigence de la version cible ; sa faisabilité reste à démontrer. LuaLaTeX est le compilateur du mode PDF Desktop ; Gramps Web et la présence du compilateur sur serveur ne sont pas qualifiées. L’export de sources LaTeX/Git du livre reste facultatif.
- Rapport de contrôle séparé limité aux contradictions de dates/lieux d’un même fait. Aucun avertissement documentaire ajouté dans le livre.
- La règle de recadrage retrouvée dans la discussion de conception n’est pas détaillée dans la v1.1 : conserver la provenance S2 et résoudre les variantes de régions dans le prototype médias, en respectant la reproduction principale unique.

## Scénarios de la v1.1 et lots responsables

Les résultats attendus exacts sont conservés au § 15 de S4. « À réaliser » signifie qu’aucune conformité de bout en bout n’est revendiquée.

| Scénario | Sujet | Tâches | État |
| --- | --- | --- | --- |
| AC-01 | Couple central et génération zéro | L1.3, L4.1, L5.1 | Couple central, générations et liens présents ; graphes et contrat LaTeX qualifiés (PR #44), recette complète restante |
| AC-02 | Refus du couple incomplet | L1.3–L1.7 | Validé en CLI Gramps 6.0.8 ; CI 36288791405 |
| AC-03 | Descendants des autres unions | L4.3–L4.4 | Qualifié sur graphe et contrat LaTeX (PR #43) ; recette HTML/PDF depuis Gramps restante |
| AC-04 | Filiations explicites multiples | L3.1, L4.4 | Liens de filiation typés implémentés et qualifiés sur graphe (PR #43) ; recette complète restante |
| AC-05 | Implexes, fiche unique et cycles | L4.4–L4.5 | Occurrences et fiches uniques implémentées, qualifiées sur graphe (PR #43) ; recette complète restante |
| AC-06 | Collatéral documenté sans expansion | L4.1, L4.5 | Expansion des collatéraux bornée, qualifiée sur graphe (PR #43) ; recette complète restante |
| AC-07 | Éligibilité et BOOK_PROFILE=YES | L3.3, L4.5 | Règle d’éligibilité et BOOK_PROFILE=YES implémentés, qualifiés sur graphe (PR #43) ; recette Gramps restante |
| AC-08 | Événement familial et fiche | L3.2, L5.2 | Événements familiaux et fiches présents et qualifiés sur graphe (PR #43) ; recette complète restante |
| AC-09 | Famille monoparentale dans le parcours | L3.1, L4.4, L5.2 | Familles monoparentales prises en charge dans le parcours et qualifiées sur graphe (PR #43) ; recette complète restante |
| AC-10 | Note Markdown partagée | L3.3, L5.2, L6.2, L7.3 | Markdown et styles natifs rendus en HTML/LaTeX ; partage entre contextes à vérifier avec Gramps |
| AC-11 | Exclusion des notes non étiquetées | L3.3, L5.2 | Notes non marquées BOOK_PUBLICATION exclues des références éditoriales ; recette native complète restante |
| AC-12 | Portraits et photo pleine page | L5.5, L6.1, L7.4 | Portraits et reproductions médias présents dans les rendus ; sélection, recadrage, ZIP et rendu visuel à vérifier |
| AC-13 | Priorité BOOK_EXCLUDE | L3.3, L5.5 | BOOK_EXCLUDE appliqué au traitement et à la publication des médias ; scénario natif de priorité restant à vérifier |
| AC-14 | Citations réutilisées et multiples | L3.4, L5.3–L5.4, L6.4 | Citations réutilisables, appels contextuels, numérotation, renvois et annexe implémentés ; scénario complet restant |
| AC-15 | Document partagé et reproduction unique | L5.4–L5.5 | Placements dédupliqués par handle média et appels documentaires reliés ; cas partagé à vérifier dans les deux rendus |
| AC-16 | Quatre cas PDF/URL | L2.4, L5.5 | Un portrait fictif recadré est intégré au PDF depuis Gramps ; les quatre cas restent à valider avec médias Gramps |
| AC-17 | Pagination finale cohérente | L6.4–L6.5 | PDF A4 de 9 pages produit depuis Gramps macOS 6.0.8 et livres synthétiques de 18 et 4 pages examinés ; sommaire et légende du portrait corrigés ; parcours interactif Desktop et comparaison aux maquettes restent à vérifier |
| AC-18 | Fait sans citation et source sans dépôt | L3.4, L5.4 | Modèle de citations tolère appels et dépôts absents ; cas documentaires à vérifier dans la sortie finale |
| AC-19 | Contradictions et rapport séparé | L3.7, L5.7 | Rapport séparé BOOK_FACT_ID implémenté : dates disjointes en conflit, lieux différents à examiner ; recette de données restante |
| AC-20 | Équivalence PDF/HTML et usage hors ligne | L6, L7, L8.1 | Sorties PDF et HTML ZIP autonomes disponibles ; équivalence de contenu et navigation hors ligne restent à vérifier |
| AC-21 | Livre long et limites graphiques | L2.3, L6.3, L6.6 | Fixture synthétique riche de 18 pages A4 avec 80 événements, note longue, portrait, photo pleine page, citations et annexe examinée ; limites graphiques avec médias Gramps réels et comparaison aux maquettes encore à qualifier |
| AC-22 | Desktop et Web complets | L1, L2.5, L8.2 | Sélection/export JSON contrôlés sur Desktop macOS ; installation et parcours complet Desktop/Web restent à qualifier |
| AC-23 | Échappement et absence d’injection | L2.6, L6.2, L7.3 | Échappement HTML, liens restreints et chemins ZIP relatifs implémentés ; recette de sécurité dédiée restante |
| AC-24 | Stabilité du contenu et des ancres | L4.6, L5.6, L8.1 | Identifiants et ancres stables produits par le modèle et les rendus ; stabilité entre générations à vérifier |
| AC-25 | Métadonnées indépendantes de la langue | L3.3, L8.4 | Noms techniques et métadonnées BOOK_* en anglais ; test de comportement avec différentes langues Gramps restant |
| AC-26 | Documentation FR/EN et contrôle CI | L1.8, L8.4 | README et guides complets FR/EN présents, catalogue français compilé à la construction ; CI réussie sur Python 3.10–3.13, intégration Gramps 6.0.8 et LuaLaTeX ; parcours Desktop/Web complet à qualifier |
| AC-27 | Transmission des maquettes | L0.1, L6.1 | Originaux locaux récupérés et PDFs consultés ; transmission privée requise pour un nouveau clone |
