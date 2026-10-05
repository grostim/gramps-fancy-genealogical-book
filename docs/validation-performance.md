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

On N=100, the tagged A4 candidate PDF shrinks from 165 to 161 pages and from 1,398,169 to 1,362,256 bytes (−2.57%). All 303 entries and 579 calls remain; all 1,861 internal links, 1,475 identity-derived targets, and 317 distinct URI targets are present, with no unresolved internal destination. Extracted call-label text is identical after page references are normalized. Link annotations increase from 3,073 to 3,079, with six additional external annotations and the same URI target set. Physical pages 99, 100, 153, 154, 155, and 161 were reviewed at 110 dpi with no observed overlap or clipping. The PDF structure contains 12,215 elements, down from 13,339. One candidate compilation took 65.629 s versus 63.968 s for the reference; each variant was measured once using different Python versions, so it did not establish a compile-time change. The repeated comparison on a consistent environment below supersedes that timing estimate.

On N=1,000, the LaTeX source shrinks by 11,144 bytes (−0.23%). One diagnostic LuaHBTeX pass measures 101.872 CPU seconds in the appendix, compared with 108.100 s in the previous profile (−5.76%), and 262.122 wall seconds versus 272.254 s (−3.72%). These are single-run measurements on the same fixture, macOS, and compiler; the previous profile used CPython 3.14.0 and this run used CPython 3.12.14. The tagged diagnostic PDF shrinks from 1,572 to 1,535 pages and from 13,582,172 to 13,242,192 bytes, but references do not converge in one pass. Its wall time still exceeds the production limits of 120 seconds per pass and 180 seconds overall; the final multipass N=1,000 PDF remains to be produced. See the [raw data](validation-latex-citation-paragraphs-20261002.json).

### Repeated N=100 compilation after consolidation — October 2, 2026

The ungrouped reference variant (commit `c6d0480`) and the consolidated renderer (commit `11bc028`) were each compiled three times on the same machine, with the same branching fixture and benchmark tool. The six runs alternated reference, candidate, candidate, reference, reference, candidate. All six multipass compilations through the production helper succeeded. The environment was macOS 27.0 arm64, CPython 3.12.10, Mistune 3.3.4, Pillow 9.5.0, and LuaHBTeX 1.24.0 (TeX Live 2026).

| Measurement | Ungrouped — three values; median | Consolidated paragraphs — three values; median | Median change |
| --- | ---: | ---: | ---: |
| Full PDF compilation (s) | 65.344950; 66.342804; 66.120247 — **66.120247** | 63.398461; 63.673968; 63.491654 — **63.491654** | −3.98% |
| LaTeX source (bytes) | 496,971; 496,971; 496,971 — **496,971** | 495,847; 495,847; 495,847 — **495,847** | −0.23% |
| Final PDF (bytes) | 1,398,173; 1,398,173; 1,398,167 — **1,398,173** | 1,362,252; 1,362,253; 1,362,256 — **1,362,253** | −2.57% |
| Sampled temporary peak (bytes) | 3,274,166; 3,274,158; 3,274,166 — **3,274,166** | 3,238,060; 3,238,062; 3,238,064 — **3,238,062** | −1.10% |

The median compilation improves by 2.629 s on this fixture but remains slightly above the provisional 60-second budget. This repeat confirms the N=100 gain; it does not qualify N=1,000. The preceding diagnostic profile still took 262.122 s for one pass, and no final multipass PDF has been produced at that size. The temporary peak is sampled every 100 ms, so shorter peaks may be missed. Full reports for all six runs are in the [raw data](validation-latex-citation-paragraph-repeats-20261002.json).

### Consolidated LaTeX anchors — October 2, 2026

Each identity anchor now calls a LaTeX macro with its ID once. The macro expands to the previous `\hypertarget` and `\label` commands, keeping the same clickable destination and page reference key. On the N=1,000 branching source with 200 synthetic portraits, expanding all 14,498 macro calls in a comparison copy reproduces the reference source byte for byte. Generated source shrinks from 4,889,154 to 4,381,781 bytes (−10.38%).

