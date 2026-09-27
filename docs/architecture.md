# Architecture

The project follows six deliberately separated responsibilities:

1. **Gramps integration** — registration, options, database access and report lifecycle.
2. **Extraction and normalization** — people, families, events, sources, citations, notes and media.
3. **Genealogical engine** — ancestry, descendants, generations, branches and deduplication.
4. **Editorial model** — the common book structure consumed by every renderer.
5. **LaTeX renderer** — print-oriented composition and PDF compilation.
6. **HTML renderer** — static web output and ZIP distribution.

The extraction layer now builds a framework-independent JSON v0.2 snapshot. It includes the selected family, its members, directly linked unions and parent families, event references and roles, date fields, places, person addresses and associations, notes, citations, sources, repository references, media references, tags and attributes. Handle-keyed caches avoid fetching an object more than once within a snapshot; missing optional references become structured diagnostics.

This is still an extraction boundary, not a complete genealogy graph walk or editorial book. The report consumes this richer snapshot, while the HTML and LaTeX renderers remain placeholders. Notes expose their text only when tagged `BOOK_PUBLICATION`. Private flags are preserved, and the JSON privacy summary indicates when the snapshot contains private records or associations. The report does not yet show the publication warning required before exporting a finished book.

The adapter uses Gramps database getters only. It does not modify the database, filter out private records that the supplied database makes readable, or attempt to bypass access restrictions. The current snapshot follows one relationship hop from the central family; L4 will add deliberate ancestry and descendant traversal.

Technical identifiers and metadata use English names. Reserved publication metadata uses the `BOOK_*` prefix, for example `BOOK_PUBLICATION`, `BOOK_PROFILE`, `BOOK_EXCLUDE`, and `BOOK_FEATURED`.

For Gramps 6 registration and manual add-on packaging conventions, the project consulted [`grostim/gramps-two-way-fan-chart`](https://github.com/grostim/gramps-two-way-fan-chart). It is an implementation reference only; its genealogy and rendering code are not copied into this project.
