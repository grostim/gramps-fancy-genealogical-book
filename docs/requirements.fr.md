# Suivi des références et exigences

État au 27 septembre 2026. Les identifiants ci-dessous sont propres à ce suivi et ne remplacent pas ceux des 24 scénarios annoncés dans la spécification originale.

## Sources

- S1 : discussion « Spécification plugin Gramps », conversation `6ab6271b-2764-83eb-bee1-104a02c02d59`.
- S2 : discussion « Concevoir un livre généalogique », conversation `6ab57872-e2e4-83eb-b0b9-1c0081b338b0`.
- S3 : [synthèse locale](specification-v1.1.md), établie à partir de S1.

Le document complet `Gramps_Fancy_Genealogical_Book_Specification_v1.1.md`, l’archive `Gramps_Fancy_Genealogical_Book_Specification_v1.1_et_maquettes.zip` et les maquettes `maquette_structure_livret_familial` / `maquette_livret_familial_evenements_sources` (PDF et HTML) restent à importer. Les liens `sandbox:/mnt/data/...` de la discussion n’ont pas fourni de fichiers accessibles dans le workspace. Les recherches locales ciblées n’ont pas retrouvé ces documents.

## Matrice provisoire

| ID local | Exigence retrouvée | Source | Lot | Preuve ou état |
| --- | --- | --- | --- | --- |
| REF-01 | Plugin Gramps 6 installable et sélection d’une famille | S1 | L1 | Archive extraite dans un profil isolé ; export CLI Gramps 6.0.8 validé |
| REF-02 | Modèle intermédiaire indépendant et testable | S1 | L1–L3 | Tests unitaires ; JSON avec identifiants et relations |
| REF-03 | Documentation FR/EN, code et métadonnées anglais | S1 | Tous | README FR/EN ; interface traduisible, catalogue FR restant |
| REF-04 | Architecture en six responsabilités | S1 | L2–L7 | Frontières initiales ; moteur généalogique et livre complet à réaliser |
| REF-05 | Ascendance par générations et descendance par branches | S2 | L4 | Détails à rapprocher de la v1.1 complète |
| REF-06 | Repères généalogiques en haut de page et renvois | S2 | L4–L7 | À réaliser |
| REF-07 | Événements de vie, portraits et photos complémentaires | S2 | L3, L5–L7 | À réaliser |
| REF-08 | Citations partagées entre faits, annexes compactes | S2 | L3, L5–L7 | À réaliser |
| REF-09 | URL complètes et régions de médias Gramps | S2 | L2, L5–L7 | À prototyper |
| REF-10 | BOOK_PUBLICATION, BOOK_PROFILE, BOOK_EXCLUDE, BOOK_FEATURED | S1 | L3–L5 | Noms confirmés ; sémantique et priorités à extraire du document complet |
| REF-11 | Respect des droits, objets privés lisibles selon Gramps | S1 | L2–L3, L8 | Adaptateur utilisant la base fournie ; recette spécifique restante |
| REF-12 | LaTeX/PDF, HTML et ZIP ; faisabilité Gramps Web | S1 | L2, L6–L8 | Rendus de démonstration ; sorties et compatibilité Web non validées |

## Décision d’intégration du premier jalon

Le rapport emploie `CATEGORY_WEB`, mécanisme natif pour les rapports qui génèrent leurs propres fichiers. Il conserve ainsi le sélecteur de famille et le cycle de rapport Gramps, sans ouvrir un document PDF/ODT avant validation. Une option `destination` désigne explicitement le fichier JSON ; les futurs rendus restent à implémenter. Cette catégorie ne constitue pas une validation de Gramps Web.

Le statut d’enregistrement est `EXPERIMENTAL` : le statut `UNSTABLE` utilisé initialement est masqué par les versions publiques de Gramps. Ce choix est fondé sur le code installé et sur un essai de découverte réel.

## Points ouverts

- Importer les originaux puis associer les 24 scénarios à leurs tâches et preuves.
- Conserver la revue du premier jalon avant d’engager le moteur complet.
- Confirmer la licence de distribution déclarée GPL dans les métadonnées avant publication d’une version distribuée.
- Le dépôt GitHub a été créé privé ; les distributions publiques demandent une décision de visibilité.
