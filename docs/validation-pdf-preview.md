# Synthetic PDF preview review

## Artifact

- File: `output/pdf/gramps-fancy-book-preview.pdf` (local, generated artifact; not tracked in Git)
- SHA-256: `a06793d3e69460380cd8304c5b586bc4c132f4def5b351ed0bbcbcf5efdc4d72`
- Size: 739,729 bytes; 193 A4 pages; LuaTeX 1.24.0
- Synthetic dataset: 202 people and 101 families
- PDF outlines: seven sections — ancestry, descent, family connections, family notices, person profiles, documentary appendix, and person index

## Visual review

Rendered at 110 dpi and visually inspected PDF pages 1–4, 10, 27, 55, 100, 121, 130, 187, and 193. The sample covers the cover, contents, genealogy sections, family notices, profiles, a portrait, the appendix, and the person index.

No clipping, overlap, or missing page number was visible in the inspected pages. Section headings, contents entries, cross-reference text, source details, and the index fit within the page margins. Long URLs wrap across lines; some breaks occur inside a hostname, so their readability still needs review. The sample inspection does not establish that every page is free of layout defects.

## Limits and remaining work

- Portraits in this benchmark are seeded random pixels from `scripts/benchmark_book.py`, not representative photographs. The image page is useful only to exercise image placement and cropping.
- The cover and sparse genealogy pages reflect the synthetic dataset; they do not establish the final visual design.
- `pdfinfo` reports `Tagged: no`; PDF accessibility has not been qualified.
- The inspected pages have not been compared with the private reference mockups. Full-document review, long-link readability, screen-reader/accessibility checks, and comparison against v1.1 design principles remain open.

## AC-20 preview — reviewed 29 September 2026

- Local, untracked file: `gramps-fancy-book-ac20-parity-preview.pdf` in the `l85-build-validation` validation worktree; SHA-256 `f0482918f12faaca707d9d421906e0f79c8e7405369a83859b322b66a76047c1`.
- Size: 470,833 bytes; 118 A4 pages; LuaTeX 1.24.0; 122-person synthetic dataset.
- PDF pages 1, 2, 4, 19, 40, 49, 75, 90, 115, and 118 were rendered at 110 dpi and reviewed. No overlap or clipped text was visible in this sample; the cover, contents, profiles, family notices, appendix, and index remain readable. Page 49 uses a synthetic portrait for layout only.
- This PDF predates the book-language parameter and therefore shows English headings. `pdfinfo` reports `Tagged: no`; full review, accessibility, and comparison with private mockups remain open.

## French book-language preview — 29 September 2026

- Local, untracked file: `output/pdf/gramps-fancy-book-language-preview-fr.pdf`; SHA-256 `cdcaafe8c417a06e989fa264e4dc14342fbaa38d135cd462b5e43f26cb70756d`.
- 18 physical A4 pages, 56,659 bytes; LuaTeX 1.24.0. The compact synthetic model covers the cover, contents, ancestry, descent, family connections and notices, person profiles, documentary appendix, and person index.
- The 18-page version was compiled with `fr` selected. Physical pages 2, 9, 10, and 18 were rechecked after the final compile: the contents and index are readable, and a long profile continues onto the next page without visible overlap. The other sections were reviewed on the same prototype in the previous inspection.
- Names, dates, descriptions, and records are fictional. This output confirms French generated labels in a prototype, not yet full integration through the Gramps UI with a real genealogy database. `pdfinfo` reports `Tagged: no`; accessibility and comparison with private mockups remain open.

## Shared preview after PR #106 — 29 September 2026

- Local, untracked file: `output/pdf/gramps-fancy-book-step-preview-fr.pdf`, generated from `main` commit `5fb7bc7` with the repository renderers. SHA-256: `b3d16126c94ebba0c4dcd0c7424017a15153c976241ff430f2588e90880e6b66`.
- The fictional model has 22 people, 11 families, 33 events, 3 notes, 33 citations, and two cropped PNG derivatives; the associated HTML ZIP was generated from this same model. The PDF has 22 A4 pages (109,106 bytes), compiled by LuaHBTeX 1.24.0.
- All 22 pages were rendered at 90 dpi. A contact sheet and physical pages 7, 16, 19, and 22 were inspected separately; no overlap or clipped text was visible in those views. The appendix contains long URLs, and the portraits are synthetic pixels.
- `pdfinfo` reports `Tagged: no`. Accessibility, comparison with the private mockups, and a full high-resolution review remain open.

