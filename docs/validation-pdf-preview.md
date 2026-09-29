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
