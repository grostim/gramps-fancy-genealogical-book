# Synthetic PDF preview review

## Single-item profile sections — 1 October 2026

- Local preview: `output/pdf/gramps-fancy-book-single-event-profile-preview-20261001.pdf`; SHA-256 `6ae26746fcc1588982c7be0786226f6ad8de146636280bc5e9846cafc698c3ac`.
- The synthetic branching fixture contains 202 people, 101 families, 303 events, 20 portraits and 303 citations. LuaHBTeX 1.24.0 produced a tagged 177-page A4 PDF of 1,470,734 bytes. Records and portraits are fictional.
- Physical pages 57–58 were rendered at 130 dpi and reviewed. Single events and source references appear as compact rows beneath their headings. The portrait and its caption remain centered; no clipping or overlap was visible on these pages.
- The candidate retains the exact 1,805 named book destinations, 3,073 link annotations and 2,669 `Link` structure elements from the previous preview. It has 292 `L` and 1,174 `LI` elements, down by 404 each.
- The review is targeted and does not cover every page at high resolution, real Gramps data, a screen reader, Desktop export, or PDF/UA conformance. No PDF/UA conformance is claimed.

## Single-call citation reference — 1 October 2026

- Local preview: `output/pdf/gramps-fancy-book-single-call-citation-preview-20261001.pdf`; SHA-256 `3cf5f9b8025258db353f71d2292875c5bc0e5d244d5bbbda47f9cd143dfc2578`.
- The synthetic branching fixture contains 202 people, 101 families, 303 events, 20 portraits, and 303 citations. LuaHBTeX 1.24.0 produced a tagged, 193-page A4 PDF of 1,583,991 bytes. Records and portraits are fictional.
- Physical page 123 was rendered at 130 dpi and reviewed. Citations used once show a localized “See” reference linked to the associated profile or family notice; citations with multiple calls retain a bulleted list. No overlap or clipped text was visible on the inspected page.
- All 1,805 named book destinations remain. The structure contains 696 `L`, 1,578 `LI`, and 2,669 `Link` elements, compared with 972, 1,854, and 2,669 in the immediately preceding preview.
- This targeted inspection does not cover all pages at high resolution, real Gramps data, a screen reader, Desktop export, or PDF/UA conformance. No PDF/UA conformance is claimed.

## Current preview — 1 October 2026

- Local, untracked file: `output/pdf/gramps-fancy-book-preview.pdf`; SHA-256 `1196e8e97c80033c20a97ae34ef36a515b2f244d5fc8a1331a723c93f27bc2c2`.
- The PDF is 647,443 bytes and 55 A4 pages. LuaHBTeX 1.24.0 compiled it; `pdfinfo` reports a tagged PDF 2.0 (`Tagged: yes`). The synthetic dataset contains 202 people and 101 families.
- All 55 pages were rendered at 100 dpi and reviewed on three contact sheets. Physical pages 11, 12, 18, 25, 33, and 49 were also inspected at that resolution. No overlap, clipped text, or missing page number was visible, including in the family connections and person index.
- To support this volume of nested family links, the renderer closes and reopens the nested list every 20 parent-child links. This avoids the unbalanced `tagpdf` hook error encountered during compilation while preserving list structure. The final compilation completed without layout warnings.
- Records and visuals are synthetic. The tagged PDF has not been qualified with a screen reader, and no PDF/UA claim is made. Comparison with the private mockups and review with representative photographs remain open.

## Earlier 193-page preview — historical record

- Earlier local artifact, since replaced at the same path by the current preview above; its previous SHA-256 was `a06793d3e69460380cd8304c5b586bc4c132f4def5b351ed0bbcbcf5efdc4d72`.
- Size: 739,729 bytes; 193 A4 pages; LuaTeX 1.24.0
- Synthetic dataset: 202 people and 101 families
- PDF outlines: seven sections — ancestry, descent, family connections, family notices, person profiles, documentary appendix, and person index

## Visual review

Rendered at 110 dpi and visually inspected PDF pages 1–4, 10, 27, 55, 100, 121, 130, 187, and 193. The sample covers the cover, contents, genealogy sections, family notices, profiles, a portrait, the appendix, and the person index.

