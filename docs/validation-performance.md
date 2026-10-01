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
