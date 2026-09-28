# Architecture

This page describes the implementation on the current development line and separates shipped behavior from validation that still needs to be demonstrated.

The project has six responsibilities:

1. **Gramps integration** — report registration, options, database access, and report lifecycle.
2. **Extraction and normalization** — conversion of Gramps people, families, events, sources, citations, notes, and media into framework-independent records.
3. **Genealogical traversal** — bounded ancestry and descendant paths, generations, branches, occurrences, and deduplication.
4. **Editorial model** — ordered book parts, family notices, person profiles, notes, citations, media placements, and navigation targets.
5. **LaTeX renderer** — print-oriented book source with cross-references and page references.
6. **HTML renderer** — static book pages and an offline ZIP archive.

## Snapshot and traversal

The extraction pipeline emits JSON schema 0.8. Stable family-section and person-occurrence IDs connect partners, children, parent-child relationships, and repeated appearances. Occurrences retain generation, branch, and lineage-path information, including alternative paths to the same person. Each person points to a primary occurrence even when no full profile is created. Ancestry and descendant limits are independent and default to unlimited; partners encountered through marriage do not start additional ancestry expansion.

The adapter reads through Gramps database getters and does not modify the database. It reports missing or inaccessible references as diagnostics and preserves private flags on data that the supplied database makes readable. It does not bypass Gramps access controls. Before each export, the user must acknowledge that readable private data and information about living people may be included; previous Desktop acknowledgements are reset for each run. This confirmation does not filter or anonymize the output.

## Editorial model and publication rules

The ordered book model links the cover and front matter, contents, ancestry and descendant sections, family notices, eligible person profiles, documentary material, and the person index. Notes enter publication references only when tagged `BOOK_PUBLICATION`. The six cover/front-matter roles are read from qualifying notes linked directly to the selected reference family (F0). Person profiles can be selected by the implemented eligibility rules, including `BOOK_PROFILE=YES`.

Family notices are unique per family and point to every context in which the family appears. Citation targets are unique per Gramps Citation handle; each call retains its context and field path. Citation entries link to their Source, that Source's repositories, and eligible attached media. Compact numbering follows first use in book order. Media placements are unique per Gramps media handle and retain their contextual regions and citation associations.

The separate consistency report groups events only when they share an explicit `BOOK_FACT_ID`. It identifies disjoint date ranges as confirmed conflicts and differing place references for review. This report does not merge event records or change the book's event list. Similar dates, places, event types, or descriptions never create a group.

## Media and renderers

The media utility resolves database-relative paths through Gramps and refuses media marked `BOOK_EXCLUDE`. Raster images are EXIF-oriented, cropped to the requested region, and written as lossless PNG. For PDFs, a citation URL takes precedence; an unlinked multipage PDF remains a reference, while an unlinked single-page PDF may be rasterized at 300 DPI subject to a pixel ceiling. Pillow and pypdfium2 are optional dependencies. Recoverable conversion errors become structured diagnostics.

The LaTeX renderer composes the book's cover and front matter, genealogy, profiles, family notices, citations, media, index, and cross-references. The Gramps report can compile this source into a PDF with LuaLaTeX; the compiler runs without shell escape, repeats until auxiliary references stabilize, and rejects unresolved references or overfull boxes. LuaLaTeX is optional and required only for PDF output. The PDF mode is experimental; installation in Gramps and page-by-page visual review remain validation steps.

The HTML renderer produces a static book with internal navigation, citation links, notes, media, and an index. The ZIP includes `index.html`, embedded styles, and approved PNG derivatives at relative paths, so it can be opened offline after extraction. The current renderer includes responsive layout, a skip link, visible keyboard focus, and informative image alternatives.

The report's automatic format selection maps `.pdf` to LuaLaTeX PDF output, `.zip` to HTML ZIP, and legacy `.json` destinations to JSON snapshots; explicit output formats remain available. This compatibility behavior does not imply that Gramps Web has been qualified.

## Remaining validation

Implementation is ahead of its end-to-end evidence. The outstanding work includes running the original acceptance scenarios against supported Gramps Desktop and Web versions; checking real media and relative links in an extracted offline ZIP; reviewing keyboard, screen-reader, and viewport behavior; and visually comparing generated PDF pages with the specification and supplied mockups. See [the L7 validation record](validation-l7.fr.md) for the current evidence and limitations.

Technical identifiers and reserved publication metadata use English names and the `BOOK_*` prefix, for example `BOOK_PUBLICATION`, `BOOK_PROFILE`, `BOOK_EXCLUDE`, `BOOK_FEATURED`, and `BOOK_FACT_ID`.

For Gramps 6 registration and manual add-on packaging conventions, the project consulted [grostim/gramps-two-way-fan-chart](https://github.com/grostim/gramps-two-way-fan-chart). It is an implementation reference only; its genealogy and rendering code are not copied.
