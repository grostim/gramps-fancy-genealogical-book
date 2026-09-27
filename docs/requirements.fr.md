# Suivi des références et exigences

État au 27 septembre 2026. Les identifiants ci-dessous sont propres à ce suivi et ne remplacent pas ceux des 27 scénarios retrouvés dans la spécification originale.

## Sources

- S1 : discussion « Spécification plugin Gramps », conversation `6ab6271b-2764-83eb-bee1-104a02c02d59`.
- S2 : discussion « Concevoir un livre généalogique », conversation `6ab57872-e2e4-83eb-b0b9-1c0081b338b0`.
- S3 : [synthèse locale](specification-v1.1.md), établie à partir de S1.

- S4 : [transcription intégrale de la v1.1](reference/specification-v1.1.visible.txt), extraite de l’aperçu ChatGPT le 27 septembre 2026 ; voir la [provenance](reference/README.md). Elle contient AC-01 à AC-27. Le [Markdown original](reference/Gramps_Fancy_Genealogical_Book_Specification_v1.1.md) et les quatre maquettes ont ensuite été retrouvés dans le ZIP téléchargé. L’original prime ; les maquettes sont conservées localement hors Git.

## Matrice provisoire

| ID local | Exigence retrouvée | Source | Lot | Preuve ou état |
| --- | --- | --- | --- | --- |
| REF-01 | Plugin Gramps 6 installable et sélection d’une famille | S1 | L1 | Archive extraite dans un profil isolé ; export CLI Gramps 6.0.8 validé |
| REF-02 | Modèle intermédiaire indépendant et testable | S1 | L1–L3 | Tests unitaires ; JSON avec identifiants et relations |
| REF-03 | Documentation FR/EN, code et métadonnées anglais | S1 | Tous | README FR/EN ; interface traduisible, catalogue FR restant |
| REF-04 | Architecture en six responsabilités | S1 | L2–L7 | Frontières initiales ; moteur généalogique et livre complet à réaliser |
| REF-05 | Ascendance par générations et descendance par branches | S2 | L4 | Règles § 4 : filiations explicites, autres unions, occurrences multiples |
| REF-06 | Repères généalogiques en haut de page et renvois | S2 | L4–L7 | À réaliser |
| REF-07 | Événements de vie, portraits et photos complémentaires | S2 | L3, L5–L7 | À réaliser |
| REF-08 | Citations partagées entre faits, annexes compactes | S2 | L3, L5–L7 | À réaliser |
| REF-09 | URL complètes et régions de médias Gramps | S2 | L2, L5–L7 | À prototyper |
| REF-10 | BOOK_PUBLICATION, BOOK_PROFILE, BOOK_EXCLUDE, BOOK_FEATURED | S1 | L3–L5 | § 6 : étiquette de note, attribut individuel YES, étiquettes médias ; exclusion prioritaire |
| REF-11 | Respect des droits, objets privés lisibles selon Gramps | S1 | L2–L3, L8 | Adaptateur utilisant la base fournie ; recette spécifique restante |
| REF-12 | LaTeX/PDF, HTML et ZIP ; faisabilité Gramps Web | S1 | L2, L6–L8 | Rendus de démonstration ; sorties et compatibilité Web non validées |

## Décision d’intégration du premier jalon

Le rapport emploie `CATEGORY_WEB`, mécanisme natif pour les rapports qui génèrent leurs propres fichiers. Il conserve ainsi le sélecteur de famille et le cycle de rapport Gramps, sans ouvrir un document PDF/ODT avant validation. Une option `destination` désigne explicitement le fichier JSON ; les futurs rendus restent à implémenter. Cette catégorie ne constitue pas une validation de Gramps Web.

Le statut d’enregistrement est `EXPERIMENTAL` : le statut `UNSTABLE` utilisé initialement est masqué par les versions publiques de Gramps. Ce choix est fondé sur le code installé et sur un essai de découverte réel.

## Points ouverts

- Références récupérées ; conserver leur transmission privée aux futurs intervenants. Les 27 scénarios sont associés aux tâches ci-dessous.
- Conserver la revue du premier jalon avant d’engager le moteur complet.
- Confirmer la licence de distribution déclarée GPL dans les métadonnées avant publication d’une version distribuée.
- Le dépôt GitHub a été créé privé ; les distributions publiques demandent une décision de visibilité.

## Règles désormais établies

