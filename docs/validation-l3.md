# L3 validation — extraction and normalization

Updated 27 September 2026. This validates the first JSON v0.2 snapshot; it does not mark all of L3 complete.

## Coverage

- `GrampsDatabaseAdapter` extracts the selected family, its members, and the unions/parent families directly referenced by those people.
- Parent-child links retain each parent's relationship type, original order, citations, notes, and the child-reference privacy flag.
- Individual and family events retain their associations and roles. Dates preserve entered text, components, qualifiers, bounds, and the Gramps serialization; places remain separate handle-linked records.
- The model includes alternate names, attributes, person associations and addresses, media and crop regions, notes, citations, sources, repositories, URLs, and tags.
- Note text is included only when the Gramps note has `BOOK_PUBLICATION`. A private note with that tag remains available, as required; working notes remain linked without their content.
- `BOOK_PROFILE = YES`, `BOOK_EXCLUDE`, and `BOOK_FEATURED` are read from their Gramps scopes. Invalid `BOOK_PROFILE` values and missing references produce structured diagnostics.
- Privacy flags remain on their records and associations. `privacy.contains_private_data` indicates whether the snapshot includes private data; readable records are not filtered.

## Checks run

```sh
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
.venv/bin/python build_addon.py
.venv/bin/python scripts/verify_gramps.py --gramps /Applications/Gramps.app/Contents/MacOS/Gramps
```

Results: 12 unit tests passed, Ruff passed, the add-on archive built, and the integration runner passed with Gramps macOS 6.0.8 in a temporary profile. The fictional GEDCOM fixture exercises birth, occupation, marriage, an approximate date, places, three citations, a source, a repository, and a media reference. The runner also checks incomplete-family and destination errors, explicit replacement, and protection of existing files.

Unit tests additionally cover media crop rectangles, multiple tags, publishable and unpublished notes, private data, person associations, addresses, typed parent-child links (including an explicit `None` relation), missing optional references, and avoiding repeated reads of referenced records.

## Remaining limits

- The snapshot is not the complete genealogy graph. Ancestry/descendant traversal and depth rules belong to L4.
- The native Gramps XML fixture now includes the `BOOK_PUBLICATION` tag and synthetic media crop rectangles. Source images and notes are fictional.
- The native Gramps recipe now verifies AC-11: an untagged working note linked to the central person and family keeps its source links but its text is absent from the editorial model, HTML, and PDF. It also tests all six F0 note roles, their direct family association, the publication gate, and diagnostics for duplicate, multirole, unpublished, and empty notes. Entry through the Gramps 6 interface remains to be checked.
- The privacy confirmation is implemented and partly validated on Desktop. Gramps Web remains unqualified; PDF and HTML/ZIP generation are delivered in L6–L7 with partial recipes.
