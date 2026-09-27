"""Editorial book skeleton assembled from the genealogy model."""

from collections.abc import Iterator
from dataclasses import fields, is_dataclass, replace

from .domain import (
    EditorialBook,
    EditorialCitationCall,
    EditorialCitationEntry,
    EditorialFamilyNotice,
    EditorialPart,
    EditorialPortrait,
    EditorialProfile,
    Event,
    EventReference,
    Family,
    FamilySection,
    Genealogy,
    Media,
    MediaReference,
    Note,
    Person,
    PersonOccurrence,
    Place,
)


def build_editorial_book(
    genealogy: Genealogy,
    reference_family_handle: str,
    people_by_handle: dict[str, Person],
    families_by_handle: dict[str, Family],
    notes_by_handle: dict[str, Note],
    media_by_handle: dict[str, Media],
    events_by_handle: dict[str, Event],
    places_by_handle: dict[str, Place],
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
                event_refs=_chronological_event_refs(family.links.events, events_by_handle),
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
                event_refs=(
                    _chronological_event_refs(person.links.events, events_by_handle)
                    if person is not None
                    else ()
                ),
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

    citation_entries, citation_call_ids = _build_citation_entries(
        profiles,
        family_notices,
        people_by_handle,
        families_by_handle,
        notes_by_handle,
        media_by_handle,
        events_by_handle,
        places_by_handle,
    )
    profiles = [
        replace(
            profile,
            citation_call_ids=citation_call_ids.get(profile.profile_id, ()),
        )
        for profile in profiles
    ]
    family_notices = [
        replace(
            notice,
            citation_call_ids=citation_call_ids.get(notice.notice_id, ()),
        )
        for notice in family_notices
    ]

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
            EditorialPart(
                "documentary-appendix",
                "documentary_appendix",
                citation_entry_ids=tuple(entry.entry_id for entry in citation_entries),
            ),
            EditorialPart(
                "person-index",
                "person_index",
                person_occurrence_ids=tuple(person_occurrence_ids),
            ),
        ),
        profiles=tuple(profiles),
        family_notices=tuple(family_notices),
        cover_portraits=tuple(cover_portraits),
        citation_entries=citation_entries,
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


def _chronological_event_refs(
    event_refs: tuple[EventReference, ...], events_by_handle: dict[str, Event]
) -> tuple[EventReference, ...]:
    def event_key(
        item: tuple[int, EventReference]
    ) -> tuple[bool, int, int, int, str]:
        original_index, reference = item
        event = events_by_handle.get(reference.event_handle)
        sort_value = (
            event.date.sort_value
            if event is not None and event.date is not None
            else None
        )
        return (
            sort_value is None,
            sort_value if sort_value is not None else 0,
            reference.order,
            original_index,
            reference.event_handle,
        )

    return tuple(
        reference for _, reference in sorted(enumerate(event_refs), key=event_key)
    )


