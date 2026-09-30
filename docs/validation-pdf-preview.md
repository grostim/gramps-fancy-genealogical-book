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
- This prototype confirms compilation with the local version; it does not establish PDF/UA-2 conformance for the book. The official [LaTeX tagging status](https://latex3.github.io/tagging-project/tagging-status/) lists `article`, `fancyhdr`, `graphicx`, and `xurl` as compatible; graphics need alternative text, TikZ needs a description, `ulem` is currently incompatible because `TextDecoration` attributes are missing, and `babel` remains unchecked for languages. The renderer now supplies `TextDecorationType=LineThrough` for its `\sout` use without changing the visual strike. The [usage instructions](https://latex3.github.io/tagging-project/documentation/usage-instructions) require each graphic to have alternative text or be marked decorative. `veraPDF` is not installed on this Mac, and no full conformance validation has been performed.

## First tagged production-renderer preview — 30 September 2026

- Local, untracked file: `output/pdf/gramps-fancy-book-tagged-preview-fr-20260930.pdf`; SHA-256 `54f934e96dd990b4fc83805fe3745d13a177eaee50221fd0d137e19d38e231c9`.
- The five-page A4 PDF compiled with LuaHBTeX 1.24.0 and TeX Live 2026. `pdfinfo` reports `Tagged: yes`, PDF 2.0, and language `fr-FR`. Inspection of `/StructTreeRoot` with `pypdf` found three `/Figure` elements with alternative text: “Portrait de Jeanne Exemple”, “Acte de naissance de Jeanne Exemple, extrait de recette fictive.”, and “Portrait de Jeanne Exemple”. The circular cover portrait appears as a single figure.
- All five pages were rendered at 90 dpi and visually inspected; the full-page reproduction caption now sits below the image. Names, document text, and images are fictional; the images are synthetic gradients. This confirms compilation, PDF language metadata, several image alternatives, and layout for this fixture. It does not qualify real Gramps data, the full reading order, or PDF/UA conformance.
- `ulem` remains in use for struck-through notes; the renderer now attaches the missing `TextDecorationType=LineThrough` layout attribute to a tagged `Span`. Compatibility of `babel` in French and English, actual reading order, and a screen-reader review remain open. `veraPDF` is not installed. Do not describe this output as PDF/UA compliant.

## Semantic tagging for struck-through notes — 30 September 2026

- The renderer declares the PDF layout attribute `/O /Layout /TextDecorationType /LineThrough` and attaches it to a `/Span` around each `\sout`. The text remains one extractable sequence, and `ulem` still draws the line.
- The renderer produced a [local three-page preview](../output/pdf/gramps-fancy-book-strikethrough-preview-fr-20260930.pdf), SHA-256 `b5e308af5ff81278af5aa8ce9d9adc6a6edf03c81f3f86ac66b9e46584bae208`. `pdfinfo` reports a tagged PDF 2.0 document in `fr-FR`. `pdfinfo -struct` shows the `Span` and its `TextDecorationType /LineThrough` attribute; `pdftotext` preserves the text; and the introduction page still shows the strike line.
- This French compilation also exposed a Babel warning: when tagging is enabled, Babel-French disables its list customizations because they are incompatible with the new tagged-list implementation. Since the book uses lists, their French appearance and structure still need review. The official [LaTeX compatibility registry](https://latex3.github.io/tagging-project/tagging-status/) lists `french` as unchecked; the CTAN page for [Babel-French](https://ctan.org/pkg/babel-french?lang=en) marks it incompatible with tagged PDF.
- LaTeX still lists the `ulem` package as currently incompatible because this attribute is missing; this project wrapper supplies it for the `\sout` command used here, but does not qualify every `ulem` command. The full tree, `babel` languages, `veraPDF`, and screen-reader checks remain open; no PDF/UA claim is made.