A high-resolution reinspection on 30 September confirms this historical file no longer represents the current header: on physical pages 16 and 17, the folio visually touches the section label. The file was generated from commit `5fb7bc7`, before the header correction in PR #114. The current AC-15 PDF below provides evidence for the corrected header.

## Native AC-15 PDF — full review on 30 September 2026

- Local, untracked file: `output/pdf/gramps-fancy-book-ac15-shared-media-review.pdf`; SHA-256 `f1ac11b304668363c92bcd31415b663ddd39c4ca16b56eea502f78ea5e2fe0df`.
- Nine A4 pages, 45,802 bytes, LuaTeX 1.24.0. Synthetic Gramps AC-15/AC-23 fixture with a reproduction cited twice and injection strings used only for the security check.
- All nine pages were rendered at 160 dpi and inspected: cover, contents, ancestry, descent, family links, family notice, profile, source appendix, and index. Header labels and folios are separated; no overlap or clipped text was observed.
- The `<img ... onerror=...>` and `<script>...</script>` strings appear as text in the profile and family notice. The appendix shows one shared reproduction, and the other citation points to it. The fixture’s URLs remain legible within the page width.
- `pdfinfo` reports `Tagged: no`. This security fixture contains fictional data and does not qualify final design, accessibility, or comparison with the private mockups.

## Tagged PDF feasibility prototype — 30 September 2026

