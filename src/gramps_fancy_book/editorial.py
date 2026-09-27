"""Editorial book skeleton assembled from the genealogy model."""

from .domain import (
    EditorialBook,
    EditorialFamilyNotice,
    EditorialPart,
    EditorialPortrait,
    EditorialProfile,
    Family,
    FamilySection,
    Genealogy,
    Media,
    MediaReference,
    Note,
    Person,
    PersonOccurrence,
)


def build_editorial_book(
    genealogy: Genealogy,
    reference_family_handle: str,
    people_by_handle: dict[str, Person],
    families_by_handle: dict[str, Family],
    notes_by_handle: dict[str, Note],
    media_by_handle: dict[str, Media],
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
    ordered_sections = (*ancestry_sections, *descent_sections)
    sections_by_family: dict[str, list[FamilySection]] = {}
    for section in ordered_sections:
        sections_by_family.setdefault(section.family_handle, []).append(section)

    family_notices: list[EditorialFamilyNotice] = []
    ancestry_section_ids = {section.section_id for section in ancestry_sections}
    descent_section_ids = {section.section_id for section in descent_sections}
    for family_handle, family_sections in sections_by_family.items():
        family = families_by_handle.get(family_handle)
        if family is None:
            continue
        family_notices.append(
            EditorialFamilyNotice(
                notice_id=f"family-notice:{family_handle}",
                family_handle=family_handle,
                primary_section_id=family_sections[0].section_id,
                family_section_ids=tuple(section.section_id for section in family_sections),
                note_handles=_published_note_handles(family.links.notes, notes_by_handle),
                event_refs=family.links.events,
                media_refs=family.links.media,
            )
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

    occurrences_by_person: dict[str, list[PersonOccurrence]] = {}
    for part in (genealogy.ancestry, genealogy.descent):
        for generation in part.generations:
            for occurrence in generation.occurrences:
                occurrences_by_person.setdefault(
                    occurrence.person_handle, []
                ).append(occurrence)

    profiles = []
    for person_handle in genealogy.profile_handles:
        person = people_by_handle.get(person_handle)
        person_occurrences = occurrences_by_person.get(person_handle, ())
        primary = next(
            (
                occurrence
                for occurrence in person_occurrences
                if occurrence.is_primary_profile
            ),
            None,
        )
        family_section_ids = tuple(
            dict.fromkeys(
                section_id
                for occurrence in person_occurrences
                for section_id in occurrence.family_section_ids
            )
        )
        profiles.append(
            EditorialProfile(
                profile_id=f"person:{person_handle}",
                person_handle=person_handle,
                primary_occurrence_id=(
                    primary.occurrence_id if primary is not None else None
                ),
                family_section_ids=family_section_ids,
                note_handles=(
                    _published_note_handles(person.links.notes, notes_by_handle)
                    if person is not None
                    else ()
                ),
                portrait=(
                    _primary_portrait(person, media_by_handle)
                    if person is not None
                    else None
                ),
                event_refs=person.links.events if person is not None else (),
                media_refs=person.links.media if person is not None else (),
            )
        )

    reference_family = families_by_handle.get(reference_family_handle)
    cover_portraits = []
    for person in (
        (reference_family.father, reference_family.mother)
        if reference_family is not None
        else ()
    ):
        if person is None:
            continue
        portrait = _primary_portrait(person, media_by_handle)
        if portrait is not None:
            cover_portraits.append(portrait)

    body_parts = (
        "front-matter",
        "ancestry",
        "descent",
        "documentary-appendix",
        "person-index",
    )
    return EditorialBook(
        parts=(
            EditorialPart("cover", "cover"),
            EditorialPart("front-matter", "front_matter"),
            EditorialPart("contents", "table_of_contents", part_ids=body_parts),
            EditorialPart(
                "ancestry",
                "ancestry",
                family_section_ids=tuple(section.section_id for section in ancestry_sections),
                family_notice_ids=tuple(
                    notice.notice_id
                    for notice in family_notices
                    if notice.primary_section_id in ancestry_section_ids
                ),
            ),
            EditorialPart(
                "descent",
                "descent",
                family_section_ids=tuple(section.section_id for section in descent_sections),
                family_notice_ids=tuple(
                    notice.notice_id
                    for notice in family_notices
                    if notice.primary_section_id in descent_section_ids
                ),
            ),
            EditorialPart("documentary-appendix", "documentary_appendix"),
            EditorialPart(
                "person-index",
                "person_index",
                person_occurrence_ids=tuple(person_occurrence_ids),
            ),
        ),
        profiles=tuple(profiles),
        family_notices=tuple(family_notices),
        cover_portraits=tuple(cover_portraits),
    )


def _published_note_handles(
    note_handles: tuple[str, ...], notes_by_handle: dict[str, Note]
) -> tuple[str, ...]:
    return tuple(
        handle
        for handle in note_handles
        if (note := notes_by_handle.get(handle)) is not None and note.is_publishable
    )


def _primary_portrait(
    person: Person, media_by_handle: dict[str, Media]
) -> EditorialPortrait | None:
    for media_ref in person.links.media:
        media = media_by_handle.get(media_ref.media_handle)
        if (
            media is not None
            and media.mime_type.casefold().startswith("image/")
            and not media.is_excluded
        ):
            return EditorialPortrait(
                person_handle=person.handle,
                media_ref=media_ref,
                caption=media.description,
            )
    return None
