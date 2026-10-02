# Performance measurement — L8.3

Repeated measurements on 2026-09-29 with macOS 27.0 arm64 and CPython 3.14.0, Gramps 6.0.8 and its embedded Python 3.13.2, LuaHBTeX 1.24.0 (TeX Live 2026), Pillow 12.3.0 and Mistune 3.3.4.

## Method and synthetic data sets

Run from the repository root in a Python environment with the project and its media extra installed (pip install -e ".[media]"); LuaLaTeX must be available on PATH:

    PYTHONPATH=src python scripts/benchmark_book.py --shape both --descendant-couples 10 100 1000 --with-media --compile-pdf-for 100 --repeat 3

    PYTHONPATH=src python scripts/benchmark_gramps_extraction.py --gramps /Applications/Gramps.app/Contents/MacOS/Gramps --scenario branching ancestors multiple-unions pedigree-collapse media --descendant-couples 10 100 1000 --repeat 3 --output docs/validation-gramps-scenarios-20260929.json

In the first benchmark, each size runs three times; the reported durations and memory peaks are medians. JSON, HTML and LaTeX sizes are stable across those repetitions. Gramps imports are measured separately, and regenerated internal handles cause small changes in JSON size.

Two structures are compared:

- Wide data set: one central couple with N children and their partners. Every person gets a profile; there are no events or media. This preserves the original reference case, but does not represent a deep tree.
- Branching data set: N descendant unions distributed across branches, with at most two children per family. Each person has a birth event and each family has a union event. Every event has a citation; sources are shared across 25 citations; one repository and multiple places are included. Publishable notes appear about once per 12 people and once per 10 families. A synthetic PNG portrait with a crop region appears about once per 10 people.

The first script measures model construction, derivative preparation, JSON serialization, both renderers and the HTML ZIP archive. It also compiles a PDF for the small branching case. Media consists of deterministic pseudo-random images, not real portraits.

The second script invokes the Gramps CLI report on synthetic GEDCOM files. Every repetition gets a fresh `GRAMPSHOME` profile; the script installs the repository archive and copies Mistune into the temporary profile. The first branching-only measurements are in [validation-gramps-extraction-20260929.json](validation-gramps-extraction-20260929.json). Five expanded scenarios and their raw measurements are in [validation-gramps-scenarios-20260929.json](validation-gramps-scenarios-20260929.json). Timing added only to the temporary report copy separates `GrampsDatabaseAdapter.read_snapshot_by_gramps_id` from model construction. End-to-end time and peak RSS also include Gramps startup, GEDCOM import and JSON writing. No normal Gramps tree is opened or changed.

The expanded scenarios use N = 10, 100 or 1,000:

- **Branching:** the reference descendant tree, with at most two children per family.
- **Ancestry:** N ancestor unions split between the central partners. One parent line continues at each generation to measure depth without exponential growth.
- **Multiple unions:** the branching tree, with one additional childless union and a unique partner for every descendant.
- **Pedigree collapse:** the branching tree, with one cousin union and child added per five descendant unions. Cousins belong to different branches and share ancestors.
- **Media:** the branching tree, with a valid 1 × 1 pixel PNG linked to every tenth person. Each reference points to a distinct media object.

Expected record counts are checked after every import. Every synthetic fact has one citation, and the source and repository are shared. The expanded run uses host CPython 3.13.7, Gramps 6.0.8 and its embedded Python 3.13.2. Its medians are separate from the earlier extraction run, which used host CPython 3.14.0.

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

### Complete PDF compilation — untagged baseline from 29 September

These timings describe the renderer before PDF tagging was enabled; they are not comparable with the current tagged renderer.

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

### Expanded scenarios through Gramps

Three separate databases were imported per scenario and size. “Facts / citations” match because every synthetic fact has a citation. JSON size and RSS are in decimal MB.

| Scenario | N | People | Families | Facts / citations | Media | Adapter (s) | Model (s) | Complete report (s) | Peak RSS (MB) | JSON (MB) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Branching | 10 | 22 | 11 | 33 | 0 | 0.005 | 0.003 | 0.801 | 188.8 | 0.326 |
| Branching | 100 | 202 | 101 | 303 | 0 | 0.035 | 0.023 | 1.073 | 206.6 | 2.870 |
| Branching | 1,000 | 2,002 | 1,001 | 3,003 | 0 | 0.360 | 0.227 | 3.896 | 305.0 | 28.587 |
| Ancestry | 10 | 22 | 11 | 33 | 0 | 0.005 | 0.003 | 0.807 | 188.8 | 0.319 |
| Ancestry | 100 | 202 | 101 | 303 | 0 | 0.036 | 0.024 | 1.083 | 206.9 | 3.005 |
| Ancestry | 1,000 | 2,002 | 1,001 | 3,003 | 0 | 0.361 | 0.701 | 4.840 | 363.3 | 52.090 |
| Multiple unions | 10 | 32 | 21 | 53 | 0 | 0.007 | 0.004 | 0.833 | 190.0 | 0.503 |
| Multiple unions | 100 | 302 | 201 | 503 | 0 | 0.056 | 0.037 | 1.261 | 215.7 | 4.623 |
| Multiple unions | 1,000 | 3,002 | 2,001 | 5,003 | 0 | 0.571 | 0.397 | 5.861 | 372.1 | 46.109 |
| Pedigree collapse | 10 | 24 | 13 | 37 | 0 | 0.005 | 0.003 | 0.810 | 188.7 | 0.369 |
| Pedigree collapse | 100 | 222 | 121 | 343 | 0 | 0.039 | 0.025 | 1.118 | 209.0 | 3.294 |
| Pedigree collapse | 1,000 | 2,202 | 1,201 | 3,403 | 0 | 0.401 | 0.256 | 4.325 | 321.0 | 32.939 |
| Media | 10 | 22 | 11 | 33 | 2 | 0.005 | 0.003 | 0.802 | 188.8 | 0.333 |
| Media | 100 | 202 | 101 | 303 | 20 | 0.035 | 0.023 | 1.077 | 207.0 | 2.940 |
| Media | 1,000 | 2,002 | 1,001 | 3,003 | 200 | 0.362 | 0.230 | 3.976 | 308.0 | 29.281 |

