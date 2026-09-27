"""Normalization and model construction."""

from .conventions import BOOK_SCHEMA_VERSION
from .domain import BookModel, Family, Snapshot


def build_book_model(family: Family | Snapshot) -> BookModel:
    if isinstance(family, Snapshot):
        people = list(family.people.values())
        return BookModel(
            reference_family=family.reference_family,
            people=people,
            metadata={
                "BOOK_SCHEMA_VERSION": BOOK_SCHEMA_VERSION,
                "BOOK_REFERENCE_FAMILY": family.reference_family.handle,
            },
            families=family.families,
            events=family.events,
            places=family.places,
            notes=family.notes,
            citations=family.citations,
            sources=family.sources,
            repositories=family.repositories,
            media=family.media,
            tags=family.tags,
            diagnostics=family.diagnostics,
        )

    family_members = [person for person in (family.father, family.mother) if person is not None]
    family_members.extend(family.children)
    people_by_handle = {person.handle: person for person in family_members}
    return BookModel(
        reference_family=family,
        people=list(people_by_handle.values()),
        metadata={"BOOK_SCHEMA_VERSION": BOOK_SCHEMA_VERSION, "BOOK_REFERENCE_FAMILY": family.handle},
        families={family.handle: family},
    )