Three complete N=100 compilations per variant, alternating in the same macOS 27 arm64, CPython 3.12.10, and LuaHBTeX 1.24.0 environment, all succeeded. Median duration moves from 63.431 to 63.317 s (−0.18%); this difference is too small to establish a time gain. N=100 source shrinks from 495,847 to 444,279 bytes (−10.40%), and the sampled temporary peak from 3,238,060 to 3,186,495 bytes (−1.59%); median PDF size is effectively unchanged (1,362,251 versus 1,362,254 bytes). The fixture used Pillow 9.5.0, below the declared optional minimum of 10. Both variants used that same version, and this measurement does not qualify media processing. It does not resolve the N=1,000 compilation timeout. See the [six reports and source comparison](validation-latex-anchor-macro-20261002.json).

### LaTeX URL source without repetition — October 2, 2026

The 909 URL renderings in the N=100 fixture now pass the host and suffix to `\bookurl` only once each. The macro reconstructs the full clickable URL and preserves the two visual line-breaking settings. The instrumented N=100 source shrinks by 34,208 bytes (444,452 to 410,244, −7.70%); N=1,000, with 9,009 calls, shrinks by 344,541 bytes (4,381,781 to 4,037,240, −7.86%). For every call in the corpus, the former full URL is exactly the concatenation of the two new arguments.

An N=100 multipass compile produces a tagged A4 PDF of 161 pages. Compared with the previous preview, extracted text and all 3,079 link targets are identical, including 1,218 URI annotations and 1,861 internal links; all 3,560 named destinations remain. PDF size moves from 1,362,256 to 1,362,254 bytes. One instrumented first pass took 20.507 s for the baseline and 20.751 s for the candidate, which does not establish a compile-time gain. N=1,000 still exceeds the production timeout and was not recompiled. The [PDF preview](../output/pdf/gramps-fancy-book-url-source-preview-20261002.pdf) uses only synthetic data; see the [raw data](validation-latex-url-source-20261002.json).

An isolated appendix profile also tried one visible `\nolinkurl` call and, for diagnosis only, omitting `\href`. The first variant did not improve the single pass (20.982 s versus 20.507 s). Omitting the link reduced it to 18.045 s, but removed the required clickable URLs. Neither prototype is shipped.

### Complete N=1,000 large-book compile — October 2, 2026

The synthetic branching N=1,000 fixture (2,002 people, 1,001 families, 3,003 events, 3,003 citations, and 200 synthetic 96 × 72 portraits) was rendered with the current source. The production LuaLaTeX helper was invoked directly with diagnostic limits of 600 seconds per pass and 1,800 seconds overall. Three passes completed in 253.537, 261.122, and 276.413 seconds, for 791.078 seconds (13 minutes 11 seconds) overall. The final tagged A4 PDF has 1,535 pages and is 13,103,813 bytes. Its final log contains no undefined references or margin overflow recognized by the helper. Its 31,271 link annotations comprise 19,210 internal links, all resolved among 34,883 named destinations, and 12,061 URI links.

The cover and physical pages 500, 1,000, and 1,535 were rendered at 900 pixels for targeted inspection, with no observed clipping or overlap. This does not review all 1,535 pages or exercise the Gramps GUI. The result demonstrates convergence at this size when the time limit permits it; the provisional 60-second performance target is still unmet. The **Allow extended PDF compilation (up to 30 minutes)** option retains the standard limit by default and applies the diagnostic limits only to PDF exports that select it. See the [raw record](validation-latex-n1000-extended-20261002.json) and [local preview](../output/pdf/gramps-fancy-book-n1000-extended-preview-20261002.pdf).

### Tighter documentary appendix spacing — October 5, 2026

The citation list is now composed inside a local group that adjusts `\@listi` before `\begin{itemize}`. The `\itemsep=2pt`, `\parsep=0pt`, `\topsep=2pt`, and `\partopsep=0pt` values therefore take effect when the list is initialized, without affecting other book lists.

On the branching N=100 fixture with media, three tagged candidate compiles converged in 62.057, 62.779, and 62.580 seconds (62.580-second median), compared with 62.269, 62.773, and 62.772 seconds (62.772-second median) for the reference. The median difference is −0.192 seconds (−0.31%), too small to establish a compile-time gain. LaTeX source grows by 225 bytes while the median PDF shrinks by 2,534 bytes (0.19%). The PDF falls from 133 to 130 pages, and the reviewed pages fit more citations in the same space.

