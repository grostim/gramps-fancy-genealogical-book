# Add-on package lifecycle validation — September 29, 2026

## Environment and method

- Gramps Desktop 6.0.8 on macOS 27.0 arm64, using its embedded Python 3.13.2.
- Source `main` at commit `106eae276871238b0dd2c373cae5879e7f600119`; add-on registration version `0.9.0`.
- Archive rebuilt with `build_addon.py`: SHA-256 `e99fbe4c9c19c5817c95c97f7ada6020c2a66473445095815dc6e186a63de366`.
- A temporary `GRAMPSHOME` profile was used without opening a personal family tree. Mistune 3.3.4 was installed only into that profile’s library directory. The synthetic GEDCOM and its one-pixel portrait were copied into the temporary directory; Gramps reported `No errors detected` on import.

## Results

| Step | Check | Result |
| --- | --- | --- |
| Install | Extract the archive into the profile, then export an HTML ZIP from the CLI | Gramps discovers the report; the ZIP passes integrity validation and contains `index.html` (2,450 bytes). |
| Reinstall | Replace the complete `GrampsFancyBook/` directory with the same archive built at version `0.9.0`, then export PDF | A new Gramps process discovers the report; the output begins with the `%PDF-` signature (27,971 bytes). |
| Remove | Delete only the installed add-on directory and invoke the report again | Gramps returns `Unknown report name` and creates no output file. |

The temporary profile, dependency, ZIP, and PDF were removed when the check ended. The built archives and output artifacts contain no real family data.

## Scope and limitations

The replacement exercised here reinstalls the same `0.9.0` version; it does not prove an upgrade between two versions. The historical `0.8.0` source at commit `a8c3797`, rebuilt for this check, fails to load under Gramps 6.0.8: its `.gpr.py` calls `get_addon_translator(__file__)`, but Gramps does not inject `__file__` into this registration context. It is therefore not a valid upgrade baseline for this matrix. There is currently no version published in GitHub Releases.

