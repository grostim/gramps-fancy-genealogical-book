# Gramps Fancy Genealogical Book

[Français](README.fr.md) · [Action plan (French)](docs/action-plan.fr.md) · [Architecture (French)](docs/architecture.fr.md) · [Architecture](docs/architecture.md) · [Contributing](CONTRIBUTING.md) · [Troubleshooting](docs/troubleshooting.md) · [L2 prototypes](prototypes/README.md) · [Media validation](docs/validation-media.md)

An experimental Gramps 6 add-on for a family genealogical book. The Gramps report creates a self-contained HTML book ZIP by default, can compile a PDF with LuaLaTeX, and retains a JSON snapshot mode for diagnostics. Targeted PDF reviews have used fictional fixtures with 15 mm margins. An earlier 0.9.0 archive, with PDF-renderer sources matching commit `b8141bc`, produced a tagged nine-page A4 reference PDF in Gramps Desktop 6.0.8-1; all nine pages were reviewed. On October 9, the current renderer also produced a tagged 103-page A4 GUI PDF and an HTML ZIP from an isolated fictional tree with twenty public portraits. The initial page-by-page review found an orphaned line in citation [299]; after correcting citation pagination, a new PDF was generated and its appendix pages were re-reviewed. PDF/UA conformance, screen-reader behavior, and broader Desktop-version coverage remain unqualified ([validation record](docs/validation-addon-lifecycle.md)).

## What works now

- Native Gramps family selector, HTML ZIP output by default, and JSON snapshot output for diagnostics.
- JSON v0.8 model with genealogy occurrences, typed relationship links and an ordered editorial structure. Stable navigation targets and an alphabetical person index point to each profile or its primary occurrence. Eligible person profiles and one family notice per in-scope family link to published notes, portraits and their captions, events, media and family sections.
- Ancestry and descendant extraction defaults to unlimited depth; each direction can also be limited independently with a non-negative integer.
- Book headings and renderer-owned labels follow the language configured in Gramps, with French/English manual overrides and English fallback for unsupported locales. Names, notes, dates and source text are not translated.
- Structured dates use Gramps' date displayer while preserving the raw serialized date; each parent-child link exposes its recorded parentage type.
- Preservation of handles, Gramps IDs, original order, crop regions and privacy flags.
- Published notes are rendered in HTML and LaTeX with Mistune's AST parser; raw HTML is emitted as literal text, and native semantic Gramps styles take precedence over Markdown syntax in the same note. See the documented [normalization policy](docs/decisions/003-note-markup.md).
- Unicode JSON, structured media-conversion diagnostics, a separate event-fact consistency report and coordinated replacement of model/report/media outputs.
- Existing files preserved unless **Replace an existing file** is enabled.
- PDF output uses the preliminary LaTeX renderer, which includes an automatic A4 cover with F0 editorial titles and text, couple names and available circular portrait medallions, plus genealogy sections, profiles, family notices, per-call citation footnotes with abbreviated source details and links to final appendix pages, and the person index. The first page-by-page review of a 103-page GUI export found an orphaned cross-reference line in citation [299]. The renderer now keeps compact media-free citation entries together; the corrected export was generated and its appendix pages were visually re-reviewed. Broader scenarios and accessibility checks remain outstanding.
- Reproducible add-on archive, unit tests and a real Gramps CLI integration runner.

## F0 editorial notes

To customize the cover and front matter:

1. In Gramps, create or reuse the native tags `BOOK_PUBLICATION` and the six role tags below. These identify notes; they are not built-in Gramps note types.
2. Create one note per role, add its text, and assign both `BOOK_PUBLICATION` and exactly one role tag.
3. In the editor for the selected F0 family, open the **Notes** tab and link each note directly to that family. Matching tags on notes linked to another family do not apply.

| Tag | Content |
| --- | --- |
| `BOOK_TITLE` | Cover title; replaces the default title |
| `BOOK_SUBTITLE` | Cover subtitle; the couple’s names remain visible |
| `BOOK_AUTHOR` | Author on the cover |
| `BOOK_PUBLICATION_DATE` | Publication date on the cover, entered as note text |
| `BOOK_DEDICATION` | Dedication in the front matter |
| `BOOK_INTRODUCTION` | Introduction, after the dedication |

