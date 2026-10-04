# L4 progress — genealogy traversal

Updated on 4 October 2026. L4 remains in progress; AC-01 and AC-03 to AC-09 are qualified against the model and textual LaTeX contract. AC-03 now has a native Gramps CLI fixture verified in HTML and PDF. Entry through the Gramps interface and pagination of a full book remain to be validated.

## Available traversal

- F0 must contain two known partners, which become P0 and P1 at generation 0.
- Ancestry and descendant limits are independent. `unlimited` is the default; zero or a non-negative integer can also be selected.
- The Gramps adapter recursively loads the families and people linked in those directions, then keeps unions and siblings as context. It does not expand the ancestry of a spouse introduced only through a descendant's union.
- The Gramps-independent engine produces negative and positive generations, family sections, occurrence roles, branch roots, and parentage paths.
- F0 appears as one section at the start of ancestry; the descendant part keeps the central occurrences as references. Children of ancestors' other unions appear as context without expanding their descendants.
- Explicit child-parent relationships recorded as `None` are not traversed. Single-parent families encountered in the graph remain valid.
- A path that revisits a person is kept as a visible occurrence, reported as a diagnostic, and stopped before the loop is expanded again.
- Profile eligibility follows `BOOK_PROFILE = YES` or a substantive individual/family event other than birth or death.
- Each occurrence carries `primary_occurrence_id` pointing to the person’s first appearance, even when no full profile exists. For an eligible person, `profile_anchor` and `is_primary_profile` still identify the single profile and its primary occurrence.
- Within a generation, branch, and family group, comparable disjoint birth ranges sort chronologically. Overlapping ranges, equal dates, and uncomparable dates use a stable Gramps ID/handle tie-breaker; missing or uncomparable dates remain at the end of the group. No precise birth order is inferred from an ambiguous range.
- Event timelines use Gramps' comparable bounds instead of its scalar sort value. Events with overlapping ranges retain source position, with the technical key as a stable tie-breaker; uncomparable dates follow classifiable dates.
- Family sections follow generation and branch-occurrence order, then the source order of unions in the relevant Gramps partner or child family list. The family identifier is only a deterministic tie-breaker.
- Each family section has a stable ID, references its in-scope partner and child occurrences, and exposes parent-child links with the Gramps-normalized relationship type for each parent when available. Each occurrence links back to its sections; generation, branch, path, and profile anchor provide the genealogy-marker data.
- The native T-04 recipe imports and rereads `Adopted`, `Foster`, and `None` links through Gramps 6.0.8. The model retains the values, traversal follows both recorded parent links, and a single-parent family is shown with only its known partner. The same fixture confirms that a Marriage event associated with F0 retains Gramps' `Family` role. Entering these values in the Gramps interface and trying the other relationship types remain open.
- The native AC-03 recipe adds a second union F0003 to the central parent and a child eligible through `BOOK_PROFILE=YES`. After Gramps 6.0.8 import, the child appears once in generation 1 and in F0003's family section; the model and HTML create only one profile. The child's and partner's names and their links appear in HTML and PDF.

## Remaining before L4 exit

- `tests/test_genealogy_acceptance.py` qualifies AC-01 and AC-03 to AC-09 with synthetic graphs and checks their LaTeX output. `scripts/verify_gramps.py` now covers AC-03 from the native fixture through the model, HTML ZIP, and PDF; the Gramps interface workflow remains open.
- `tests/test_date_ranges.py` checks transitive overlap groups, source-order preservation for event timelines, use of bounds when scalar sort values disagree, and final placement of textual/uncomparable dates. On 4 October, the complete suite passes: 54 tests.
- The LaTeX and HTML renderers consume the `genealogy` model. Their contracts are covered to different degrees; pagination, multipass references, and final PDF appearance still need visual review in L6.
- The editorial model already provides profiles, family notices, an index, and navigation targets to the LaTeX renderer. These checks cover their textual structure, not the final paginated composition.
- The six F0 editorial roles and their publication/diagnostic rules now have native Gramps CLI integration coverage. The Gramps 6 interface workflow and visual acceptance remain open; see [decision 004](decisions/004-f0-editorial-notes.md).

See the [action plan](action-plan.fr.md#l4--parcours-généalogiques-et-sélection) and [requirements](requirements.fr.md) for the full tasks and exit criteria.

## PDF CLI smoke check — 29 September 2026

Gramps 6.0.8 on macOS generated a 9-page A4 PDF from the synthetic native database using LuaHBTeX 1.24.0. The fixture included a portrait derivative, which appears on the cover and in the person's profile. This confirms the Gramps-to-PDF integration on a small synthetic book; it does not qualify long-book pagination, all media/URL cases, accessibility, or final visual acceptance, which remain open for L6.

## AC-03 CLI PDF check — 4 October 2026

Gramps 6.0.8 and LuaHBTeX 1.24.0 generated a 10-page A4 PDF. The person from the other union appears in generation 1, in the family connections with both parents, and then in profiles and the index. Visual review found the links and wrapped lines readable; visual validation of a complete book remains in L6.