The candidate remains tagged PDF 2.0, A4, and `en-US`. It contains all 303 citation entries and 909 visible URL strings; the 317 distinct URI destinations match the reference. All 1,762 internal links remain resolved. Both PDFs have 1,212 URI annotation rectangles that cover visible text, with identical per-destination counts; the candidate has eight additional empty 2 × 2 point rectangles after reflow. It has 3,529 named destinations (the reference’s three destinations `page.130` through `page.132` belong to pages removed by the compaction), 40 figures with alternative text, and no unresolved internal destination. Physical appendix pages 85, 105, and 124 were reviewed with no observed overlap or clipping; this is a three-page sample, not a review of the complete PDF. See the [measurements and audit](validation-latex-compact-appendix-20261005.json) and the [candidate PDF](../output/pdf/gramps-fancy-book-compact-annex-n100-20261005.pdf), SHA-256 `d342bafdea506aa6d51f3d14c0e4c435c29374cba547e483d4364a4c16b45710`.

### Diagnostic N=1,000 compile after appendix compaction — October 5, 2026

The synthetic branching N=1,000 fixture, with 2,002 people, 1,001 families, 3,003 events, 3,003 citations, and 200 synthetic 96 × 72 portraits, was recompiled from the current source after PR #258 merged. The production PDF helper converged using extended diagnostic limits of 600 seconds per pass and 1,800 seconds overall; this direct synthetic-model compile did not run through Gramps Desktop. Total wall time was 741.591 seconds for this single run. The report did not record the pass count or individual pass times.

The tagged A4 PDF 2.0 in `en-US` has 1,239 pages and is 12,620,918 bytes. It contains 34,587 named destinations and 29,427 link annotations: 17,341 internal links, all resolved, and 12,086 URI links to 3,125 distinct destinations. All 3,003 citation entries [1] through [3003] are present. All 400 figures have alternative text. The appendix spans physical pages 784–1181, and the person index spans pages 1182–1239. The [raw record](validation-latex-current-source-n1000-20261005.json) contains the PDF SHA-256.

The cover, one profile page, the start, middle, and end of the appendix, and the start and end of the person index (physical pages 1, 500, 784, 966, 1181, 1182, and 1239) were inspected; no clipping or overlap was observed in this sample. This is not a page-by-page review. Compared with the October 2 diagnostic (791.078 seconds, 1,535 pages, 13,103,813 bytes), this PDF is shorter and smaller; cumulative renderer changes between the runs mean the differences cannot be attributed to appendix compaction alone. The standard production limits (120 seconds per pass, 180 seconds overall) and provisional 60-second target are still exceeded. Extended compilation is required for this large PDF, so the N=1,000 production envelope is not qualified. The Gramps GUI path also remains to be validated.

### Single-pass LuaLaTeX profile of the current source — October 5, 2026

A direct LuaLaTeX pass was timed on the branching N=1,000 fixture with 200 synthetic portraits. `os.clock()` markers were inserted only into a temporary source copy before the seven main sections. The tagged A4, 1,239-page diagnostic pass took 245.200 wall seconds. Measured CPU intervals were 30.646 seconds for family connections, 21.237 for family notices, 45.900 for person profiles, 95.377 for the documentary appendix, and 20.005 for the person index. The appendix remains the longest section. These intervals include page layout and shipout between markers; tagpdf finalization after the last marker is not attributed to a section.

The October 1 profile measured 108.100 CPU seconds for the appendix. The difference cannot be attributed to one change: the source and settings have evolved, and a single-pass diagnostic PDF has unconverged references. This profile guides another page-margin reduction; it does not establish that production targets have been met. The standard 120-second per-pass and 180-second total limits remain exceeded. The [raw record](validation-latex-current-profile-n1000-20261005.json) documents the markers and limitations.

### Page margins reduced to 15 mm — October 5, 2026

Following feedback that the 20 mm page margins looked too large, the LaTeX source now uses 15 mm on each side. This increases the text measure from about 170 mm to 180 mm. The same branching N=1,000 book with 200 synthetic portraits was recompiled through the production helper with extended diagnostic limits: 738.982 seconds, producing a tagged A4 PDF 2.0 with 1,214 pages, 12,587,394 bytes, and `en-US` language.

Compared with the current 20 mm PDF, this version has 25 fewer pages and is 33,524 bytes smaller. One run per variant does not establish a time gain: the measured durations were 741.591 and 738.982 seconds. All 3,003 citations remain present, all 17,341 internal links resolve, the 12,072 URI annotations still cover the same 3,125 distinct destinations, and all 400 figures have alternative text. The appendix spans physical pages 776–1159; the person index spans pages 1160–1214.