## Interpretation and limitations

The branching case adds substantial work absent from the wide data set: at 2,002 people, it processes 3,003 events and citations, 267 notes and 200 media derivatives. Under tracemalloc, JSON serialization takes 3.217 s on the largest data set and the additional peak reaches 68.41 MB. These instrumented durations do not directly predict production response times.

The Gramps measurements show that the adapter reads 2,002 people, 1,001 families and 3,003 events/citations in 0.351 s; the complete CLI report takes 3.815 s and reaches 305.04 MB peak RSS. RSS includes the Gramps application and cannot be compared directly with the additional Python heap tracked by tracemalloc in the other benchmark.

The new cases cover deep ancestry, additional unions, pedigree-collapse links and media references from an imported Gramps database. At N = 1,000, the ancestry shape produces 52.1 MB of JSON and takes 0.701 s to build the model; multiple unions produce the largest RSS in this set at 372.1 MB. These results cover controlled GEDCOM files and the macOS CLI report. The ancestry shape is a deep line rather than a complete ancestral tree; secondary unions are childless; 1 × 1 images measure references and metadata, not decoding or cropping real photographs. Final thresholds still need confirmation after qualifying the target environments, especially Gramps Web.

## Proposed reference envelope — 1 October 2026

To make L8.3 actionable, these provisional budgets use the only measured reference configuration above: macOS 27.0 arm64, Gramps 6.0.8 and LuaHBTeX 1.24.0. They are not CI gates or guarantees for other machines. Compare medians from three identical runs.

| Reference workload | Proposed budget | Observed result |
| --- | --- | --- |
| Gramps CLI export, N=1,000, five synthetic shapes | ≤ 10 s; RSS ≤ 512 MB; JSON ≤ 64 MB | Separate maxima: 5.861 s and 372.1 MB RSS (multiple unions); 52.090 MB JSON (ancestry) |
| Branching PDF compile, 2,002 people, 3,003 events and 200 derived media files | ≤ 60 s; PDF ≤ 16 MB | Current tagged renderer: timeout after 120.804 s, no PDF; untagged baseline: 34.714 s and 7,074,362 bytes |
| Generate fixture, derivatives and HTML ZIP, N=100 with 20 PNGs at 1,600 × 1,200 | ≤ 8 s total; `tracemalloc` peak ≤ 256 MB | 2.071 s for fixture generation, 1.484 s for derivatives, and 1.149 s for the archive; 4.704 s and 126.17 MB traced peak overall |

The renderer now limits LuaLaTeX to 120 s per pass and 180 s overall, replacing the previous theoretical maximum of five 120-second passes. This time guard is wider than the PDF performance budget and stops a stuck export. The RSS and final-file budgets remain qualification criteria, not runtime-enforced limits. Temporary-directory disk usage has an initial measurement but is not capped; these criteria must be qualified on a clean installation and other environments before they become release thresholds.

### Temporary workspace measured on 1 October 2026

The benchmark sums the logical sizes of files under its temporary directory every 100 ms. It ignores symbolic links; files created and removed between samples can be missed. This measures the local synthetic benchmark workspace, not total system temporary storage. The preceding statement that temporary usage was unmeasured describes the state before this first measurement.

| Case | PDF result | Observed temporary-file peak |
| --- | --- | ---: |
| 100 unions, 20 synthetic 1,600 × 1,200 PNGs, derivatives and HTML ZIP | PDF compilation not requested | 157,472,942 bytes |
| 100 unions, standard 96 × 72 portraits, PDF | Compiled in 163.058 s; 1,935,494 bytes | 4,837,119 bytes |
| 1,000 unions, 200 standard 96 × 72 portraits, PDF | `timeout` after 120.804 s; no PDF delivered | 24,584,541 bytes before termination |

