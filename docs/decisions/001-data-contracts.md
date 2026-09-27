# ADR 001 — Data contracts / Contrats de données

Status: accepted for extraction v0.2; 2026-09-27. This document does not redefine the v1.1 requirements.

## English

### Boundaries

1. The Gramps adapter reads the supplied database and produces a normalized snapshot. It retains handles, public IDs, relationship types, association roles, original positions and access limitations. It never modifies the database.
2. Traversal produces occurrences and paths, not copies of people. A path-local visited set stops cycles; a separate global registry selects the primary occurrence without discarding alternate relationships.
3. Editorial assembly selects profiles, facts, notes, citations, media placements, anchors and index entries. All ordering decisions happen here or in traversal.
4. Renderers consume a resolved editorial model. They do not query Gramps or reselect the genealogy. PDF page numbers are resolved by compilation; HTML uses the same stable anchors.

### Identity and order

| Concept | Proposed contract |
| --- | --- |
| Object identity | `(object_type, handle)` within one snapshot; public Gramps ID remains a display field |
| Occurrence identity | Object key plus deterministic path of typed relationship edges |
| Source dates | Original display representation, qualifiers and available comparison bounds; no invented precision |
| Main occurrence | First occurrence in deterministic book order, with one optional full profile |
| Anchors | Safe type prefix plus deterministic digest of the internal key; never derive anchors from page numbers or display names |
| Citations | One entry per citation handle; editorial number follows first use in final book order |
| Media derivatives | Source-content digest + rectangle + orientation/conversion policy version |
| Media placement | One documentary reproduction per media identity; derivative cache identity does not override this requirement |
| Ordering | Branch/parent/union grouping, comparable dates, original position where required, then stable technical key |

JSON v0.2 is the first handle-keyed extraction snapshot, not the final editorial schema. It includes a `privacy.contains_private_data` summary and structured diagnostics. Future incompatible extraction or book-model changes must increment the schema version instead of silently repurposing this one.

### Outputs and diagnostics

A run has a staging directory and produces exactly the selected PDF or HTML ZIP. Validate the staged result before replacing a previous deliverable. Separate user cancellation, fatal generation errors, recoverable technical diagnostics and the narrowly scoped genealogy conflict report (§ 12). Logs and real-family exports are local run artifacts, never repository fixtures.

Resolve before implementation: overlapping date bounds, six editorial note roles on F0, “none” parent-child links, media-reference regions versus unique documentary placement, native rich notes plus Markdown, authorized private-object visibility.

## Français

### Frontières

1. L’adaptateur lit la base fournie et produit un instantané normalisé : handles, identifiants publics, types de filiation, rôles, positions d’origine et limites d’accès. Il ne modifie jamais la base.
2. Le parcours produit des occurrences et des chemins, pas des copies de personnes. Une pile locale coupe les cycles ; un registre global distinct choisit l’occurrence principale sans supprimer les liens alternatifs.
3. L’assemblage éditorial décide des fiches, faits, notes, citations, médias, ancres et index. Les choix d’ordre appartiennent à ce niveau ou au parcours.
4. Les rendus consomment le modèle résolu, sans relire Gramps ni recalculer le périmètre. La compilation résout les pages PDF ; HTML utilise les mêmes ancres stables.

### Identité et ordre

| Concept | Contrat proposé |
| --- | --- |
| Objet | `(type_objet, handle)` dans un instantané ; identifiant Gramps public conservé pour affichage |
| Occurrence | Clé objet et chemin déterministe d’arêtes typées |
| Dates | Affichage original, qualificatifs et bornes disponibles, sans précision inventée |
| Occurrence principale | Première occurrence dans l’ordre du livre ; au plus une fiche complète |
| Ancres | Préfixe de type et empreinte déterministe de la clé ; indépendantes du nom et de la page |
| Citations | Une entrée par handle ; numéro selon le premier appel dans l’ordre éditorial final |
| Dérivés médias | Empreinte du contenu + rectangle + version de la politique orientation/conversion |
| Placement média | Une reproduction documentaire par objet ; le cache des dérivés ne change pas cette règle |
| Tri | Branche/parent/union, dates comparables, position d’origine si requise, puis clé technique stable |

Le JSON v0.2 est le premier instantané d’extraction indexé par handle, pas le schéma éditorial final. Il inclut le résumé `privacy.contains_private_data` et des diagnostics structurés. Toute évolution incompatible de l’extraction ou du modèle du livre devra augmenter la version plutôt que réaffecter silencieusement les champs.

### Sorties et diagnostics

Chaque exécution possède son répertoire temporaire et produit exclusivement le PDF ou ZIP HTML choisi. Le résultat est contrôlé avant remplacement d’un livrable précédent. Distinguer annulation, erreur bloquante, diagnostic technique récupérable et rapport généalogique limité au § 12. Les journaux et exports réels restent locaux, hors fixtures versionnées.

Restent à éprouver : dates aux bornes superposées, six rôles de notes sur F0, filiation « aucun », régions de médias et reproduction unique, Markdown avec notes riches, visibilité autorisée des objets privés.
