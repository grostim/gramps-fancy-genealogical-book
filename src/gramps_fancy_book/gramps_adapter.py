"""Read-only boundary between Gramps and the framework-independent model."""

from collections import defaultdict, deque
from typing import Any, Protocol

from .conventions import BOOK_EXCLUDE, BOOK_FEATURED, BOOK_PROFILE, BOOK_PUBLICATION
from .domain import (
    Address,
    Attribute,
    ChildRelationship,
    Citation,
    DateValue,
    Diagnostic,
    Event,
    EventReference,
    Family,
    Media,
    MediaReference,
    Note,
    ObjectLinks,
    Person,
    PersonRelationship,
    Place,
    Repository,
    RepositoryReference,
    Snapshot,
    Source,
    Tag,
    Url,
)


class FamilySource(Protocol):
    def get_family(self, handle: str) -> Family: ...


_GETTERS = {
    "family": "get_family_from_handle",
    "person": "get_person_from_handle",
    "event": "get_event_from_handle",
    "place": "get_place_from_handle",
    "note": "get_note_from_handle",
    "citation": "get_citation_from_handle",
    "source": "get_source_from_handle",
    "repository": "get_repository_from_handle",
    "media": "get_media_from_handle",
    "tag": "get_tag_from_handle",
}


class GrampsDatabaseAdapter:
    """Extract Gramps objects without changing the database or filtering private data."""

    def __init__(self, database: object, *, date_language: str | None = None) -> None:
        self.database = database
        self._date_displayer = None
        if date_language:
            try:
                from gramps.gen.utils.grampslocale import GrampsLocale
            except ImportError:
                pass
            else:
                self._date_displayer = GrampsLocale(lang=date_language).date_displayer
        self._cache: dict[str, dict[str, Any]] = defaultdict(dict)
        self._diagnostics: list[Diagnostic] = []
        self._diagnostic_keys: set[tuple[str, str, str]] = set()
        self._records: dict[str, dict[str, Any]] = defaultdict(dict)

    def get_family(self, handle: str) -> Family:
        """Keep the original small FamilySource contract for simple callers."""
        family = self._get_primary("family", handle)
        if family is None:
            raise LookupError(f"No family exists for handle {handle!r}")

        father = self._simple_person(_call(family, "get_father_handle"), required=True)
        mother = self._simple_person(_call(family, "get_mother_handle"), required=True)
        children = []
        for child_ref in _sequence(family, "get_child_ref_list"):
            child_handle = getattr(child_ref, "ref", None)
            if not child_handle:
                raise LookupError("Family contains a child reference without a handle.")
            person = self._simple_person(child_handle, required=True)
            if person is None:
                raise LookupError(f"Family references an unavailable person: {child_handle!r}")
            children.append(person)

        return Family(
            handle=_string(_call(family, "get_handle", handle)),
            gramps_id=_string(_call(family, "get_gramps_id", "")),
            father=father,
            mother=mother,
            children=tuple(children),
        )

    def get_family_by_gramps_id(self, gramps_id: str) -> Family:
        if not gramps_id:
            raise ValueError("Select a reference family.")
        family = self.database.get_family_from_gramps_id(gramps_id)
        if family is None:
            raise LookupError(f"No family exists for Gramps ID {gramps_id!r}")
        return self.get_family(family.get_handle())

    def read_snapshot(
        self,
        family_handle: str,
        max_ancestor_depth: int | None = None,
        max_descendant_depth: int | None = None,
    ) -> Snapshot:
        """Read the selected couple's directed genealogy and required family context."""
        self._reset_snapshot_state()
        return self._read_snapshot(family_handle, max_ancestor_depth, max_descendant_depth)

    def read_snapshot_by_gramps_id(
        self,
        gramps_id: str,
        max_ancestor_depth: int | None = None,
        max_descendant_depth: int | None = None,
    ) -> Snapshot:
        if not gramps_id:
            raise ValueError("Select a reference family.")
        self._reset_snapshot_state()
        family = self.database.get_family_from_gramps_id(gramps_id)
        if family is None:
            raise LookupError(f"No family exists for Gramps ID {gramps_id!r}")
        handle = _string(_call(family, "get_handle", ""))
        self._cache["family"][handle] = family
        return self._read_snapshot(handle, max_ancestor_depth, max_descendant_depth)

    def _reset_snapshot_state(self) -> None:
        self._cache = defaultdict(dict)
        self._diagnostics = []
        self._diagnostic_keys = set()
        self._records = defaultdict(dict)

    def _read_snapshot(
        self,
        family_handle: str,
        max_ancestor_depth: int | None,
        max_descendant_depth: int | None,
    ) -> Snapshot:
        _validate_depth(max_ancestor_depth, "ancestry")
        _validate_depth(max_descendant_depth, "descendant")
        reference_family = self._family_record(family_handle, required=True)
        if reference_family.father is None or reference_family.mother is None:
            raise ValueError("The reference family must have two known partners.")
        roots = (reference_family.father.handle, reference_family.mother.handle)
        contextual_people = self._expand_ancestors(roots, max_ancestor_depth)
        contextual_people.update(
            self._expand_descendants(roots, max_descendant_depth, family_handle)
        )
        self._load_contextual_unions(contextual_people)
        associated_people = {
            relation.person_handle
            for person in self._records["person"].values()
            for relation in person.relationships
        }
        for person_handle in sorted(associated_people):
            self._person_record(person_handle, required=False, context="person association")

        self._hydrate_references()
        return Snapshot(
            reference_family=reference_family,
            families=dict(self._records["family"]),
            people=dict(self._records["person"]),
            events=dict(self._records["event"]),
            places=dict(self._records["place"]),
            notes=dict(self._records["note"]),
            citations=dict(self._records["citation"]),
            sources=dict(self._records["source"]),
            repositories=dict(self._records["repository"]),
            media=dict(self._records["media"]),
            tags=dict(self._records["tag"]),
            diagnostics=list(self._diagnostics),
        )

    def _expand_ancestors(self, roots: tuple[str, str], limit: int | None) -> set[str]:
        queue = deque((handle, 0) for handle in dict.fromkeys(roots))
        visited: set[str] = set()
        contextual_people: set[str] = set()
        while queue:
            person_handle, depth = queue.popleft()
            if person_handle in visited:
                continue
            visited.add(person_handle)
            person = self._records["person"].get(person_handle)
            if person is None:
                continue
            for family_handle in person.family_handles:
                family = self._family_record(family_handle, required=False)
                if family is not None:
                    contextual_people.update(
                        partner.handle for partner in (family.father, family.mother)
                        if partner is not None and partner.handle != person_handle
                    )
                    if depth > 0:
                        for child in family.children:
                            relationship = next(
                                (
                                    item for item in family.child_relationships
                                    if item.person_handle == child.handle
                                ),
                                None,
                            )
                            if not _child_link_is_none(family, relationship, person_handle):
                                contextual_people.add(child.handle)
            if limit is not None and depth >= limit:
                continue
            for family_handle in person.parent_family_handles:
                family = self._family_record(family_handle, required=False)
                if family is None:
                    continue
                if depth > 0:
                    contextual_people.update(
                        child.handle for child in family.children
                        if child.handle != person_handle
                    )
                relationship = next(
                    (
                        item for item in family.child_relationships
                        if item.person_handle == person_handle
                    ),
                    None,
                )
                for parent in (family.father, family.mother):
                    if parent is None or _child_link_is_none(family, relationship, parent.handle):
                        continue
                    queue.append((parent.handle, depth + 1))

        return contextual_people

    def _expand_descendants(
        self,
        roots: tuple[str, str],
        limit: int | None,
        central_family_handle: str,
    ) -> set[str]:
        queue = deque((handle, 0) for handle in dict.fromkeys(roots))
        visited: set[str] = set()
        contextual_people: set[str] = set()
        while queue:
            person_handle, depth = queue.popleft()
            if person_handle in visited:
                continue
            visited.add(person_handle)
            person = self._records["person"].get(person_handle)
            if person is None:
                continue
            family_handles = list(person.family_handles)
            if depth == 0 and central_family_handle not in family_handles:
                family_handles.append(central_family_handle)
            for family_handle in family_handles:
                family = self._family_record(family_handle, required=False)
                if family is None:
                    continue
                contextual_people.update(
                    partner.handle for partner in (family.father, family.mother)
                    if partner is not None and partner.handle != person_handle
                )
                if limit is not None and depth >= limit:
                    continue
                for child in family.children:
                    relationship = next(
                        (
                            item for item in family.child_relationships
                            if item.person_handle == child.handle
                        ),
                        None,
                    )
                    if not _child_link_is_none(family, relationship, person_handle):
                        queue.append((child.handle, depth + 1))
        return contextual_people

    def _load_contextual_unions(self, person_handles: set[str]) -> None:
        """Load one-hop unions for profile eligibility without traversing descendants."""
        for person_handle in sorted(person_handles):
            person = self._records["person"].get(person_handle)
            if person is None:
                continue
            for family_handle in person.family_handles:
                self._family_record(family_handle, required=False)

    def _get_primary(self, kind: str, handle: str | None) -> Any:
        if not handle:
            return None
        if handle not in self._cache[kind]:
            method = getattr(self.database, _GETTERS[kind])
            self._cache[kind][handle] = method(handle)
        return self._cache[kind][handle]

    def _simple_person(self, handle: str | None, *, required: bool = False) -> Person | None:
        if not handle:
            return None
        person = self._get_primary("person", handle)
        if person is None:
            if required:
                raise LookupError(f"Family references an unavailable person: {handle!r}")
            return None
        name = _call(_call(person, "get_primary_name"), "get_name", "")
        return Person(
            handle=handle,
            name=_string(name),
            gramps_id=_string(_call(person, "get_gramps_id", "")),
        )

    def _family_record(self, handle: str, *, required: bool) -> Family | None:
        if handle in self._records["family"]:
            return self._records["family"][handle]
        obj = self._get_primary("family", handle)
        if obj is None:
            if required:
                raise LookupError(f"No family exists for handle {handle!r}")
            self._diagnose("missing_reference", "family", handle, "Family reference is unavailable.")
            return None

        father = self._person_record(_call(obj, "get_father_handle"), required=required)
        mother = self._person_record(_call(obj, "get_mother_handle"), required=required)
        children: list[Person] = []
        child_relationships: list[ChildRelationship] = []
        for index, child_ref in enumerate(_sequence(obj, "get_child_ref_list")):
            child_handle = getattr(child_ref, "ref", None)
            if not child_handle:
                if required:
                    raise LookupError("Family contains a child reference without a handle.")
                self._diagnose(
                    "missing_person_handle", "family", handle,
                    "Child reference has no person handle.",
                )
                continue
            child = self._person_record(child_handle, required=required, context=handle)
            if child is None:
                continue
            children.append(child)
            child_relationships.append(
                ChildRelationship(
                    person_handle=child_handle,
                    father_relation=_plain_relation(_call(child_ref, "get_father_relation")),
                    mother_relation=_plain_relation(_call(child_ref, "get_mother_relation")),
                    order=index,
                    citations=tuple(_sequence(child_ref, "get_citation_list")),
                    notes=tuple(_sequence(child_ref, "get_note_list")),
                    private=_optional_bool(child_ref, "get_privacy"),
                )
            )

        record = Family(
            handle=_string(_call(obj, "get_handle", handle)),
            gramps_id=_string(_call(obj, "get_gramps_id", "")),
            father=father,
            mother=mother,
            children=tuple(children),
            relationship=_type_text(_call(obj, "get_relationship")),
            child_relationships=tuple(child_relationships),
            links=self._object_links(obj, include_events=True),
        )
        self._records["family"][handle] = record
        return record

    def _person_record(
        self, handle: str | None, *, required: bool, context: str = ""
    ) -> Person | None:
        if not handle:
            return None
        if handle in self._records["person"]:
            return self._records["person"][handle]
        obj = self._get_primary("person", handle)
        if obj is None:
            if required:
                raise LookupError(f"Family references an unavailable person: {handle!r}")
            self._diagnose("missing_reference", "person", handle, "Person reference is unavailable.", context)
            return None
        primary_name = _call(obj, "get_primary_name")
        name = _call(primary_name, "get_name", "")
        alternate_names = tuple(
            _string(_call(name_obj, "get_name", name_obj))
            for name_obj in _sequence(obj, "get_alternate_names")
        )
        relationships = []
        for index, relation_ref in enumerate(_sequence(obj, "get_person_ref_list")):
            related_handle = getattr(relation_ref, "ref", None)
            if not related_handle:
                self._diagnose(
                    "missing_person_handle", "person", handle,
                    "Person association has no referenced person handle.",
                )
                continue
            relationships.append(
                PersonRelationship(
                    person_handle=_string(related_handle),
                    relation=_string(_call(relation_ref, "get_relation", "") or getattr(relation_ref, "rel", "")),
                    order=index,
                    citations=tuple(_sequence(relation_ref, "get_citation_list")),
                    notes=tuple(_sequence(relation_ref, "get_note_list")),
                    private=_optional_bool(relation_ref, "get_privacy"),
                )
            )
        links = self._object_links(obj, include_events=True)
        for attribute in links.attributes:
            if attribute.type == BOOK_PROFILE and attribute.value != "YES":
                self._diagnose(
                    "invalid_metadata_value", "person", handle,
                    f"{BOOK_PROFILE} must have the value YES to force a profile.",
                )
        record = Person(
            handle=_string(_call(obj, "get_handle", handle)),
            name=_string(name),
            gramps_id=_string(_call(obj, "get_gramps_id", "")),
            alternate_names=alternate_names,
            gender=_plain_relation(_call(obj, "get_gender")),
            family_handles=tuple(_sequence(obj, "get_family_handle_list")),
            parent_family_handles=tuple(_sequence(obj, "get_parent_family_handle_list")),
            relationships=tuple(relationships),
            addresses=tuple(self._address(address, index) for index, address in enumerate(_sequence(obj, "get_address_list"))),
            urls=self._urls(obj),
            links=links,
        )
        self._records["person"][handle] = record
        return record

    def _object_links(self, obj: Any, *, include_events: bool = False) -> ObjectLinks:
        events = ()
        if include_events:
            event_refs = _sequence(obj, "get_event_ref_list")
            events = tuple(
                EventReference(
                    event_handle=_string(getattr(ref, "ref", "")),
                    role=_type_text(_call(ref, "get_role")),
                    order=index,
                    citations=tuple(_sequence(ref, "get_citation_list")),
                    notes=tuple(_sequence(ref, "get_note_list")),
                    attributes=tuple(self._attribute(attribute) for attribute in _sequence(ref, "get_attribute_list")),
                    private=_optional_bool(ref, "get_privacy"),
                )
                for index, ref in enumerate(event_refs)
                if getattr(ref, "ref", None)
            )
            for ref in event_refs:
                if not getattr(ref, "ref", None):
                    self._diagnose(
                        "missing_event_handle", "event", "", "Event reference has no handle.",
                        _string(_call(obj, "get_handle", "")),
                    )

        return ObjectLinks(
            citations=tuple(_sequence(obj, "get_citation_list")),
            notes=tuple(_sequence(obj, "get_note_list")),
            tag_handles=tuple(_sequence(obj, "get_tag_list")),
            attributes=tuple(self._attribute(attribute) for attribute in _sequence(obj, "get_attribute_list")),
            media=tuple(
                self._media_reference(ref, index)
                for index, ref in enumerate(_sequence(obj, "get_media_list"))
                if getattr(ref, "ref", None)
            ),
            events=events,
            private=_optional_bool(obj, "get_privacy"),
        )

    def _address(self, obj: Any, order: int) -> Address:
        return Address(
            street=_string(_call(obj, "get_street", "")),
            locality=_string(_call(obj, "get_locality", "")),
            city=_string(_call(obj, "get_city", "")),
            county=_string(_call(obj, "get_county", "")),
            state=_string(_call(obj, "get_state", "")),
            country=_string(_call(obj, "get_country", "")),
            postal=_string(_call(obj, "get_postal_code", "") or _call(obj, "get_postal", "")),
            phone=_string(_call(obj, "get_phone", "")),
            date=self._date(obj),
            order=order,
            citations=tuple(_sequence(obj, "get_citation_list")),
            notes=tuple(_sequence(obj, "get_note_list")),
            private=_optional_bool(obj, "get_privacy"),
        )

    def _media_reference(self, ref: Any, index: int) -> MediaReference:
        rectangle = _call(ref, "get_rectangle")
        return MediaReference(
            media_handle=_string(getattr(ref, "ref", "")),
            rectangle=tuple(rectangle) if rectangle else None,
            order=index,
            private=_optional_bool(ref, "get_privacy"),
            citations=tuple(_sequence(ref, "get_citation_list")),
            notes=tuple(_sequence(ref, "get_note_list")),
            attributes=tuple(self._attribute(attribute) for attribute in _sequence(ref, "get_attribute_list")),
        )

    def _attribute(self, obj: Any) -> Attribute:
        return Attribute(
            type=_type_text(_call(obj, "get_type")),
            value=_string(_call(obj, "get_value", "")),
            citations=tuple(_sequence(obj, "get_citation_list")),
            notes=tuple(_sequence(obj, "get_note_list")),
            private=_optional_bool(obj, "get_privacy"),
        )

    def _date(self, obj: Any) -> DateValue | None:
        if obj is None:
            return None
        raw_date = _call(obj, "get_date_object")
        if raw_date is None:
            return None
        ymd = _call(raw_date, "get_ymd")
        stop_ymd = _call(raw_date, "get_stop_ymd")
        sort_value = _call(raw_date, "get_sort_value")
        text = _string(_call(raw_date, "get_text", ""))
        date_displayer = self._date_displayer
        if date_displayer is None:
            try:
                from gramps.gen.datehandler import displayer as date_displayer
            except ImportError:
                date_displayer = None
        display = (
            _string(date_displayer.display(raw_date)) or text
            if date_displayer is not None
            else text
        )
        return DateValue(
            display=display,
            sort_value=int(sort_value) if sort_value not in (None, 0) else None,
            modifier=_integer_or_none(_call(raw_date, "get_modifier")),
            quality=_integer_or_none(_call(raw_date, "get_quality")),
            calendar=_integer_or_none(_call(raw_date, "get_calendar")),
            ymd=tuple(ymd) if ymd else None,
            stop_ymd=tuple(stop_ymd) if stop_ymd else None,
            range=_plain_relation(_call(raw_date, "get_start_stop_range")),
            raw=_plain_relation(_call(raw_date, "serialize")),
        )

    def _event_record(self, handle: str) -> Event | None:
        if handle in self._records["event"]:
            return self._records["event"][handle]
        obj = self._optional_primary("event", handle, "Event reference is unavailable.")
        if obj is None:
            return None
        place_handle = _call(obj, "get_place_handle") or None
        record = Event(
            handle=_string(_call(obj, "get_handle", handle)),
            gramps_id=_string(_call(obj, "get_gramps_id", "")),
            type=_type_text(_call(obj, "get_type")),
            description=_string(_call(obj, "get_description", "")),
            date=self._date(obj),
            place_handle=_string(place_handle) if place_handle else None,
            links=self._object_links(obj),
        )
        self._records["event"][handle] = record
        return record

    def _place_record(self, handle: str) -> Place | None:
        if handle in self._records["place"]:
            return self._records["place"][handle]
        obj = self._optional_primary("place", handle, "Place reference is unavailable.")
        if obj is None:
            return None
        place_name = _call(obj, "get_name")
        name = _call(place_name, "get_value", place_name)
        record = Place(
            handle=_string(_call(obj, "get_handle", handle)),
            gramps_id=_string(_call(obj, "get_gramps_id", "")),
            name=_string(name),
            title=_string(_call(obj, "get_title", "")),
            links=self._object_links(obj),
        )
        self._records["place"][handle] = record
        return record

    def _note_record(self, handle: str) -> Note | None:
        if handle in self._records["note"]:
            return self._records["note"][handle]
        obj = self._optional_primary("note", handle, "Note reference is unavailable.")
        if obj is None:
            return None
        links = self._object_links(obj)
        publishable = any(
            self._tag_name(tag_handle) == BOOK_PUBLICATION for tag_handle in links.tag_handles
        )
        styled_text = _call(obj, "get_styledtext") if publishable else None
        styled_tags = tuple(
            _plain_relation(_call(tag, "serialize"))
            for tag in _sequence(styled_text, "get_tags")
        )
        return self._store(
            "note",
            handle,
            Note(
                handle=_string(_call(obj, "get_handle", handle)),
                gramps_id=_string(_call(obj, "get_gramps_id", "")),
                text=_string(styled_text) if publishable and styled_text is not None else None,
                format=_plain_relation(_call(obj, "get_format")),
                type=_plain_relation(_call(obj, "get_type")),
                is_publishable=publishable,
                styled_tags=styled_tags,
                links=links,
            ),
        )

    def _citation_record(self, handle: str) -> Citation | None:
        if handle in self._records["citation"]:
            return self._records["citation"][handle]
        obj = self._optional_primary("citation", handle, "Citation reference is unavailable.")
        if obj is None:
            return None
        source_handle = _call(obj, "get_reference_handle") or None
        return self._store(
            "citation",
            handle,
            Citation(
                handle=_string(_call(obj, "get_handle", handle)),
                gramps_id=_string(_call(obj, "get_gramps_id", "")),
                source_handle=_string(source_handle) if source_handle else None,
                page=_string(_call(obj, "get_page", "")),
                date=self._date(obj),
            confidence=_plain_relation(_call(obj, "get_confidence_level")),
                urls=self._urls(obj),
                links=self._object_links(obj),
            ),
        )

    def _source_record(self, handle: str) -> Source | None:
        if handle in self._records["source"]:
            return self._records["source"][handle]
        obj = self._optional_primary("source", handle, "Source reference is unavailable.")
        if obj is None:
            return None
        refs = []
        for index, ref in enumerate(_sequence(obj, "get_reporef_list")):
            repository_handle = getattr(ref, "ref", None) or _call(ref, "get_reference_handle")
            if not repository_handle:
                self._diagnose(
                    "missing_repository_handle", "repository", "",
                    "Repository reference has no handle.", handle,
                )
                continue
            refs.append(
                RepositoryReference(
                    repository_handle=_string(repository_handle),
                    call_number=_string(_call(ref, "get_call_number", "")),
                    media_type=_type_text(_call(ref, "get_media_type")),
                    order=index,
                    notes=tuple(_sequence(ref, "get_note_list")),
                    private=_optional_bool(ref, "get_privacy"),
                )
            )
        return self._store(
            "source",
            handle,
            Source(
                handle=_string(_call(obj, "get_handle", handle)),
                gramps_id=_string(_call(obj, "get_gramps_id", "")),
                title=_string(_call(obj, "get_title", "")),
                author=_string(_call(obj, "get_author", "")),
                publication_info=_string(_call(obj, "get_publication_info", "")),
                abbreviation=_string(_call(obj, "get_abbreviation", "")),
                repository_refs=tuple(refs),
                urls=self._urls(obj),
                links=self._object_links(obj),
            ),
        )

    def _repository_record(self, handle: str) -> Repository | None:
        if handle in self._records["repository"]:
            return self._records["repository"][handle]
        obj = self._optional_primary("repository", handle, "Repository reference is unavailable.")
        if obj is None:
            return None
        return self._store(
            "repository",
            handle,
            Repository(
                handle=_string(_call(obj, "get_handle", handle)),
                gramps_id=_string(_call(obj, "get_gramps_id", "")),
                name=_string(_call(obj, "get_name", "")),
                type=_type_text(_call(obj, "get_type")),
                urls=self._urls(obj),
                links=self._object_links(obj),
            ),
        )

    def _media_record(self, handle: str) -> Media | None:
        if handle in self._records["media"]:
            return self._records["media"][handle]
        obj = self._optional_primary("media", handle, "Media reference is unavailable.")
        if obj is None:
            return None
        tag_handles = tuple(_sequence(obj, "get_tag_list"))
        tag_names = {self._tag_name(tag_handle) for tag_handle in tag_handles}
        return self._store(
            "media",
            handle,
            Media(
                handle=_string(_call(obj, "get_handle", handle)),
                gramps_id=_string(_call(obj, "get_gramps_id", "")),
                path=_string(_call(obj, "get_path", "")),
                description=_string(_call(obj, "get_description", "")),
                mime_type=_string(_call(obj, "get_mime_type", "")),
                checksum=_string(_call(obj, "get_checksum", "")),
                tag_handles=tag_handles,
                is_excluded=BOOK_EXCLUDE in tag_names,
                is_featured=BOOK_FEATURED in tag_names,
                links=self._object_links(obj),
            ),
        )

    def _tag_record(self, handle: str) -> Tag | None:
        if handle in self._records["tag"]:
            return self._records["tag"][handle]
        obj = self._optional_primary("tag", handle, "Tag reference is unavailable.")
        if obj is None:
            return None
        return self._store(
            "tag",
            handle,
            Tag(handle=_string(_call(obj, "get_handle", handle)), name=_string(_call(obj, "get_name", ""))),
        )

    def _tag_name(self, handle: str) -> str:
        tag = self._tag_record(handle)
        return tag.name if tag else ""

    def _urls(self, obj: Any) -> tuple[Url, ...]:
        values = []
        for url in _sequence(obj, "get_url_list"):
            values.append(
                Url(
                    path=_string(_call(url, "get_path", "")),
                    description=_string(_call(url, "get_description", "")),
                    type=_type_text(_call(url, "get_type")),
                )
            )
        return tuple(values)

    def _optional_primary(self, kind: str, handle: str, message: str) -> Any:
        obj = self._get_primary(kind, handle)
        if obj is None:
            self._diagnose("missing_reference", kind, handle, message)
        return obj

    def _store(self, kind: str, handle: str, record: Any) -> Any:
        self._records[kind][handle] = record
        return record

    def _diagnose(
        self, code: str, object_type: str, handle: str, message: str, context: str = ""
    ) -> None:
        key = code, object_type, handle
        if key in self._diagnostic_keys:
            return
        self._diagnostic_keys.add(key)
        self._diagnostics.append(
            Diagnostic(
                code=code,
                severity="warning",
                object_type=object_type,
                handle=handle,
                message=message,
                context=context,
            )
        )

    def _hydrate_references(self) -> None:
        """Resolve handle associations iteratively so cycles never recurse."""
        previous_sizes: tuple[int, ...] = ()
        while True:
            for kind in ("family", "person", "event", "place", "note", "citation", "source", "repository", "media"):
                for record in tuple(self._records[kind].values()):
                    for tag_handle in _record_tag_handles(record):
                        self._tag_record(tag_handle)
                    links = getattr(record, "links", ObjectLinks())
                    for citation_handle in links.citations:
                        self._citation_record(citation_handle)
                    for note_handle in links.notes:
                        self._note_record(note_handle)
                    for attribute in links.attributes:
                        self._hydrate_attribute_references(attribute)
                    for media_ref in links.media:
                        self._media_record(media_ref.media_handle)
                        for citation_handle in media_ref.citations:
                            self._citation_record(citation_handle)
                        for note_handle in media_ref.notes:
                            self._note_record(note_handle)
                        for attribute in media_ref.attributes:
                            self._hydrate_attribute_references(attribute)
                    for event_ref in links.events:
                        self._event_record(event_ref.event_handle)
                        for citation_handle in event_ref.citations:
                            self._citation_record(citation_handle)
                        for note_handle in event_ref.notes:
                            self._note_record(note_handle)
                        for attribute in event_ref.attributes:
                            self._hydrate_attribute_references(attribute)
                    for child_ref in getattr(record, "child_relationships", ()):
                        for citation_handle in child_ref.citations:
                            self._citation_record(citation_handle)
                        for note_handle in child_ref.notes:
                            self._note_record(note_handle)
                    for person_ref in getattr(record, "relationships", ()):
                        for citation_handle in person_ref.citations:
                            self._citation_record(citation_handle)
                        for note_handle in person_ref.notes:
                            self._note_record(note_handle)
                    for address in getattr(record, "addresses", ()):
                        for citation_handle in address.citations:
                            self._citation_record(citation_handle)
                        for note_handle in address.notes:
                            self._note_record(note_handle)
                    if isinstance(record, Event) and record.place_handle:
                        self._place_record(record.place_handle)
                    if isinstance(record, Citation) and record.source_handle:
                        self._source_record(record.source_handle)
                    if isinstance(record, Source):
                        for ref in record.repository_refs:
                            self._repository_record(ref.repository_handle)
                            for note_handle in ref.notes:
                                self._note_record(note_handle)
            sizes = tuple(len(self._records[kind]) for kind in _GETTERS)
            if sizes == previous_sizes:
                break
            previous_sizes = sizes

    def _hydrate_attribute_references(self, attribute: Attribute) -> None:
        for citation_handle in attribute.citations:
            self._citation_record(citation_handle)
        for note_handle in attribute.notes:
            self._note_record(note_handle)


