# Architecture

The project follows six deliberately separated responsibilities:

1. **Gramps integration** — registration, options, database access and report lifecycle.
2. **Extraction and normalization** — people, families, events, sources, citations, notes and media.
3. **Genealogical engine** — ancestry, descendants, generations, branches and deduplication.
4. **Editorial model** — the common book structure consumed by every renderer.
5. **LaTeX renderer** — print-oriented composition and PDF compilation.
6. **HTML renderer** — static web output and ZIP distribution.

The current code implements Gramps report registration and a reference-family option, extracts the selected family through `GrampsDatabaseAdapter`, builds the shared editorial model, and includes placeholder HTML/LaTeX renderers. The add-on build script assembles the source package beside the Gramps entry points so the report can be installed independently of the development checkout.

The adapter uses Gramps database getters only. It does not replace the database or attempt to bypass permissions. Integration behavior must still be confirmed in a running Gramps 6 installation.

Technical identifiers and metadata use English names. Reserved publication metadata uses the `BOOK_*` prefix, for example `BOOK_PUBLICATION`, `BOOK_PROFILE`, `BOOK_EXCLUDE`, and `BOOK_FEATURED`.

For Gramps 6 registration and manual add-on packaging conventions, the project consulted [`grostim/gramps-two-way-fan-chart`](https://github.com/grostim/gramps-two-way-fan-chart). It is an implementation reference only; its genealogy and rendering code are not copied into this project.
