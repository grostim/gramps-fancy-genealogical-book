# Foundation validation — 2026-09-27

[Français](validation-l1.fr.md)

## Environment and isolation

macOS Gramps 6.0.8, bundled Python 3.13.2. Only the synthetic GEDCOM fixture (four people, two families) was used. The CLI integration runner installs the archive in a temporary Gramps profile, outside the source checkout, with a separate cache. No personal family tree was used.

## Completed checks

- Nine unit tests, Ruff and deterministic packaging passed.
- The installed add-on resolves the selected family, preserving Unicode, public Gramps IDs and internal handles.
- The adapter can represent a single-parent family; selecting an incomplete reference couple is rejected under AC-02.
- Invalid/empty family selection, existing-output protection, explicit replacement, missing/unavailable/invalid destinations and temporary-file cleanup are covered by CLI integration.
- The file-collision diagnostic now suggests another destination or explicit replacement without exposing the temporary path.
- Gramps may return zero for report errors: the runner checks diagnostics and output contents as well.

[CI run 36288791405](https://github.com/grostim/gramps-fancy-genealogical-book/actions/runs/36288791405), commit `3fcd1e9`, passed on Python 3.10–3.13 plus real Gramps 6.0.8 on Ubuntu 24.04.

## macOS GUI

After unlocking the Mac, the isolated `FancyBookSynthetic` profile was used to open the report from Reports → Web Pages, open the native family selector, choose F0001, enter a JSON destination and export with replacement disabled. The JSON contained F0001 and I0001/I0002/I0003 with the expected Unicode names and handles.

Reopening the report preserved family and destination. Submitting the same destination showed a report error; SHA-256 confirmed the existing file was unchanged. The subsequent foundation review replaced the low-level collision detail with an actionable message. Other invalid selections/destinations were checked in CLI, not all repeated in the GUI.

## Reproduction

```sh
.venv/bin/ruff check .
.venv/bin/pytest -q
.venv/bin/python build_addon.py
.venv/bin/python scripts/verify_gramps.py --gramps /Applications/Gramps.app/Contents/MacOS/Gramps
```

## Remaining scope

The minimal L1 flow is demonstrated in CLI and macOS GUI and is ready for foundation review. Full AC-22 Desktop/Web acceptance, complete translation, PDF/HTML books and the complete set of 27 acceptance scenarios remain future work. The recovered design originals and mockup review are documented under [reference/](reference/README.md).
