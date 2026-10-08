# Performance measurement — L8.3

Repeated measurements on 2026-09-29 with macOS 27.0 arm64 and CPython 3.14.0, Gramps 6.0.8 and its embedded Python 3.13.2, LuaHBTeX 1.24.0 (TeX Live 2026), Pillow 12.3.0 and Mistune 3.3.4.

## Method and synthetic data sets

Run from the repository root in a Python environment with the project, media extra, and development tools installed (pip install -e ".[dev,media]"); LuaLaTeX must be available on PATH:

    PYTHONPATH=src python scripts/benchmark_book.py --shape both --descendant-couples 10 100 1000 --with-media --compile-pdf-for 100 --repeat 3

    PYTHONPATH=src python scripts/benchmark_gramps_extraction.py --gramps /Applications/Gramps.app/Contents/MacOS/Gramps --scenario branching ancestors multiple-unions pedigree-collapse media --descendant-couples 10 100 1000 --repeat 3 --output docs/validation-gramps-scenarios-20260929.json

In the first benchmark, each size runs three times; the reported durations and memory peaks are medians. JSON, HTML and LaTeX sizes are stable across those repetitions. Gramps imports are measured separately, and regenerated internal handles cause small changes in JSON size.

Two structures are compared:

- Wide data set: one central couple with N children and their partners. Every person gets a profile; there are no events or media. This preserves the original reference case, but does not represent a deep tree.
- Branching data set: N descendant unions distributed across branches, with at most two children per family. Each person has a birth event and each family has a union event. Every event has a citation; sources are shared across 25 citations; one repository and multiple places are included. Publishable notes appear about once per 12 people and once per 10 families. A synthetic PNG portrait with a crop region appears about once per 10 people.

The first script measures model construction, derivative preparation, JSON serialization, both renderers and the HTML ZIP archive. It also compiles a PDF for the small branching case. `tracemalloc` measures the Python heap, but not native allocations or child processes; during PDF compilation the script separately samples the LuaTeX process RSS every 100 ms with `psutil`. This can miss shorter peaks and is distinct from the Python heap peak. Media consists of deterministic pseudo-random images, not real portraits.

PDF benchmarks use the renderer's standard 120-second per-pass and 180-second total limits by default. For a large fixture, pass `--extended-pdf-compilation` with `--compile-pdf-for`; it selects the renderer's 600-second per-pass and 1,800-second total limits. The JSON report records whether extended compilation was selected.

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

A synthetic N=10 preview compiled with LuaHBTeX 1.24.0 is a 23-page tagged A4 PDF. `pypdf` found 455 named destinations, including 206 targets with the expected name format, 342 link annotations, and no missing internal destination. Physical pages 1, 6, 7, 11, 20, and 23 were rendered at 120 dpi and reviewed. See the [detailed measurements](validation-latex-short-targets-20261001.json) and local PDF preview (no longer in this checkout), SHA-256 `3757bc729a94a5c885fb26a2581417c4fe009148156b7978ab65af71b5faf51b`.

The N=1,000 PDF was not recompiled; the previous timeout remains unresolved. The people, events, media, and citations in the preview are synthetic.

### Rejected experiment — indexed PDF destinations — 1 October 2026

A temporary prototype replaced target IDs with labels such as `target-0`, `target-1`, and so on. It sorted reversible Base64 seeds, then rewrote references in `\gfbpagelink`, `\hyperlink`, `\hypertarget`, and `\label`. This scheme depends on the complete target set: adding a target whose seed sorts before an existing one shifts that target's label. A review comment on PR #201 correctly noted that this violates the identity-derived anchor contract in [decision 001](decisions/001-data-contracts.md). The prototype was therefore removed; production destinations remain identity-derived using the 96-bit BLAKE2s digests from PR #200.

The prototype measurements remain useful for isolating the cost of short labels. For N=1,000, the LaTeX source shrinks from 7,167,003 bytes with direct Base64 labels to 4,532,920 bytes (−36.76%), and from 5,147,816 bytes with BLAKE2s to 4,532,920 (−11.95%). Three source-generation measurements have a 0.873835 s median, compared with 0.640712 s for BLAKE2s. A full prototype compilation succeeded in three passes of 261.899, 259.468, and 259.112 s, for 781.415 s total and a 13,215,543-byte PDF; this diagnostic run temporarily raised the limits to 420 s per pass and 900 s total. Production limits remain 120 s per pass and 180 s total, so the N=1,000 timeout is unresolved.

On N=100, one compile per variant took 68.629 s with sequential prototype labels and 68.898 s with BLAKE2s; the 0.39% difference is indicative. The prototype PDF shrank from 1,455,375 to 1,371,810 bytes (−5.74%). Its N=10 preview is a 23-page tagged A4 PDF; `pypdf` found 455 named destinations, 206 unique and dense numeric targets, and 342 link annotations, including 210 internal links, with no unresolved destination. This is a prototype artifact, not the current renderer output. See the [raw data](validation-latex-indexed-targets-20261001.json) and local prototype preview (no longer in this checkout), SHA-256 `60920f931695a1593259640acfd1b3c89378528d9a29f90ff64c423ba93c7aee`.

### Instrumented LuaLaTeX pass profile — N=1,000 — 1 October 2026

With production BLAKE2s destinations, one instrumented pass on the N=1,000 branching fixture completed in 274.902 s. The CPU checkpoints place about 118.174 s in the documentary appendix, 46.416 s in person profiles, 32.010 s in family connections, and 21.692 s in family notices. TeX ships pages asynchronously; these intervals between source markers identify the main costs but do not isolate every page-shipout cost. This profile predates the removal of unreferenced citation-call anchors described below. See the [raw checkpoints](validation-latex-n1000-section-profile-20261001.json).

### Removed unreferenced citation-call anchors — 1 October 2026

Each citation call in the appendix had its own PDF destination, but no PDF link targeted those destinations: the visible call label already links directly to the profile or family notice. The renderer no longer emits these unused anchors. Destinations that are actually linked remain identity-derived through BLAKE2s.

On N=1,000, removing 3,270 destinations shrinks the LaTeX source from 5,147,816 to 4,918,916 bytes (−4.45%); median generation falls from 0.640712 to 0.620243 s. On N=100, one compile per variant takes 67.994 s instead of 68.898 s (−1.31%, indicative), and the PDF shrinks from 1,455,375 to 1,437,997 bytes (−1.19%). The 169-page tagged preview retains 3,073 link annotations and has no unresolved internal destination. Physical pages 12, 29, 49, 99, and 163 were reviewed at 110 dpi; layout remains readable across family connections, notices, profiles, the appendix, and the index. The N=1,000 PDF was not recompiled after this change. See the [raw data](validation-latex-call-anchor-pruning-20261001.json) and local PDF preview (no longer in this checkout), SHA-256 `74eb25edc8d9c3504585beef7172e49256d9b165fc6500684e544a5104465923`.

### Grouped citation appendix metadata — 1 October 2026

Citation source details, repositories, URLs, and media captions remain on separate readable rows, composed within one tagged paragraph per citation. Multiple calls still use a list, and links back to profiles or notices are unchanged.