The cover, one profile, the start, middle, and end of the appendix, and the start and end of the index (pages 1, 500, 776, 967, 1159, 1160, and 1214) were reviewed with no observed clipping or overlap. This is not a page-by-page review. Extended compilation remains necessary: the duration still exceeds the standard 120-second per-pass and 180-second total limits, as well as the provisional 60-second target. See the [raw record and comparisons](validation-latex-margins15-n1000-20261005.json).

### PDF compression trials at N=100 — October 5, 2026

Three baseline compiles of the branching N=100 case with 20 synthetic portraits and current 15 mm margins have medians of 62.622 seconds and 1,312,082 bytes. Three compiles with `\pdfvariable compresslevel=1` take 62.853 seconds and produce 1,498,415 bytes: 0.37% slower and 14.2% larger. One run at level 0 takes 62.519 seconds but produces a 6,463,651-byte PDF, 4.93 times the baseline size; the single run cannot establish a timing result. Three runs with `\pdfvariable objcompresslevel=1` take 63.203 seconds and produce 1,312,077 bytes, with no measurable speed gain.

The PDFs remain tagged and have 127 pages. No alternate compression setting is retained; LaTeX composition remains the focus for further profiling. These trials cover N=100 on one machine. See the [raw measurements](validation-luatex-compression-n100-20261005.json) for timings, sizes, and limits.

### Rejected trial — LuaLaTeX draft-mode first pass — October 5, 2026

A temporary variant ran the first pass of an extended PDF build with `-draftmode`, then ran later passes normally. The idea was to reduce the cost of writing the intermediate PDF. On the same branching N=1,000 case with 200 synthetic portraits, the variant took 741.368 seconds versus 738.982 seconds for the reference: 2.386 seconds (0.32%) slower in these single runs. Both outputs have 1,214 tagged A4 pages, are 12,587,394 bytes, and produce identical extracted text. Their recorded structure also matches: 34,562 named destinations, 29,413 link annotations including 17,341 internal links and 12,072 URI links, with no missing internal targets.

The profiled N=100 compile with media took 62.703 seconds overall. Its draft pass took 20.776 seconds, followed by two normal passes at 20.900 and 20.909 seconds; the last two produced the same auxiliary-file fingerprint. The recent reference median is 62.622 seconds. The first auxiliary file has a different fingerprint, so it cannot replace the normal passes needed to stabilize references. No gain was established and the temporary change was removed. Standard production limits are still exceeded at N=1,000. One candidate large build and one N=100 profile do not provide a statistical timing comparison. See the [raw record](validation-latex-draft-first-pass-n1000-20261005.json).

### tagpdf finalization at N=1,000 — October 5, 2026

The timing hooks built into tagpdf were enabled only in a temporary copy of the current source with 15 mm margins. On the branching N=1,000 book with 200 portraits, one direct LuaLaTeX pass took 243.149 wall seconds and produced a 987-page tagged diagnostic PDF. This one-pass file has unconverged references and is not the final book.

Finalization took 21.167 CPU seconds: 17.9 seconds to write structure elements (`StructElems`), 2.92 seconds for the `IDTree`, and 0.342 seconds for the `ParentTree`; each remaining phase took less than 0.004 seconds. Writing structure elements accounts for 84.57% of measured finalization. All finalization is about 8.7% of this pass's wall time; even an unrealistic removal of all of it would not explain the gap to the 120-second per-pass limit. The [official tagpdf source](https://github.com/latex3/tagpdf/blob/main/tagpdf-tree.dtx) itself describes writing structure elements as slow.

Tagging remains enabled. This one run does not establish a statistical trend or qualify the production budget. Earlier section markers attributed 95.377 CPU seconds to the appendix on an earlier source; profiling should continue on the dominant book sections instead of focusing only on finalization. Detailed timings are in the [raw record](validation-tagpdf-finalization-n1000-20261005.json).

### Documentary appendix profile by citation group — N=1,000 — October 5, 2026

The current 15 mm source was instrumented in a temporary copy with markers every 250 citation entries. One direct pass produced a tagged 987-page diagnostic PDF in 244.663 wall seconds; references did not converge. The twelve full groups of 250 citations total 93.835 CPU seconds, averaging 7.820 seconds per group. Their durations range from 6.752 to 8.893 seconds; the final three citations take 0.205 seconds.

