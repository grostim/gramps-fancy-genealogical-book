"""Normalization and model construction."""

from .conventions import BOOK_SCHEMA_VERSION
from .domain import BookModel, Family, Snapshot
from .editorial import build_editorial_book
from .traversal import build_genealogy


def _snapshot_people(snapshot: Snapshot):
    people = dict(snapshot.people)
    for family in (snapshot.reference_family, *snapshot.families.values()):
        for person in (family.father, family.mother, *family.children):
            if person is not None:
                people.setdefault(person.handle, person)
    return people


def _snapshot_families(snapshot: Snapshot):
    families = dict(snapshot.families)
    families.setdefault(snapshot.reference_family.handle, snapshot.reference_family)
    return families


def build_book_model(
    family: Family | Snapshot,
    max_ancestor_depth: int | str | None = None,
    max_descendant_depth: int | str | None = None,
) -> BookModel:
    if isinstance(family, Snapshot):
        genealogy = build_genealogy(family, max_ancestor_depth, max_descendant_depth)
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
            diagnostics=[*family.diagnostics, *genealogy.diagnostics],
            genealogy=genealogy,
            editorial_book=build_editorial_book(
                genealogy,
                family.reference_family.handle,
                _snapshot_people(family),
                _snapshot_families(family),
                family.notes,
                family.media,
                family.events,
                family.places,
            ),
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
