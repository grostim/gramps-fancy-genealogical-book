# Performance measurement — L8.3

Repeated measurements on 2026-09-29 with macOS 27.0 arm64 and CPython 3.14.0, Gramps 6.0.8 and its embedded Python 3.13.2, LuaHBTeX 1.24.0 (TeX Live 2026), Pillow 12.3.0 and Mistune 3.3.4.

## Method and synthetic data sets

Run from the repository root in a Python environment with the project and its media extra installed (pip install -e ".[media]"); LuaLaTeX must be available on PATH:

    PYTHONPATH=src python scripts/benchmark_book.py --shape both --descendant-couples 10 100 1000 --with-media --compile-pdf-for 100 --repeat 3

    PYTHONPATH=src python scripts/benchmark_gramps_extraction.py --gramps /Applications/Gramps.app/Contents/MacOS/Gramps --descendant-couples 10 100 1000 --repeat 3 --output docs/validation-gramps-extraction-20260929.json

In the first benchmark, each size runs three times; the reported durations and memory peaks are medians. JSON, HTML and LaTeX sizes are stable across those repetitions. Gramps imports are measured separately, and regenerated internal handles cause small changes in JSON size.

Two structures are compared:

- Wide data set: one central couple with N children and their partners. Every person gets a profile; there are no events or media. This preserves the original reference case, but does not represent a deep tree.
- Branching data set: N descendant unions distributed across branches, with at most two children per family. Each person has a birth event and each family has a union event. Every event has a citation; sources are shared across 25 citations; one repository and multiple places are included. Publishable notes appear about once per 12 people and once per 10 families. A synthetic PNG portrait with a crop region appears about once per 10 people.

The first script measures model construction, derivative preparation, JSON serialization, both renderers and the HTML ZIP archive. It also compiles a PDF for the small branching case. Media consists of deterministic pseudo-random images, not real portraits.

The second script invokes the Gramps CLI report on balanced synthetic GEDCOM trees, each imported into a fresh `GRAMPSHOME` profile for every repetition. It installs the archive built from the repository and copies Mistune into the temporary profile because the macOS app does not provide that dependency. The raw measurements are saved in [validation-gramps-extraction-20260929.json](validation-gramps-extraction-20260929.json). Timing added only to the temporary report copy separates `GrampsDatabaseAdapter.read_snapshot_by_gramps_id` from model construction. End-to-end time and peak RSS also include Gramps startup, GEDCOM import and JSON writing. No normal Gramps tree is opened or changed.

## Duration and memory results

Times are in seconds. Additional peak is the maximum traced Python heap above the already-loaded snapshot and source images. MB uses decimal units.

### Wide data set

| Descendant couples N | People | Families | Model | JSON | HTML | LaTeX | HTML ZIP | Additional peak (MB) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 22 | 11 | 0.009 | 0.018 | 0.001 | 0.001 | 0.002 | 0.58 |
| 100 | 202 | 101 | 0.078 | 0.144 | 0.009 | 0.012 | 0.010 | 3.31 |
| 1,000 | 2,002 | 1,001 | 0.751 | 1.419 | 0.086 | 0.120 | 0.093 | 31.09 |

### Branching data set with media

| Descendant couples N | People | Families | Events / citations | Notes | Media / derivatives | Model | Derivatives | JSON | HTML | LaTeX | HTML ZIP | Additional peak (MB) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 22 | 11 | 33 | 3 | 2 / 2 | 0.016 | 0.001 | 0.038 | 0.004 | 0.006 | 0.006 | 1.88 |
| 100 | 202 | 101 | 303 | 27 | 20 / 20 | 0.136 | 0.010 | 0.327 | 0.034 | 0.051 | 0.045 | 7.26 |
| 1,000 | 2,002 | 1,001 | 3,003 | 267 | 200 / 200 | 1.335 | 0.099 | 3.217 | 0.341 | 0.518 | 0.430 | 68.41 |

### Output sizes

| Shape | N | JSON (bytes) | HTML (bytes) | LaTeX (bytes) | HTML ZIP (bytes) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Wide | 10 | 85,862 | 23,911 | 66,732 | 2,706 |
| Wide | 100 | 762,212 | 188,611 | 613,752 | 10,445 |
| Wide | 1,000 | 7,525,712 | 1,835,611 | 6,083,952 | 80,717 |
| Branching | 10 | 186,329 | 62,297 | 128,262 | 34,409 |
| Branching | 100 | 1,639,117 | 543,853 | 1,188,448 | 331,657 |
| Branching | 1,000 | 16,265,394 | 5,363,871 | 11,797,460 | 3,306,591 |

### Complete PDF compilation

| Descendant couples N | People | Events | Media | Median LuaLaTeX time | Range | PDF (bytes) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 202 | 303 | 20 | 4.483 s | 4.377–4.573 s | 739,729 |
| 1,000 | 2,002 | 3,003 | 200 | 34.459 s | 34.303–34.714 s | 7,074,362 |

The medium case was compiled three times with the main command. The three large PDF compilations used:

    PYTHONPATH=src python scripts/benchmark_book.py --shape branching --descendant-couples 1000 --with-media --compile-pdf-for 1000 --repeat 3

All six PDFs compiled without layout warnings.

### Extraction through Gramps

Each size was imported into a new Gramps database three times. Times and the memory peak are medians; memory is the Gramps process's maximum RSS measured with macOS `/usr/bin/time -l`, in decimal MB.

| Descendant couples N | People | Families | Events / citations | Notes | Places | Adapter (s) | Model (s) | Complete JSON report (s) | Peak RSS (MB) | Median JSON (bytes) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 22 | 11 | 33 | 2 | 22 | 0.0041 | 0.0027 | 0.755 | 188.78 | 326,342 |
| 100 | 202 | 101 | 303 | 26 | 25 | 0.0333 | 0.0220 | 1.035 | 206.68 | 2,870,536 |
| 1,000 | 2,002 | 1,001 | 3,003 | 266 | 25 | 0.3515 | 0.2240 | 3.815 | 305.04 | 28,585,990 |

Every event has one citation. The dataset shares one source and repository; notes are attached to selected people and families. Expected object counts were checked after every import. Profiles are not reused across repetitions, so Gramps regenerates its internal handles and JSON size varies slightly (326,199–326,410, 2,869,817–2,870,998, and 28,583,790–28,588,036 bytes by size). The data volume is consistent, but byte-for-byte identity is not expected across freshly imported databases.

## Interpretation and limitations

The branching case adds substantial work absent from the wide data set: at 2,002 people, it processes 3,003 events and citations, 267 notes and 200 media derivatives. Under tracemalloc, JSON serialization takes 3.217 s on the largest data set and the additional peak reaches 68.41 MB. These instrumented durations do not directly predict production response times.

The Gramps measurements show that the adapter reads 2,002 people, 1,001 families and 3,003 events/citations in 0.351 s; the complete CLI report takes 3.815 s and reaches 305.04 MB peak RSS. RSS includes the Gramps application and cannot be compared directly with the additional Python heap tracked by tracemalloc in the other benchmark.

This does not set acceptance thresholds yet. The imported graph covers branching descendants only; ancestry, multiple unions, pedigree collapse and media still need measurements through Gramps. The pseudo-random images in the direct benchmark do not reproduce the compression of real photos. Tracemalloc excludes native Pillow allocations and the LuaLaTeX subprocess's memory. Set thresholds after these scenarios and target production environments have been measured.
