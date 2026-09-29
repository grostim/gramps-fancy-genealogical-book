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

## Standard Gramps labels — 29 September 2026

A complementary check uses a fictional native Gramps database with the standard `Birth` and `Marriage` events, a custom `Profession` type, a parent-child relationship, and a `Primary` role.

| Book language | Gramps locale | Inspected outputs | Result |
| --- | --- | --- | --- |
| French | English | PDF and HTML ZIP | `Naissance`, `Mariage`, `Principal`, and the parentage label `Naissance` are translated; `Profession` is preserved as entered |
| English | French | HTML ZIP | `Birth`, `Marriage`, `Primary`, and the parentage label `Birth` remain English; `Profession` is preserved as entered |

The fixture’s entered event description remains intact. The French PDF has 10 A4 pages. The cover, contents, family paths, notices, profiles, appendix, and index were sampled visually; page 3 and accessibility were not qualified. The PDF is untagged (`Tagged: no`). Its SHA-256 is `f01792f5b5b85cd6fcb3f5502ec26b1419dce452d4885402ad2fe5c3a946bcfa`.

## Limits

- These checks invoke the Gramps Desktop executable through its CLI with isolated profiles. They do not verify the report option’s graphical display or selection in the report dialog.
- The check does not compare every note and event string; it confirms retention of the entered name. All fixture data is fictional.
- Gramps-formatted date text is not reformatted by the renderer; its appearance when a different book language is selected remains to be decided and verified.
- The demonstration PDF uses a small tree and synthetic portraits; final layout, PDF accessibility, and comparison with private mockups are outside this check.
