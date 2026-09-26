"""Framework-independent contracts for the first book-model milestone."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Person:
    handle: str
    name: str


@dataclass(frozen=True)
class Family:
    handle: str
    father: Person | None = None
    mother: Person | None = None
    children: tuple[Person, ...] = ()


@dataclass
class BookModel:
    reference_family: Family
    people: list[Person] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "reference_family": {
                "handle": self.reference_family.handle,
                "father": _person_dict(self.reference_family.father),
                "mother": _person_dict(self.reference_family.mother),
                "children": [_person_dict(person) for person in self.reference_family.children],
            },
            "people": [_person_dict(person) for person in self.people],
            "metadata": dict(self.metadata),
        }


def _person_dict(person: Person | None) -> dict[str, str] | None:
    return None if person is None else {"handle": person.handle, "name": person.name}

