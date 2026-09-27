# Architecture

The project follows six deliberately separated responsibilities:

1. **Gramps integration** — registration, options, database access and report lifecycle.
2. **Extraction and normalization** — people, families, events, sources, citations, notes and media.
3. **Genealogical engine** — ancestry, descendants, generations, branches and deduplication.
4. **Editorial model** — the common book structure consumed by every renderer.
5. **LaTeX renderer** — print-oriented composition and PDF compilation.
6. **HTML renderer** — static web output and ZIP distribution.

The extraction and traversal layers now build a framework-independent JSON v0.7 model. Family sections have stable IDs and link to the in-scope partner and child occurrences; parent-child links retain the relevant occurrence IDs and the recorded relationship type for each parent. Each occurrence also carries `primary_occurrence_id` for the person’s first appearance, even when no full profile exists; it points back to its family sections and carries generation, branch, and path data for the genealogy marker. An ordered editorial structure links the cover, front matter, contents, ancestry, descent, documentary appendix and person index to family sections and occurrences. Eligible person profiles reference their events, media and family sections. One editorial family notice is created for each in-scope family, with a canonical section and links to every context section where that family appears; its family event and media references are stored once even if the family has multiple appearances. Narrative composition, captions and source entries remain to be built. Independent ancestry and descendant limits bound extraction; both default to unlimited. Handle-keyed caches avoid fetching an object more than once within a snapshot; missing optional references become structured diagnostics.

The traversal model assigns each occurrence a part, generation, family and branch roots while preserving alternative lineage paths. Unions and partners provide context without becoming new traversal roots. The HTML and LaTeX renderers do not consume this traversal model yet and remain placeholders. Notes expose their text only when tagged `BOOK_PUBLICATION`. Private flags are preserved, and the JSON privacy summary indicates when the snapshot contains private records or associations. The report does not yet show the publication warning required before exporting a finished book.

The adapter uses Gramps database getters only. It does not modify the database, filter out private records that the supplied database makes readable, or attempt to bypass access restrictions. It loads only the selected ancestry and descendant paths plus required family context, without expanding the ancestry of spouses introduced only by marriage.

Technical identifiers and metadata use English names. Reserved publication metadata uses the `BOOK_*` prefix, for example `BOOK_PUBLICATION`, `BOOK_PROFILE`, `BOOK_EXCLUDE`, and `BOOK_FEATURED`.

For Gramps 6 registration and manual add-on packaging conventions, the project consulted [`grostim/gramps-two-way-fan-chart`](https://github.com/grostim/gramps-two-way-fan-chart). It is an implementation reference only; its genealogy and rendering code are not copied into this project.
