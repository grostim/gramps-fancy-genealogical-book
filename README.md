# Gramps Fancy Genealogical Book

A modular Gramps 6 plugin for selecting a reference family and producing a shared intermediate book model, later rendered as LaTeX/PDF and HTML.

This repository starts from the functional and technical specification v1.1 and the family-book mockups discussed in the design conversation. The first milestone provides a Gramps 6 report that selects a reference family and exports a testable JSON intermediate model.

## Current milestone

- framework-independent domain model;
- Gramps 6 report registration and reference-family option;
- adapter boundary for Gramps data access;
- deterministic family selection and normalization;
- intermediate JSON-serializable book model;
- placeholder HTML and LaTeX renderers sharing the same model;
- add-on packaging entry point;
- bilingual documentation and continuous integration.

The complete book composition engine is deliberately out of scope for this first milestone.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
```

The domain package does not require Gramps to run its unit tests. The Gramps report entry point is in `gramps60/GrampsFancyBook` and delegates extraction to `GrampsDatabaseAdapter`.

Build a manual-install archive with:

```bash
python build_addon.py
```

The resulting `gramps60/download/GrampsFancyBook.addon.tgz` can be installed from Gramps' Plugin Manager. The first report output is a JSON model; PDF/HTML book composition is future work.

See [README.fr.md](README.fr.md) and [docs/architecture.md](docs/architecture.md).
