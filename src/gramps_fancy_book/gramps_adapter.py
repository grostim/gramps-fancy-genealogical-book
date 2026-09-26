"""Boundary between the domain pipeline and Gramps' database APIs."""

from typing import Protocol

from .domain import Family


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

        return Family(
            handle=family.get_handle(),
            father=self._person(family.get_father_handle()),
            mother=self._person(family.get_mother_handle()),
            children=tuple(
                person
                for child_ref in family.get_child_ref_list()
                if (person := self._person(child_ref.ref)) is not None
            ),
        )

    def get_family_by_gramps_id(self, gramps_id: str) -> Family:
        family = self.database.get_family_from_gramps_id(gramps_id)
        if family is None:
            raise LookupError(f"No family exists for Gramps ID {gramps_id!r}")
        return self.get_family(family.get_handle())

    def _person(self, handle: str | None):
        if not handle:
            return None
        from .domain import Person

        person = self.database.get_person_from_handle(handle)
        if person is None:
            return None
        name = person.get_primary_name().get_name()
        return Person(handle=handle, name=name)
