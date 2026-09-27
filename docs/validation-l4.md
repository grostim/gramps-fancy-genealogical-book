# L4 progress — genealogy traversal

First increment prepared on 27 September 2026. L4 is still in progress; this note describes the implemented contract and does not claim that all acceptance scenarios have been qualified.

## Available traversal

- F0 must contain two known partners, which become P0 and P1 at generation 0.
- Ancestry and descendant limits are independent. `unlimited` is the default; zero or a non-negative integer can also be selected.
- The Gramps adapter recursively loads the families and people linked in those directions, then keeps unions and siblings as context. It does not expand the ancestry of a spouse introduced only through a descendant's union.
- The Gramps-independent engine produces negative and positive generations, family sections, occurrence roles, branch roots, and parentage paths.
- F0 appears as one section at the start of ancestry; the descendant part keeps the central occurrences as references. Children of ancestors' other unions appear as context without expanding their descendants.
- Explicit child-parent relationships recorded as `None` are not traversed. Single-parent families encountered in the graph remain valid.
- A path that revisits a person is kept as a visible occurrence, reported as a diagnostic, and stopped before the loop is expanded again.
- Profile eligibility follows `BOOK_PROFILE = YES` or a substantive individual/family event other than birth or death. Only the first occurrence gets the primary profile anchor; later occurrences retain its link.
- Generation order is deterministic. Complete exact birth dates sort chronologically; absent or uncertain dates use a stable identifier as their tie-breaker.

## Remaining before L4 exit

- Complex scenarios AC-03 to AC-09 (other unions, multiple parentage, pedigree collapse, collateral relatives, family events, and depth boundaries) still need qualification against a reference graph.
- The HTML and LaTeX renderers do not consume the `genealogy` model yet and remain contract demonstrations.
- The model does not yet create profiles, timelines, indexes, or editorial positions from L5.
- The six central-family editorial notes and their Gramps 6 conventions still need separate validation.

See the [action plan](action-plan.fr.md#l4--parcours-généalogiques-et-sélection) and [requirements](requirements.fr.md) for the full tasks and exit criteria.
