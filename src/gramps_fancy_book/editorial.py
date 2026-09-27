"""Editorial book skeleton assembled from the genealogy model."""

from .domain import EditorialBook, EditorialPart, Genealogy


def build_editorial_book(
    genealogy: Genealogy,
    reference_family_handle: str,
) -> EditorialBook:
    """Create the stable top-level book order and link it to in-scope records."""
    ancestry_sections = [
        section
        for section in genealogy.family_sections
        if section.part == "ancestry"
    ]
    central_section = next(
        (
            section
            for section in ancestry_sections
            if section.family_handle == reference_family_handle
            and "central" in section.roles
        ),
        None,
    )
    if central_section is not None:
        ancestry_sections.remove(central_section)
        ancestry_sections.insert(0, central_section)

    descent_sections = tuple(
        section
        for section in genealogy.family_sections
        if section.part == "descent"
    )

    person_occurrence_ids: list[str] = []
    seen_primary_occurrences: set[str] = set()
    for part in (genealogy.ancestry, genealogy.descent):
        for generation in part.generations:
            for occurrence in generation.occurrences:
                primary_id = occurrence.primary_occurrence_id or occurrence.occurrence_id
                if primary_id not in seen_primary_occurrences:
                    seen_primary_occurrences.add(primary_id)
                    person_occurrence_ids.append(primary_id)

    body_parts = ("front-matter", "ancestry", "descent", "documentary-appendix", "person-index")
    return EditorialBook(
        parts=(
            EditorialPart("cover", "cover"),
            EditorialPart("front-matter", "front_matter"),
            EditorialPart("contents", "table_of_contents", part_ids=body_parts),
            EditorialPart(
                "ancestry",
                "ancestry",
                family_section_ids=tuple(section.section_id for section in ancestry_sections),
            ),
            EditorialPart(
                "descent",
                "descent",
                family_section_ids=tuple(section.section_id for section in descent_sections),
            ),
            EditorialPart("documentary-appendix", "documentary_appendix"),
            EditorialPart(
                "person-index",
                "person_index",
                person_occurrence_ids=tuple(person_occurrence_ids),
            ),
        )
    )
