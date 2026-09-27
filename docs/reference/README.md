# Design source provenance

The original [specification v1.1](Gramps_Fancy_Genealogical_Book_Specification_v1.1.md), dated 2026-09-25, was recovered on 2026-09-27 from `Gramps_Fancy_Genealogical_Book_Specification_v1.1_et_maquettes.zip` in Downloads. Its bytes and the four mockups match the archive. [manifest.json](manifest.json) records sizes and SHA-256 checksums.

Source: [Spécification plugin Gramps](https://chatgpt.com/c/6ab6271b-2764-83eb-bee1-104a02c02d59). The original has 18 sections and **27** acceptance scenarios, AC-01–AC-27. It supersedes the earlier visible-text transcription, retained for traceability.

The four mockups are available locally under `reference_maquette/`, deliberately ignored by Git because they contain real family data (§ 13). Transfer them privately to future implementers; a fresh clone does not contain them. The plugin archive and test fixtures exclude these references. Consult [mockup-review.md](mockup-review.md) before implementing templates.

# Provenance française

La [spécification originale v1.1](Gramps_Fancy_Genealogical_Book_Specification_v1.1.md), datée du 25 septembre 2026, a été récupérée le 27 septembre depuis l’archive ZIP présente dans Téléchargements. Le Markdown et les quatre maquettes sont identiques aux fichiers de l’archive ; leurs tailles et empreintes SHA-256 figurent dans [manifest.json](manifest.json).

L’original comporte 18 sections et **27 scénarios AC-01 à AC-27**. Il remplace comme référence la transcription visible antérieure, conservée pour traçabilité.

Les quatre maquettes sont disponibles localement dans `reference_maquette/`. Elles contiennent des données familiales réelles et sont exclues de Git conformément au § 13. Un clone neuf ne les contient pas : leur transmission privée reste nécessaire pour les futurs intervenants. Elles sont aussi exclues de l’archive du plugin et des fixtures. Consulter la [revue des maquettes](mockup-review.md) avant l’implémentation graphique.