No clipping, overlap, or missing page number was visible on the pages reviewed at the time. Section headings, contents entries, cross-reference text, source details, and the index fit within the page margins. Long URLs wrapped across lines and some breaks occurred inside a hostname. This earlier review did not establish that every page was free of layout defects; the file has since been replaced by the current preview.

## Limits and remaining work

- Portraits in this benchmark are seeded random pixels from `scripts/benchmark_book.py`, not representative photographs. The image page is useful only to exercise image placement and cropping.
- The cover and sparse genealogy pages reflect the synthetic dataset; they do not establish the final visual design.
- `pdfinfo` reported `Tagged: no` at the time; accessibility of this earlier PDF was not qualified.
- For this original sample, the inspected pages have not been compared with the private reference mockups, and long-link readability was not separately reviewed. The newer AC-20 preview below has a complete page-by-page visual pass and a targeted long-link review; screen-reader/accessibility checks and comparison against v1.1 design principles remain open.

## AC-20 preview — reviewed 29 September 2026

- Local, untracked file: `gramps-fancy-book-ac20-parity-preview.pdf` in the `l85-build-validation` validation worktree; SHA-256 `f0482918f12faaca707d9d421906e0f79c8e7405369a83859b322b66a76047c1`.
- Size: 470,833 bytes; 118 A4 pages; LuaTeX 1.24.0; 122-person synthetic dataset.
- PDF pages 1, 2, 4, 19, 40, 49, 75, 90, 115, and 118 were rendered at 110 dpi and reviewed. No overlap or clipped text was visible in this sample; the cover, contents, profiles, family notices, appendix, and index remain readable. Page 49 uses a synthetic portrait for layout only.
- This PDF predates the book-language parameter and therefore shows English headings. `pdfinfo` reports `Tagged: no`; full review, accessibility, and comparison with private mockups remain open.

## AC-20 PDF generation navigation preview — 30 September 2026

- Local, untracked files built from the generation-navigation change: output/pdf/gramps-fancy-book-ac20-generation-navigation-preview-20260930.pdf (SHA-256 acd9dc0d1d84c6026775fa38c861405d52befa94e5e9abbfb20992f8f1057ea2) and output/gramps-fancy-book-ac20-generation-navigation-preview-20260930.zip (SHA-256 3f474d1a067f169d819438e0fd5664cd62063514f0664a5b041fbaa21f974bf1). The ZIP is byte-identical to the earlier archive.
- The synthetic model has 122 people, 61 families, 183 events, 17 notes, 183 citations, and 12 derived media files. The PDF is 1,186,027 bytes and 118 A4 pages, compiled with LuaHBTeX 1.24.0. PDFinfo reports Tagged: yes.
- All 118 pages were reviewed on ten contact sheets at 60 dpi. Physical pages 3 and 4, which show ancestry and descent generation navigation, were rendered at 110 dpi; pages 75 (documentary appendix) and 118 (person index) were then inspected at 150 dpi. No overlap or clipped text was visible in these views. Some long URLs break inside a hostname; their readability and the section-anchor mapping were reviewed in the current preview documented below. All 2,421 internal PDF links resolve, and the seven generation targets match the HTML anchors.
- At the time of this earlier targeted review, comparison with the private mockups had not yet been done. The later six-page side-by-side comparison is documented below; a full high-resolution comparison remains open. This review also does not replace a Gramps UI export or PDF accessibility qualification. When this preview was generated, six top-level HTML fragments lacked matching stable PDF destinations. PR #147 aligned the five content-section anchors; `main-content` remains an HTML-only skip link. The current fragment check is documented below.

## Current AC-20 preview — shared HTML/PDF anchors and URL review — 30 September 2026

