# PDF accessibility qualification

## Automated PDF/UA-2 audit — October 9, 2026

Production emits tagged PDF 2.0. Its `DocumentMetadata` command currently
sets only `lang` and `tagging=on`, with no PDF/UA conformance declaration.

This audit uses **veraPDF Greenfield 1.30.3**, the stable distribution built
on October 7, installed only in a temporary directory. The profile is
explicitly `ua2`; metadata repair is disabled:

```sh
verapdf --flavour ua2 --format xml book.pdf > report.xml
```

An explicit profile avoids automatic fallback to a PDF/A profile when the
file has no standard declaration. See the [validation documentation](https://docs.verapdf.org/cli/validation/).
Hashes, versions and per-file results are retained in the
[record](validation-pdf-accessibility-20261009.json) and the complete
[XML report](validation-pdf-accessibility-20261009.xml).
All fixtures are fictional; no personal tree is used.

### Observed results

| Fixture | Pages | Reported passed / failed rules | Reported passed / failed checks |
| --- | ---: | ---: | ---: |
| Dense CI fixture, English | 16 | 1,727 / 1 | 58,223 / 1 |
| Dense CI fixture, French | 15 | 1,727 / 1 | 58,532 / 1 |
| Sparse CI fixture, English | 4 | 1,727 / 1 | 3,368 / 1 |
| N=1,000, installed tagpdf 0.99y | 1,108 | 1,727 / 1 | 10,996,605 / 1 |

All four audits terminate normally, with no reported parsing failure,
out-of-memory condition or veraPDF exception. Exit code is 1 and all
four files are **noncompliant** with the requested profile. The sole
reported failure is ISO 14289-2:2024, clause 5, test 1: the XMP metadata
lacks the PDF/UA identification schema. This matches production source.

The three CI PDFs come from commit `c99a378`, PR #336,
[run 37936272667](https://github.com/grostim/gramps-fancy-genealogical-book/actions/runs/37936272667),
artifact `11618726899`. The large PDF comes from renderer `bf80ada`,
pair 1, installed variant of the
[N=1,000 benchmark](validation-latex-tagpdf-version-paired-n1000-20261009.json).
It was not recompiled for this audit. No metadata repair or production
conformance declaration was introduced.

## Scope and next steps

veraPDF covers machine-verifiable requirements. Its
[documentation](https://docs.verapdf.org/validation/) explicitly distinguishes
machine and human checks for PDF/UA. Automated results do not qualify
alternative-text relevance, heading semantics or actual assistive reading order.

Before claiming conformance or enabling its production declaration:

1. Review reading order on the cover, contents, profiles, family notices,
   notes, citations, appendix and index, including continuation pages and
   footnote references.
2. Qualify heading, list, link, figure and strikethrough announcements with
   a screen reader in French and English. Record the screen reader and PDF
   viewer versions, pages and observations.
3. Review alternative-text relevance and decorative artifacts with
   representative photographs; synthetic portraits do not qualify these.
4. If these checks pass, qualify a diagnostic build with the appropriate
   PDF/UA-2 declaration; repeat automated checks and compare content, links,
   geometry and pagination before adopting it in production.
5. Repeat on current native Gramps Desktop outputs and target environments.
   Synthetic qualification and tagpdf version comparisons remain separate.

Existing structure, ParentTree/OBJR link and BBox checks remain useful.
They do not replace these checks.

## Continuous machine-verifiable checks

`scripts/verify_pdf_ua2.py` runs the explicit `ua2` profile, preserves XML
and stderr and rejects additional failures. Its default mode requires an
automatically compliant result. CI uses `--allow-missing-identification`
to permit only the known ISO 14289-2:2024 clause 5 test 1 failure,
MainXMPPackage object, `containsPDFUAIdentification == true`.
JSON still reports `is_compliant: false` and
`human_accessibility_qualified: false`.

CI pins veraPDF 1.30.3 by versioned URL and SHA-256. Reports for the English,
French and sparse fixtures, including negative controls, are uploaded even
after failure. Execution errors, incomplete reports and other failures
reject the baseline.

Use a fresh report directory:

```sh
python scripts/verify_pdf_ua2.py book.pdf --verapdf /path/to/verapdf \
  --report-directory /tmp/ua2-new-report --allow-missing-identification
```

Local controls show an intact clone is accepted, while missing document
language and a removed Figure Alt attribute are rejected despite the
metadata exception. An **empty Alt** probe was accepted by veraPDF 1.30.3:
the existing renderer audit still requires nonempty alternative text,
and human review must check its relevance. These controls do not qualify
every validator rule. See the [control record](validation-pdf-ua2-ci-controls-20261009.json).

The preserved 103-page GUI PDF with twenty public portraits was also
audited: one failure for the same missing identification schema, with
1,002,036 reported successful checks. Its renderer predates moving the
`samepage` group after `\item`; this evidence does not replace a current
GUI re-export. The [complete report](validation-pdf-accessibility-native-gui-20261009.xml)
is retained.

## Final CI qualification and current native export

PR #339 was merged after
[run 37946900354](https://github.com/grostim/gramps-fancy-genealogical-book/actions/runs/37946900354)
succeeded at commit `1283c51`. Artifact `11624441929` contains the six
expected records: English, French, sparse, intact clone and two corruptions.
The downloaded archive matches its GitHub digest. Normal outputs and the
intact clone pass the automatic baseline; missing language and removed Alt
are rejected. The PDFs remain noncompliant with PDF/UA-2 because they lack
the identification schema.

A fresh Gramps 6.0.8-1 profile also received the current archive, with
Mistune and media dependencies installed only there. The checkout was
removed from `PYTHONPATH`. The fictional fixture has 202 people, 101 families,
303 citations and twenty public portraits. Its native CLI PDF has 103 pages
and 77,489,201 bytes. All 2,034 links pass the ParentTree/OBJR ownership and
destination audit; all twenty figures have nonempty Alt and valid BBox.
veraPDF reports only the same missing identification schema.

All **103 rendered pages** have identical pixels to the preserved corrected
GUI PDF from October 9, using PDFium at 108 dpi on this host. Physical pages
1, 22, 70 and 97 were also inspected directly: no observed clipping, readable
portrait attribution and citation [299] entirely on page 97. The full
comparison covers pixels at that resolution, not screen-reader behavior or
the current GUI export path.

The single observed native duration of 41.955 seconds includes extraction
and report generation; it is neither compiler-only timing nor a paired
benchmark. The PDF remains above the 16 MiB size target. No image cap or
conformance declaration is adopted. See the
[complete record](validation-native-current-portraits-20261009.json).
