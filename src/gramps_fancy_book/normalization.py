"""Normalization and model construction."""

from .domain import BookModel, Family


def build_book_model(family: Family) -> BookModel:
    people = [person for person in (family.father, family.mother) if person is not None]
    people.extend(family.children)
    return BookModel(
        reference_family=family,
        people=list(dict.fromkeys(people)),
        metadata={"BOOK_SCHEMA_VERSION": "0.1", "BOOK_REFERENCE_FAMILY": family.handle},
    )