- The earlier 97-page French AC-20 preview, generated before tagging was enabled, remains untagged (`pdfinfo`: `Tagged: no`). TeX Live 2026 Basic on the Mac includes `tagpdf` 0.99y (2026-01-29); CTAN published 1.0g (2026-09-23), see [TagPDF on CTAN](https://ctan.org/pkg/tagpdf?lang=en).
- A temporary one-page document compiled with LuaHBTeX 1.24.0, `\DocumentMetadata{lang=en,pdfstandard=ua-2,tagging=on}`, and the renderer’s existing packages. `pdfinfo` recognized PDF 2.0 as tagged. Inspection of `/StructTreeRoot` with `pypdf` found two `/Figure` elements with `/Alt` values for `\includegraphics` and `tikzpicture`; strikethrough text and the link remained visible in text extraction. The rendered page was inspected visually.
- This prototype confirms compilation with the local version; it does not establish PDF/UA-2 conformance for the book. The official [LaTeX tagging status](https://latex3.github.io/tagging-project/tagging-status/) lists `article`, `fancyhdr`, `graphicx`, and `xurl` as compatible; graphics need alternative text, TikZ needs a description, `ulem` is currently incompatible because `TextDecoration` attributes are missing, and `babel` remains unchecked for languages. The renderer now supplies `TextDecorationType=LineThrough` for its `\sout` use without changing the visual strike. The [usage instructions](https://latex3.github.io/tagging-project/documentation/usage-instructions) require each graphic to have alternative text or be marked decorative. At this stage veraPDF had not yet been installed, so no full conformance validation had been performed.

## First tagged production-renderer preview — 30 September 2026

- Local, untracked file: `output/pdf/gramps-fancy-book-tagged-preview-fr-20260930.pdf`; SHA-256 `54f934e96dd990b4fc83805fe3745d13a177eaee50221fd0d137e19d38e231c9`.
- The five-page A4 PDF compiled with LuaHBTeX 1.24.0 and TeX Live 2026. `pdfinfo` reports `Tagged: yes`, PDF 2.0, and language `fr-FR`. Inspection of `/StructTreeRoot` with `pypdf` found three `/Figure` elements with alternative text: “Portrait de Jeanne Exemple”, “Acte de naissance de Jeanne Exemple, extrait de recette fictive.”, and “Portrait de Jeanne Exemple”. The circular cover portrait appears as a single figure.
- All five pages were rendered at 90 dpi and visually inspected; the full-page reproduction caption now sits below the image. Names, document text, and images are fictional; the images are synthetic gradients. This confirms compilation, PDF language metadata, several image alternatives, and layout for this fixture. It does not qualify real Gramps data, the full reading order, or PDF/UA conformance.
- `ulem` remains in use for struck-through notes; the renderer now attaches the missing `TextDecorationType=LineThrough` layout attribute to a tagged `Span`. Compatibility of `babel` in French and English, actual reading order, and a screen-reader review remain open. At this stage veraPDF had not yet been installed. Do not describe this output as PDF/UA compliant.

## Semantic tagging for struck-through notes — 30 September 2026

- The renderer declares the PDF layout attribute `/O /Layout /TextDecorationType /LineThrough` and attaches it to a `/Span` around each `\sout`. The text remains one extractable sequence, and `ulem` still draws the line.
- The renderer produced a [local three-page preview](../output/pdf/gramps-fancy-book-strikethrough-preview-fr-20260930.pdf), SHA-256 `b5e308af5ff81278af5aa8ce9d9adc6a6edf03c81f3f86ac66b9e46584bae208`. `pdfinfo` reports a tagged PDF 2.0 document in `fr-FR`. `pdfinfo -struct` shows the `Span` and its `TextDecorationType /LineThrough` attribute; `pdftotext` preserves the text; and the introduction page still shows the strike line.
- This French compilation also exposed a Babel warning: when tagging is enabled, Babel-French disables its list customizations because they are incompatible with the new tagged-list implementation. The first preview contained no list to inspect. A focused check is documented below; the official [LaTeX compatibility registry](https://latex3.github.io/tagging-project/tagging-status/) still lists `french` as unchecked, and the CTAN page for [Babel-French](https://ctan.org/pkg/babel-french?lang=en) marks it incompatible with tagged PDF.
- LaTeX still lists the `ulem` package as currently incompatible because this attribute is missing; this project wrapper supplies it for the `\sout` command used here, but does not qualify every `ulem` command. The full tree, `babel` languages, `veraPDF`, and screen-reader checks remain open; no PDF/UA claim is made.

## French labels in tagged lists — 30 September 2026

- Local, untracked file: `output/pdf/gramps-fancy-book-french-list-preview-fr-20260930.pdf`; SHA-256 `a290a17e620e5a55d3f7d3deb960611373c87aaf799cbdfc01498e72f58fabd5`.
- The four-page synthetic fixture compiled with LuaHBTeX 1.24.0 and TeX Live 2026. `pdfinfo` reports tagged PDF 2.0 in `fr-FR`. `pdfinfo -struct` shows `L` and `LI` elements; `pdftotext -layout` preserves em dash markers before both index names. All four pages were rendered and inspected; the cover, struck-through text, contents, and index are legible.
- For generated French lists, the renderer redefines the standard `\labelitemi` through `\labelitemiv` commands to `\textemdash` because Babel-French disables its list customizations when tagging is active. These kernel commands retain the em dash in tagged list items; PR #136 CI confirmed compatibility with its pinned TeX Live image. Poppler 24.04.0 emits `Syntax Warning: Attribute ListNumbering value is of wrong type (name)` when inspecting the tree, while the PDF ClassMap contains `/ListNumbering /Unordered`. The PDF 2.0 reference from the [PDF Association](https://pdfa.org/download-area/cheat-sheets/StructureAttributes.pdf) lists `Unordered` as a valid value, so this warning alone does not show that the file is malformed. This fixture does not establish PDF/UA conformance.

## Full French preview with tagged lists — 30 September 2026

- Local, untracked file: [`output/pdf/gramps-fancy-book-french-tagged-renderer-preview-20260930.pdf`](../output/pdf/gramps-fancy-book-french-tagged-renderer-preview-20260930.pdf); SHA-256 `4f7f306a48acb5f45561f667d887638814b37932b11f83a225c43280c4963de7`.
- The synthetic PDF has 19 A4 pages and was compiled with LuaHBTeX 1.24.0 / TeX Live 2026. It includes the cover, contents, genealogy sections, a synthetic image, a long profile and notes, the documentary appendix, and the person index. `pdfinfo` confirms tagged PDF 2.0 and language `fr-FR`.
- The local structure check finds nine `L` lists and 90 `LI` items, with `ListNumbering /Unordered`; text extraction retains the em dashes before index names. All 19 pages were rendered to a contact sheet, and physical pages 1, 2, 8, 17, 18, and 19 were also inspected in detail. No visual defects were found.
- Data and visuals are fictional. This review and the CI check verify this fixture, not full Babel compatibility or PDF/UA conformance; no PDF/UA profile is claimed.

## veraPDF check and document-title metadata — 30 September 2026

- The official veraPDF 1.30.2 CLI was downloaded from the project site, verified against the GPG signature and fingerprint published by veraPDF, then installed temporarily under `/tmp` with the CLI component only. It was not added to the repository or installed globally.
- On the original 19-page French tagged preview above, the PDF/UA-2 profile reported three rules: missing PDF/UA identification in XMP, missing `/ViewerPreferences /DisplayDocTitle true`, and missing `dc:title`. The formal identification remains intentionally absent: the project does not claim PDF/UA before reading order, packages, and screen-reader behavior are qualified.
- The renderer writes `dc:title` from the editorial `BOOK_TITLE` note (or the localized cover-title fallback) and asks PDF viewers to display that title. The structural verifier confirms this metadata, nine `L` lists, 90 `LI` items, the index em dash markers, four `H3` headings, and no `H4` headings.
- A static structure-tree audit found that `\paragraph` subheadings were tagged as `H4` even though the document had no `H3` elements. The current change maps that role to `H3` with `role/new-tag`, preserving the visual style. The updated preview, [`output/pdf/gramps-fancy-book-french-tagged-renderer-reading-order-preview-20260930.pdf`](../output/pdf/gramps-fancy-book-french-tagged-renderer-reading-order-preview-20260930.pdf), is a 19-page A4 PDF (SHA-256 `e90d35095f48af1fe16e1a5ad2a6ad7469f15c27966e36cb8709384013fde6ef`). All 19 pages were rendered to a contact sheet and inspected; no visible defects were found.
- On the updated preview, veraPDF 1.30.2 passes 1,726 rules and fails one: missing PDF/UA identification (rule 5-1). This machine check does not certify PDF/UA conformance, which the project does not claim.
- A separate two-page French PDF, [`output/pdf/gramps-fancy-book-title-metadata-preview-fr-20260930.pdf`](../output/pdf/gramps-fancy-book-title-metadata-preview-fr-20260930.pdf), also checks a title note with accents, an ampersand, a hash sign, and bold formatting. Its XMP title is “Histoire d’Élise & Louis #2”; SHA-256 `7486adba99d7190374d63ef5f92154c0d3d9df18a5018ace91440dcb31e399a1`. Both pages were visually inspected.
- Static traversal of the tagged tree follows the broad publication order: cover, contents, genealogy and family sections, individual profiles, appendix, and index. It finds eight H1, four H2, four H3, nine lists, and 90 list items. All four `/Figure` elements have non-empty `/Alt` text; the CI verifier now enforces this rule.
- The rich English fixture was also compiled locally: 18 A4 pages, language `en-US`, title “Family history,” eight H1, four H2, four H3, nine lists, 90 items, and four figures with alternative text. CI now applies the same structure checks to the English and French outputs. The names, events, and descriptions remain fictional, and several sample descriptions are in French; this check does not qualify full translation or general Babel compatibility.
- These static checks do not establish actual narration or complete on-screen reading order.
- A screen-reader test remains necessary, as does general `babel` and `ulem` compatibility. veraPDF documents the profiles and the `-f ua2` option in its [CLI validation guide](https://docs.verapdf.org/cli/validation/); installation and signature verification are in the [official installation guide](https://docs.verapdf.org/install/). LaTeX documents role remapping with [`role/new-tag`](https://latex3.github.io/tagging-project/documentation/usage-instructions).
