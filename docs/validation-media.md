# Media validation / Pillow and PDFium

Status as of 2026-09-30.

## Verified scope

CI installs the `media` extra across the Python 3.10–3.13 matrix and exercises conversions with synthetic images and single- and multipage PDFs. The Gramps integration matrix runs on Ubuntu 24.04 with Python 3.12 and Gramps 6.0.7 and 6.0.8. The local run of this recipe uses Gramps Desktop 6.0.8 on macOS with an isolated database.

The native Gramps CLI recipe covers AC-13: a fictional image present on disk carries both `BOOK_EXCLUDE` and `BOOK_FEATURED`, and its reference carries a dedicated citation used nowhere else. The model export confirms that the source object retains both tags but receives no placement, editorial reference or derivative; its exclusive citation is omitted from the appendix. The ZIP includes only the two expected images for other media, with no AC-13 description or citation detail. This qualifies native XML import and CLI export; see the Desktop recipe below. Entering the tags through the GUI remains unverified.

### AC-13 — Gramps Desktop export — 2026-09-30

- The current add-on archive (SHA-256 `8227d8b223cecf3e9fb5841f11ac066051dc6fcc4db8492ebe9d4ac19d975965`) ran in Gramps Desktop `6.0.8-1` on macOS 27.0 arm64. A fresh temporary profile contains only the fictional `FancyBook GUI AC13` tree.
- After import, a native Gramps export confirms media object M0006 exists on disk, carries both `BOOK_EXCLUDE` and `BOOK_FEATURED`, and retains the description `AC13_EXCLUDED_FEATURED_MARKER`. Citation C0003 carries `AC13_EXCLUDED_CITATION_MARKER`; its only reference comes from media M0006.
- The GUI `.zip` export is `tmp/gramps-gui-ac13-run-20260930/approved-ac13.zip` (SHA-256 `9b1f8431c8c2285c2a9a1f0cf931257cb66dba2b56455ba7bfc23978749da470`). `unzip -t` passes. The archive contains `index.html` and two expected PNGs. All 32 IDs are unique, all 33 links resolve, both images have local files and alt text, and neither the excluded media name nor its markers appear in the HTML.
- The GUI `.pdf` export is `output/pdf/gramps-fancy-book-ac13-gui-20260930.pdf` (SHA-256 `aba8e44e2a97b863588d4b3f73a78ecc2ee3177be2e16e892026fe10c9ec21f8`), nine A4 pages and 80,742 bytes; `pdfinfo` reports `Tagged: yes`. The markers are absent from extracted text and the image inventory excludes the AC-13 PNG. All nine pages were rendered at 100 DPI and reviewed, with no visible clipping or overlap. This does not establish PDF/UA conformance.
- The privacy acknowledgement was unchecked by default and was confirmed for both fictional-data exports. This qualifies GUI export from a native Gramps database prepared with the tags; it does not yet verify entering those tags in the GUI editors.

The Gramps CLI recipe creates four fictional PDF documents, attaches them to native citations, then generates an HTML ZIP. It confirms all four AC-16 rules: an unlinked single-page PDF produces a 300-DPI PNG; an unlinked multipage PDF remains a reference; both PDFs with a URL remain links, regardless of page count. The ZIP contains the first document's derivative, all four references and the repository URL associated with the two linked citations. ZIP integrity is checked. The cropped synthetic portrait and coordinated replacement of the JSON file and media directory are also covered.

The same scenario can also produce a PDF book with `scripts/verify_gramps.py --pdf-output <file.pdf> --lualatex /Library/TeX/texbin/lualatex`. Gramps 6.0.8 on macOS and LuaHBTeX 1.24.0 produced a nine-page French A4 PDF, kept locally at `output/pdf/gramps-fancy-book-ac16-pdf-cases.pdf` (an unversioned output). All nine pages were reviewed at 110 DPI: no visible clipping or overlap; the appendix renders the unlinked single-page document as an image, retains multipage documents as references, and includes the repository URL for the two linked citations. The source PDFs are blank synthetic pages and the portraits are fictional; this review does not qualify the final design or accessibility.

To make the optional dependencies available to Gramps CLI during the recipe, `scripts/verify_gramps.py` copies Pillow and PDFium into its temporary Gramps profile. This is test-only setup; it does not configure a user's Gramps Desktop installation.

The integration uses no real family data. Source files are unchanged; the portrait and four PDFs exist only in the test's temporary directory.

## Remaining checks

The `test_excluded_featured_media_is_absent_from_generated_books` test builds a synthetic Gramps snapshot with one media record carrying both tags. It checks that its editorial references and attached citations create no placement or derivative, the ZIP contains only `index.html`, and neither the description nor an `<img>` appears in HTML or LaTeX. The fictional source path does not exist, so an attempted read would fail the test.

For AC-13, export through the Gramps interface is now confirmed with a fictional native database carrying both tags; entering the tags through the GUI remains to be checked. For AC-16, the GUI options, realistic source documents and comparison with the design mockups remain to be checked.

## Installation

For development, install the project together with test and media dependencies:

\`\`\`sh
python -m pip install -e '.[dev,media]'
\`\`\`

In a Gramps Desktop environment that supports pip, run `python -m pip install 'Pillow>=10' 'pypdfium2>=4'` with the same Python interpreter that launches Gramps, then restart the application. Installing with another Python can put the packages in an environment the add-on cannot see.

The converters remain optional. The report still exports JSON and records a diagnostic when it cannot create a derivative. They are therefore not declared in `requires_mod`: Gramps 6.0 treats that field as a hard plugin-loading requirement, and its string form expects an importable module name, while Pillow is distributed as `Pillow` and imported as `PIL`. Making this optional feature a hard prerequisite would prevent JSON export when those packages are absent.

## Limits

CI qualifies dependency installation and media processing with Gramps 6.0.7 and 6.0.8 on Ubuntu 24.04. The AC-16 recipe also passes with the Gramps 6.0.8 macOS app executable when dependencies are added to the temporary profile. macOS and Windows installers, as well as isolated distributions such as Flatpak and Snap, still need validation against their own Python environments.

Gramps Web runs reports on the server. Its dependencies must be installed in the server's Python environment or image, and no test server has been exercised here. This validation does not claim Gramps Web compatibility. A Web proof needs a disposable server instance with synthetic data.

References: [Gramps add-on development](https://www.gramps-project.org/wiki/index.php/Addons_Development), [dependency handling in Gramps 6.0.8](https://github.com/gramps-project/gramps/tree/v6.0.8/gramps/gen/utils), [Gramps Web reports](https://www.grampsweb.org/user-guide/reports/).
