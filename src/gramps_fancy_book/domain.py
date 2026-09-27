"""Framework-independent records used by extraction and book generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields, is_dataclass
from enum import Enum
from typing import Any

from .conventions import BOOK_PROFILE


@dataclass(frozen=True)
class Attribute:
    type: str
    value: str
    citations: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    private: bool | None = None


@dataclass(frozen=True)
class Tag:
    handle: str
    name: str


@dataclass(frozen=True)
class DateValue:
    """Original date display and comparison data; no precision is inferred."""

    display: str = ""
    sort_value: int | None = None
    modifier: int | None = None
    quality: int | None = None
    calendar: int | None = None
    ymd: tuple[int, int, int] | None = None
    stop_ymd: tuple[int, int, int] | None = None
    range: Any = None
    raw: Any = None


@dataclass(frozen=True)
class MediaReference:
    media_handle: str
    rectangle: tuple[int, ...] | None = None
    order: int = 0
    private: bool | None = None
    citations: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    attributes: tuple[Attribute, ...] = ()


@dataclass(frozen=True)
class EventReference:
    event_handle: str
    role: str = ""
    order: int = 0
    citations: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    attributes: tuple[Attribute, ...] = ()
    private: bool | None = None


@dataclass(frozen=True)
class ChildRelationship:
    person_handle: str
    father_relation: Any = None
    mother_relation: Any = None
    order: int = 0
    citations: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    private: bool | None = None


@dataclass(frozen=True)
class PersonRelationship:
    person_handle: str
    relation: str = ""
    order: int = 0
    citations: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    private: bool | None = None


@dataclass(frozen=True)
class Address:
    street: str = ""
    locality: str = ""
    city: str = ""
    county: str = ""
    state: str = ""
    country: str = ""
    postal: str = ""
    phone: str = ""
    date: DateValue | None = None
    order: int = 0
    citations: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    private: bool | None = None


@dataclass(frozen=True)
class RepositoryReference:
    repository_handle: str
    call_number: str = ""
    media_type: str = ""
    order: int = 0
    notes: tuple[str, ...] = ()
    private: bool | None = None


@dataclass(frozen=True)
class Url:
    path: str
    description: str = ""
    type: str = ""


@dataclass(frozen=True)
class ObjectLinks:
    """Gramps associations retained as handles, with their source order."""

    citations: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    tag_handles: tuple[str, ...] = ()
    attributes: tuple[Attribute, ...] = ()
    media: tuple[MediaReference, ...] = ()
    events: tuple[EventReference, ...] = ()
    private: bool | None = None


@dataclass(frozen=True)
class Person:
    handle: str
    name: str
    gramps_id: str = ""
    alternate_names: tuple[str, ...] = ()
    gender: Any = None
    family_handles: tuple[str, ...] = ()
    parent_family_handles: tuple[str, ...] = ()
    relationships: tuple[PersonRelationship, ...] = ()
    addresses: tuple[Address, ...] = ()
    urls: tuple[Url, ...] = ()
    links: ObjectLinks = field(default_factory=ObjectLinks)

    @property
    def book_profile_forced(self) -> bool:
        return any(
            attribute.type == BOOK_PROFILE and attribute.value == "YES"
            for attribute in self.links.attributes
        )


@dataclass(frozen=True)
class Family:
    handle: str
    father: Person | None = None
    mother: Person | None = None
    children: tuple[Person, ...] = ()
    gramps_id: str = ""
    relationship: str = ""
    child_relationships: tuple[ChildRelationship, ...] = ()
    links: ObjectLinks = field(default_factory=ObjectLinks)


@dataclass(frozen=True)
class Event:
    handle: str
    gramps_id: str = ""
    type: str = ""
    description: str = ""
    date: DateValue | None = None
    place_handle: str | None = None
    links: ObjectLinks = field(default_factory=ObjectLinks)


@dataclass(frozen=True)
class Place:
    handle: str
    gramps_id: str = ""
    name: str = ""
    title: str = ""
    links: ObjectLinks = field(default_factory=ObjectLinks)


@dataclass(frozen=True)
class Note:
    handle: str
    gramps_id: str = ""
    text: str | None = None
    format: Any = None
    type: Any = None
    is_publishable: bool = False
    styled_tags: tuple[Any, ...] = ()
    links: ObjectLinks = field(default_factory=ObjectLinks)


@dataclass(frozen=True)
class Citation:
    handle: str
    gramps_id: str = ""
    source_handle: str | None = None
    page: str = ""
    date: DateValue | None = None
    confidence: Any = None
    urls: tuple[Url, ...] = ()
    links: ObjectLinks = field(default_factory=ObjectLinks)


@dataclass(frozen=True)
class Source:
    handle: str
    gramps_id: str = ""
    title: str = ""
    author: str = ""
    publication_info: str = ""
    abbreviation: str = ""
    repository_refs: tuple[RepositoryReference, ...] = ()
    urls: tuple[Url, ...] = ()
    links: ObjectLinks = field(default_factory=ObjectLinks)


@dataclass(frozen=True)
class Repository:
    handle: str
    gramps_id: str = ""
    name: str = ""
    type: str = ""
    urls: tuple[Url, ...] = ()
    links: ObjectLinks = field(default_factory=ObjectLinks)


@dataclass(frozen=True)
class Media:
    handle: str
    gramps_id: str = ""
    path: str = ""
    description: str = ""
    mime_type: str = ""
    checksum: str = ""
    tag_handles: tuple[str, ...] = ()
    is_excluded: bool = False
    is_featured: bool = False
    links: ObjectLinks = field(default_factory=ObjectLinks)


@dataclass(frozen=True)
class PersonOccurrence:
    occurrence_id: str
    person_handle: str
    generation: int
    family_handle: str | None = None
    branch_handles: tuple[str, ...] = ()
    roles: tuple[str, ...] = ()
    lineage_paths: tuple[tuple[str, ...], ...] = ()
    profile_anchor: str | None = None
    is_primary_profile: bool = False
    family_section_ids: tuple[str, ...] = ()
    primary_occurrence_id: str | None = None


@dataclass(frozen=True)
class Generation:
    number: int
    occurrences: tuple[PersonOccurrence, ...] = ()


@dataclass(frozen=True)
class GenealogyPart:
    name: str
    generations: tuple[Generation, ...] = ()


@dataclass(frozen=True)
class FamilySection:
    family_handle: str
    part: str
    generation: int
    branch_handles: tuple[str, ...] = ()
    roles: tuple[str, ...] = ()
    section_id: str = ""
    partner_occurrence_ids: tuple[str, ...] = ()
    child_occurrence_ids: tuple[str, ...] = ()
    parent_child_links: tuple[ParentChildLink, ...] = ()


@dataclass(frozen=True)
class ParentChildLink:
    parent_occurrence_id: str
    child_occurrence_id: str
    relationship_type: Any = None


@dataclass(frozen=True)
class Genealogy:
    ancestry: GenealogyPart
    descent: GenealogyPart
    family_sections: tuple[FamilySection, ...] = ()
    profile_handles: tuple[str, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: str
    object_type: str
    handle: str
    message: str
    context: str = ""


@dataclass
class Snapshot:
    reference_family: Family
    families: dict[str, Family] = field(default_factory=dict)
    people: dict[str, Person] = field(default_factory=dict)
    events: dict[str, Event] = field(default_factory=dict)
    places: dict[str, Place] = field(default_factory=dict)
    notes: dict[str, Note] = field(default_factory=dict)
    citations: dict[str, Citation] = field(default_factory=dict)
    sources: dict[str, Source] = field(default_factory=dict)
    repositories: dict[str, Repository] = field(default_factory=dict)
    media: dict[str, Media] = field(default_factory=dict)
    tags: dict[str, Tag] = field(default_factory=dict)
    diagnostics: list[Diagnostic] = field(default_factory=list)


@dataclass(frozen=True)
class EditorialPart:
    part_id: str
    kind: str
    family_section_ids: tuple[str, ...] = ()
    family_notice_ids: tuple[str, ...] = ()
    person_occurrence_ids: tuple[str, ...] = ()
    part_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class EditorialProfile:
    profile_id: str
    person_handle: str
    primary_occurrence_id: str | None = None
    family_section_ids: tuple[str, ...] = ()
    note_handles: tuple[str, ...] = ()
    portrait_ref: MediaReference | None = None
    event_refs: tuple[EventReference, ...] = ()
    media_refs: tuple[MediaReference, ...] = ()


@dataclass(frozen=True)
class EditorialPortrait:
    person_handle: str
    media_ref: MediaReference


@dataclass(frozen=True)
class EditorialFamilyNotice:
    notice_id: str
    family_handle: str
    primary_section_id: str
    family_section_ids: tuple[str, ...] = ()
    note_handles: tuple[str, ...] = ()
    event_refs: tuple[EventReference, ...] = ()
    media_refs: tuple[MediaReference, ...] = ()


@dataclass(frozen=True)
class EditorialBook:
    parts: tuple[EditorialPart, ...] = ()
    profiles: tuple[EditorialProfile, ...] = ()
    family_notices: tuple[EditorialFamilyNotice, ...] = ()
    cover_portraits: tuple[EditorialPortrait, ...] = ()


@dataclass
class BookModel:
    reference_family: Family
    people: list[Person] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    families: dict[str, Family] = field(default_factory=dict)
    events: dict[str, Event] = field(default_factory=dict)
    places: dict[str, Place] = field(default_factory=dict)
    notes: dict[str, Note] = field(default_factory=dict)
    citations: dict[str, Citation] = field(default_factory=dict)
    sources: dict[str, Source] = field(default_factory=dict)
    repositories: dict[str, Repository] = field(default_factory=dict)
    media: dict[str, Media] = field(default_factory=dict)
    tags: dict[str, Tag] = field(default_factory=dict)
    diagnostics: list[Diagnostic] = field(default_factory=list)
    genealogy: Genealogy | None = None
    editorial_book: EditorialBook | None = None

    def to_dict(self) -> dict[str, object]:
        """Return JSON-safe data while keeping each Gramps object keyed by handle."""
        diagnostics = list(self.diagnostics)
        if self.genealogy is not None:
            diagnostics.extend(
                item for item in self.genealogy.diagnostics if item not in diagnostics
            )
            genealogy = _plain(self.genealogy)
            genealogy.pop("diagnostics", None)
        else:
            genealogy = None
        return _plain(
            {
                "reference_family": self.reference_family,
                "people": self.people,
                "families": self.families,
                "events": self.events,
                "places": self.places,
                "notes": self.notes,
                "citations": self.citations,
                "sources": self.sources,
                "repositories": self.repositories,
                "media": self.media,
                "tags": self.tags,
                "diagnostics": diagnostics,
                "genealogy": genealogy,
                "editorial_book": self.editorial_book,
                "privacy": {"contains_private_data": _contains_private_data(self)},
                "metadata": self.metadata,
            }
        )


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _plain(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _contains_private_data(value: Any) -> bool:
    if is_dataclass(value):
        return any(
            bool(getattr(value, item.name)) if item.name == "private" else _contains_private_data(getattr(value, item.name))
            for item in fields(value)
        )
    if isinstance(value, dict):
        return any(_contains_private_data(item) for item in value.values())
    if isinstance(value, (tuple, list)):
        return any(_contains_private_data(item) for item in value)
    return False
