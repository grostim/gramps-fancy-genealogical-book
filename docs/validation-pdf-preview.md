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