The compiled medium case exceeds the provisional 60-second budget. The N=1,000 case reached the 120-second per-pass limit twice with 10 ms sampling and a third time at 100 ms; the sampling interval therefore does not explain the timeout. The earlier medians of 4.483 s for N=100 and 34.459 s for N=1,000 were measured on 29 September, before tagged PDF output was enabled by [PR #132](https://github.com/grostim/gramps-fancy-genealogical-book/pull/132), merged on 30 September, and before the family-list fix in [PR #180](https://github.com/grostim/gramps-fancy-genealogical-book/pull/180), merged on 1 October. They are not directly comparable with the current tagged renderer. A diagnostic compilation of the same small book took 19.104 s with `tagging=on` and 9.039 s with tagging disabled only in the temporary copy; this suggests a meaningful tagging cost but does not by itself explain the medium and large book times. Repeat current measurements after qualifying or optimizing the tagged renderer; the proposed PDF envelope is not confirmed. See the [raw temporary-workspace record](validation-temp-disk-20261001.json).

### PDF structure-destination diagnostic — 1 October 2026

A branching fixture without media (N=10, 22 people, 11 families, 33 events) was compiled three times per variant in fresh temporary directories through the production renderer's `_compile_latex` helper with LuaHBTeX 1.24.0. The `activate/struct-dest=false` variant disables destinations for structure elements while keeping tagging enabled, as described in the [tagpdf documentation](https://tug.ctan.org/macros/latex/contrib/tagpdf/tagpdf-code.pdf).

| Setting | Compilation (s, median [range]) | PDF (bytes, median [range]) |
| --- | ---: | ---: |
| Current tagging | 19.633 [19.179–19.883] | 221,701 [221,701–221,702] |
| Structure destinations disabled | 19.543 [19.121–19.991] | 211,287 [211,283–211,291] |

Both files are recognized as tagged and contain 25 A4 pages. The structure tree reported by `pdfinfo -struct` is identical in the same order (2,520 elements, including 525 links, 441 paragraphs and 217 list items); all 561 named destinations, 132 external-link annotations and extracted text are identical. `pdfinfo -struct` also emits 114 identical `ListNumbering` attribute warnings for each file; this record is not a conformance check.

Disabling structure destinations reduces the median PDF size by 10,414 bytes (4.7%), but improves the median compile time by only 0.090 s from 19.633 s (0.46%), too little to justify an optimization. No production setting is changed; this fixture does not confirm the PDF budget or predict medium and large books. Tree inspection does not replace a screen-reader check. Raw results are in the [tagpdf measurement record](validation-tagpdf-structure-20261001.json).

A second experiment directly disables `para/tagging` in the temporary copy immediately before `\begin{document}`. Across three compilations of the same fixture, the median is 19.937 s [19.759–20.111], compared with 19.633 s for current tagging; the PDFs are each 221,551 bytes, versus the current median of 221,701 bytes. Poppler reports `Tagged: no` for all three files. They retain 25 pages, 561 named destinations, 132 external links and 27,853 extracted text characters, identical across repetitions. The timing difference (+0.304 s, +1.55%) is not a gain, and tagging is lost, so this setting is ruled out. This is a small-fixture diagnostic, not a proposed configuration.

### LuaLaTeX pass profile — 1 October 2026

One run per variant timed each LuaLaTeX subprocess launched by the production `_compile_latex` helper in a fresh temporary directory. The branching fixtures contain two synthetic portraits at N=10 and twenty at N=100 (96 × 72 pixels). At N=100, the tagged and untagged diagnostic copies use the same model, media and rendered source; only `tagging=on` is replaced with `tagging=off` in the temporary source.

| Case | Passes | Time per pass (s) | Total (s) | PDF size |
| --- | ---: | ---: | ---: | ---: |
| N=10, tagged | 3 | 6.794; 6.829; 6.828 | 20.452 | 255,856 bytes |
| N=100, tagged | 3 | 53.302; 53.800; 54.063 | 161.166 | 1,935,504 bytes |
| N=100, tagging disabled for diagnosis | 2 | 32.694; 32.923 | 65.639 | 868,690 bytes |

At N=100, all three tagged passes take about 54 seconds each, bringing the complete generation to 161.166 seconds. The untagged copy is 2.46 times faster, but Poppler reports `Tagged: no` for its 194-page PDF. This points to a substantial tagging cost, but does not support disabling it in production. Each variant was run once; these figures guide further profiling and do not establish a new statistical budget. The record also includes the LaTeX source sizes: [raw pass profile](validation-latex-pass-profile-20261001.json).

The N=10 convergence profile explains the third tagged pass: adding the table-of-contents entries changes the sole auxiliary record `@tag@LastPage`, from 1,921 to 1,949 marked-content chunks and from 2,520 to 2,541 structure elements. The table of contents and page count are already stable, but extracted text changes between passes 1 and 2. The counters then stabilize, and extracted text, structure, destinations and links remain unchanged between passes 2 and 3. The [tagpdf code that derives structure-ID padding from `tagstruct`](https://github.com/latex3/tagpdf/blob/main/tagpdf-tree.dtx#L1895-L1903) and [assembles the ParentTree through `tagmcabs`](https://github.com/latex3/tagpdf/blob/main/tagpdf-tree.dtx#L2203-L2214) relies on these values; excluding them from the convergence check could leave an incomplete PDF. Optimization must therefore reduce per-pass cost while retaining the passes.

A single instrumented first pass of the branching N=100 fixture, with tagging enabled and twenty 96 × 72 pixel portraits, took 52.284 s and produced a tagged 194-page PDF. Each section timer runs to the next section marker and includes page breaks and shipout.

| Section | Time (s) |
| --- | ---: |
| Ancestry | 0.033 |
| Descent | 1.26 |
| Family connections | 13.5 |
| Family notices | 5.1 |
| Person profiles | 10.5 |
| Documentary appendix | 14.1 |
| Person index | 3.03 |
| Timed sections total | 47.523 |
| Complete pass | 52.284 |

Family connections, the documentary appendix and person profiles dominate this pass. Internal tagpdf hooks time tree finalization at 3.284 s, including 2.77 s to write structure elements. This one instrumented run guides further profiling; it does not establish a statistical budget or break down LaTeX operations within each section. The PDF remains tagged (Tagged: yes). Raw results are in the [pass profile](validation-latex-pass-profile-20261001.json).

### Compact PDF destination encoding — 1 October 2026

On the same N=100 fixture, each comparison used fresh temporary directories. The base32 variant changes only internal PDF target names. Each full run uses the production helper's three passes, and the variant order is reversed for the second pair.

| Target encoding | Times (s) | Median (s) | Compiled source | Median final PDF |
| --- | ---: | ---: | ---: | ---: |
| UTF-8 hexadecimal | 159.271; 157.841 | 158.556 | 1,265,310 bytes | 1,935,501 bytes |
| Lowercase base32 without padding | 143.177; 146.125 | 144.651 | 1,123,555 bytes | 1,946,333 bytes |

Median full compile time falls by 8.77% and source size by 141,755 bytes (11.2%). Both PDFs retain 194 A4 pages and tagging. They contain the same 4,905 named destinations, including 1,805 book targets, each remapped one-to-one. Poppler's structure output and extracted text are byte-for-byte identical within both pairs. The tradeoff is a final PDF increase of about 10,833 bytes (0.56%). Two pairs support this renderer optimization but do not establish a statistical budget. The earlier N=100 source-size figure of 1,249,510 bytes matches rendering before media derivatives are prepared; this comparison includes the derivatives actually compiled. Raw details are in the [pass profile](validation-latex-pass-profile-20261001.json).

### Compact repeated page-link source — 1 October 2026

The page-reference macro expands to the same two clickable text spans and page reference as the previous inline source. On the same N=100 fixture, two three-pass compiles produced a median source size of 821,686 bytes, down 301,869 bytes (26.86%) from the base32 reference. The sampled temporary-workspace peak fell from 4,837,119 to about 4,345,714 bytes (10.16%). Median compile time was 145.045 s versus 144.651 s for the base32 reference, which is no measurable runtime improvement. The final PDF stayed effectively the same size (1,946,325 versus 1,946,333 bytes). The generated 194-page PDF is tagged; its 4,905 destinations, Poppler structure output and extracted text match the base32 reference byte-for-byte. This confirms a source and temporary-space reduction, not faster compilation. The comparison uses CPython 3.13.7 for the macro variant and 3.14.0 for the reference; LuaHBTeX 1.24.0 is common to both. See the raw [pass profile](validation-latex-pass-profile-20261001.json).

### One PDF link for the name and page — 1 October 2026

The page-reference macro now makes the person's name and printed page number one clickable link. On the same fixture and runtime as the preceding two-link macro, two three-pass compiles took 116.948 s and 116.991 s (median 116.969 s), 19.36% below the preceding median of 145.045 s. The 194-page tagged PDF fell by 226,728 bytes (11.65%), from a median 1,946,325 to 1,719,597 bytes. Its sampled temporary-workspace peak fell by 4.93%. The structure contains 2,869 Link elements, down from 4,814; all 4,905 named destinations remain. Extracted text is byte-for-byte identical to the earlier PDF. The changed structure hash reflects the intentionally consolidated link annotations; pages 12–13 of the family-connection section were reviewed for layout. Details are in the [pass profile](validation-latex-pass-profile-20261001.json).

The grouped profile clarifies the high family-connections cost: fifty sections with children contain 200 parent-child links and take 10.90 s across the first two groups of 25; the 51 childless sections take about 2.50 s. Those timers include page breaks. Groups of 25 profiles and appendix citations are much more even, at around 1.1 to 1.4 s. The result aligns with the nested relationship lists, but the timing does not separate their composition from layout and page output.

### Grouped child and parentage entries — 1 October 2026

The PDF family-connection section now lists each child once and groups that child's recorded parents and relationship types underneath. This follows the HTML renderer's child-first grouping while preserving the recorded parentage links. The baseline is the single-link renderer from PR #190; both variants use the same branching fixture and twenty 96 × 72 synthetic portraits on macOS 27.0 arm64, CPython 3.13.7 and LuaHBTeX 1.24.0.

| Case | Baseline | Grouped | Change |
| --- | ---: | ---: | ---: |
| N=100 LaTeX source | 821,686 bytes | 801,556 bytes | −20,130 bytes (−2.45%) |
| N=100 full PDF compile, two runs | 116.948 s; 116.991 s | 111.406 s; 110.942 s | Median 116.969 → 111.174 s (−4.95%) |
| N=100 final PDF size | 1,719,597 bytes | median 1,628,692 bytes | −90,905 bytes (−5.29%) |
| N=1,000 LaTeX source | 8,119,289 bytes | 7,917,825 bytes | −201,464 bytes (−2.48%) |
| N=1,000 full PDF compile | `timeout` at 122.715 s | `timeout` at 122.718 s | No measurable improvement; neither produced a PDF |

The grouped N=100 PDF is tagged, 195 pages, and 1,628,695 bytes. Poppler reports 2,669 Link structure elements, down from 2,869, and all 1,805 named book targets are present. Pages 12–13 show the grouped parentage; the relationship type can wrap onto its own continuation line but remains readable. The N=1,000 source and compile result show that this reduction alone does not resolve the large-book timeout. The local preview is `output/pdf/gramps-fancy-book-parentage-grouping-preview-20261001.pdf`; its records and synthetic portraits are fictitious. These are targeted measurements, not a three-run performance qualification.

### Inline reference for single-call citations — 1 October 2026

In the documentary appendix, a citation with one call now uses a localized “See”/“Voir” paragraph and keeps the clickable link to its profile or family notice. Citations with multiple calls remain lists. This retains every call anchor and avoids a one-item nested list for the common one-call case.

| Case | Parentage-grouping preview | Single-call reference | Change |
| --- | ---: | ---: | ---: |
| N=100 source LaTeX | 801,556 bytes | 794,104 bytes | −7,452 bytes (−0.93%) |
| N=100 full PDF compile | 111.174 s median from two runs | 101.429 s, one run | −8.8% versus the prior median; targeted only |
| N=100 final PDF | 1,628,695 bytes | 1,583,991 bytes | −44,704 bytes (−2.74%) |
| PDF pages | 195 | 193 | −2 |
| Structure elements `L` / `LI` / `Link` | 972 / 1,854 / 2,669 | 696 / 1,578 / 2,669 | −276 lists and list items; links unchanged |

The latest tagged PDF retains all 1,805 named book targets. Physical page 123 was rendered at 130 dpi and reviewed: single-call references read as “See/Voir” paragraphs, while multiple calls remain bulleted; no clipping or overlap was visible in that targeted page. The compile comparison uses one run against the preceding two-run median and is not a stable timing estimate. The N=1,000 source and full PDF compilation have not yet been repeated for this change. The local preview at `../output/pdf/gramps-fancy-book-single-call-citation-preview-20261001.pdf` contains fictitious records and portraits; SHA-256 `3cf5f9b8025258db353f71d2292875c5bc0e5d244d5bbbda47f9cd143dfc2578`.

### Single-item person-profile sections — 1 October 2026

For a profile with exactly one event or one distinct citation entry, the PDF now prints the event or linked source reference as a paragraph beneath its heading. Multiple events and multiple sources remain itemized. On the N=100 branching fixture, all 202 profiles have one event; each has one distinct source reference. The fixture also contains 16 profiles with two citation calls that resolve to the same entry, so the renderer still deduplicates repeated entries.

| Case | Single-call citation preview | Profile paragraphs | Change |
| --- | ---: | ---: | ---: |
| N=100 LaTeX source | 794,104 bytes | 786,832 bytes | −7,272 bytes (−0.92%) |
| N=100 full production compile | 101.429 s, one run | 93.419 s, one run | −8.010 s (−7.90%); indicative only |
| N=100 tagged PDF | 1,583,991 bytes; 193 pages | 1,470,734 bytes; 177 pages | −113,257 bytes (−7.15%); −16 pages |
| Structure `L` / `LI` / `Link` | 696 / 1,578 / 2,669 | 292 / 1,174 / 2,669 | −404 lists and list items; links unchanged |

The candidate retains exactly the same 1,805 named book destinations and 3,073 PDF link annotations as the preceding preview. Physical pages 57–58 were rendered at 130 dpi and reviewed; the compact event/source rows remain legible and no clipping or overlap was visible. The old and new timings are single runs, not a stable performance estimate; the N=1,000 case and profiles with multiple distinct events or citations still need measurement. See the [raw measurement](validation-latex-profile-singletons-20261001.json) and local preview at `../output/pdf/gramps-fancy-book-single-event-profile-preview-20261001.pdf` (SHA-256 `6ae26746fcc1588982c7be0786226f6ad8de146636280bc5e9846cafc698c3ac`).

### Single-item family notices — 1 October 2026

In PDF family notices, one event and one distinct source entry now appear as paragraphs beneath their headings; multiple entries remain lists. The N=100 branching fixture has 101 notices, each with one event and one distinct citation. This variant is compared with the PDF after the single-item person-profile change.

| Case | Profile-singleton reference | Compact family notices | Change |
| --- | ---: | ---: | ---: |
| N=100 LaTeX source | 786,832 bytes | 783,196 bytes | −3,636 bytes (−0.46%) |
| N=100 full compile | 93.419 s, one run | 90.315 s, one run | −3.104 s (−3.32%), indicative |
| N=100 tagged PDF | 1,470,734 bytes; 177 pages | 1,409,982 bytes; 169 pages | −60,752 bytes (−4.13%); −8 pages |
| Structure `L` / `LI` / `Link` | 292 / 1,174 / 2,669 | 90 / 972 / 2,669 | −202 lists and list items; links unchanged |

All 1,805 named book destinations and 3,073 link annotations remain identical. Physical pages 29 and 31 were rendered at 130 dpi and reviewed; no clipping or visible overlap was found. Each compile time is a single run. At N=1,000, source size falls from 7,771,881 to 7,735,845 bytes (−0.46%), but both compiles time out after about 122.65 s and produce no PDF. Sampled temporary-file peaks are 22,266,020 bytes for the reference and 23,310,001 for the candidate; this single measurement does not show lower disk use. The large-book timeout remains unresolved. See the [raw data](validation-latex-family-notices-20261001.json) and local preview at `../output/pdf/gramps-fancy-book-single-event-notice-preview-20261001.pdf` (SHA-256 `0b3b395928504f2ad8a1b6412d878443a64200be5fe533892f080a2804db00b0`).

### Partial LuaLaTeX first-pass profile — N=1,000 — 1 October 2026

The current source after compacting family notices is 7,735,845 bytes for 2,002 people, 1,001 families, 3,003 events, 3,003 citations, 1,001 notices, 2,002 profiles, and 200 synthetic portraits. A temporary copy received Lua `os.clock()` markers before the main sections and every 100 entries in larger sections. One pass was launched with production options in a fresh directory; the diagnostic timeout was 121 s. The values below are Lua-reported CPU intervals rounded to the nearest millisecond. The instrumentation adds markers to the document, and its overhead was not subtracted.

| Completed section or block | CPU (s) |
| --- | ---: |
| Cover, front matter, and contents | 0.022 |
| Ancestry | 0.030 |
| Descent | 10.686 |
| Family connections, 500 sections with children | 39.627 |
| Family connections, 500 sections without children | 13.910 |
| End of family connections | 0.056 |
| First 1,000 family notices | 29.593 |
| End of family notices | 0.047 |
| First 800 of 2,002 person profiles | 24.365 |

LuaHBTeX hit the timeout after 121.023 s. The log shows it was still in the profile section; the documentary appendix and person index were not reached. The interrupted PDF file (3,727,852 bytes) has no trailer dictionary or xref table and is not a deliverable PDF. This partial profile shows that family connections with parentage links, family notices, and profiles already consume nearly all of one pass; it does not measure the appendix. The results point to parentage links and repeated page-link generation as the next areas to investigate. They are not an uninstrumented performance measurement. See the [raw data](validation-latex-first-pass-n1000-20261001.json).

### Rejected experiment — repeated running-header marks — N=100 — 1 October 2026

A temporary variant emitted `\markright` in family connections, notices, and profiles only when the context string changed.

| Measure | Reference | Candidate |
| --- | ---: | ---: |
| N=100 full compile | 90.315 s | 90.613 s |
| PDF | 1,409,982 bytes; 169 pages | 1,410,100 bytes; 169 pages |
| Named destinations counted by pypdf | 3,898 | 3,898 |
| Link annotations | 3,073 | 3,073 |
| Tagged PDF | yes | yes |
| Identical extracted text per page | yes | no |

Both extractions contain 215,988 characters, but running context headers and the pagination of several entries differ, including physical pages 13–16 and 30–31. The temporary preview was removed and the source change was reverted.

Each timing comes from one run, and the runs are not directly comparable: they used CPython 3.14.0 and 3.13.7, respectively. The result establishes no performance gain and does not preserve the current output. See the [raw data](validation-latex-running-header-marks-20261001.json); the latest accepted preview remains the [compact-notice PDF](../output/pdf/gramps-fancy-book-single-event-notice-preview-20261001.pdf).

### LaTeX escaping with a translation table — N=1,000 — 1 October 2026

`escape_latex_text` now uses `str.translate` with a precomputed translation table instead of a character-by-character Python generator. On the branching fixture with 1,000 descendant unions, 2,002 people, and 200 synthetic portraits, three source-generation measurements fall from a 2.202271 s median to 2.034793 s (−7.61%, or −0.167478 s). Both variants use CPython 3.14.0 on the same Mac, with three repetitions each.

The generated LaTeX source is byte-identical: 7,735,845 bytes and SHA-256 `26cc3b3a77946413b08f19ee058de3ba451d7e359e40c32eb6167c94c05950e9` before and after. The PDF compile was not repeated: this improves only Python source generation and does not reduce the dominant LuaLaTeX work. The N=1,000 timeout remains unresolved. See the [raw measurements](validation-latex-text-translation-20261001.json).

### URL-safe Base64 PDF target labels — N=1,000 — 1 October 2026

Hyperref target IDs now use unpadded URL-safe Base64 (`A–Z`, `a–z`, digits, `-`, and `_`) instead of unpadded lowercase Base32. On the same N=1,000 branching fixture with 200 synthetic portraits, three LaTeX-generation measurements fall from a 2.034938 s median to 0.613341 s (−69.86%). The generated source shrinks from 7,735,845 to 7,167,003 bytes (−568,842 bytes, −7.35%). Both series use CPython 3.14.0 on the same Mac.

A fictitious N=10 book compiled with LuaHBTeX 1.24.0 into a 22-page tagged A4 PDF. `pypdf` found 452 named destinations, including 204 `target-*` labels using the expected alphabet, and 342 link annotations with no missing internal named destination. Physical pages 5, 6, 14, and 22 were rendered at 120 dpi and visually reviewed.

A separate N=100 comparison with 20 synthetic portraits was run once per variant on macOS 27.0 arm64, CPython 3.14.0, and LuaHBTeX 1.24.0:

| Measure | Base32 | URL-safe Base64 | Difference |
| --- | ---: | ---: | ---: |
| LaTeX generation | 0.205227 s | 0.061724 s | −69.92% |
| LaTeX source | 783,196 bytes | 725,713 bytes | −57,483 (−7.34%) |
| Full PDF compile | 90.437760 s | 84.805061 s | −5.632699 s (−6.23%) |
| PDF | 1,409,982 bytes | 1,405,934 bytes | −4,048 (−0.29%) |

The compile-time comparison has one run per variant and is indicative. The N=1,000 PDF was not recompiled; its earlier timeout remains unresolved. See the [raw data](validation-latex-url-safe-targets-20261001.json) and local preview at `../output/pdf/gramps-fancy-book-target-encoding-preview-20261001.pdf` (SHA-256 `feda0dcb2bd5ab550dff8592ba673d4271bff952757705a126bcf426c2017078`).

### Compact PDF destinations with BLAKE2s digests — 1 October 2026

Hyperref names keep the `target-` prefix and now encode a 96-bit BLAKE2s digest of each stable ID using unpadded URL-safe Base64. Names are deterministic, independent of pagination, and much shorter than a reversible encoding of the complete ID. For 17,768 targets, the theoretical probability of at least one collision is about 2 × 10⁻²¹.

On the N=1,000 branching fixture with 2,002 people and 200 synthetic portraits, source shrinks from 7,167,003 to 5,147,816 bytes (−28.17%). Median LaTeX generation rises from 0.612325 to 0.640712 s (+0.028387 s, +4.64%), a small cost compared with PDF compilation. Each variant has three repetitions on macOS 27 arm64 and CPython 3.14.0; the Base64 reference was replayed in the same environment using the previous encoder.

On the N=100 fixture with 20 portraits, one full compile per variant falls from 84.805061 to 68.898323 s (−15.906738 s, −18.76%). Source shrinks from 725,713 to 521,949 bytes (−28.08%). The candidate PDF is 1,455,375 bytes, 49,441 bytes (+3.52%) larger than the reference. Each compile time is a single indicative run.

A synthetic N=10 preview compiled with LuaHBTeX 1.24.0 is a 23-page tagged A4 PDF. `pypdf` found 455 named destinations, including 206 targets with the expected name format, 342 link annotations, and no missing internal destination. Physical pages 1, 6, 7, 11, 20, and 23 were rendered at 120 dpi and reviewed. See the [detailed measurements](validation-latex-short-targets-20261001.json) and [PDF preview](../output/pdf/gramps-fancy-book-short-target-digest-preview-20261001.pdf), SHA-256 `3757bc729a94a5c885fb26a2581417c4fe009148156b7978ab65af71b5faf51b`.

The N=1,000 PDF was not recompiled; the previous timeout remains unresolved. The people, events, media, and citations in the preview are synthetic.

### Rejected experiment — indexed PDF destinations — 1 October 2026

A temporary prototype replaced target IDs with labels such as `target-0`, `target-1`, and so on. It sorted reversible Base64 seeds, then rewrote references in `\gfbpagelink`, `\hyperlink`, `\hypertarget`, and `\label`. This scheme depends on the complete target set: adding a target whose seed sorts before an existing one shifts that target's label. A review comment on PR #201 correctly noted that this violates the identity-derived anchor contract in [decision 001](decisions/001-data-contracts.md). The prototype was therefore removed; production destinations remain identity-derived using the 96-bit BLAKE2s digests from PR #200.

The prototype measurements remain useful for isolating the cost of short labels. For N=1,000, the LaTeX source shrinks from 7,167,003 bytes with direct Base64 labels to 4,532,920 bytes (−36.76%), and from 5,147,816 bytes with BLAKE2s to 4,532,920 (−11.95%). Three source-generation measurements have a 0.873835 s median, compared with 0.640712 s for BLAKE2s. A full prototype compilation succeeded in three passes of 261.899, 259.468, and 259.112 s, for 781.415 s total and a 13,215,543-byte PDF; this diagnostic run temporarily raised the limits to 420 s per pass and 900 s total. Production limits remain 120 s per pass and 180 s total, so the N=1,000 timeout is unresolved.

On N=100, one compile per variant took 68.629 s with sequential prototype labels and 68.898 s with BLAKE2s; the 0.39% difference is indicative. The prototype PDF shrank from 1,455,375 to 1,371,810 bytes (−5.74%). Its N=10 preview is a 23-page tagged A4 PDF; `pypdf` found 455 named destinations, 206 unique and dense numeric targets, and 342 link annotations, including 210 internal links, with no unresolved destination. This is a prototype artifact, not the current renderer output. See the [raw data](validation-latex-indexed-targets-20261001.json) and [prototype preview](../output/pdf/gramps-fancy-book-indexed-targets-preview-20261001.pdf), SHA-256 `60920f931695a1593259640acfd1b3c89378528d9a29f90ff64c423ba93c7aee`.

### Instrumented LuaLaTeX pass profile — N=1,000 — 1 October 2026

With production BLAKE2s destinations, one instrumented pass on the N=1,000 branching fixture completed in 274.902 s. The CPU checkpoints place about 118.174 s in the documentary appendix, 46.416 s in person profiles, 32.010 s in family connections, and 21.692 s in family notices. TeX ships pages asynchronously; these intervals between source markers identify the main costs but do not isolate every page-shipout cost. This profile predates the removal of unreferenced citation-call anchors described below. See the [raw checkpoints](validation-latex-n1000-section-profile-20261001.json).

### Removed unreferenced citation-call anchors — 1 October 2026

Each citation call in the appendix had its own PDF destination, but no PDF link targeted those destinations: the visible call label already links directly to the profile or family notice. The renderer no longer emits these unused anchors. Destinations that are actually linked remain identity-derived through BLAKE2s.

On N=1,000, removing 3,270 destinations shrinks the LaTeX source from 5,147,816 to 4,918,916 bytes (−4.45%); median generation falls from 0.640712 to 0.620243 s. On N=100, one compile per variant takes 67.994 s instead of 68.898 s (−1.31%, indicative), and the PDF shrinks from 1,455,375 to 1,437,997 bytes (−1.19%). The 169-page tagged preview retains 3,073 link annotations and has no unresolved internal destination. Physical pages 12, 29, 49, 99, and 163 were reviewed at 110 dpi; layout remains readable across family connections, notices, profiles, the appendix, and the index. The N=1,000 PDF was not recompiled after this change. See the [raw data](validation-latex-call-anchor-pruning-20261001.json) and [PDF preview](../output/pdf/gramps-fancy-book-no-unused-call-targets-preview-20261001.pdf), SHA-256 `74eb25edc8d9c3504585beef7172e49256d9b165fc6500684e544a5104465923`.

### Grouped citation appendix metadata — 1 October 2026

Citation source details, repositories, URLs, and media captions remain on separate readable rows, composed within one tagged paragraph per citation. Multiple calls still use a list, and links back to profiles or notices are unchanged.

On N=100, one candidate compile takes 63.967656 s, compared with 67.993585 s for the previous variant (−5.92%, one measured run per variant). The tagged A4 PDF shrinks from 169 to 165 pages and from 1,437,993 to 1,398,169 bytes (−2.77%). All 3,073 link annotations, including 1,861 internal links, remain; no named internal destination is unresolved, and the set of identity-derived `target-*` destinations is unchanged. Extracted text is identical after removing running headers and recalculated page references. Physical pages 99 (appendix) and 165 (index) were visually reviewed at 110 dpi with no observed clipping or overlap. The N=1,000 LaTeX source shrinks from 4,918,916 to 4,900,298 bytes (−0.38%); no final multipass N=1,000 PDF was produced, so its timeout remains to be qualified. See the [raw data](validation-latex-appendix-metadata-20261001.json) and [PDF preview](../output/pdf/gramps-fancy-book-appendix-metadata-compact-preview-20261001.pdf), SHA-256 `6c51b6cb0756faacd2bff70676af756b04f63a54d09ded006d5b7aa90c66ebbc`.

### Current profile after targeted reductions — one N=1,000 pass

A new instrumented pass on the current renderer completed with LuaHBTeX. CPU intervals between markers were 38.963 s for family connections, 21.979 s for notices, 46.727 s for profiles, 108.100 s for the appendix, and 21.048 s in the index through its 2,000-entry checkpoint. The previous profile, before both targeted reductions, recorded 118.174 s in the appendix; this 10.074 s decrease (−8.52%) combines the removal of unreferenced citation-call anchors and metadata paragraph grouping, so it does not isolate either change.

Direct wall-clock timing around the LuaLaTeX process measured 272.254 s for this pass. The diagnostic run had no timeout; this duration exceeds the production limits of 120 seconds per pass and 180 seconds overall. The section-marker intervals are CPU measurements and are not used for comparisons with those wall-clock limits. LuaLaTeX wrote a tagged A4 diagnostic PDF with 1,572 pages, but one pass does not converge references, so that file is not a final preview. No full multipass N=1,000 PDF was produced after these changes. See the [full checkpoints](validation-latex-n1000-current-profile-20261001.json).

### Citation paragraph consolidation — October 2, 2026

Each citation title and its metadata rows are now composed within one paragraph with visible line breaks. When no rendered media interrupts the entry, its single link back to a profile or notice shares that paragraph. Media reproductions keep their position, and multiple calls remain a list.

On N=100, the tagged A4 candidate PDF shrinks from 165 to 161 pages and from 1,398,169 to 1,362,256 bytes (−2.57%). All 303 entries and 579 calls remain; all 1,861 internal links, 1,475 identity-derived targets, and 317 distinct URI targets are present, with no unresolved internal destination. Extracted call-label text is identical after page references are normalized. Link annotations increase from 3,073 to 3,079, with six additional external annotations and the same URI target set. Physical pages 99, 100, 153, 154, 155, and 161 were reviewed at 110 dpi with no observed overlap or clipping. The PDF structure contains 12,215 elements, down from 13,339. One candidate compilation took 65.629 s versus 63.968 s for the reference; each variant was measured once using different Python versions, so this does not establish a compile-time gain or regression.

On N=1,000, the LaTeX source shrinks by 11,144 bytes (−0.23%). One diagnostic LuaHBTeX pass measures 101.872 CPU seconds in the appendix, compared with 108.100 s in the previous profile (−5.76%), and 262.122 wall seconds versus 272.254 s (−3.72%). These are single-run measurements on the same fixture, macOS, and compiler; the previous profile used CPython 3.14.0 and this run used CPython 3.12.14. The tagged diagnostic PDF shrinks from 1,572 to 1,535 pages and from 13,582,172 to 13,242,192 bytes, but references do not converge in one pass. Its wall time still exceeds the production limits of 120 seconds per pass and 180 seconds overall; the final multipass N=1,000 PDF remains to be produced. See the [raw data](validation-latex-citation-paragraphs-20261002.json).