A role note without `BOOK_PUBLICATION`, without text, or with multiple role tags is omitted with a diagnostic. If multiple valid notes supply the same role, the first in F0’s note-link order is kept and later ones are reported. F0 role notes are not repeated in its family notice. The title and publication text are never inferred from genealogical data.

The integration recipe now uses native Gramps notes for all six roles and covers a missing publication tag, ambiguous roles, empty text, and duplicate roles in CLI export. Entry through the Gramps 6 interface and visual PDF acceptance remain to be qualified. See the [F0 notes decision](docs/decisions/004-f0-editorial-notes.md) and the [Gramps 6 manual for note and family editing](https://gramps-project.org/wiki/index.php/Gramps_6.0_Wiki_Manual).

Traversal follows recorded parent-child links. Unions, partners and siblings are included as context without automatically expanding their own lineages. The LaTeX renderer is experimental; final typography, a converged PDF and visual acceptance remain outstanding. See the [L3 validation record](docs/validation-l3.md), the [L4 progress note](docs/validation-l4.md), [note markup policy](docs/decisions/003-note-markup.md), and [requirement tracking](docs/requirements.fr.md).

## Build and install

The archive build compiles the French Gramps report catalog from `gramps60/GrampsFancyBook/po/fr-local.po` and bundles it as `addon.mo`. It also checks that the versions in `pyproject.toml`, the Gramps registration, and the POT/PO catalogs agree. GNU gettext (`msgfmt`) must be available on `PATH`; install the `gettext` package if needed (for example, `brew install gettext` on macOS).

```sh
python3 build_addon.py
```

This command creates the archive locally; the file is ignored by Git and is not yet published as a GitHub release.

Extract `gramps60/download/GrampsFancyBook.addon.tgz` into the Gramps 6 user plugins directory, preserving its `GrampsFancyBook/` folder, then restart Gramps. Typical locations:

- macOS: `~/Library/Application Support/gramps/gramps60/plugins/`
- Linux: `${XDG_DATA_HOME:-$HOME/.local/share}/gramps/gramps60/plugins/`
- Isolated profile: `$GRAMPSHOME/gramps/gramps60/plugins/`

To install an update manually, quit Gramps first and replace the complete `GrampsFancyBook/` folder with the folder from the new archive; do not merge individual files. Restart Gramps after replacing it. To uninstall the add-on, quit Gramps, remove only that folder, then restart the application. Other add-ons and Gramps family trees are not affected. The isolated profile lifecycle check is recorded in the [package validation](docs/validation-addon-lifecycle.md).

In Gramps, the report is registered under **Reports → Web Pages**. This category supports add-ons that write their own files without the built-in PDF/ODT backend. The default report output is a self-contained `.zip` HTML book that can be extracted and viewed locally. Select PDF book (LuaLaTeX) or let automatic mode select PDF from a `.pdf` destination; LuaLaTeX must be available on the Gramps process `PATH` or, on macOS, at the standard BasicTeX/MacTeX location `/Library/TeX/texbin/lualatex`. The JSON snapshot remains available for diagnostics and writes a `.json` model, a separate `<name>_consistency.json` control report and, when images can be converted, a neighboring `<name>_media/` folder. The control report compares only events with the same native Gramps event attribute `BOOK_FACT_ID`; it records disjoint date ranges as conflicts and differing place references for manual review. To obtain it, select **JSON snapshot and consistency report** and a `.json` destination; **Replace an existing file** also replaces the report and neighboring media directory. The destination directory must already exist. See [how to declare and inspect versions of one fact](docs/consistency-report.md).

PDF compilation normally has a three-minute overall limit (two minutes per pass). For a large book, select **Allow extended PDF compilation (up to 30 minutes)** in the report options; each pass is then limited to ten minutes. This setting affects only PDF output and does not guarantee that a very long book meets the target performance budget.

The HTML and LaTeX note renderers require Mistune 3.x. Install it in the Python environment used by Gramps Desktop or the Gramps Web service with `python -m pip install 'mistune>=3,<4'`. The add-on declares `mistune` as a required module; installing the Python package from this repository also installs it through `pyproject.toml`.

Image and PDF converters remain optional so JSON export works without them. For development, install the project and its dependencies with `python -m pip install -e '.[dev,media]'`. In a Gramps Desktop environment that supports pip, install `Pillow` and `pypdfium2` with the same Python interpreter that launches Gramps, then restart Gramps: `python -m pip install 'Pillow>=10' 'pypdfium2>=4'`. A missing dependency produces a diagnostic and the affected derivatives are omitted. PDF output additionally requires LuaLaTeX (provided by TeX Live) on the `PATH` used to launch Gramps or at `/Library/TeX/texbin/lualatex` on macOS. The first full review of the 103-page GUI PDF found citation [299] split across a page break. After correcting citation pagination, the GUI export was repeated and the affected appendix pages were visually re-reviewed. Broader scenarios, PDF/UA conformance, and screen-reader behavior also remain unqualified. CI qualifies Ubuntu 24.04, Python 3.12 and Gramps 6.0.7–6.0.8; see the [media validation record](docs/validation-media.md). Gramps Web execution remains unqualified: the packages would need to be installed in the server environment, and no test instance has been validated.

## Book language

Book language defaults to the language configured in Gramps. Select French or English in the report options to override it; unsupported Gramps locales use English. This changes renderer-owned headings, navigation and accessibility labels in both PDF and HTML output. Names, notes, event descriptions and source text are not translated. Dates retain the display string already formatted by Gramps during extraction.

## CLI example

```sh
gramps -i examples/reference-family.ged -a report \
  -p "name=gramps_fancy_genealogical_book,reference_family=F0001,max_ancestor_depth=unlimited,max_descendant_depth=unlimited,book_language=auto,output_format=json_snapshot,privacy_acknowledged=True,destination=/absolute/path/family.json"
```

The `privacy_acknowledged=True` option is required for every CLI export. In Desktop and Web, confirm the privacy option for each export. The report does not filter or anonymize readable data. Use `overwrite=True` in the option string to permit replacement. The [sample GEDCOM](examples/reference-family.ged) contains only fictional people, places and archive references, with no media. For isolated, automated testing use the runner below, which installs the archive into a temporary Gramps profile and imports its own fixture from `tests/fixtures/`. On macOS the executable is `/Applications/Gramps.app/Contents/MacOS/Gramps`.

To try the book output, use the command above with `output_format=pdf` and a `.pdf` destination, or `output_format=html_zip` and a `.zip` destination. Gramps must be able to find LuaLaTeX to generate the PDF.

## Development and validation

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev,media]'
.venv/bin/ruff check .
.venv/bin/pytest -q
.venv/bin/python build_addon.py
.venv/bin/python scripts/verify_gramps.py --gramps /path/to/gramps
```

Unit tests do not require Gramps. The integration runner requires Python 3.12+ and Gramps 6.0; it checks outputs and diagnostics because Gramps may return exit code zero for a failed report. CI targets Python 3.10–3.13 for the domain and Gramps 6.0.7 and 6.0.8 for stable integration. A non-blocking canary also exercises Gramps 6.1.0-beta2 from a pinned upstream commit; it retargets only the temporary CI package manifest to probe the newer APIs and does not declare stable support.

See the [L1 validation record](docs/validation-l1.md), the [L3 validation record](docs/validation-l3.md), and the [media validation record](docs/validation-media.md) for executed checks and remaining limitations.

The reference family must have two known partners (AC-02). Full source requirements: [original specification](docs/reference/Gramps_Fancy_Genealogical_Book_Specification_v1.1.md), with [provenance](docs/reference/README.md).

## License

Distributed under the GNU General Public License, version 3 or any later version. See [LICENSE](LICENSE).