The intervals include composition and page shipout; they do not separate the cost of citation fields, links, images, or structure elements. No single block dominates, so the workload appears distributed across repeated entry processing. This is one diagnostic pass on one machine and does not qualify the final converged PDF. No production change follows yet. Raw timings are in the [group profile](validation-latex-appendix-groups-n1000-20261005.json).

### Untagged intermediate first pass, tagged final PDF — October 5, 2026

The renderer now runs only the first LuaLaTeX pass with `tagging=off`, then restores the original source before subsequent passes. References still use the usual convergence check; the installed PDF is produced by a tagged pass. Three sizes were compared with one compile per variant in fresh directories. Both variants take three passes for each fixture: N=1 drops from 5.128 to 4.862 seconds (−5.19%), N=10 from 10.193 to 9.047 seconds (−11.24%), and N=100 with 20 media items from 61.829 to 51.621 seconds (−16.51%). Every candidate PDF is tagged and has the same page count; the N=10 and N=100 files also match their reference sizes.

At N=100, extracted-text, structure, named-destination, and URI-link hashes match between variants, with no layout warning. One paired run per size on one machine is not enough for a statistical comparison. Three new N=100 compiles through the production helper subsequently confirmed the current timing; see the section below. N=1,000 has also been rebuilt with this optimization; that measurement is detailed later. The [initial paired record](validation-latex-untagged-first-pass-20261005.json) preserves the comparative measurements.

### Qualification after optimization — N=1,000 — October 5, 2026

The branching N=1,000 book, with 200 portraits and 15 mm margins, was rebuilt through the production helper with extended limits (600 seconds per pass, 1,800 seconds total). It took 576.678 seconds, compared with 738.982 seconds in the earlier run: 162.304 seconds faster (−21.96%) across these two single runs. Both PDFs are tagged, have 1,214 pages, and are 12,587,394 bytes. Extracted-text, structure-tree, named-destination, and URL-annotation hashes match.

This confirms a gain without changing the checked outputs, but the duration still exceeds the standard 180-second total limit. One compile per variant is not a statistical comparison; the N=1,000 production budget is therefore still unmet. The [raw record](validation-latex-untagged-first-pass-n1000-20261005.json) contains hashes and limits.

### Repeated builds with the current renderer — N=100 — October 5, 2026

Three branching N=100 builds with 20 portraits at 96 × 72 pixels ran through the production helper on commit `c4f7b15`. They took 51.175, 51.643, and 51.729 seconds; the median is 51.643 seconds. All three are below the provisional 60-second target. Generated LaTeX source is identical across runs (410,393 bytes), and the PDFs are 1,312,074 or 1,312,083 bytes. This current series confirms the N=100 target on this machine; it is not a variant comparison and does not qualify the N=1,000 book for production. The [raw data](validation-latex-untagged-first-pass-n100-20261005.json) records every run.

### Defer hyperlinks on the first pass — N=100 — October 5, 2026

A temporary variant adds hyperref's `draft` option alongside `tagging=off` on the first pass only. The [official hyperref manual](https://tug.ctan.org/macros/latex/contrib/hyperref/doc/hyperref-doc.pdf) says `draft` turns off hypertext features; the original source is restored before later passes. Across three builds per variant, the median drops from 51.643 to 45.109 seconds (−6.534 seconds, −12.65%). All three candidate PDFs are tagged and have 127 pages; extracted-text, structure-tree, destination, and URL hashes match the reference. Binary file sizes vary by a few bytes between some runs, with no difference in the compared outputs.

This N=100 result is promising. The follow-up N=1,000 measurement is recorded below; it is one run and the production budget remains unmet. The [raw measurements](validation-latex-hyperref-draft-first-pass-n100-20261005.json) detail both N=100 series.

### Defer hyperlinks on the first pass — N=1,000 qualification — October 5, 2026

The same branching N=1,000 case with 15 mm margins and 200 synthetic portraits was rebuilt through the production helper after PR #272 merged. With extended diagnostic limits (600 seconds per pass, 1,800 seconds total), the build took 514.058 seconds. The previous run with `tagging=off` on the first pass took 576.678 seconds, a reduction of 62.620 seconds (−10.86%). Compared with the 15 mm baseline PDF (738.982 seconds), the cumulative reduction is 224.924 seconds (−30.44%). Each value comes from one compile.