This check used the CLI binary in the Desktop application bundle. It does not qualify the graphical add-on manager, an upgrade between versions, or Gramps Web. Manual steps are in [Build and install](../README.md#build-and-install).

## Requalification of the current archive — October 6, 2026

Two builds with `build_addon.py` produce the same `0.9.0` archive: SHA-256 `357ce674720f914a4788d99956680b42df5bc84991cee6b7589b85a8a362852c`, 88,346 bytes, and 29 members. It contains the PDF renderer and compiled `locale/fr/LC_MESSAGES/addon.mo`, with no Python cache files.

The local archive `gramps60/download/GrampsFancyBook.addon.tgz`, ignored by Git and dated October 5 before this rebuild, is regenerated with these bytes. Two fresh local builds produce identical bytes and SHA-256. The builder now rejects version mismatches between `pyproject.toml`, the Gramps registration, and the PO/POT `Project-Id-Version` headers. The French and English README explain how to build the archive; no GitHub Release has been published.

The archive was extracted into a new temporary `GRAMPSHOME` profile and used with Gramps Desktop 6.0.8 (embedded Python 3.13.2); the integration runner uses CPython 3.13.7. The checkout `PYTHONPATH` is removed. Native verification passes for the model, HTML ZIP and JSON exports, error paths, and PDF generation from the installed archive. The tagged French PDF has 18 A4 pages (159,047 bytes). One interior page was reviewed at 100 dpi; no clipping was visible, and its margins look consistent with the configured 15 mm. The [raw record](validation-gramps-clean-install-20261006.json) contains environment details and scope limits.

The local run above uses the CLI in a clean profile, not an install through the graphical add-on manager. French was selected for the book renderer; this invocation does not exercise the translated report UI or provide a full visual review. The separate GUI qualification below covers one reference export. Screen-reader review, other Desktop versions, and Gramps Web remain unqualified.

The first hosted CI run associated with [PR #294](https://github.com/grostim/gramps-fancy-genealogical-book/pull/294) passed on Gramps 6.0.7 and 6.0.8 using the pinned LuaLaTeX image. Both jobs installed the archive in a temporary environment, ran native checks, and produced a tagged A4 PDF with 16 pages: 151,136 bytes on 6.0.7 and 151,180 bytes on 6.0.8. The `GrampsFancyBook-PDF-Gramps-6.0.7` and `GrampsFancyBook-PDF-Gramps-6.0.8` artifacts are retained for 14 days in the [CI run](https://github.com/grostim/gramps-fancy-genealogical-book/actions/runs/37515424979). The Python 3.10–3.13, Windows 3.10–3.13, macOS, Gramps 6.1 canary, and LaTeX prototype jobs also passed. This qualifies CLI export from the archive on those versions; it does not replace the graphical-install check or a full visual review.

## Native Plugin Manager installer — October 9, 2026

`scripts/verify_addon_installer.py` calls `gramps.gen.plug.utils.load_addon_file`, the backend used by Plugin Manager, in a fresh disposable profile. The local check used embedded Python 3.13.2 from Gramps Desktop 6.0.8-1. Two builds of commit `a5448614948a6c796dfa9fe82721de62f80a3392` produce identical bytes: SHA-256 `f11cca39c47bd6beed9f189feefec4a268b0ee0bf722c791a3e0010038e596d5`, 29 files.

The installer accepts the archive and all 29 installed files match their archived bytes. Reinstallation restores a `MANIFEST` file deliberately altered in this disposable profile. A diagnostic archive targeting Gramps `99.0` is rejected without changing installed files. The [raw record](validation-native-addon-installer-20261009.json) preserves the results. The Gramps 6.0.7 and 6.0.8 CI jobs now run this check before exports and preserve its JSON with their archive; their results remain to be checked on the corresponding PR.

This qualifies the installation backend, not GUI interaction, upgrades between versions or obsolete-file cleanup by the manager. The GUI recipe remains outstanding; the Mac was locked during this check.

## GUI qualification of the archive renderer baseline — October 6, 2026

The test used Gramps Desktop 6.0.8-1 on macOS in the temporary profile `tmp/l8-4-gui-example-20261006/profile`, launched with an explicit `GRAMPSHOME`. The profile initially contained no tree. The `L8_4 GUI reference family 20261006` tree was created there and populated from the fictional `reference-family.gramps` fixture. Gramps recognized four people, two families, one source, three events, three citations, two places, and one repository. No personal tree was opened.

The report appears under **Rapports → Pages web → Livre généalogique illustré pour Gramps**. The interface was in French; the options explicitly selected **Français** and **Livre PDF (LuaLaTeX)**, and the privacy acknowledgement was checked. The output directory was `output/pdf/`. The add-on installed in this profile came from archive `0.9.0`; the SHA-256 hashes of `GrampsFancyBook.py`, `gramps_fancy_book/report.py`, and `gramps_fancy_book/renderers/latex.py` match the sources at commit `b8141bc`.

The export produced the [reference GUI PDF](../output/pdf/gramps-fancy-book-reference-family-gui-20261006.pdf): nine A4 pages, PDF tagging enabled, 53,135 bytes, SHA-256 `79fa54bdd13df112c3e5b57688f64e9f330b2c07edb3f82f9fefabf1a9849fd6`. All nine pages were rendered at 110 dpi and reviewed. Interior pages retain margins of about 15 mm, with no clipping or overlap. The centered cover and short sections naturally leave more open space with this small fixture; the whitespace is not caused by expanded margins. This qualifies report loading and GUI PDF export on Gramps 6.0.8-1 with LuaHBTeX 1.24.0 (TeX Live 2026) for that source state. Four later commits modified the PDF renderer (`2a14b4f`, `7e02043`, `03bcda1`, `7598042`); this historical PDF does not qualify the current renderer. The current renderer has since been re-exported in the GUI with archival portraits; see the qualification below. Other Desktop versions, Gramps Web, screen readers, and PDF/UA remain unqualified.

## GUI requalification with archival portraits — October 9, 2026

The recipe used Gramps Desktop 6.0.8-1 on macOS 27.0 arm64, embedded Python 3.13.2, and LuaHBTeX 1.24.0 (TeX Live 2026). The application ran with a fresh temporary `GRAMPSHOME`; no personal tree was opened. Archive `0.9.0` was rebuilt from commit `35b57038889626a6d97af89a307fbd64374913a4` (SHA-256 `c1d4a107f15856a7b55bd10f4f9b5af63fc70bd1390407c5a601930840376df3`). The source hashes for `report.py` and the LaTeX renderer are `55ef2aa9501d3aed4df1282a10fecb01213b426de177c04af31a71e99084a8d6` and `2120b2a6030531251fe52f0df96017147c3e4f392cabfb8ba973a3cf5d41a16b`.

A generated synthetic GEDCOM imported without error. The Gramps tree contained 202 people, 101 fictional families, and twenty historical Wellcome Collection portraits under CC BY 4.0. Their JPEG sources total 13,741,822 bytes; provenance and license details are in [wellcome-open-portraits-cc-by.json](fixtures/wellcome-open-portraits-cc-by.json). The Gramps UI was in French and the privacy acknowledgement was confirmed for this fictional export.

The first GUI PDF contains 103 A4 pages, is 77,489,999 bytes, and reports `Tagged: yes` (PDF 2.0). SHA-256: `e8077819a51dff84387679db903716067f3cb18737ac489484d75ddabafb6e9c`. Export time was about 70.1 seconds. The twenty images retained in the PDF range from 1,600 × 1,540 to 1,601 × 2,700 pixels, at an effective 301–418 ppi. All 103 pages were rendered and reviewed page by page in nine contact sheets (12 pages per sheet except the last, which contains 7); physical pages 22, 35, 49, 70, 96, 98, and 103 were also inspected individually at 120 dpi. That first review found a real pagination defect: the final cross-reference line of citation [299] appeared by itself at the top of the next page.

The renderer now keeps media-free citation entries with at most three calls on one page. A fresh GUI export from the same fictional tree remains a tagged 103-page A4 PDF, 77,489,335 bytes; SHA-256: `c2778863a1237840d248a1a4d9cb9cc83e1b41a0a76b3c55b3bbe829c0b1d871`. The `latex.py` source used for this export has SHA-256 `5fa4616031656e10ef24154ef7893e04551c7fe53a25d9420277a992a6b07171`. Physical pages 96–103 of the new export were rendered at 120 dpi and re-reviewed. Citation [299] now appears in full on physical PDF page 97 (printed folio 96), with no orphan line or other visible layout issue on the reviewed pages. Pages outside the appendix are unaffected by this renderer change and remain covered by the original page-by-page review. The corrected PDF is at `/tmp/gfb-l84-gui-renderer-20261009-y59h24x5/wellcome-portraits-n100-gui-recheck.pdf`. This visual review is not a PDF/UA audit.

The HTML ZIP from the same tree contains `index.html` and twenty images (21 files total). It is 76,222,817 bytes; `unzip -t` passes. SHA-256: `4dabfba9430567e16e941da6ee77204ee3d02635537050a0692718a62f4e4d05`. The HTML index contains Wellcome Collection and CC BY 4.0 attributions. Both outputs are unversioned local artifacts kept under `/tmp/gfb-l84-gui-renderer-20261009-y59h24x5/`.

This requalifies current-renderer loading and PDF/HTML export through the Gramps GUI on one isolated macOS/Gramps configuration with public photographs. The initial exhaustive review found the citation pagination defect; after the renderer change, the affected appendix pages were re-reviewed with no visible layout defect. Installation through the graphical add-on manager, media imported from an existing user tree, other Desktop versions, Gramps Web, screen readers, and PDF/UA remain unqualified.