def _build_citation_entries(
    profiles: list[EditorialProfile],
    family_notices: list[EditorialFamilyNotice],
    people_by_handle: dict[str, Person],
    families_by_handle: dict[str, Family],
    notes_by_handle: dict[str, Note],
    media_by_handle: dict[str, Media],
    events_by_handle: dict[str, Event],
    places_by_handle: dict[str, Place],
) -> tuple[tuple[EditorialCitationEntry, ...], dict[str, tuple[str, ...]]]:
    calls_by_citation: dict[str, list[EditorialCitationCall]] = {}
    call_ids_by_context: dict[str, list[str]] = {}

    def add_record(
        context_id: str,
        owner_type: str,
        owner_handle: str,
        path: str,
        record: object,
    ) -> None:
        for field_path, citation_handle in _citation_paths(record, path):
            call_id = f"citation-call:{context_id}:{field_path}"
            call = EditorialCitationCall(
                call_id=call_id,
                citation_handle=citation_handle,
                context_id=context_id,
                owner_type=owner_type,
                owner_handle=owner_handle,
                field_path=field_path,
            )
            calls_by_citation.setdefault(citation_handle, []).append(call)
            call_ids_by_context.setdefault(context_id, []).append(call_id)

    def add_event_context(
        context_id: str, reference_index: int, event_reference: EventReference
    ) -> None:
        event = events_by_handle.get(event_reference.event_handle)
        if event is None:
            return
        add_record(
            context_id,
            "event",
            event.handle,
            f"event[{reference_index}]:{event_reference.order}:{event.handle}",
            event,
        )
        if event.place_handle is not None:
            place = places_by_handle.get(event.place_handle)
            if place is not None:
                add_record(
                    context_id,
                    "place",
                    place.handle,
                    f"event[{reference_index}]:place:{place.handle}",
                    place,
                )

    def add_media_context(
        context_id: str, reference_index: int, media_ref: MediaReference
    ) -> None:
        media = media_by_handle.get(media_ref.media_handle)
        if media is not None:
            add_record(
                context_id,
                "media",
                media.handle,
                f"media[{reference_index}]:{media_ref.order}:{media.handle}",
                media,
            )

    for profile in profiles:
        person = people_by_handle.get(profile.person_handle)
        if person is None:
            continue
        add_record(profile.profile_id, "person", person.handle, "person", person)
        for index, event_reference in enumerate(profile.event_refs):
            add_event_context(profile.profile_id, index, event_reference)
        for index, media_reference in enumerate(profile.media_refs):
            add_media_context(profile.profile_id, index, media_reference)
        for index, note_handle in enumerate(profile.note_handles):
            note = notes_by_handle.get(note_handle)
            if note is not None:
                add_record(
                    profile.profile_id,
                    "note",
                    note.handle,
                    f"note:{index}:{note.handle}",
                    note,
                )

    for notice in family_notices:
        family = families_by_handle.get(notice.family_handle)
        if family is None:
            continue
        add_record(notice.notice_id, "family", family.handle, "family", family)
        for index, event_reference in enumerate(notice.event_refs):
            add_event_context(notice.notice_id, index, event_reference)
        for index, media_reference in enumerate(notice.media_refs):
            add_media_context(notice.notice_id, index, media_reference)
        for index, note_handle in enumerate(notice.note_handles):
            note = notes_by_handle.get(note_handle)
            if note is not None:
                add_record(
                    notice.notice_id,
                    "note",
                    note.handle,
                    f"note:{index}:{note.handle}",
                    note,
                )

    entries = tuple(
        EditorialCitationEntry(
            entry_id=f"citation:{citation_handle}",
            citation_handle=citation_handle,
            calls=tuple(calls),
        )
        for citation_handle, calls in calls_by_citation.items()
    )
    return entries, {
        context_id: tuple(call_ids)
        for context_id, call_ids in call_ids_by_context.items()
    }


def _citation_paths(value: object, path: str) -> Iterator[tuple[str, str]]:
    if is_dataclass(value) and not isinstance(value, type):
        for item in fields(value):
            if isinstance(value, Family) and item.name in {"father", "mother", "children"}:
                continue
            child = getattr(value, item.name)
            child_path = f"{path}.{item.name}"
            if item.name == "citations":
                for index, citation_handle in enumerate(child):
                    yield f"{child_path}[{index}]", citation_handle
            elif isinstance(child, dict):
                for key in sorted(child, key=str):
                    yield from _citation_paths(child[key], f"{child_path}[{key}]")
            elif isinstance(child, (tuple, list)):
                for index, item_value in enumerate(child):
                    yield from _citation_paths(item_value, f"{child_path}[{index}]")
            else:
                yield from _citation_paths(child, child_path)
    elif isinstance(value, dict):
        for key in sorted(value, key=str):
            yield from _citation_paths(value[key], f"{path}[{key}]")
    elif isinstance(value, (tuple, list)):
        for index, item_value in enumerate(value):
            yield from _citation_paths(item_value, f"{path}[{index}]")