def _sequence(obj: Any, method: str) -> tuple[Any, ...]:
    if obj is None:
        return ()
    value = _call(obj, method)
    return tuple(value or ())


def _call(obj: Any, method: str, default: Any = None) -> Any:
    if obj is None:
        return default
    function = getattr(obj, method, None)
    if function is None:
        return default
    return function() if callable(function) else function


def _string(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _type_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    xml_string = getattr(value, "xml_str", None)
    if callable(xml_string):
        return str(xml_string())
    for attr in ("string", "value"):
        result = getattr(value, attr, None)
        if result not in (None, ""):
            return str(result)
    return str(value)


def _integer_or_none(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _optional_bool(obj: Any, method: str) -> bool | None:
    value = _call(obj, method)
    return bool(value) if value is not None else None


def _plain_relation(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    xml_string = getattr(value, "xml_str", None)
    if callable(xml_string):
        return str(xml_string())
    if isinstance(value, (tuple, list)):
        return tuple(_plain_relation(item) for item in value)
    if isinstance(value, dict):
        return {str(key): _plain_relation(item) for key, item in value.items()}
    for attr in ("value", "string"):
        result = getattr(value, attr, None)
        if result is not None:
            return _plain_relation(result)
    serialize = getattr(value, "serialize", None)
    return _plain_relation(serialize()) if callable(serialize) else str(value)


def _record_tag_handles(record: Any) -> tuple[str, ...]:
    handles = list(getattr(getattr(record, "links", None), "tag_handles", ()))
    if isinstance(record, Media):
        handles.extend(record.tag_handles)
    return tuple(dict.fromkeys(handles))


def _validate_depth(value: int | None, direction: str) -> None:
    if value is not None and (
        isinstance(value, bool) or not isinstance(value, int) or value < 0
    ):
        raise ValueError(f"The maximum {direction} depth must be a non-negative integer.")


def _child_link_is_none(family: Family, relationship: ChildRelationship | None, parent_handle: str) -> bool:
    if relationship is None:
        return False
    if family.father is not None and family.father.handle == parent_handle:
        value = relationship.father_relation
    elif family.mother is not None and family.mother.handle == parent_handle:
        value = relationship.mother_relation
    else:
        return True
    if value is False:
        return True
    return isinstance(value, str) and value.strip().casefold() == "none"
