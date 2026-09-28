# Gramps Fancy Genealogical Book

[Français](README.fr.md) · [Action plan (French)](docs/action-plan.fr.md) · [Architecture (French)](docs/architecture.fr.md) · [Architecture](docs/architecture.md) · [Contributing](CONTRIBUTING.md) · [Troubleshooting](docs/troubleshooting.md) · [L2 prototypes](prototypes/README.md) · [Media validation](docs/validation-media.md)

An experimental Gramps 6 add-on for a family genealogical book. The Gramps report now creates a self-contained HTML book ZIP by default, while retaining a JSON snapshot mode for diagnostics and a preliminary LaTeX book. Keyboard and small-screen improvements have been implemented; manual accessibility review and final PDF layout validation remain outstanding.

## What works now

- Native Gramps family selector, HTML ZIP output by default, and JSON snapshot output for diagnostics.
- JSON v0.8 model with genealogy occurrences, typed relationship links and an ordered editorial structure. Stable navigation targets and an alphabetical person index point to each profile or its primary occurrence. Eligible person profiles and one family notice per in-scope family link to published notes, portraits and their captions, events, media and family sections.
- Ancestry and descendant extraction defaults to unlimited depth; each direction can also be limited independently with a non-negative integer.
- Structured dates use Gramps' date displayer while preserving the raw serialized date; each parent-child link exposes its recorded parentage type.
- Preservation of handles, Gramps IDs, original order, crop regions and privacy flags.
- Published notes are rendered in HTML and LaTeX with Mistune's AST parser; raw HTML is emitted as literal text, and native semantic Gramps styles take precedence over Markdown syntax in the same note. See the documented [normalization policy](docs/decisions/003-note-markup.md).
- Unicode JSON, structured media-conversion diagnostics, a separate event-fact consistency report and coordinated replacement of model/report/media outputs.
- Existing files preserved unless **Replace an existing file** is enabled.
- Preliminary LaTeX output includes an automatic A4 cover with F0 editorial titles and text, couple names and available circular portrait medallions, plus genealogy sections, profiles, family notices, numbered citation references, clickable page references and the person index. Final PDF visual validation remains outstanding.
- Reproducible add-on archive, unit tests and a real Gramps CLI integration runner.

## F0 editorial notes

To customize the front matter, create one Gramps note per role and attach the native `BOOK_PUBLICATION` tag plus exactly one role tag: `BOOK_TITLE`, `BOOK_SUBTITLE`, `BOOK_INTRODUCTION`, `BOOK_DEDICATION`, `BOOK_AUTHOR` or `BOOK_PUBLICATION_DATE`. Link each note directly to the selected family. Duplicate roles use the note order in Gramps; a note with multiple role tags is omitted with a diagnostic. The Gramps 6 interface workflow and visual PDF compilation still need validation.

Traversal follows recorded parent-child links. Unions, partners and siblings are included as context without automatically expanding their own lineages. The LaTeX renderer is experimental; final typography, a converged PDF and visual acceptance remain outstanding. See the [L3 validation record](docs/validation-l3.md), the [L4 progress note](docs/validation-l4.md), [note markup policy](docs/decisions/003-note-markup.md), and [requirement tracking](docs/requirements.fr.md).

## Build and install

The archive build compiles the French Gramps report catalog from `gramps60/GrampsFancyBook/po/fr-local.po` and bundles it as `addon.mo`. GNU gettext (`msgfmt`) must be available on `PATH`; install the `gettext` package if needed (for example, `brew install gettext` on macOS).

```sh
python3 build_addon.py
```

Extract `gramps60/download/GrampsFancyBook.addon.tgz` into the Gramps 6 user plugins directory, preserving its `GrampsFancyBook/` folder, then restart Gramps. Typical locations:

- macOS: `~/Library/Application Support/gramps/gramps60/plugins/`
- Linux: `${XDG_DATA_HOME:-$HOME/.local/share}/gramps/gramps60/plugins/`
- Isolated profile: `$GRAMPSHOME/gramps/gramps60/plugins/`

In Gramps, the report is registered under **Reports → Web Pages**. This category supports add-ons that write their own files without the built-in PDF/ODT backend. The default report output is a self-contained `.zip` HTML book that can be extracted and viewed locally. The JSON snapshot remains available for diagnostics and writes a `.json` model, a separate `<name>_consistency.json` control report and, when images can be converted, a neighboring `<name>_media/` folder. The control report compares only events with the same native Gramps event attribute `BOOK_FACT_ID`; it records disjoint date ranges as conflicts and differing place references for manual review. For a diagnostic snapshot, select JSON snapshot and a `.json` destination; **Replace an existing file** also replaces the report and neighboring media directory. The destination directory must already exist.

The HTML and LaTeX note renderers require Mistune 3.x. Install it in the Python environment used by Gramps Desktop or the Gramps Web service with `python -m pip install 'mistune>=3,<4'`. The add-on declares `mistune` as a required module; installing the Python package from this repository also installs it through `pyproject.toml`.

Image and PDF converters remain optional so JSON export works without them. For development, install the project and its dependencies with `python -m pip install -e '.[dev,media]'`. In a Gramps Desktop environment that supports pip, install `Pillow` and `pypdfium2` with the same Python interpreter that launches Gramps, then restart Gramps: `python -m pip install 'Pillow>=10' 'pypdfium2>=4'`. A missing dependency produces a diagnostic and the affected derivatives are omitted. CI currently qualifies Ubuntu 24.04, Python 3.12 and Gramps 6.0.8; see the [media validation record](docs/validation-media.md). Gramps Web execution remains unqualified: the packages would need to be installed in the server environment, and no test instance has been validated.

## CLI example

```sh
gramps -i tests/fixtures/reference-family.ged -a report \
  -p "name=gramps_fancy_genealogical_book,reference_family=F0001,max_ancestor_depth=unlimited,max_descendant_depth=unlimited,output_format=json_snapshot,destination=/absolute/path/family.json"
```

Use `overwrite=True` in the option string to permit replacement. The bundled GEDCOM contains fictional people. For isolated, automated testing use the runner below, which installs the archive into a temporary Gramps profile and imports only this fixture. On macOS the executable is `/Applications/Gramps.app/Contents/MacOS/Gramps`.

## Development and validation

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/ruff check .
.venv/bin/pytest -q
.venv/bin/python build_addon.py
.venv/bin/python scripts/verify_gramps.py --gramps /path/to/gramps
```

Unit tests do not require Gramps. The integration runner requires Python 3.12+ and Gramps 6.0; it checks outputs and diagnostics because Gramps may return exit code zero for a failed report. CI targets Python 3.10–3.13 for the domain and Gramps 6.0.8 for integration.

See the [L1 validation record](docs/validation-l1.md), the [L3 validation record](docs/validation-l3.md), and the [media validation record](docs/validation-media.md) for executed checks and remaining limitations.

The reference family must have two known partners (AC-02). Full source requirements: [original specification](docs/reference/Gramps_Fancy_Genealogical_Book_Specification_v1.1.md), with [provenance](docs/reference/README.md).
