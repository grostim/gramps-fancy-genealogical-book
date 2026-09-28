"""Editorial book skeleton assembled from the genealogy model."""

from collections.abc import Iterator
from dataclasses import fields, is_dataclass, replace
from unicodedata import combining, normalize

from .domain import (
    Citation,
    EditorialBook,
    EditorialCitationCall,
    EditorialCitationEntry,
    EditorialFamilyNotice,
    EditorialMediaPlacement,
    EditorialMediaUse,
    EditorialNavigationTarget,
    EditorialPart,
    EditorialPersonIndexEntry,
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
    RepositoryReference,
    Source,
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
    citations_by_handle: dict[str, Citation],
    sources_by_handle: dict[str, Source],
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
        notice_id = f"family-notice:{family_handle}"
        note_handles = _published_note_handles(family.links.notes, notes_by_handle)
        event_refs = _chronological_event_refs(family.links.events, events_by_handle)
        family_notices.append(
            EditorialFamilyNotice(
                notice_id=notice_id,
                family_handle=family_handle,
                primary_section_id=family_sections[0].section_id,
                family_section_ids=tuple(section.section_id for section in family_sections),
                note_handles=note_handles,
                event_refs=event_refs,
                media_refs=family.links.media,
                note_target_ids=tuple(
                    _contextual_target_id("note", notice_id, handle, index)
                    for index, handle in enumerate(note_handles)
                ),
                event_target_ids=tuple(
                    _contextual_target_id("event", notice_id, reference.event_handle, index)
                    for index, reference in enumerate(event_refs)
                ),
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
        note_handles = (
            _published_note_handles(person.links.notes, notes_by_handle)
            if person is not None
            else ()
        )
        event_refs = (
            _chronological_event_refs(person.links.events, events_by_handle)
            if person is not None
            else ()
        )
        profile_id = f"person:{person_handle}"
        profiles.append(
            EditorialProfile(
                profile_id=profile_id,
                person_handle=person_handle,
                primary_occurrence_id=(
                    primary.occurrence_id if primary is not None else None
                ),
                family_section_ids=family_section_ids,
                note_handles=note_handles,
                portrait=(
                    _primary_portrait(person, media_by_handle)
                    if person is not None
                    else None
                ),
                event_refs=event_refs,
                media_refs=person.links.media if person is not None else (),
                note_target_ids=tuple(
                    _contextual_target_id("note", profile_id, handle, index)
                    for index, handle in enumerate(note_handles)
                ),
                event_target_ids=tuple(
                    _contextual_target_id("event", profile_id, reference.event_handle, index)
                    for index, reference in enumerate(event_refs)
                ),
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
        citations_by_handle,
        sources_by_handle,
    )
    media_placements = _build_media_placements(
        profiles,
        family_notices,
        citation_entries,
        cover_portraits,
        media_by_handle,
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
    parts = (
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
    )
    person_index = _build_person_index(genealogy, people_by_handle)
    parts = tuple(
        replace(part, person_index_entry_ids=tuple(item.entry_id for item in person_index))
        if part.part_id == "person-index"
        else part
        for part in parts
    )
    book = EditorialBook(
        parts=parts,
        profiles=tuple(profiles),
        family_notices=tuple(family_notices),
        cover_portraits=tuple(cover_portraits),
        citation_entries=citation_entries,
        media_placements=media_placements,
    )
    book = replace(book, person_index=person_index)
    return replace(
        book,
        navigation_targets=_build_navigation_targets(book, genealogy),
    )


def _build_person_index(
    genealogy: Genealogy, people_by_handle: dict[str, Person]
) -> tuple[EditorialPersonIndexEntry, ...]:
    occurrences_by_person: dict[str, list[PersonOccurrence]] = {}
    for part in (genealogy.ancestry, genealogy.descent):
        for generation in part.generations:
            for occurrence in generation.occurrences:
                occurrences_by_person.setdefault(occurrence.person_handle, []).append(
                    occurrence
                )

    profile_handles = set(genealogy.profile_handles)
    entries = []
    for person_handle, occurrences in occurrences_by_person.items():
        occurrence_ids = tuple(
            dict.fromkeys(occurrence.occurrence_id for occurrence in occurrences)
        )
        primary_occurrence_id = next(
            (
                occurrence.primary_occurrence_id
                for occurrence in occurrences
                if occurrence.primary_occurrence_id
            ),
            occurrence_ids[0],
        )
        profile_id = (
            f"person:{person_handle}" if person_handle in profile_handles else None
        )
        person = people_by_handle.get(person_handle)
        display_name = person.name if person is not None else ""
        entries.append(
            EditorialPersonIndexEntry(
                entry_id=f"person-index:{person_handle}",
                person_handle=person_handle,
                display_name=display_name,
                target_id=profile_id or primary_occurrence_id,
                occurrence_ids=occurrence_ids,
                profile_id=profile_id,
                alternate_names=person.alternate_names if person is not None else (),
            )
        )
    return tuple(sorted(entries, key=_person_index_sort_key))


def _person_index_sort_key(
    entry: EditorialPersonIndexEntry,
) -> tuple[bool, str, str, str]:
    decomposed = normalize("NFKD", entry.display_name)
    primary_key = "".join(
        character for character in decomposed if not combining(character)
    ).casefold()
    return (
        not bool(primary_key),
        primary_key,
        entry.display_name.casefold(),
        entry.person_handle,
    )


def _build_navigation_targets(
    book: EditorialBook, genealogy: Genealogy
) -> tuple[EditorialNavigationTarget, ...]:
    targets: dict[str, EditorialNavigationTarget] = {}
    references: set[str] = set()

    def add_target(
        target_id: str,
        target_type: str,
        object_id: str,
        *,
        context_id: str | None = None,
    ) -> None:
        targets.setdefault(
            target_id,
            EditorialNavigationTarget(
                target_id=target_id,
                target_type=target_type,
                object_id=object_id,
                context_id=context_id,
            ),
        )

    _add_references(
        references,
        *(part.part_ids for part in book.parts),
        *(part.family_section_ids for part in book.parts),
        *(part.family_notice_ids for part in book.parts),
        *(part.citation_entry_ids for part in book.parts),
        *(part.person_occurrence_ids for part in book.parts),
        *(part.person_index_entry_ids for part in book.parts),
    )
    for part in book.parts:
        add_target(part.part_id, "part", part.part_id)

    for section in genealogy.family_sections:
        add_target(section.section_id, "family_section", section.family_handle)
        _add_references(
            references,
            section.partner_occurrence_ids,
            section.child_occurrence_ids,
            tuple(link.parent_occurrence_id for link in section.parent_child_links),
            tuple(link.child_occurrence_id for link in section.parent_child_links),
        )
    for genealogy_part in (genealogy.ancestry, genealogy.descent):
        for generation in genealogy_part.generations:
            for occurrence in generation.occurrences:
                add_target(occurrence.occurrence_id, "person_occurrence", occurrence.person_handle)
                _add_references(
                    references,
                    (occurrence.primary_occurrence_id,) if occurrence.primary_occurrence_id else (),
                    occurrence.family_section_ids,
                    (occurrence.profile_anchor,) if occurrence.profile_anchor else (),
                )

    for profile in book.profiles:
        add_target(profile.profile_id, "person_profile", profile.person_handle)
        _add_references(
            references,
            (profile.primary_occurrence_id,) if profile.primary_occurrence_id else (),
            profile.family_section_ids,
            profile.citation_call_ids,
            profile.note_target_ids,
            profile.event_target_ids,
            tuple(f"media:{reference.media_handle}" for reference in profile.media_refs),
            (
                (f"media:{profile.portrait.media_ref.media_handle}",)
                if profile.portrait is not None
                else ()
            ),
        )
        for target_id, note_handle in zip(profile.note_target_ids, profile.note_handles):
            add_target(
                target_id,
                "published_note",
                note_handle,
                context_id=profile.profile_id,
            )
        for target_id, event_ref in zip(profile.event_target_ids, profile.event_refs):
            add_target(
                target_id,
                "event_reference",
                event_ref.event_handle,
                context_id=profile.profile_id,
            )

    for notice in book.family_notices:
        add_target(notice.notice_id, "family_notice", notice.family_handle)
        _add_references(
            references,
            (notice.primary_section_id,),
            notice.family_section_ids,
            notice.citation_call_ids,
            notice.note_target_ids,
            notice.event_target_ids,
            tuple(f"media:{reference.media_handle}" for reference in notice.media_refs),
        )
        for target_id, note_handle in zip(notice.note_target_ids, notice.note_handles):
            add_target(
                target_id,
                "published_note",
                note_handle,
                context_id=notice.notice_id,
            )
        for target_id, event_ref in zip(notice.event_target_ids, notice.event_refs):
            add_target(
                target_id,
                "event_reference",
                event_ref.event_handle,
                context_id=notice.notice_id,
            )

    for entry in book.citation_entries:
        add_target(entry.entry_id, "citation_entry", entry.citation_handle)
        _add_references(
            references,
            tuple(call.call_id for call in entry.calls),
            tuple(f"citation:{call.citation_handle}" for call in entry.calls),
            tuple(f"media:{reference.media_handle}" for reference in entry.media_refs),
        )
        for call in entry.calls:
            add_target(call.call_id, "citation_call", call.citation_handle)
            _add_references(references, (call.context_id,))

    for placement in book.media_placements:
        add_target(placement.placement_id, "media_placement", placement.media_handle)
        for use in placement.uses:
            _add_references(references, (use.context_id,))

    for portrait in book.cover_portraits:
        _add_references(references, (f"media:{portrait.media_ref.media_handle}",))
    for entry in book.person_index:
        add_target(entry.entry_id, "person_index_entry", entry.person_handle)
        _add_references(references, (entry.target_id,))

    for target_id in references.difference(targets):
        targets[target_id] = EditorialNavigationTarget(
            target_id=target_id,
            target_type="out_of_scope",
            object_id=target_id,
            availability="out_of_scope",
        )
    return tuple(targets[target_id] for target_id in sorted(targets))


def _add_references(references: set[str], *groups: tuple[str, ...]) -> None:
    for group in groups:
        references.update(item for item in group if item)


def _contextual_target_id(
    target_type: str, context_id: str, object_id: str, index: int
) -> str:
    return f"{target_type}:{context_id}:{object_id}:{index}"


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
    citations_by_handle: dict[str, Citation],
    sources_by_handle: dict[str, Source],
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
            source_handle=(
                citation.source_handle
                if (citation := citations_by_handle.get(citation_handle)) is not None
                else None
            ),
            repository_refs=_citation_repository_refs(
                citation_handle,
                citations_by_handle,
                sources_by_handle,
            ),
            media_refs=_citation_media_refs(
                citation_handle,
                citations_by_handle,
                media_by_handle,
            ),
            calls=tuple(calls),
        )
        for citation_handle, calls in calls_by_citation.items()
    )
    return entries, {
        context_id: tuple(call_ids)
        for context_id, call_ids in call_ids_by_context.items()
    }


def _citation_repository_refs(
    citation_handle: str,
    citations_by_handle: dict[str, Citation],
    sources_by_handle: dict[str, Source],
) -> tuple[RepositoryReference, ...]:
    citation = citations_by_handle.get(citation_handle)
    if citation is None or citation.source_handle is None:
        return ()
    source = sources_by_handle.get(citation.source_handle)
    return source.repository_refs if source is not None else ()


def _citation_media_refs(
    citation_handle: str,
    citations_by_handle: dict[str, Citation],
    media_by_handle: dict[str, Media],
) -> tuple[MediaReference, ...]:
    citation = citations_by_handle.get(citation_handle)
    if citation is None:
        return ()
    return tuple(
        media_ref
        for media_ref in citation.links.media
        if (media := media_by_handle.get(media_ref.media_handle)) is not None
        and not media.is_excluded
    )


def _build_media_placements(
    profiles: list[EditorialProfile],
    family_notices: list[EditorialFamilyNotice],
    citation_entries: tuple[EditorialCitationEntry, ...],
    cover_portraits: list[EditorialPortrait],
    media_by_handle: dict[str, Media],
) -> tuple[EditorialMediaPlacement, ...]:
    uses_by_media: dict[str, list[EditorialMediaUse]] = {}

    def add_use(
        context_type: str,
        context_id: str,
        media_ref: MediaReference,
        citation_handles: tuple[str, ...] = (),
    ) -> None:
        media = media_by_handle.get(media_ref.media_handle)
        if media is None or media.is_excluded:
            return
        uses_by_media.setdefault(media.handle, []).append(
            EditorialMediaUse(
                context_type=context_type,
                context_id=context_id,
                media_ref=media_ref,
                citation_handles=tuple(dict.fromkeys(citation_handles)),
            )
        )

    for profile in profiles:
        for media_ref in profile.media_refs:
            add_use("profile", profile.profile_id, media_ref, media_ref.citations)

    for notice in family_notices:
        for media_ref in notice.media_refs:
            add_use("family_notice", notice.notice_id, media_ref, media_ref.citations)

    for entry in citation_entries:
        for media_ref in entry.media_refs:
            add_use(
                "citation",
                entry.entry_id,
                media_ref,
                (entry.citation_handle, *media_ref.citations),
            )

    for portrait in cover_portraits:
        add_use("cover", "cover", portrait.media_ref)

    return tuple(
        EditorialMediaPlacement(
            placement_id=f"media:{media_handle}",
            media_handle=media_handle,
            caption=media_by_handle[media_handle].description,
            is_featured=media_by_handle[media_handle].is_featured,
            uses=tuple(uses),
        )
        for media_handle, uses in uses_by_media.items()
    )


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
