# Media validation / Pillow and PDFium

Status as of 2026-09-28.

## Verified scope

CI installs the `media` extra across the Python 3.10–3.13 matrix and exercises conversions with synthetic images and single- and multipage PDFs. The Gramps Desktop integration job targets Ubuntu 24.04, Python 3.12 and Gramps 6.0.8. It creates a fictional portrait in a temporary media directory, imports it into an isolated database, then checks PNG cropping, manifest output and coordinated replacement of the JSON file and media directory.

The integration uses no real family data. Source files are unchanged; the portrait exists only in the test's temporary directory.

## Remaining publication check

In Gramps, tag one fictional media object with both `BOOK_EXCLUDE` and `BOOK_FEATURED`, then create an HTML ZIP book. This acceptance check passes only if the excluded object is absent from every rendered `<img>` reference in `index.html` and absent from every `media/` entry in the ZIP. The same object must not be opened or converted during generation. This manual scenario has not yet been run.

## Installation

For development, install the project together with test and media dependencies:

\`\`\`sh
python -m pip install -e '.[dev,media]'
\`\`\`

In a Gramps Desktop environment that supports pip, run `python -m pip install 'Pillow>=10' 'pypdfium2>=4'` with the same Python interpreter that launches Gramps, then restart the application. Installing with another Python can put the packages in an environment the add-on cannot see.

The converters remain optional. The report still exports JSON and records a diagnostic when it cannot create a derivative. They are therefore not declared in `requires_mod`: Gramps 6.0 treats that field as a hard plugin-loading requirement, and its string form expects an importable module name, while Pillow is distributed as `Pillow` and imported as `PIL`. Making this optional feature a hard prerequisite would prevent JSON export when those packages are absent.

## Limits

CI qualifies dependency installation and media processing with Gramps 6.0.8 on Ubuntu 24.04. macOS and Windows installers, as well as isolated distributions such as Flatpak, Snap and the macOS application bundle, still need validation against their own Python environments.

Gramps Web runs reports on the server. Its dependencies must be installed in the server's Python environment or image, and no test server has been exercised here. This validation does not claim Gramps Web compatibility. A Web proof needs a disposable server instance with synthetic data.

References: [Gramps add-on development](https://www.gramps-project.org/wiki/index.php/Addons_Development), [dependency handling in Gramps 6.0.8](https://github.com/gramps-project/gramps/tree/v6.0.8/gramps/gen/utils), [Gramps Web reports](https://www.grampsweb.org/user-guide/reports/).