On N=100, one candidate compile takes 63.967656 s, compared with 67.993585 s for the previous variant (−5.92%, one measured run per variant). The tagged A4 PDF shrinks from 169 to 165 pages and from 1,437,993 to 1,398,169 bytes (−2.77%). All 3,073 link annotations, including 1,861 internal links, remain; no named internal destination is unresolved, and the set of identity-derived `target-*` destinations is unchanged. Extracted text is identical after removing running headers and recalculated page references. Physical pages 99 (appendix) and 165 (index) were visually reviewed at 110 dpi with no observed clipping or overlap. The N=1,000 LaTeX source shrinks from 4,918,916 to 4,900,298 bytes (−0.38%); no final multipass N=1,000 PDF was produced, so its timeout remains to be qualified. See the [raw data](validation-latex-appendix-metadata-20261001.json) and local PDF preview (no longer in this checkout), SHA-256 `6c51b6cb0756faacd2bff70676af756b04f63a54d09ded006d5b7aa90c66ebbc`.

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

An N=100 multipass compile produces a tagged A4 PDF of 161 pages. Compared with the previous preview, extracted text and all 3,079 link targets are identical, including 1,218 URI annotations and 1,861 internal links; all 3,560 named destinations remain. PDF size moves from 1,362,256 to 1,362,254 bytes. One instrumented first pass took 20.507 s for the baseline and 20.751 s for the candidate, which does not establish a compile-time gain. N=1,000 still exceeds the production timeout and was not recompiled. The local PDF preview was generated only with synthetic data and is no longer present in this checkout; see the [raw data](validation-latex-url-source-20261002.json).

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

### Link cost profile and fixed-arity socket dispatch trial — N=100 — October 5, 2026

One instrumented current-renderer profile counts 2,959 Lua `linksplit` calls and about 0.018 seconds of aggregate Lua CPU. The TeX macro that inserts each `OBJR` is called 2,959 times; its instrumented interval is about 0.483 seconds, including marker overhead, so treat it as an upper bound. The 127-page PDF retains 2,978 annotations, 2,978 link ParentTree/OBJR mappings, and 3,526 named destinations.