The final PDF is tagged, has 1,214 pages, and is 12,587,399 bytes—five bytes larger than either previous version. Extracted-text, structure-tree, destination, and URL hashes match across all three PDFs. Their bytes are not identical. The run still requires extended limits and exceeds the standard 180-second total budget; one measurement per variant does not establish a statistical trend. This run did not include a full visual review. The [raw record](validation-latex-hyperref-draft-first-pass-n1000-20261005.json) contains hashes, configuration, and limits.

### Rejected trial — factor shared source fields — N=100 — October 5, 2026

A variant replaced repeated source-author and publication-information strings in the appendix with a shared LaTeX macro. On the branching N=100 fixture with media, generated source fell from 410,393 to 409,857 bytes (−536). The tagged 127-page PDF took 45.042 seconds, 0.067 seconds (0.15%) below the previous 45.109-second median. The run is 0.044 seconds faster than the best of the three baseline runs, but its difference from the median is smaller than the 0.132-second width of that series; one measurement does not establish a speedup.

Extracted-text, structure-tree, named-destination, and URL hashes match the reference. The variant is still rejected: one run does not establish a measurable speedup, and no production change is retained. N=1,000 was not rebuilt and no full visual review was performed. See the [raw record](validation-latex-shared-citation-fields-n100-20261005.json).

### Rejected trial — leave the second pass untagged — N=100 — October 5, 2026

A second variant keeps tagging disabled for the first two passes; `hyperref` is in `draft` mode only on the first pass and is active again on the second. A clean-source rerun using the 410,393-byte production LaTeX source converged in four passes and took 54.800 seconds, 9.691 seconds (21.48%) slower than the 45.109-second baseline median. The initial run took 54.689 seconds. Both candidate timings exceed the three baseline runs (45.086–45.218 seconds).

Extracted-text, structure-tree, destination, and URL hashes match the reference. The trial is rejected because this pass sequence requires a fourth pass and does not speed up the export. Its temporary code was removed. No full visual review or N=1,000 compile was performed for this variant. See the [raw record](validation-latex-defer-tagging-second-pass-n100-20261005.json).

### Repeat optimized build — N=1,000 — October 5, 2026

A third full compile with the current renderer took 534.127 seconds. Across the three runs (514.058, 509.888, and 534.127 seconds), the measured median is 514.058 seconds and the range is 24.239 seconds (4.72% of the median). All compiles use extended diagnostic limits and remain well above the standard 180-second total limit.

All three PDFs are tagged PDF 2.0 and have 1,214 pages. They are 12,587,399, 12,587,395, and 12,587,393 bytes. Extracted-text, structure-tree, destination, and URL hashes match exactly. No full visual review was performed for the third run. See the [raw measurements](validation-latex-hyperref-draft-first-pass-n1000-repeats-20261005.json).

### Rejected URL authority macro — N=100 — October 5, 2026

A temporary rendered-source transform replaces the authority `https://archives.example.test` in 909 `bookurl` commands with one LaTeX macro. This reduces the source from 410,393 to 394,997 bytes (−3.75%). Three candidate compiles take 45.245, 45.180, and 49.784 seconds; their median is 45.245 seconds, 0.136 seconds (0.30%) slower than the 45.109-second reference median. Extracted text, structure, destinations, and URLs match in all three candidate PDFs. The change is rejected because the smaller source does not produce a measurable speedup. No production code was retained. See the [raw measurements](validation-latex-url-host-macros-n100-20261005.json).

### Link-generation cost diagnostic — N=100 — October 5, 2026

A diagnostic run keeps tagging active but uses `hyperref` draft mode in all three passes. It takes 33.836 seconds, compared with the 45.109-second production median (−24.99%). The 127-page PDF remains tagged and has the same extracted text, but it contains no link annotations or named destinations. This measures link generation as a significant part of the work on this fixture, while confirming that disabling links is not a valid production change. The next investigation will look for a cheaper way to retain all annotations and Link structure elements. See the [raw profile](validation-latex-hyperref-all-draft-n100-20261005.json).

### Rejected low-level internal-link wrapper — N=100 — October 5, 2026

