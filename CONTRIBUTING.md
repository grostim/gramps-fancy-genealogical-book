# Contributing

This project is an experimental Gramps 6 add-on. Contributions should keep the boundary between Gramps integration, normalized data, genealogy traversal, editorial model, and renderers clear. See the [architecture guide](docs/architecture.md) and the [French guide](CONTRIBUTING.fr.md).

## Before opening a pull request

- Start from the current `main` branch and make a focused branch for the change.
- Keep changes aligned with the specification and record any changed acceptance behavior in `docs/requirements.fr.md` and `docs/action-plan.fr.md`.
- Use Conventional Commits, for example `feat(html): add family navigation` or `docs: clarify installation`.
- Describe user-visible behavior, validation performed, and limitations in the pull request.

## Protect family data

Use the fictional data in `tests/fixtures/reference-family.ged` and synthetic records in tests. Do not commit a real family tree, names, dates, places, photographs, scans, exported JSON, or logs containing personal data. Remove personal data from issue reports and pull request examples.

## Development setup

The package supports Python 3.10 and later. From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev,media]'
.venv/bin/ruff check .
.venv/bin/pytest -q
.venv/bin/python build_addon.py
```

The add-on build also needs GNU gettext's `msgfmt` on `PATH` when compiling the French report catalog. Install the system `gettext` package if the command is unavailable. The `media` extra installs Pillow and pypdfium2 for media conversion, which the test suite imports.

For the real Gramps integration runner, use Python 3.12 or later with Gramps 6.0 installed:

```sh
.venv/bin/python scripts/verify_gramps.py --gramps /path/to/gramps
```

The runner installs the built add-on into a temporary Gramps profile and imports the fictional reference GEDCOM. It does not require a personal database. CI covers Python 3.10–3.13 and uses Gramps 6.0.7 and 6.0.8 for integration; a local run on another Gramps patch version is useful evidence but does not replace either CI target.

## Translation and generated files

Add or update report labels in `gramps60/GrampsFancyBook/po/fr-local.po`. The build compiles this catalog and includes the resulting `addon.mo` in the archive. Keep translations in sync with source labels. Do not commit generated `.mo` files or `gramps60/download/GrampsFancyBook.addon.tgz`; the build creates the catalog temporarily and the archive is generated output.

## Pull request checklist

- Explain the intended behavior and link the relevant requirement or plan item.
- List the checks actually run and their results; do not describe an unrun check as passed.
- Include only fictional, privacy-safe examples.
- Update user and developer documentation when behavior, setup, supported environments, or known limitations change.
- Identify any manual Gramps Desktop or Web work still needed.
