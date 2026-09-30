# Media validation / Pillow and PDFium

Status as of 2026-09-30.

## Verified scope

CI installs the `media` extra across the Python 3.10–3.13 matrix and exercises conversions with synthetic images and single- and multipage PDFs. The Gramps integration job targets Ubuntu 24.04, Python 3.12 and Gramps 6.0.8. The local run of this recipe uses Gramps Desktop 6.0.8 on macOS with an isolated database.

The Gramps CLI recipe creates four fictional PDF documents, attaches them to native citations, then generates an HTML ZIP. It confirms all four AC-16 rules: an unlinked single-page PDF produces a 300-DPI PNG; an unlinked multipage PDF remains a reference; both PDFs with a URL remain links, regardless of page count. The ZIP contains the first document's derivative, all four references and the repository URL associated with the two linked citations. ZIP integrity is checked. The cropped synthetic portrait and coordinated replacement of the JSON file and media directory are also covered.

To make the optional dependencies available to Gramps CLI during the recipe, `scripts/verify_gramps.py` copies Pillow and PDFium into its temporary Gramps profile. This is test-only setup; it does not configure a user's Gramps Desktop installation.

The integration uses no real family data. Source files are unchanged; the portrait and four PDFs exist only in the test's temporary directory.

## Remaining checks

The `test_excluded_featured_media_is_absent_from_generated_books` test builds a synthetic Gramps snapshot with one media record carrying both tags. It checks that its editorial references and attached citations create no placement or derivative, the ZIP contains only `index.html`, and neither the description nor an `<img>` appears in HTML or LaTeX. The fictional source path does not exist, so an attempted read would fail the test.

The native AC-13 recipe remains outstanding: apply both `BOOK_EXCLUDE` and `BOOK_FEATURED` to a fictional media object, then generate an HTML ZIP through the Gramps UI. AC-16 is verified at the model and HTML ZIP levels; a final PDF containing all four variants and an in-app visual review remain to be produced.

## Installation

For development, install the project together with test and media dependencies:

\`\`\`sh
python -m pip install -e '.[dev,media]'
\`\`\`

In a Gramps Desktop environment that supports pip, run `python -m pip install 'Pillow>=10' 'pypdfium2>=4'` with the same Python interpreter that launches Gramps, then restart the application. Installing with another Python can put the packages in an environment the add-on cannot see.

The converters remain optional. The report still exports JSON and records a diagnostic when it cannot create a derivative. They are therefore not declared in `requires_mod`: Gramps 6.0 treats that field as a hard plugin-loading requirement, and its string form expects an importable module name, while Pillow is distributed as `Pillow` and imported as `PIL`. Making this optional feature a hard prerequisite would prevent JSON export when those packages are absent.

## Limits

CI qualifies dependency installation and media processing with Gramps 6.0.8 on Ubuntu 24.04. The AC-16 recipe also passes with the Gramps 6.0.8 macOS app executable when dependencies are added to the temporary profile. macOS and Windows installers, as well as isolated distributions such as Flatpak and Snap, still need validation against their own Python environments.

Gramps Web runs reports on the server. Its dependencies must be installed in the server's Python environment or image, and no test server has been exercised here. This validation does not claim Gramps Web compatibility. A Web proof needs a disposable server instance with synthetic data.

References: [Gramps add-on development](https://www.gramps-project.org/wiki/index.php/Addons_Development), [dependency handling in Gramps 6.0.8](https://github.com/gramps-project/gramps/tree/v6.0.8/gramps/gen/utils), [Gramps Web reports](https://www.grampsweb.org/user-guide/reports/).