Three candidates then replace `\UseTaggingSocket` with `\tag_socket_use:nn` in the URI/GoTo hooks. Their median is 44.709 seconds (43.504–44.714), 0.400 seconds (0.89%) below the 45.109-second reference median. The candidate spread is 1.210 seconds, larger than the difference, so no speedup is established. All three PDFs retain the 2,978 annotations, reciprocal ParentTree/OBJR references, 2,671 Link roles, text, URI targets, and destinations. The source grows by 611 bytes. Reject the trial; no production change was retained. The [tagpdf guide](https://github.com/latex3/tagpdf/blob/main/tagpdf-user.dtx) describes this lower-level socket API as slightly more efficient, but this fixture shows no measurable gain. See the [raw record](validation-latex-hyperref-link-socket-dispatch-n100-20261005.json).

### LaTeX source generation time — full N=1,000 book — October 5, 2026

The current synthetic benchmark generated the branching N=1,000 book three times, with 2,002 people, 3,003 citations, and 200 portraits. Generating the complete 4,037,562-byte LaTeX source took 0.982, 0.980, and 0.980 seconds; the median was 0.980 seconds. PDF compilation was not run in this measurement.

This is about 0.19% of the recent optimized N=1,000 PDF compilation median (514.058 seconds), an indicative comparison across runs. It covers the whole book rather than only the appendix, so the Python cost for the appendix itself is below one second. Python-side optimization cannot account for a substantial reduction in PDF time. Further performance work belongs in LuaLaTeX composition and page output. The [raw record](validation-latex-generation-n1000-20261005.json) gives the runs and limitations.

### URL line-break profile and correction — N=100 — October 5, 2026

A temporary source for the branching N=100 book (202 people, 101 families, 303 events and citations, 27 notes, no media) was instrumented around page links, anchors, and URLs. Across three direct passes, 909 bookurl outputs accumulate 1.604–1.626 seconds of CPU time (1.614-second median); 1,743 page links take 0.038 seconds and 1,455 anchors take 0.015 seconds. A candidate replaces two nolinkurl calls with one call around the complete visible address while retaining the href target.

The candidate records a 1.582-second median CPU interval for the 909 bookurl outputs (1.582–1.597 seconds), 1.90% below the instrumented two-call median. This does not establish an end-to-end compile-time gain. To check annotations without measurement markers, each uninstrumented PDF was then compiled directly in three passes until references converged. Both tagged A4 PDFs have 105 pages and retain 2,978 Link annotations, 1,220 URI annotations with the same ordered target set, 2,667 Link roles, 2,978 OBJR references, and 3,083 ParentTree keys. After removing running headers and extraction whitespace, their text hashes match. The candidate PDF is 975,032 bytes versus 975,450 for the baseline.

A 140-dpi visual review of pages 67 and 70 shows the candidate breaking URLs after slash instead of splitting “register” between “reg” and “ister,” including when the break falls at a page boundary. A separate fixture confirms the exact target and visible text for a URL containing %2F, query parameters, and the #record fragment. The renderer change is retained for URL readability, with no performance claim. The [raw record](validation-latex-macro-profile-n100-20261005.json) distinguishes the instrumented timing runs from the uninstrumented PDFs and documents their limits.

### Hyperlink macro profile — N=1,000 — October 6, 2026

A temporary copy instruments `\hyperlink` and `\href` calls on the branching N=1,000 fixture with 200 portraits, keeping tagging and links active. One direct pass takes 245.080 seconds wall time and 243.830 seconds of user CPU. The 17,334 `\hyperlink` calls accumulate 52.063 CPU seconds; the 9,009 `\href` calls accumulate 27.386 seconds. Their combined 79.449 seconds account for 32.58% of measured user CPU. Timed intervals surround the macros and TeX processing; marker overhead was not quantified, and this does not separate hyperref work from tagpdf work.

The tagged diagnostic PDF has 1,214 A4 pages, 34,562 destinations, 17,341 GoTo annotations, 12,072 URI annotations, 26,350 Link roles, 29,413 OBJR associations, and 400 figures. The seven additional GoTo annotations, Link roles, and OBJR nodes versus the factorial profile come from seven table-of-contents entries read from an already populated `.toc` file. The reference PDF was the first pass, with an empty table of contents and unresolved page references; extracted-text hashes differ, and the instrumented log still says labels have changed. These files are therefore not a matched semantic or convergence comparison.

This profile directs the next diagnostic toward internal and URI link paths; it establishes neither a speedup nor a reason to change the renderer. Repeat with matched `.aux`/`.toc` states and quantify marker overhead before adopting an optimization. See the [raw record](validation-latex-link-macro-profile-n1000-20261006.json) and the [local diagnostic PDF](../tmp/lualatex-link-macro-profile-n1000-20261006/book.pdf).

### Matched hyperlink macro instrumentation check — N=100 — October 6, 2026

Three pairs of direct N=100 passes each start from identical source with no `.aux`, `.toc`, or `.out` files. The order alternates reference and instrumentation. Median wall times are 20.690 seconds without markers and 20.620 seconds with instrumentation (−0.070 seconds, or −0.34%). The reference range is 0.860 seconds; paired differences range from −0.080 to +0.630 seconds. This series measures neither compile-time overhead nor a speedup.

Instrumented intervals have medians of 5.564 seconds across 1,751 `\hyperlink` calls and 2.690 seconds across 909 `\href` calls. All six tagged 105-page PDFs have identical 3,484 destinations, 1,751 GoTo links, 1,220 URI links, 2,660 Link roles, 2,971 OBJR/`StructParent` associations, and extracted text across reference and candidate. The PDFs differ at the byte level; no performance benefit is established. These first passes have unconverged page references, and the check does not isolate marker cost or distinguish hyperref from tagpdf work.

This comparison finds no semantic change from instrumentation in this N=100 case. It does not qualify the N=1,000 profile or a converged production export. See the [raw record](validation-latex-link-macro-matched-n100-20261006.json).

### Matched hyperlink macro instrumentation check — N=1,000 — October 6, 2026

Three pairs of direct passes each start from identical populated `.aux` and `.toc` files; `.out` is absent. The order is reference/instrumented, instrumented/reference, then reference/instrumented. Median wall times are 245.227 seconds for the reference and 245.818 seconds with markers, a 0.591-second (0.24%) increase. Paired differences are +1.658, +0.701, and +0.052 seconds. The 1.402-second reference range exceeds the difference between medians; these three pairs do not establish measurable overhead.

Median instrumented intervals are 52.142 seconds across 17,334 `\hyperlink` calls and 27.453 seconds across 9,009 `\href` calls. All six tagged 1,214-page A4 PDFs have 34,562 destinations, 17,341 GoTo annotations, 12,072 URI annotations, 26,350 `Link` roles, and 29,413 OBJR/`StructParent` associations. Extracted-text and URI-target hashes match; PDF bytes differ. This one-pass output from a populated `.toc` is diagnostic, not a qualification of a converged build. The check does not separate hyperref from tagpdf costs and does not justify a renderer change. See the [raw record](validation-latex-link-macro-matched-n1000-20261006.json).


### Hyperref macro profile after ParentTree batching — N=1,000 — October 6, 2026

One direct tagged pass with the current populated auxiliary files takes 212.560 seconds. Instrumentation times complete calls to `\hyperlink` and `\href`: 17,601 calls accumulate 49.005 seconds and 9,009 calls accumulate 26.052 seconds. These intervals include work performed below hyperref, including tagpdf operations; they overlap conceptually and must not be added as independent costs. Marker overhead was not measured separately.

The audit finds the same 1,140 pages, 38,025 destinations, 32,950 annotations with `StructParent`, 32,950 correctly referenced OBJR associations, 400 figures with alt text, and normalized text hash as the converged ParentTree-batched PDF. This diagnostic pass provides no matched timing comparison and does not justify a production change. The next step profiles tagpdf structure and marked-content operations from the same auxiliary state. See the [raw record](validation-latex-link-macro-profile-parenttree-batched-n1000-20261006.json) and the [temporary diagnostic PDF](../tmp/pdfs/link-profile-parenttree-batched-n1000-20261006/book.pdf).


### Tagpdf operation profile beneath links — N=1,000 — October 6, 2026

In one 211.630-second direct tagged pass, Lua wrappers time `tag_struct_begin:n` 128,031 times for 51.132 seconds and `tag_mc_begin:n` 124,747 times for 11.943 seconds. `tag_struct_end:` accumulates 3.577 seconds, `tag_mc_begin_pop:n` 4.999 seconds, `tag_mc_end:` 1.795 seconds, and `tag_mc_end_push:` 1.477 seconds. These inclusive intervals may overlap; wrapper overhead was not calibrated. The LuaTeX shipout hook associates annotations with structures 32,944 times in 1.802 seconds; the inline insertion path is not used by this engine.

The 1,140-page PDF matches the converged control for all 38,025 destinations, 32,950 annotations and their OBJR/ParentTree owners, roles, 400 alt texts, and normalized text hash. The profile identifies structure creation as the next area to investigate, but does not establish that a safe optimization exists. No production change is retained. See the [raw record](validation-latex-tagpdf-link-operations-profile-parenttree-batched-n1000-20261006.json) and the [temporary diagnostic PDF](../tmp/pdfs/tagpdf-link-ops-profile-parenttree-batched-n1000-20261006/book.pdf).


### Tagpdf TeX/Lua table profile — N=1,000 — October 6, 2026

One direct tagged pass records 1,061,820 tagpdf property updates accumulating 12.428 seconds, 157,703 sequence appends accumulating 2.378 seconds, and 128,031 calls to create property and sequence tables (0.961 and 0.879 seconds). `__tag_struct_set_tag_info:nnn` accumulates 15.867 seconds across 128,031 calls; this includes property writes already counted, and other intervals may also overlap. The 221.430-second wall time reflects heavier instrumentation and is not a production timing.

The PDF audit confirms equivalence with the converged control: 1,140 pages, 38,025 destinations, 32,950 links with correct OBJR/ParentTree ownership, no missing figure alt text, and the same normalized text hash. Two prototypes buffer Lua mirror updates in groups of 128, flushing either at each batch or at shipout and before tagpdf finalization. They take 300.26 and 364.93 seconds, respectively, against 212.56 seconds for the direct reference pass. Each variant ran once with the hyperlink timing wrappers and identical `.aux`/`.toc` seeds; both are rejected as materially slower. No production change is retained. The next profile breaks down `tag_struct_begin:n` while keeping ParentTree batching and auditing the resulting PDF. See the [raw record](validation-latex-tagpdf-lua-mirror-batching-n1000-20261006.json), the [initial profile](validation-latex-tagpdf-structure-storage-profile-parenttree-batched-n1000-20261006.json), and the [temporary PDF](../tmp/pdfs/tagpdf-lua-mirror-page-batched-n1000-20261006/book.pdf).

### Internal `tag_struct_begin:n` profile — N=1,000 — October 6, 2026

One heavily instrumented 223.68-second pass breaks down 128,031 calls to `tag_struct_begin:n`. Structure-key parsing accumulates 15.882 seconds and tag/namespace assignment 14.486 seconds. Role resolution takes 2.746 seconds, property and sequence table creation totals 3.026 seconds, and child insertion takes 3.214 seconds. These timers are nested; they must not be added to the outer 57.968-second structure-begin interval. Deferred parent-child validation does not run on each structure begin. One sequence timer targeted the wrong variant; its actual work is included in the child-insertion interval.

The tagged 1,140-page A4 PDF keeps all 38,025 destinations, 32,950 link annotations and their OBJR/ParentTree owners, the same roles, all 400 figure alt texts, and the same extracted-text hash as the converged control. This single heavily instrumented pass is not a production performance result. No code change is retained. The next profile isolates repeated PDF-name conversion and property writes inside tag assignment. See the [raw record](validation-latex-tagpdf-struct-begin-internals-profile-parenttree-batched-n1000-20261006.json) and the [temporary PDF](../tmp/pdfs/tagpdf-struct-begin-internals-profile-parenttree-batched-n1000-20261006/book.pdf).

### PDF-name conversion fast-path prototypes — N=1,000 — October 6, 2026

Three temporary variants target frequent ASCII structure-tag names. A 21-name linear `\str_case` list passes the full PDF audit but takes 255.88 seconds, 43.32 seconds slower than the 212.56-second reference. Control-sequence dispatch takes 247.58 seconds and fails semantic equivalence: its PDF has 1,040 fewer ParentTree keys and a different extracted-text hash. A short list for `Link`, `text`, and `text-unit` passes the audit but takes 217.09 seconds (+4.53 seconds, +2.13%) in one run. No gain is established; all three variants are rejected and do not change the renderer. See the [raw record](validation-latex-tagpdf-pdf-name-fastpath-n1000-20261006.json), the [equivalent full-list PDF](../tmp/pdfs/tagpdf-pdf-name-fastpath-profile-parenttree-batched-n1000-20261006/book.pdf), the [equivalent short-list PDF](../tmp/pdfs/tagpdf-pdf-name-common-fastpath-profile-parenttree-batched-n1000-20261006/book.pdf), and the [rejected PDF](../tmp/pdfs/tagpdf-pdf-name-csname-fastpath-profile-parenttree-batched-n1000-20261006/book.pdf).

### Selective tagpdf Lua-mirror writes — N=1,000 — October 6, 2026

A temporary prototype keeps TeX property and sequence updates but sends only `tag`, `rolemap`, `parentrole`, and `parentnum` property keys to Lua, while suppressing sequence-mirror writes. The pass takes 242.05 seconds against the 212.56-second reference, and its audit fails: it has 1,040 fewer ParentTree keys and a different extracted-text hash. Static inspection did not identify every mirror consumer. The prototype is rejected with no production change; retain all private mirror writes in subsequent investigations. See the [raw record](validation-latex-tagpdf-lua-mirror-filter-n1000-20261006.json) and the [rejected temporary PDF](../tmp/pdfs/tagpdf-lua-mirror-selective-profile-parenttree-batched-n1000-20261006/book.pdf).

### RSS follow-up for the converged ParentTree-batched build — N=1,000 — October 6, 2026

A complete recompile of the exact generated LaTeX source (SHA-256 `b40c13e8…`) converges in three passes: 26.509, 234.010, and 240.461 seconds, for 500.995 seconds total. macOS `ru_maxrss` records a peak of **1,104,003,072 bytes (1,052.86 MiB)** among child processes, primarily LuaLaTeX; the 512 MiB reference is exceeded. The temporary workspace peaks at 22,614,240 logical bytes (21.57 MiB). This covers compilation and its working directory, not allocations in the full Gramps export process.

The rebuilt PDF retains all audited properties of the previous converged PDF: 1,140 A4 pages, 38,025 destinations, matching structure roles, 400 figures with alt text, 32,950 link annotations with correct OBJR/ParentTree ownership, and the same normalized-text hash. Its binary hash differs; `/CreationDate`, `/ModDate`, and the trailer ID also changed. A byte-level diff was not performed. The two full builds took 449.174 and 500.995 seconds; this pair does not attribute the elapsed-time difference. The 180-second compilation target also remains unmet. See the [RSS and audit record](validation-latex-parenttree-batched-rss-n1000-20261006.json), the [initial converged-build record](validation-latex-parenttree-batched-converged-n1000-20261006.json), and the [recompiled PDF](../tmp/l8-3-rss-parenttree-batched-n1000-20261006/book.pdf).

### Deduplicating shared appendix URLs — N=100 — October 7, 2026

The renderer continues to print every citation's own URLs. In the documentary appendix, it now prints each source and repository URL only at that shared record's first occurrence. Source and repository details, every citation, and its internal references remain in place. All 317 unique URI targets remain accessible, including all 303 citation-specific targets.

Three converged production-helper builds of the same synthetic branching N=100 book, each in a fresh directory, produced these results:

| Variant | Durations (s) | Median (s) | Median PDF (bytes) | Pages | bookurl macros | Link annotations | URI annotations |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Reference | 45.346; 45.563; 45.471 | 45.471 | 1,402,062 | 121 | 909 | 3,335 | 1,216 |
| Deduplicated shared URLs | 41.161; 41.116; 41.131 | 41.131 | 1,312,919 | 117 | 317 | 2,449 | 330 |

Median compile time falls by 4.340 seconds (9.54%), and the median PDF shrinks by 89,143 bytes (6.36%). All 2,119 internal links remain and resolve to their targets. All 40 figure tags retain non-empty alternative text and a /BBox with positive width and height; some appendix figures move as the shorter text reflows. Every remaining link annotation has the correct ParentTree owner. Pages 77, 78, and 87 were visually inspected; retained URLs are complete and the images do not overlap the text.

This check covers N=100 on a synthetic fixture and does not yet establish whether the N=1,000 PDF budget is met. The dedicated strikethrough recipe validator does not apply to this fixture because it lacks the required passage; the audit therefore used PDF structure checks and visual review of the listed pages. The control has four fewer pages (121 to 117); the only missing named destinations are page.117 through page.120, and no internal link targets them. Timings, LaTeX hashes, and the detailed audit are in the [raw record](validation-latex-citation-url-dedup-n100-20261007.json).

### N=1,000 confirmation — October 7, 2026

One converged N=1,000 candidate build is compared with the converged production control built on October 6. There is only one candidate build and one historical control, so this indicates the direction of the gain without replacing paired repetitions.

| Variant | Compile (s) | PDF (bytes) | Pages | bookurl macros | Link annotations | URI annotations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Converged control | 449.174 | 13,461,234 | 1,140 | 9,009 | 32,950 | 12,072 |
| Deduplicated shared URLs | 423.847 | 12,556,083 | 1,096 | 3,125 | 24,126 | 3,248 |

The candidate saves 25.327 seconds (5.64%) and 905,151 bytes (6.72%). All 3,125 unique URI targets remain, including all 3,003 citation-specific targets; all 20,878 internal links resolve. None of the 44 removed trailing page destinations is targeted by an internal link. All 400 figures retain non-empty alternative text and a valid /BBox on their page; their positions were recalculated for the appendix reflow. All 24,126 remaining links have matching ParentTree owners. Candidate pages 702, 794, and 795 were visually inspected.

Compilation still takes 423.847 seconds, above the 180-second target. A repeat and RSS measurement are documented in the following section; both results still need more paired repetitions. The [initial raw record](validation-latex-citation-url-dedup-n1000-20261007.json) includes hashes, the control PDF, and the comparison audit.

### Converged repeat and RSS — N=1,000 — October 7, 2026

The same candidate source (SHA-256 `63d01782…`) and its 200 media assets were recompiled in a fresh directory. The build converged in 407.011 seconds. The earlier build of the same source took 423.847 seconds; the median of the two measurements is 415.429 seconds, with a 16.836-second range (4.05% of the median). Two measurements are not enough to characterize the variation precisely.

On macOS, `ru_maxrss` reports 1,069,842,432 bytes (1,020.28 MiB) for child processes, primarily LuaLaTeX. A one-second `ps` sample peaks at 1,067,237,376 bytes (1,017.8 MiB), and the temporary workspace peaks at 21,417,167 logical bytes (20.43 MiB), sampled every 100 ms. RSS is 34,160,640 bytes below the historical October 6 record, but that record used the earlier source without URL deduplication; this comparison does not demonstrate a stable memory improvement. The 512 MiB reference and 180-second compile target remain unmet.

The repeated PDF is tagged, PDF 2.0, and has 1,096 pages. It retains 24,126 link annotations, 3,248 URI annotations across 3,125 targets, 20,878 internal GoTo links, and all 400 figures with alternative text and valid /BBox values. Every link annotation has a matching OBJR owner in the ParentTree; the normalized extracted-text hash exactly matches the first candidate PDF. The binary hash differs because date metadata and the trailer ID are regenerated on each compile. Per-pass durations were not captured for this repeat. See the [raw repeat and RSS record](validation-latex-citation-url-dedup-repeat-rss-n1000-20261007.json) and the [recompiled PDF](../tmp/l83-shared-source-url-dedup-20261007/n1000/repeat-rss/book.pdf).

### Detailed pass profile — N=1,000 — October 7, 2026

The same candidate source was compiled in a fresh directory while measuring each LuaLaTeX process and sampling RSS once per second:

| Pass | Tagging / hyperref | Duration | Sampled peak RSS |
| --- | --- | ---: | ---: |
| 1 | off / draft | 25.596 s | 161.22 MiB |
| 2 | on / final | 199.001 s | 1,091.39 MiB |
| 3 | on / final | 198.530 s | 918.95 MiB |

The converged build takes 423.158 seconds; the two tagged passes total 397.531 seconds, or 93.94% of the build. They take nearly the same time. `ru_maxrss` peaks at 1,144,438,784 bytes (1,091.42 MiB) during the second pass. The PDF retains 1,096 pages, 24,126 links with matching OBJR/ParentTree owners, 3,125 URI targets, 20,878 internal links, all 400 accessible figures, and the normalized extracted-text hash. The source contains 17,591 `\gfbpagelink` calls, which must retain their accessible Link structure. The 180-second and 512 MiB targets remain unmet.

The profiled run's `ru_maxrss` is 74,596,352 bytes (71.14 MiB) above the previous unprofiled repeat. This pair cannot attribute the difference to profiling or run-to-run variation; peak RSS still needs repeated measurements.

The next measurement targets internal page-link cost in the tagged passes using this deduplicated source; any prototype must preserve every Link role, annotation, and ParentTree association. The [raw per-pass profile](validation-latex-citation-url-dedup-pass-profile-n1000-20261007.json) includes timings, RSS peaks, hashes, and the PDF audit.

### Hyperref macro profile on the deduplicated source — N=1,000 — October 7, 2026

One direct tagged pass was instrumented around the complete `\hyperlink` and `\href` macros, using the candidate's converged `.aux` and `.toc` files. It takes 200.481 seconds. The Lua timer records 17,601 `\hyperlink` calls with 50.906 seconds of inclusive CPU time, and 3,125 `\href` calls with 9.896 seconds.

The earlier profile of the source before URL deduplication also recorded 17,601 `\hyperlink` calls (49.005 seconds), but 9,009 `\href` calls (26.052 seconds). The candidate removes 5,884 external-link calls and about 62% of their inclusive time. The small increase in `\hyperlink` time (1.901 seconds) is not a paired comparison and does not establish a slowdown. These intervals overlap with tagpdf work and should not be added to compiler durations.

The diagnostic tagged PDF has 1,096 pages and retains 24,126 links with matching OBJR/ParentTree owners, 3,125 URI targets, 20,878 internal links, all 400 accessible figures, and the same normalized extracted-text hash. This profile makes no production code change. The next investigation can examine the internal hyperlink path while preserving all accessible structure. See the [raw hyperref profile](validation-latex-citation-url-dedup-link-profile-n1000-20261007.json), the [earlier profile](validation-latex-link-macro-profile-parenttree-batched-n1000-20261006.json), and the [diagnostic PDF](../tmp/l83-shared-source-url-dedup-20261007/n1000/hyperlink-profile/instrumented/book.pdf).

### Internal anchor profile — N=1,000 — October 7, 2026

A separate tagged pass also instruments `\hypertarget` and `\label` with the same auxiliary files. It records 14,498 calls of each macro: `\hypertarget` accumulates 9.602 seconds of CPU time and `\label` 0.235 seconds. In this same profile, `\hyperlink` accumulates 50.424 seconds over 17,601 calls and `\href` 9.697 seconds over 3,125 calls. The measurements are inclusive, run once, and the wrapper overhead was not calibrated; they target work and do not compare build times.

The diagnostic PDF retains 1,096 pages, all 24,126 link/OBJR/ParentTree associations, 3,125 URI targets, 20,878 internal links, all 400 accessible figures, and identical extracted text. Destination and label creation is smaller than the `\hyperlink` calls in this sample. The next investigation targets internal-link handling without removing Link tags. See the [raw anchor profile](validation-latex-citation-url-dedup-anchor-profile-n1000-20261007.json) and the [diagnostic PDF](../tmp/l83-shared-source-url-dedup-20261007/n1000/anchor-profile/instrumented/book.pdf).

### Internal link path prototypes — N=1,000 — October 7, 2026

Three variants were each compiled once from an identical copy of the URL-deduplicated source, with the same populated `.aux` and `.toc` files and one direct tagged LuaLaTeX pass. The reference takes 196.452 seconds. Replacing `\hyperlink` with the private `\hyper@link` API takes 209.819 seconds (+13.367 seconds, 6.80%); directly calling `\hyper@linkstart` and `\hyper@linkend` takes 205.696 seconds (+9.244 seconds, 4.71%). Replacing `\pageref*` with `\getpagerefnumber` takes 196.830 seconds (+0.378 seconds, 0.19%). These single measurements are not paired and show no gain; the private variants are rejected. The earlier profile had already measured just 0.510 seconds over 17,590 page-reference calls, about 0.20% of a pass.

All four PDFs have 1,096 pages and remain tagged PDF 2.0. The three candidates preserve the reference link signatures exactly (page, rectangle, action, and contents), all 24,126 annotation/OBJR/ParentTree associations, 3,248 URI annotations across 3,125 targets, 20,878 internal links, all 400 figures with alternative text, and the normalized-text hash. No production code is changed.

An instrumentation attempt around the legacy `\find@pdflink` and `\close@pdflink` macros records no calls: the tagged hyperref route uses a newer API. These zero counters are not timing results. Further analysis must target the active tag-aware path; the N=1,000 targets of 180 seconds and 512 MiB remain unmet. See the [raw prototype record](validation-latex-link-path-prototypes-n1000-20261007.json) and the [earlier page-reference profile](validation-latex-pageref-profile-n1000-20261006.json).

### Hyperref GoTo contents and PDF-string profiles — N=1,000 — October 7, 2026

Two separate direct tagged LuaLaTeX passes use the same URL-deduplicated source and populated `.aux`/`.toc` seeds. The first profile records 20,878 calls to the active `hyp/link/GoTo/Contents` socket, with 24.511 seconds of inclusive Lua CPU time. Creating each accessible `/Contents` string takes 22.290 seconds; inserting it into the annotation dictionary takes 1.341 seconds. A separate conversion of each internal destination name, before entering the socket, takes 12.291 seconds.

A second pass divides the PDF-string operation: `__hyp_text_purify:nN` takes 16.518 seconds and `str_set_convert:Nnnn` takes 5.336 seconds across 20,878 labels. The prefix/suffix intervals are nested inside the conversion interval and each is under 0.12 seconds; the two string assignments are also each under 0.12 seconds. These figures come from different single instrumented runs and do not form a paired comparison. Wrapper overhead is uncalibrated, and nested intervals must not be added together.

Both diagnostic PDFs are tagged PDF 2.0, have 1,096 pages, and preserve identical link signatures. All 24,126 Link annotations match their ParentTree OBJR owners; all 400 figures retain nonempty alternative text; the NFC-normalized extracted text matches. The two instrumented PDFs differ in size by six bytes. This profile makes no production change. Further work can explore text purification or UTF-16 hex conversion while keeping the accessible link text intact; any candidate needs repeated timings and the same PDF audit. The N=1,000 budgets of 180 seconds and 512 MiB remain unmet. See the [raw profiles](validation-latex-hyperref-goto-contents-profile-n1000-20261007.json) and the [diagnostic PDF](../tmp/l83-hyperref-goto-encoder-profile-20261007/book.pdf).

### Guarded PDF-string fast path for generated page links — N=1,000 — October 7, 2026

A temporary candidate bypasses Hyperref's private `\__hyp_text_purify:nN` only while `\gfbpagelink` creates a renderer-generated page link. The destination labels use `target-` plus a 96-bit BLAKE2s digest encoded with URL-safe Base64. The override checks that the private hook exists; otherwise Hyperref's normal purification remains active.

Three counterbalanced pairs use the same source, media, and populated `.aux` and `.toc` seeds. Each duration is one direct tagged LuaLaTeX pass, not a complete multi-pass export:

| Pair | Reference (s) | Candidate (s) | Saved (s) | Saved (%) |
| --- | ---: | ---: | ---: | ---: |
| 1 | 210.04 | 181.38 | 28.66 | 13.65% |
| 2 | 195.99 | 182.60 | 13.39 | 6.83% |
| 3 | 196.23 | 175.61 | 20.62 | 10.51% |
| Mean | 200.75 | 179.86 | 20.89 | 10.41% |

All three candidate PDFs match their paired references for page count, link annotation rectangles, link signatures and destinations, annotation contents, ParentTree/OBJR ownership, figure alternative text, and NFC-normalized extracted text. Each PDF is tagged PDF 2.0 with 1,096 pages, 24,126 link annotations (20,878 GoTo and 3,248 URI across 3,125 targets), 24,126 matching OBJR owners, and 400 figures with non-empty alternative text.

This repeated per-pass result supports the narrowly scoped renderer fast path. Two complete builds through the production renderer were also timed at 380.82 and 349.17 seconds. The first produced the audited 1,096-page tagged PDF; the second measured 1,180,112 KiB (1,152.45 MiB) peak LuaLaTeX RSS from 338 one-second samples. The 31.65-second spread is not evidence that the fast path caused a full-build speedup, and the repeat PDF was not retained for a second semantic audit. Both full-build durations exceed 180 seconds, and the sampled RSS exceeds 512 MiB. See the [raw paired profile and audit](validation-latex-hyperref-purify-fastpath-n1000-20261007.json), the [full-build timing and RSS record](validation-latex-hyperref-purify-fastpath-full-build-n1000-20261007.json), and the temporary [candidate PDF](../tmp/l83-hyperref-purify-page-links-repeats-20261007/pair-1/candidate/book.pdf).

### Identity conversion fast path for generated destinations — N=1,000 — October 8, 2026

The production `\gfbpagelink` path receives renderer-generated `target-*` labels containing only URL-safe ASCII. A temporary candidate skips Hyperref's `utf8/string-raw` conversion only while that page-link fast path is active; all other encodings, including the `utf16/hex` accessible Contents strings, still use the original converter.

Three paired direct tagged LuaLaTeX passes used identical populated `.aux` and `.toc` seeds with counterbalanced order:

| Pair | Reference (s) | Candidate (s) | Saved (s) | Saved (%) |
| --- | ---: | ---: | ---: | ---: |
| 1 | 164.840 | 163.508 | 1.332 | 0.81% |
| 2 | 165.537 | 163.222 | 2.315 | 1.40% |
| 3 | 165.002 | 163.018 | 1.984 | 1.20% |
| Mean | 165.126 | 163.249 | 1.877 | 1.14% |

Each PDF pair matches in all audited semantic fields and exact link signatures: 1,096 tagged PDF 2.0 pages; 24,126 links (20,878 GoTo and 3,248 URI); 3,125 URI targets; 24,126 matching OBJR/ParentTree owners with no mismatches; 400 figures with alternative text; and identical NFC text hashes. This is a modest, repeatable per-pass saving. It does not measure a complete export or establish a full-build gain. See the [raw paired profile and audit](validation-latex-hyperref-target-identity-fastpath-n1000-20261008.json) and temporary [candidate PDFs](../tmp/l83-hyperref-target-identity-paired-20261008/).

### Complete converged build after the destination identity fast path — N=1,000 — October 8, 2026

One production `write_latex_pdf` build with extended convergence took 347.43 seconds. The timed scope includes LaTeX rendering, copying prepared media, and all LuaLaTeX passes; synthetic fixture, model, and media preparation happened before timing. The 1,096-page tagged PDF is 12,556,077 bytes. One-second process sampling captured a peak of 1,173,584 KiB (1,146.08 MiB) across 336 samples.

The semantic audit matches the paired per-pass profile exactly: 24,126 link annotations (20,878 GoTo and 3,248 URI), 3,125 URI targets, 24,126 matching OBJR/ParentTree owners with no mismatches, 400 figures with non-empty alternative text, and identical normalized-text and ordered-link-signature hashes. The 180-second and 512 MiB budgets remain unmet. This is one merged-code build, so it does not attribute a full-build speed change to the destination identity fast path. See the [raw build and audit record](validation-latex-hyperref-target-identity-full-build-n1000-20261008.json) and the retained [demonstration PDF](../output/pdf/gramps-fancy-book-destination-identity-demo-n1000-20261008.pdf).

### Cache for accessible GoTo contents — N=1,000 — October 8, 2026

Three counterbalanced pairs of direct tagged LuaLaTeX passes use identical source and populated `.aux`/`.toc` seeds. The candidate caches Hyperref's `utf16/hex` `/Contents` string by generated destination, only while the renderer creates page links. Other GoTo links keep Hyperref's default path.

| Pair | Reference (s) | Candidate (s) | Saved (s) | Saved (%) |
| --- | ---: | ---: | ---: | ---: |
| 1 | 163.603 | 161.381 | 2.222 | 1.358% |
| 2 | 163.355 | 160.718 | 2.637 | 1.614% |
| 3 | 163.403 | 161.654 | 1.749 | 1.070% |
| Mean | 163.454 | 161.251 | 2.203 | 1.348% |

The candidate records 8,541 cache hits and 9,049 misses per pass. All three PDF audits match their paired references for every semantic field and ordered link signature: 1,096 tagged PDF 2.0 pages, 24,126 links (20,878 GoTo and 3,248 URI), 24,126 valid OBJR/ParentTree associations, 400 figures with alternative text, and the normalized-text hash. The renderer integrates the cache with guards for the Hyperref socket, plug assignment, encoder, and annotation dictionary writer; if those APIs are unavailable, Hyperref keeps its default behavior. See the [raw paired profile and audits](validation-latex-hyperref-goto-contents-cache-fastpath-n1000-20261008.json).

### Converged build with the GoTo cache — N=1,000 — October 8, 2026

One production `write_latex_pdf` build with extended convergence takes 344.58 seconds. The tagged PDF has 1,096 pages and is 12,556,080 bytes. One-second LuaLaTeX RSS sampling captures a maximum of 1,167,088 KiB (1,139.73 MiB) across 333 samples. The audit confirms 24,126 annotations and OBJR/ParentTree associations with no mismatch, 400 accessible figures, and the same normalized-text and link-signature hashes as the per-pass profile.

This single build verifies the integrated renderer but does not attribute a complete-build speedup to the cache; the 180-second and 512 MiB budgets remain unmet. See the [raw build record](validation-latex-hyperref-goto-contents-cache-full-build-n1000-20261008.json) and retained [demonstration PDF](../output/pdf/gramps-fancy-book-goto-contents-cache-demo-n1000-20261008.pdf).

### Repeated converged builds with the current renderer — N=100 — October 8, 2026

Three complete exports used `write_latex_pdf` with extended convergent compilation on the same branching fixture (100 descendant couples, 20 media). Fixture, model, and media preparation are outside the timed scope; peak RSS was sampled once per second.

| Run | Elapsed (s) | Peak RSS (KiB) | Peak RSS (MiB) | PDF (bytes) |
| --- | ---: | ---: | ---: | ---: |
| 1 | 35.97 | 331,584 | 323.81 | 1,312,911 |
| 2 | 35.88 | 336,032 | 328.16 | 1,312,912 |
| 3 | 35.94 | 325,872 | 318.23 | 1,312,915 |
| Median | 35.94 | 331,584 | 323.81 | — |

All three audits agree: 117 tagged PDF 2.0 pages, 2,449 links (2,119 GoTo and 330 URI), 317 URI targets, 2,449 OBJR/ParentTree associations with no mismatch, and 40 figures with alternative text. The NFC-text and ordered-link-signature hashes match across all three files. Every run meets the 180-second and 512-MiB reference budgets. This qualifies the current N=100 build; without a paired reference build, it does not attribute a gain to the GoTo cache. See the [consolidated record](validation-latex-hyperref-goto-contents-cache-full-build-n100-20261008.json).

### LuaTeX memory-counter diagnostic — N=1,000 — October 8, 2026

Five direct tagged passes were instrumented with populated auxiliary files: one reference, two passes with the GoTo cache, then one pass with tagpdf's parent-child check disabled and one with that check deferred until the end. LuaTeX counters were sampled every 100 pages and at finalization; RSS was sampled once per second. The PDFs pass the reference semantic audit and retain 1,096 pages. `dyn_used` is a LuaTeX status counter, not a byte count ([LuaTeX status documentation](https://github.com/TeXLuaCATS/LuaTeX/blob/main/resources/manual/10_tex.tex.lua)).

| Variant | Elapsed (s) | Peak RSS (MiB) | `dyn_used` before finalization | After tagpdf |
| --- | ---: | ---: | ---: | ---: |
| Cache, first profile | 163.057 | 1,078.47 | 31,760,208 | — |
| Reference | 163.957 | 1,132.78 | 30,203,384 | — |
| Cache, repeat | 161.837 | 1,036.39 | 31,760,030 | — |
| Parent-child check disabled | 160.773 | 1,096.50 | 31,760,303 | 31,802,130 |
| Check deferred until end | 161.828 | 1,145.45 | 31,760,338 | 31,802,165 |

RSS varies by 96.39 MiB across the three cache/reference profiles and by 48.95 MiB between the two one-off parent-child settings. After finalization, Lua GC counters differ by about 6.01 MiB and `dyn_used` by 35 units. These runs are exploratory, not matched or sufficiently repeated to attribute the differences to the cache or tagpdf check; they do not support disabling the check. The N=1,000 512-MiB budget remains substantially exceeded. The [detailed memory record](validation-latex-memory-profile-n1000-20261008.json) preserves checkpoints, PDF sizes, and interpretation limits.


### Repeated converged builds with the current renderer — N=10 — October 8, 2026

Three complete exports used `write_latex_pdf` with extended convergent compilation. LuaLaTeX RSS was sampled once per second; fixture preparation is outside the timed scope.

| Run | Elapsed (s) | Peak RSS (KiB) | Peak RSS (MiB) | PDF (bytes) |
| --- | ---: | ---: | ---: | ---: |
| 1 | 7.81 | 194,736 | 190.17 | 182,436 |
| 2 | 7.73 | 206,800 | 201.95 | 182,440 |
| 3 | 7.74 | 217,888 | 212.78 | 182,440 |
| Median | 7.74 | 206,800 | 201.95 | — |

All three audits agree on the tagged PDF semantics: 17 pages, 278 links (240 GoTo and 38 URI), 36 URI targets, 278 OBJR/ParentTree associations with no mismatch, and four figures with alternative text. NFC-text and link-signature hashes match. All builds stay within the 180-second and 512-MiB budgets. See the [consolidated record](validation-latex-hyperref-goto-contents-cache-full-build-n10-20261008.json).


### Renderer temporary workspace — N=10, 100, and 1,000 — October 8, 2026

One complete build per size was monitored at 100-ms intervals. The metric sums logical sizes of regular files under `output/pdf/.book-pdf-*`, the renderer's compilation directory. It excludes prior fixture, model, and media preparation; files created and removed between samples may be missed.

| Descendant couples | Elapsed (s) | Peak temporary workspace (bytes) | Peak RSS (MiB) | Semantic audit |
| ---: | ---: | ---: | ---: | --- |
| 10 | 7.75 | 332,448 | 203.30 | Passed, 17 pages |
| 100 | 35.89 | 2,249,042 | 310.88 | Passed, 117 pages |
| 1,000 | 344.09 | 21,420,988 | 1,092.44 | Passed, 1,096 pages |

The elapsed-time (180 seconds) and RSS (512 MiB) budgets are met at N=10 and N=100; both remain exceeded at N=1,000. These are first per-build reference points, not repeated bounds or a system-wide disk quota measurement. See the [detailed record](validation-latex-temp-space-20261008.json).

### Paired memory profiles for the GoTo cache — N=1,000 — October 8, 2026

To resolve the seed mismatch in the first diagnostics, three pairs of direct passes were rerun from identical populated `.aux` and `.toc` files within each pair. The only source difference is the `/Contents` cache plug for generated page links. Run order was counterbalanced; LuaTeX counters were sampled every 100 pages and RSS once per second.

| Pair | Variant | Elapsed (s) | Peak RSS (MiB) | Final `dyn_used` |
| --- | --- | ---: | ---: | ---: |
| 1 | Reference | 163.689 | 1,145.86 | 30,203,005 |
| 1 | Cache | 162.003 | 1,057.50 | 31,759,614 |
| 2 | Reference | 164.183 | 1,093.30 | 30,203,005 |
| 2 | Cache | 163.110 | 1,098.97 | 31,759,614 |
| 3 | Reference | 165.284 | 1,016.47 | 30,203,076 |
| 3 | Cache | 163.976 | 1,096.53 | 31,759,651 |

The cache saves 1.073–1.686 seconds per pass, averaging 1.356 seconds (0.825%). Its `dyn_used` counter is 1,556,575–1,556,609 units higher (about 5.154%); this is not converted to bytes. RSS varies from −88.36 to +80.06 MiB by pair, showing no stable cache-attributable effect. Each PDF retains the same 1,096 pages, 24,126 links and OBJR/ParentTree associations, 400 accessible figures, NFC-text hashes, and ordered link-signature hashes. The cache records 8,541 hits and 9,049 misses per pass.

The cache retains its modest timing gain without a demonstrated RSS effect. An `expl3` prototype was then tried on the same fixture; its partial results are recorded below. See the [detailed paired record](validation-latex-memory-cache-paired-n1000-20261008.json).

### Exploratory `expl3` cache probe — N=1,000 — October 8, 2026

An `expl3` property table temporarily replaced the per-destination cache, using the same initial auxiliary files as pair 1 of the preceding profile. The run was stopped after more than 573 seconds, when LuaLaTeX reported page 933 of 1,096; the pair 1 current-cache direct pass took 162.003 seconds. An RSS sample at 573 seconds was 813,952 KiB (794.88 MiB), not a final peak. At pages 100, 500, and 900, `dyn_used` was 0.46%, 0.83%, and 0.74% higher than the current-cache checkpoints.

Because compilation was incomplete, there is no PDF audit or full-run RSS peak. The evidence is sufficient to reject this table as a replacement: it is much slower and does not show the intended memory reduction. No production code changed. The [exploratory record](validation-latex-expl3-cache-probe-n1000-20261008.json) preserves the seeds, observations, and limitations. The next profile will track RSS and Lua heap growth together during a complete build.

### RSS and Lua heap profile on a complete build — N=1,000 — October 8, 2026

A complete production-renderer build was instrumented with LuaTeX counters every 100 pages; production code was unchanged. The three converged passes took 351.98 seconds, with a sampled peak RSS of 1,151.89 MiB across 340 one-second samples. These values include the instrumentation and are not a paired comparison with the previous build.

At the end of the final tagged pass, Lua `collectgarbage("count")` reported 396,922 KiB (about 387.62 MiB), while process RSS continued to rise near the end of the document. The Lua counter describes the heap, not RSS. This suggests the Lua heap contributes materially to memory use, but does not by itself explain the 1,151.89-MiB peak.

The audit exactly matches the previous complete build: tagged PDF 2.0, 1,096 pages, all 24,126 links associated with their OBJR/ParentTree owners, 400 figures with alternative text, and identical NFC-text/link hashes. The 180-second and 512-MiB budgets remain exceeded. The [detailed per-pass, per-second record](validation-latex-memory-rss-full-build-n1000-20261008.json) preserves the correlated data. Next measurement: a synthetic N=1,000 build without media to estimate their contribution to RSS.

### Diagnostic no-media ablation — N=1,000 — October 8, 2026

An instrumented build without synthetic media (200 media records and 400 figures removed) took 344.40 seconds and reached 1,140.77 MiB sampled RSS. Its tagged PDF has 878 pages and 24,086 links; all 24,086 links have OBJR/ParentTree associations, and there are no figures. The media build in the preceding section has 1,096 pages, 24,126 links, and 400 accessible figures, with 1,151.89 MiB peak RSS.

Across these two single runs, removing media and 218 pages lowered peak RSS by only 11.12 MiB. The final Lua heap counter was about 52 MiB lower, while RSS was nearly unchanged; these different metrics do not identify a specific memory component. This ablation is not a production-equivalent PDF and was not repeated. It suggests images are not the main source of the peak.

The profile also shows 266.81 MiB peak RSS on the first pass, where the renderer disables tagging and puts Hyperref in draft mode, versus 1,151.89 MiB on the tagged passes. Since both settings change together, this points to the tagpdf/Hyperref and ParentTree path for inspection but does not prove causality. The [detailed record](validation-latex-no-media-rss-ablation-n1000-20261008.json) preserves both audits and the measurement series. The next step is to trace growth in OBJR/ParentTree entries and GoTo annotations through the renderer and tagpdf hooks without disabling tagging.

### Complete current benchmark with extended timeouts — N=1,000 — October 8, 2026

`benchmark_book.py` generated a synthetic branching tree with 1,000 descendant unions, 2,002 people, 1,001 families, 3,003 events, 200 synthetic 96 × 72 PNG portraits, and an HTML archive. Three complete compilations using `--extended-pdf-compilation` succeeded:

| Run | PDF time (s) | PDF (bytes) | LuaTeX peak RSS (MiB) | Python heap peak (MiB) | Logical temporary workspace peak (bytes) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 378.028 | 12,556,083 | 995.73 | 78.98 | 27,718,444 |
| 2 | 392.588 | 12,556,080 | 970.19 | 78.99 | 27,718,444 |
| 3 | 377.507 | 12,556,074 | 1,166.48 | 76.18 | 27,718,445 |
| Median | 378.028 | 12,556,080 | 995.73 | 78.98 | 27,718,444 |

Elapsed time ranges from 377.51 to 392.59 seconds; RSS ranges from 970.19 to 1,166.48 MiB, a notable spread. The PDF remains under the provisional 16-MiB size target, while all three times and RSS peaks exceed the 180-second and 512-MiB budgets. Temporary workspace varies by just one byte across runs. The 26.43-MiB result applies only to this N=1,000 branching fixture with 96 × 72 images and cannot establish a general limit; the N=100 high-resolution case below exceeds 300 MiB.

Three attempts with standard timeouts expired without a complete PDF; their partial RSS values are not treated as full-build peaks. The three extended runs were on macOS 27.0 arm64; RSS samples were taken every 100 ms and may miss shorter peaks, workspace size counts logical file lengths, and none of these temporary PDFs received an independent semantic audit. No renderer setting changed. The [first-run record](validation-latex-benchmark-n1000-extended-20261008.json) and [next two runs](validation-latex-benchmark-n1000-extended-repeats-20261008.json) preserve the raw measurements.

### High-resolution fixture with HTML and PDF — N=100 — October 8, 2026

Twenty synthetic pseudo-random 1,600 × 1,200 PNG portraits represent 115,379,213 source bytes. The HTML-only measurement, repeated three times, peaks at exactly 157,472,909 bytes (150.18 MiB) of temporary workspace and 120.33–123.13 MiB Python heap. Three complete PDF exports with extended timeouts then succeed:

| Run | PDF time (s) | PDF (bytes) | LuaTeX peak RSS (MiB) | Python heap peak (MiB) | Logical temporary workspace peak (bytes) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 37.935 | 79,709,779 | 328.30 | 123.13 | 316,529,068 |
| 2 | 38.614 | 79,709,777 | 319.09 | 123.13 | 316,529,066 |
| 3 | 38.049 | 79,709,782 | 316.23 | 120.33 | 316,528,229 |
| Median | 38.049 | 79,709,779 | 319.09 | 123.13 | 316,529,066 |

For this synthetic fixture, time and RSS remain under the 180-second and 512-MiB reference budgets; PDF size exceeds 16 MiB, and temporary workspace reaches 301.86–301.87 MiB. The previously considered 64-MiB limit is therefore invalid as a general budget. Random-noise PNGs do not represent photographs; workspace is the sampled sum of logical file sizes under the benchmark temporary directory (100 ms), so very short peaks may be missed. These temporary PDFs did not receive an independent semantic audit.

The HTML-only records and PDF records are in the [three HTML runs](validation-latex-benchmark-highres-n100-html-20261008.json), [first PDF run](validation-latex-benchmark-highres-n100-pdf-20261008.json), and [PDF runs 2 and 3](validation-latex-benchmark-highres-n100-pdf-repeats-20261008.json). The benchmark's 256-MiB limit on estimated synthetic source-media volume prevents scaling this case tenfold to N=1,000 without changing the benchmark.

### Effect of media compressibility — N=100 — October 8, 2026

To isolate content, the same N=100 case was repeated with twenty 1,600 × 1,200 PNGs generated from low-resolution (100 × 75) random RGB textures, upscaled with bicubic resampling, then blurred. These are smooth synthetic textures, not photographs. The fixture, crop, renderer, and three complete PDF compilations otherwise match the pseudo-random case above.

| Median measurement | Pseudo-random PNGs | Smooth synthetic PNGs | Change |
| --- | ---: | ---: | ---: |
| PNG sources (bytes) | 115,379,213 | 51,837,250 | −55.1% |
| PDF (bytes) | 79,709,779 | 36,620,288 | −54.1% |
| Logical temporary workspace (bytes) | 316,529,066 | 144,134,561 | −54.5% |
| PDF time (s) | 38.049 | 35.649 | −6.3% |
| LuaTeX peak RSS (MiB) | 319.1 | 324.0 | +1.5% |

Across these two synthetic profiles, source size strongly tracks derivative and PDF size; LuaTeX RSS remains similar. This confirms that random noise in the first experiment artificially inflated output sizes. It does not predict the size of real photographs or justify lossy encoding or downsampling. The [raw record for the three smooth-image compilations](validation-latex-benchmark-smooth-n100-pdf-20261008.json) is available; temporary workspace is sampled every 100 ms, and the PDFs did not receive an independent semantic audit.

The next L8.3 step is to avoid setting a general temporary-space limit until realistic-media and target-environment cases are measured. Preserve accessible structures; examine derivative and PDF sizes with representative images before changing renderer behavior.