- Local, untracked file: [`output/pdf/gramps-fancy-book-ac20-shared-section-anchor-preview-20260930.pdf`](../output/pdf/gramps-fancy-book-ac20-shared-section-anchor-preview-20260930.pdf); SHA-256 `237b92ac2b10f6c99ba5d5cabd3b04068da343e0d9b96a0de1f97bcc542beda2`.
- The PDF is 1,187,795 bytes and 118 A4 pages, compiled with LuaHBTeX 1.24.0. `pdfinfo` reports a tagged PDF 2.0 with language `fr-FR`. The fictional branched dataset contains 122 people, 61 families, 183 events, 17 notes, 183 citations, and 12 derived media files.
- All 118 pages were reviewed on ten contact sheets at 50 dpi; physical pages 3, 4, 75, and 118 were inspected at 140 dpi. No overlap or clipped text was observed. On page 75, some archive URLs wrap after a period in the hostname; review at 140 dpi confirmed they remain readable. The PDF link annotation retains the complete URI, including `https://archives.example.test/item/3`; document inspection found 732 external URI links.
- The preview exposes 2,978 named PDF destinations. Of the 565 internal HTML fragments, all but `main-content` have a stable PDF destination; `main-content` is the HTML-only skip link. The five top-level content-section anchors now match between HTML and PDF, and all seven generation targets remain aligned.
- The HTML ZIP from the same preview was extracted and opened directly in Chrome with `file://`. The document renders, and all 12 PNG files are present in the extracted archive. The contents link to descent and a citation reference both open targets in `index.html`. This confirms offline opening and these links on macOS, but does not replace full-page review, a Gramps UI export, small-screen checks, or screen-reader testing.
- Portraits are synthetic pixels. The six-page side-by-side comparison is documented in the next section; it does not cover all 118 pages at high resolution. Screen-reader reading-order checks and PDF/UA qualification remain open.

## Targeted design review against v1.1 — 30 September 2026

