# L4 progress — genealogy traversal

Updated on 28 September 2026. L4 remains in progress; scenarios AC-03 to AC-09 are exercised against both the model and the textual LaTeX renderer contract. Visual PDF pagination remains to be validated in L6.

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
- Generation order is deterministic. Complete exact birth dates sort chronologically; absent or uncertain dates use a stable identifier as their tie-breaker.
- Family sections follow generation and branch-occurrence order, then the source order of unions in the relevant Gramps partner or child family list. The family identifier is only a deterministic tie-breaker.
- Each family section has a stable ID, references its in-scope partner and child occurrences, and exposes parent-child links with the Gramps-normalized relationship type for each parent when available. Each occurrence links back to its sections; generation, branch, path, and profile anchor provide the genealogy-marker data.

## Remaining before L4 exit

- `tests/test_genealogy_acceptance.py` qualifies AC-03 to AC-09 with synthetic graphs and also checks their LaTeX output: other-union context, parentage labels, one profile with cross-references, collateral relatives, family events, single-parent families, and depth boundaries.
- The LaTeX renderer consumes the `genealogy` model, with contract assertions for these scenarios. The full HTML renderer remains planned for L7; pagination, multipass references, and the final PDF appearance still need visual review in L6.
- The editorial model already provides profiles, family notices, an index, and navigation targets to the LaTeX renderer. These checks cover their textual structure, not the final paginated composition.
- The six central-family editorial notes and their Gramps 6 conventions still need separate validation.

See the [action plan](action-plan.fr.md#l4--parcours-généalogiques-et-sélection) and [requirements](requirements.fr.md) for the full tasks and exit criteria.