- F0 doit comporter deux partenaires connus (AC-02). Les familles monoparentales rencontrées dans le parcours restent valides (AC-09). Le rapport minimal rejette désormais F0 incomplète ; l’adaptateur reste capable de représenter une famille monoparentale.
- Descendance : union des descendants de P0 et P1, y compris les autres unions. Tous les liens de filiation explicites sont conservés, sans transformer « aucun » en filiation. Les collatéraux ne déclenchent pas leur propre descendance.
- Fiche : événement individuel ou familial substantiel hors naissance/décès, ou attribut BOOK_PROFILE=YES. Une seule fiche par personne, à la première occurrence déterministe.
- Notes : étiquette native BOOK_PUBLICATION obligatoire ; une note partagée est publiée dans chaque contexte. Les six rôles éditoriaux de F0 sont des propositions techniques à éprouver.
- Médias : BOOK_EXCLUDE prime sur BOOK_FEATURED ; reproduction principale unique. PDF multipages jamais reproduit ; PDF monopage reproduit seulement sans URL externe.
- Livre : couverture, préliminaires, sommaire, ascendance, descendance, annexe documentaire unique et index des personnes. Notes de bas de page et renvois vers la pagination définitive du PDF.
- Gramps Web est une exigence de la version cible ; sa faisabilité reste à démontrer. LuaLaTeX est l’hypothèse initiale. Export de sources LaTeX/Git du livre : futur facultatif.
- Rapport de contrôle séparé limité aux contradictions de dates/lieux d’un même fait. Aucun avertissement documentaire ajouté dans le livre.
- La règle de recadrage retrouvée dans la discussion de conception n’est pas détaillée dans la v1.1 : conserver la provenance S2 et résoudre les variantes de régions dans le prototype médias, en respectant la reproduction principale unique.

## Scénarios de la v1.1 et lots responsables

Les résultats attendus exacts sont conservés au § 15 de S4. « À réaliser » signifie qu’aucune conformité de bout en bout n’est revendiquée.

| Scénario | Sujet | Tâches | État |
| --- | --- | --- | --- |
| AC-01 | Couple central et génération zéro | L1.3, L4.1, L5.1 | À réaliser / recette complète restante |
| AC-02 | Refus du couple incomplet | L1.3–L1.7 | Validé en CLI Gramps 6.0.8 ; CI 36288791405 |
| AC-03 | Descendants des autres unions | L4.3–L4.4 | À réaliser / recette complète restante |
| AC-04 | Filiations explicites multiples | L3.1, L4.4 | À réaliser / recette complète restante |
| AC-05 | Implexes, fiche unique et cycles | L4.4–L4.5 | À réaliser / recette complète restante |
| AC-06 | Collatéral documenté sans expansion | L4.1, L4.5 | À réaliser / recette complète restante |
| AC-07 | Éligibilité et BOOK_PROFILE=YES | L3.3, L4.5 | À réaliser / recette complète restante |
| AC-08 | Événement familial et fiche | L3.2, L5.2 | À réaliser / recette complète restante |
| AC-09 | Famille monoparentale dans le parcours | L3.1, L4.4, L5.2 | À réaliser / recette complète restante |
| AC-10 | Note Markdown partagée | L3.3, L5.2, L6.2, L7.3 | À réaliser / recette complète restante |
| AC-11 | Exclusion des notes non étiquetées | L3.3, L5.2 | À réaliser / recette complète restante |
| AC-12 | Portraits et photo pleine page | L5.5, L6.1, L7.4 | À réaliser / recette complète restante |
| AC-13 | Priorité BOOK_EXCLUDE | L3.3, L5.5 | À réaliser / recette complète restante |
| AC-14 | Citations réutilisées et multiples | L3.4, L5.3–L5.4, L6.4 | À réaliser / recette complète restante |
| AC-15 | Document partagé et reproduction unique | L5.4–L5.5 | À réaliser / recette complète restante |
| AC-16 | Quatre cas PDF/URL | L2.4, L5.5 | À réaliser / recette complète restante |
| AC-17 | Pagination finale cohérente | L6.4–L6.5 | À réaliser / recette complète restante |
| AC-18 | Fait sans citation et source sans dépôt | L3.4, L5.4 | À réaliser / recette complète restante |
| AC-19 | Contradictions et rapport séparé | L3.7, L5.7 | À réaliser / recette complète restante |
| AC-20 | Équivalence PDF/HTML et usage hors ligne | L6, L7, L8.1 | À réaliser / recette complète restante |
| AC-21 | Livre long et limites graphiques | L2.3, L6.3, L6.6 | À réaliser / recette complète restante |
| AC-22 | Desktop et Web complets | L1, L2.5, L8.2 | À réaliser / recette complète restante |
| AC-23 | Échappement et absence d’injection | L2.6, L6.2, L7.3 | À réaliser / recette complète restante |
| AC-24 | Stabilité du contenu et des ancres | L4.6, L5.6, L8.1 | À réaliser / recette complète restante |
| AC-25 | Métadonnées indépendantes de la langue | L3.3, L8.4 | À réaliser / recette complète restante |
| AC-26 | Documentation FR/EN et contrôle CI | L1.8, L8.4 | À réaliser / recette complète restante |
| AC-27 | Transmission des maquettes | L0.1, L6.1 | Originaux locaux récupérés et PDFs consultés ; transmission privée requise pour un nouveau clone |
