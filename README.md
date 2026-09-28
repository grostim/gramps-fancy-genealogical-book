# Gramps Fancy Genealogical Book

[Français](README.fr.md) · [Action plan (French)](docs/action-plan.fr.md) · [Architecture (French)](docs/architecture.fr.md) · [Architecture](docs/architecture.md) · [L2 prototypes](prototypes/README.md)

An experimental Gramps 6 add-on for a family genealogical book. The current milestone selects a reference family, extracts its ancestry and descendant graph to the chosen depths, and exports a shared JSON model with available media derivatives. Publication-quality LaTeX/PDF and HTML remain future milestones.

## What works now

- Native Gramps family selector and explicit JSON destination.
- JSON v0.7 model with genealogy occurrences, typed relationship links and an ordered editorial structure. Eligible person profiles and one family notice per in-scope family link to published notes, portraits and their captions, events, media and family sections.
- Ancestry and descendant extraction defaults to unlimited depth; each direction can also be limited independently with a non-negative integer.
- Structured dates use Gramps' date displayer while preserving the raw serialized date; each parent-child link exposes its recorded parentage type.
- Preservation of handles, Gramps IDs, original order, crop regions and privacy flags.
- Note text is exported only when the Gramps note has the `BOOK_PUBLICATION` tag; working notes remain referenced without their content.
- Unicode JSON, structured media-conversion diagnostics and coordinated replacement of the model and its PNG sidecar directory.
- Existing files preserved unless **Replace an existing file** is enabled.
- Reproducible add-on archive, unit tests and a real Gramps CLI integration runner.

Traversal follows recorded parent-child links. Unions, partners and siblings are included as context without automatically expanding their own lineages. The output is still a data model: HTML and LaTeX functions remain contract demonstrations. See the [L3 validation record](docs/validation-l3.md), the [L4 progress note](docs/validation-l4.md), and [requirement tracking](docs/requirements.fr.md).

## Build and install

```sh
python3 build_addon.py
```

Extract `gramps60/download/GrampsFancyBook.addon.tgz` into the Gramps 6 user plugins directory, preserving its `GrampsFancyBook/` folder, then restart Gramps. Typical locations:

- macOS: `~/Library/Application Support/gramps/gramps60/plugins/`
- Linux: `${XDG_DATA_HOME:-$HOME/.local/share}/gramps/gramps60/plugins/`
- Isolated profile: `$GRAMPSHOME/gramps/gramps60/plugins/`

In Gramps, the report is registered under **Reports → Web Pages**. This category supports add-ons that write their own files without the built-in PDF/ODT backend. This milestone writes a `.json` model and, when images can be converted, a neighboring `<name>_media/` folder. The JSON points to the derived PNG files and reports media that could not be prepared. Select a reference family and a `.json` destination; **Replace an existing file** also replaces the neighboring media directory. The destination directory must already exist.

Image and PDF converters are optional. For development, install them into Gramps' Python environment with `python -m pip install -e '.[media]'`. Until installation of these dependencies is automated in Gramps Desktop/Web packages, a missing dependency becomes a diagnostic and the JSON model can still be exported.

## CLI example

```sh
gramps -i tests/fixtures/reference-family.ged -a report \
  -p "name=gramps_fancy_genealogical_book,reference_family=F0001,max_ancestor_depth=unlimited,max_descendant_depth=unlimited,destination=/absolute/path/family.json"
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

See the [L1 validation record](docs/validation-l1.md) and the [L3 validation record](docs/validation-l3.md) for executed checks and remaining limitations.

The reference family must have two known partners (AC-02). Full source requirements: [original specification](docs/reference/Gramps_Fancy_Genealogical_Book_Specification_v1.1.md), with [provenance](docs/reference/README.md).