- The tagged AC-20 preview above was compared with the visual rules in specification v1.1 (§ 6.3, 7.1, 8, 9.3–9.4) and the criteria recorded in the [mockup review](reference/mockup-review.md). Private reference files were not copied into the versioned repository or this fixture.
- On physical pages 1, 3, 4, 49, 75, and 118, A4 sizing and sans-serif text follow v1.1; `pdffonts` confirms Latin Modern Sans fonts. Running headers show the section and folio, with generation and branch added in genealogy sections. Page 4 places multiple generations together rather than forcing a page break for each. Physical pages 3, 4, 49, 75, and 118 remain readable when rendered in grayscale.
- The side-by-side comparison covered all 22 pages of the two reference PDFs and the six AC-20 pages above. The mockups use a gray “Where am I?” strip, outlined parent panels, sibling links, and footer links. The current preview instead uses running section, generation, and branch headers with folios; it keeps multiple generations on a page and follows v1.1’s compact composition. It does not reproduce the strip and footer links exactly, so that visual difference remains to be reconsidered before claiming final design fidelity.
- The random-pixel `BOOK_FEATURED` image has a dedicated page (physical page 49), with its running header, folio, and caption; its landscape placement preserves the aspect ratio and leaves a large white area below. Its busy multicolored pattern cannot establish the visual balance of real photographs: it tests placement, cropping, captioning, and reserved space only. Repeat this check with representative portrait and landscape images. This fixture's cover is text-only because the couple has no portraits.
- Physical page 75 groups several numbered documentary entries and their links; page 118 contains the person index and page references. No overlap or clipped text was visible in these views. The mockups' serif headings differ from this PDF, as expected because v1.1 requires sans-serif typography.
- Direct comparison is limited to these six representative AC-20 pages; all 118 pages were not compared with the mockups at high resolution. Screen-reader checks, PDF accessibility, and representative photographs remain to be qualified; no PDF/UA claim is made.

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
- The rich English fixture was also compiled locally: 18 A4 pages, language `en-US`, title “Family history,” eight H1, four H2, four H3, nine lists, 90 items, and four figures with alternative text. CI now applies the same structure checks to the English and French outputs. The English preamble uses Babel’s `american` option to match its `en-US` metadata and avoid Babel’s warning for generic `english`; this localizes the option but does not qualify general Babel compatibility. The names, events, and descriptions remain fictional, and several sample descriptions are in French.
- These static checks do not establish actual narration or complete on-screen reading order.
- A screen-reader test remains necessary, as does general `babel` and `ulem` compatibility. veraPDF documents the profiles and the `-f ua2` option in its [CLI validation guide](https://docs.verapdf.org/cli/validation/); installation and signature verification are in the [official installation guide](https://docs.verapdf.org/install/). LaTeX documents role remapping with [`role/new-tag`](https://latex3.github.io/tagging-project/documentation/usage-instructions).

## N=100 preview after compacting family notices — 1 October 2026

- Local preview: [`output/pdf/gramps-fancy-book-single-event-notice-preview-20261001.pdf`](../output/pdf/gramps-fancy-book-single-event-notice-preview-20261001.pdf), SHA-256 `0b3b395928504f2ad8a1b6412d878443a64200be5fe533892f080a2804db00b0`.
- The tagged PDF has 169 A4 pages and is 1,409,982 bytes. It uses a fictional branching fixture with 202 people, 101 families, 303 events/citations, 101 notices, 202 profiles, and 20 portraits at 96 × 72 pixels.
- Physical pages 29 and 31 were rendered at 130 dpi and reviewed. They include a family notice; no clipping or visible overlap was found. All 1,805 named destinations and 3,073 PDF annotations are retained from the preceding preview.
- This preview supports a visual comparison of single-item family notices with list-based notices. Genealogical records and portraits are fictional; this is not a full page-by-page review or PDF/UA qualification.

## AC-15 export through Gramps CLI with 15 mm margins — 5 October 2026

- Local, untracked PDF: [`output/pdf/gramps-fancy-book-ac15-shared-media-15mm-20261005.pdf`](../output/pdf/gramps-fancy-book-ac15-shared-media-15mm-20261005.pdf), SHA-256 `20931cecc9fa69c90f619b3e94037c84920d026bcc07ea798607d9420900b600`.
- The current add-on archive was installed in a temporary isolated Gramps profile. Gramps 6.0.8 imported the fictional AC-15 fixture and produced a French PDF with LuaHBTeX 1.24.0 / TeX Live 2026. This used the Gramps CLI report action, not the Desktop dialog.
- The PDF has nine A4 pages (66,423 bytes), PDF 2.0 tagging, and `fr-FR` language metadata. All 81 named destinations are present; all 32 internal links resolve. The three figures have non-empty alternative text.
- The appendix on physical page 8 (printed folio 7) displays one shared reproduction, with citation entries [2] and [3] pointing to it. Physical pages 7 and 8 were rendered at 120 dpi and reviewed; no visible overlap or clipped text was found.
- This recipe confirms the current 15 mm margin and the Gramps report’s PDF path on the AC-15 fixture. The Desktop dialog export and review of all nine pages are recorded below. Real media and screen-reader behavior remain open. No PDF/UA conformance is claimed. CLI measurements are in the [raw JSON record](validation-gramps-ac15-margins15-20261005.json).

## AC-15 export through Gramps Desktop with 15 mm margins — 5 October 2026

- Local, untracked PDF: [`output/pdf/gramps-fancy-book-ac15-shared-media-gui-15mm-20261005.pdf`](../output/pdf/gramps-fancy-book-ac15-shared-media-gui-15mm-20261005.pdf); SHA-256 `c0febd6aacece5a4a2e85320976a64d131ae74a3f88a316c732d59080abd7d8e`.
- The add-on archive rebuilt from commit `7c8edfbde7f8cdf98e5c5d154cea2b12dda9b10d` was installed in a temporary isolated Gramps profile. Gramps Desktop 6.0.8 exported family F0001 in French through the report dialog; the configured page margin is 15 mm. The AC-15 profile did not use the personal family tree.
- The PDF has nine A4 pages (66,423 bytes), PDF 2.0 tagging, and `fr-FR` language metadata. All 81 named destinations are present; all 32 internal links resolve. The three figures have non-empty alternative text.
- The appendix is on physical page 8 (printed folio 7). It contains one shared 120 × 80 pixel reproduction, referenced by citations [2] and [3]. All nine pages were rendered at 110 dpi and reviewed on a contact sheet; pages 7 and 8 were also inspected separately. No visible overlap or clipped text was found.
- This synthetic fixture combines AC-15 shared media with AC-23 security strings; the pseudo-tags appear as plain text. Its images are flat color and do not qualify realistic photographs. Screen-reader behavior and PDF/UA conformance remain unverified. Measurements are in the [raw record](validation-gramps-ac15-gui-20261005.json).
