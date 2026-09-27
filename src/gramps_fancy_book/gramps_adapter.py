"""Boundary between the domain pipeline and Gramps' database APIs."""

from typing import Protocol

from .domain import Family, Person


class FamilySource(Protocol):
    def get_family(self, handle: str) -> Family: ...


class GrampsDatabaseAdapter:
    """Extract the reference family through Gramps' public database interface."""

    def __init__(self, database: object) -> None:
        self.database = database

    def get_family(self, handle: str) -> Family:
        family = self.database.get_family_from_handle(handle)
        if family is None:
            raise LookupError(f"No family exists for handle {handle!r}")

        father = self._person(family.get_father_handle())
        mother = self._person(family.get_mother_handle())
        children = []
        for child_ref in family.get_child_ref_list():
            if not child_ref.ref:
                raise LookupError("Family contains a child reference without a handle.")
            children.append(self._person(child_ref.ref))

        return Family(
            handle=family.get_handle(),
            gramps_id=family.get_gramps_id(),
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

    def _person(self, handle: str | None) -> Person | None:
        if not handle:
            return None
        person = self.database.get_person_from_handle(handle)
        if person is None:
            raise LookupError(f"Family references an unavailable person: {handle!r}")
        name = person.get_primary_name().get_name()
        return Person(handle=handle, name=name, gramps_id=person.get_gramps_id())