A temporary `gfbpagelink` macro calls hyperref's low-level link-start and link-end commands directly for the renderer's safe internal target names. Three candidate compiles take 44.980, 45.434, and 46.042 seconds; the 45.434-second median is 0.325 seconds (0.72%) slower than the 45.109-second reference median. All three candidate PDFs retain the exact extracted-text, structure, destination, and URL hashes, with 2,978 link annotations and 3,526 named destinations each. The wrapper is rejected because it does not speed up compilation. See the [raw measurements](validation-latex-hyperref-link-wrapper-n100-20261005.json).

### Diagnostic without tagpdf link hooks — N=100 — October 5, 2026

Three production-helper compiles temporarily remove tagpdf's before/after hooks for GoTo and URI annotations while leaving `hyperref`, ordinary tagging, and link annotation generation active. The median is 39.473 seconds (38.974–40.092), 5.636 seconds (12.49%) below the 45.109-second production median. Each 127-page tagged PDF retains all 2,978 link annotations, 3,526 named destinations, the same destination names and URI targets, and the same extracted-text hash. The structure tree, however, loses all 2,671 `Link` roles.

The result separates two likely sources of cost: the no-hook median is 5.637 seconds above the single 33.836-second all-draft run, close to the 5.636-second gap from production to no-hook. This suggests annotation creation and Link-structure association each account for about 5.6 seconds on this fixture. The all-draft comparison is a single run, so this is an indicative breakdown rather than a controlled additive measurement. The no-hook variant is rejected because its links are missing from the accessibility structure. No production source change was retained. See the [raw measurements](validation-latex-hyperref-link-hooks-n100-20261005.json).

### Separate GoTo and URI tagging hooks — N=100 — October 5, 2026

Three serial compiles per variant remove tagpdf's hooks for one PDF link action while keeping the other hook pair active. Removing GoTo hooks gives a 41.427-second median (40.933–41.437), 3.682 seconds (8.16%) below production. Removing URI hooks gives 42.877 seconds (42.722–43.061), 2.232 seconds (4.95%) below production. Every candidate retains all 2,978 link annotations, 3,526 named destinations, identical destination names and URI targets, and the exact extracted-text hash.

The GoTo-disabled structure keeps 909 `Link` roles for the URI links; the URI-disabled structure keeps 1,762 `Link` roles for internal links. Each variant therefore drops accessible structure for the action type whose hooks were removed. GoTo hook work has the larger measured effect on this fixture, but neither variant is suitable for production. The next profile will focus on preserving the internal link roles while reducing their structure cost. See the [raw measurements](validation-latex-hyperref-link-hook-types-n100-20261005.json).

### Inline tagpdf link socket operations — N=100 — October 5, 2026

A temporary source replaces the URI and GoTo hook calls to `UseTaggingSocket` with the equivalent operations from tagpdf's current default kernel plugs. Three compiles take 43.750, 44.710, and 44.732 seconds; the median is 44.710 seconds, only 0.399 seconds (0.88%) below the 45.109-second reference. The candidate spread is 0.982 seconds, so the difference does not establish a measurable speedup.

All three PDFs retain the exact structure and text hashes, 2,671 `Link` roles, 2,978 link annotations, and 3,526 named destinations. The trial is rejected because it does not demonstrate a gain and would duplicate tagpdf's internal socket implementation in generated output. No production code was retained. See the [raw measurements](validation-latex-hyperref-link-socket-inline-n100-20261005.json).

### Rejected removal of the `linksplit` callback — N=100 — October 5, 2026

Three temporary compiles remove LuaTeX's `linksplit` callback and restore the URI and GoTo hooks to retain tagging operations. They take 44.251, 44.145, and 45.087 seconds; the 44.251-second median is 0.858 seconds (1.90%) below the 45.109-second reference. The 0.942-second candidate spread is larger than the median difference, so the run does not establish a compile-time gain. Each tagged PDF retains 127 pages, 2,978 annotations (1,762 GoTo and 1,216 URI), 3,526 destinations, the same URI targets, and identical extracted text.

Direct PDF inspection finds 2,978 Link annotations but only 2,671 distinct `StructParent` values in each candidate. Across each PDF, 303 keys are reused by 307 additional annotation fragments; the ParentTree has 2,798 total entries instead of 3,105 in the reference, including page entries. Only 2,671 `OBJR` references point back to their corresponding annotations, versus all 2,978 in production. Reject this path: the extra fragments are not individually represented in the accessibility tree. No production change was retained. N=1,000, full visual review, and screen-reader review remain unqualified. See the [raw measurements and ParentTree audit](validation-latex-hyperref-no-split-n100-20261005.json).
