# Book language validation

Recorded 29 September 2026. This check covers the language option added in PR #100 and uses only a synthetic Gramps database.

## Environment

- macOS 27.0 arm64; Gramps Desktop 6.0.8; embedded Python 3.13.2.
- LuaHBTeX 1.24.0 (TeX Live 2026) for PDF output.
- Add-on archive built from `main` at commit `53e9934`; SHA-256 `4ada701f62340190952df39780b8faf53b125f97745558aa22136d7739dd8e58`.
- A separate temporary Gramps profile was used for each export. The macOS app does not include `mistune`; version 3.3.4 was copied only into each test profile’s `plugins/lib` directory.
- Synthetic fixture with central family `F0001`, fictional names, and a synthetic portrait. No personal tree was used.

## CLI scenarios

Each row was generated in PDF and HTML ZIP through the Gramps report. PDF text was inspected with `pdftotext`; ZIPs passed `ZipFile.testzip()`.

| Book option | Gramps locale | Expected language | PDF | HTML ZIP |
| --- | --- | --- | --- | --- |
| Automatic | French | French | Passed | Passed |
| Automatic | English | English | Passed | Passed |
| French | English | French | Passed | Passed |
| English | French | English | Passed | Passed |
| Automatic | Unsupported German | English fallback | Passed | Passed |

French output contains “Ascendance” and “Table des matières”; English output contains “Ancestry” and “Contents”. Each HTML page has the matching `lang` attribute. The fictional name “Exemple, Émile” remains unchanged in all ten outputs while generated labels change language.

## Limits

- These checks invoke the Gramps Desktop executable through its CLI with isolated profiles. They do not verify the report option’s graphical display or selection in the report dialog.
- The check does not compare every note and event string; it confirms retention of the entered name. All fixture data is fictional.
- Gramps-formatted date text is not reformatted by the renderer; its appearance when a different book language is selected remains to be decided and verified.
- PDF accessibility and comparison with private mockups are outside this check.
