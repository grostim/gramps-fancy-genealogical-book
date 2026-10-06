# Internal draft — version 0.9.0 notes

**Status: preparation only.** The add-on remains marked `EXPERIMENTAL` in Gramps. No GitHub Release has been published; this document does not announce a stable version.

## Planned contents

- A Gramps 6 report centered on a reference family, with offline HTML books in ZIP archives, LuaLaTeX PDF output, and a diagnostic JSON snapshot.
- Ancestor and descendant traversal, individual profiles and family notices, an index, internal navigation, and reusable citation references.
- F0 editorial notes, events, sources and repositories, media and crop regions, alternative text, French/English book language, and a privacy acknowledgement for each export.
- Reproducible archive construction and a French catalog compiled during the build.

## Fictional example

The [English README](../README.md#cli-example) describes importing and exporting the [reference-family.ged](../examples/reference-family.ged) sample. Its people, places, and archival references are fictional; it has no media. CLI import into an isolated Gramps 6.0.8-1 profile has been confirmed; exporting the report from this example remains outstanding. See the [import record](validation-example-import-20261006.json). It is not a complete book template.

## Verification available

- CI run [37517722010](https://github.com/grostim/gramps-fancy-genealogical-book/actions/runs/37517722010) passes for Python 3.10–3.13, Windows, macOS, Gramps 6.0.7 and 6.0.8 CLI integration, the Gramps 6.1 canary, and the LuaLaTeX prototype.
- On Gramps 6.0.8 in a clean profile, the 0.9.0 archive generates JSON, HTML ZIP, and PDF output; the tagged French PDF has 18 A4 pages. Configured margins are 15 mm. See [package validation](validation-addon-lifecycle.md).
- The current CLI recipe does not prove graphical installation of the current archive. Launching the temporary Gramps window and completing the corresponding GUI export remain outstanding.

## Known limitations

- Repeatable support evidence covers CLI exports with Gramps 6.0.7 and 6.0.8. The 6.1 canary is non-blocking; other Desktop versions are unqualified.
- Gramps Web is not supported. The API 3.23.1 audit found blockers for `CATEGORY_WEB`, `.zip` archives, the server output path, and task progress. See the [Gramps Web audit](validation-gramps-web.md).
- Large books remain slow and memory intensive. One synthetic N=1,000 build took 500.995 seconds across three passes and peaked at 1,104,003,072 bytes RSS; both exceed current targets. Extended compilation avoids some timeouts but does not guarantee completion. See [performance measurements](validation-performance.md).
- PDFs are tagged, but PDF/UA conformance and screen-reader announcements have not been validated. HTML screen-reader use and realistic photographic media also need review.
- The 27 acceptance scenarios AC-01 through AC-27 are not all complete; several edits and exports through the GUI remain to be checked. See the [requirements matrix](requirements.fr.md) for each scenario’s status.
- Readable private data and information about living people may appear in the book. The report’s acknowledgement does not anonymize data; verify content and sharing rights before distribution.
- Upgrade from a previously distributed version has not been qualified. The archive is generated locally, ignored by Git, and unpublished.

## Gates before a stable version

Complete the required functional recipes or obtain explicit approval for scope changes, qualify graphical installation and exports from the current package, decide the performance targets, finish accessibility reviews, and resolve the Gramps Web blocker or obtain explicit approval for a scope change. Then review these notes and build the release artifact before publication.
