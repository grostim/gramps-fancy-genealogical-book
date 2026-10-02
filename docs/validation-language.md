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

## Date display follows the book language — 30 September 2026

The native Gramps 6.0.8 integration check exports the same events with the book set to English and French while the Gramps profile locale stays English. For `Birth`, both displayed values include 1900 and differ according to the selected language; the raw and normalized values remain identical. The marriage’s entered free-text date, “Entre l’hiver 1924 et le printemps 1925,” remains unchanged in both languages, with the same raw value.

## Desktop dialog selection — 2 October 2026

The Gramps Desktop 6.0.8 report dialog was opened with the add-on archive built from `891a10b462ec` (SHA-256 `0260be914cf71e3e5be95794f58f7d22df492ef3036bbbe4fd12304e85e6d391`). A temporary Gramps profile contained the add-on and a fictional tree of three people and one reference family, `F0001`. The profile-local `plugins/lib` directory provided `mistune` 3.3.4. Each export required a fresh privacy acknowledgement.

| Gramps locale | Dialog selection | Exported `BOOK_LANGUAGE` | JSON SHA-256 |
| --- | --- | --- | --- |
| French | Use Gramps language | `fr` | `ad2f15318697259a90b260305b627f97ba0ba5c96b224808117358c7baf981d9` |
| French | English | `en` | `96d24deae3a6efd89efc47a3ee9a64c1c495d927f72cd37fe01bf31abfadb1d9` |
| French | French | `fr` | `ad2f15318697259a90b260305b627f97ba0ba5c96b224808117358c7baf981d9` |
| Unsupported German | Use Gramps language | `en` | `96d24deae3a6efd89efc47a3ee9a64c1c495d927f72cd37fe01bf31abfadb1d9` |

All four JSON files contain the same normalized genealogy and reference family; after removing `BOOK_LANGUAGE`, their contents match. The two French outputs are byte-identical, as are the two English outputs. Under German Gramps, untranslated add-on labels appear in English while native Gramps controls are German. This GUI check covers the language selector and JSON model; the CLI checks above cover PDF and HTML ZIP output.

## Limits

- The PDF and HTML ZIP checks above invoke Gramps Desktop through its CLI with isolated profiles; the additional GUI check uses a smaller fictional JSON fixture.
- The check does not compare every note and event string; it confirms retention of the entered name. All fixture data is fictional.
- Structured dates are formatted by Gramps in the book language and the CLI fixture’s free-text date remains intact; the small GUI fixture does not contain those dates.
- The demonstration PDF uses a small tree and synthetic portraits; final layout, PDF accessibility, and comparison with private mockups are outside this check.
