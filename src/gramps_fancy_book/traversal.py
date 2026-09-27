"""Pure-Python genealogy traversal over a normalized Gramps snapshot."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Iterable

from .domain import (
    Diagnostic,
    Family,
    FamilySection,
    Genealogy,
    GenealogyPart,
    Generation,
    Person,
    PersonOccurrence,
    Snapshot,
)


@dataclass
class _Occurrence:
    part: str
    person_handle: str
    generation: int
    family_handle: str | None
    roles: set[str] = field(default_factory=set)
    branch_handles: set[str] = field(default_factory=set)
    lineage_paths: set[tuple[str, ...]] = field(default_factory=set)


@dataclass
class _FamilySection:
    part: str
    family_handle: str
    generation: int
    roles: set[str] = field(default_factory=set)
    branch_handles: set[str] = field(default_factory=set)


def parse_depth_limit(value: int | str | None) -> int | None:
    """Parse a non-negative generation limit; ``None`` means unlimited."""
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError("A generation limit must be a non-negative integer or 'unlimited'.")
    if isinstance(value, int):
        if value >= 0:
            return value
        raise ValueError("A generation limit cannot be negative.")
    if isinstance(value, str):
        text = value.strip().casefold()
        if text in {"unlimited", "all", "illimité", "illimite", "∞"}:
            return None
        try:
            limit = int(text)
        except ValueError as exc:
            raise ValueError(
                "A generation limit must be a non-negative integer or 'unlimited'."
            ) from exc
        if limit >= 0:
            return limit
        raise ValueError("A generation limit cannot be negative.")
    raise ValueError("A generation limit must be a non-negative integer or 'unlimited'.")


def build_genealogy(
    snapshot: Snapshot,
    max_ancestor_depth: int | str | None = None,
    max_descendant_depth: int | str | None = None,
) -> Genealogy:
    """Build bounded ancestry and descendant occurrences from a complete snapshot.

    The traversal follows only explicit child-parent links. Partners and siblings are
    included as context but never become traversal roots by themselves. Occurrences
    retain their generation, family, branch roots, and lineage paths so later renderers
    can distinguish repeated appearances from repeated people.
    """
    ancestor_limit = parse_depth_limit(max_ancestor_depth)
    descendant_limit = parse_depth_limit(max_descendant_depth)
    central_family = snapshot.reference_family
    if central_family.father is None or central_family.mother is None:
        raise ValueError("The reference family must have two known partners.")

    people = _snapshot_people(snapshot)
    families = dict(snapshot.families)
    families.setdefault(central_family.handle, central_family)
    roots = (central_family.father.handle, central_family.mother.handle)
    root_order = {handle: index for index, handle in enumerate(dict.fromkeys(roots))}
    occurrences: dict[tuple[str, str, int, str | None], _Occurrence] = {}
    family_sections: dict[tuple[str, str, int], _FamilySection] = {}
    diagnostics: dict[tuple[str, str, str], Diagnostic] = {}

    def add_diagnostic(code: str, object_type: str, handle: str, message: str) -> None:
        key = code, object_type, handle
        diagnostics.setdefault(
            key,
            Diagnostic(
                code=code,
                severity="warning",
                object_type=object_type,
                handle=handle,
                message=message,
            ),
        )

    def add_occurrence(
        part: str,
        person_handle: str,
        generation: int,
        family_handle: str | None,
        branch_handle: str,
        role: str,
        path: tuple[str, ...] = (),
    ) -> None:
        if person_handle not in people:
            add_diagnostic(
                "missing_traversal_person",
                "person",
                person_handle,
                "A genealogy link points to a person missing from the snapshot.",
            )
            return
        key = part, person_handle, generation, family_handle
        occurrence = occurrences.get(key)
        if occurrence is None:
            occurrence = _Occurrence(part, person_handle, generation, family_handle)
            occurrences[key] = occurrence
        occurrence.roles.add(role)
        occurrence.branch_handles.add(branch_handle)
        if role in {"central", "lineage"} and path:
            occurrence.lineage_paths.add(path)

    def add_family_section(
        part: str,
        family_handle: str,
        generation: int,
        branch_handle: str,
        role: str,
    ) -> None:
        if family_handle not in families:
            add_diagnostic(
                "missing_traversal_family",
                "family",
                family_handle,
                "A genealogy link points to a family missing from the snapshot.",
            )
            return
        key = part, family_handle, generation
        section = family_sections.get(key)
        if section is None:
            section = _FamilySection(part, family_handle, generation)
            family_sections[key] = section
        section.roles.add(role)
        section.branch_handles.add(branch_handle)

    for root_handle in roots:
        add_occurrence(
            "ancestry", root_handle, 0, central_family.handle, root_handle, "central", (root_handle,)
        )
        add_occurrence(
            "descent", root_handle, 0, central_family.handle, root_handle, "central", (root_handle,)
        )
    for root_handle in set(roots):
        add_family_section("ancestry", central_family.handle, 0, root_handle, "central")
        add_family_section("descent", central_family.handle, 0, root_handle, "central")

    _build_ancestry(
        roots,
        ancestor_limit,
        people,
        families,
        add_occurrence,
        add_family_section,
        add_diagnostic,
    )
    _build_descent(
        roots,
        descendant_limit,
        central_family.handle,
        people,
        families,
        add_occurrence,
        add_family_section,
        add_diagnostic,
    )

    eligible_profiles = _eligible_profiles(
        people, families, snapshot.events, occurrences, family_sections.values()
    )
    ordered_parts: dict[str, tuple[Generation, ...]] = {}
    primary_profiles: set[str] = set()
    profile_handles: list[str] = []
    for part in ("ancestry", "descent"):
        ordered = _ordered_occurrences(part, occurrences, people, root_order, snapshot.events)
        grouped: dict[int, list[PersonOccurrence]] = defaultdict(list)
        for item in ordered:
            profile_anchor = None
            is_primary = False
            if item.person_handle in eligible_profiles:
                profile_anchor = f"person:{item.person_handle}"
                if item.person_handle not in primary_profiles:
                    primary_profiles.add(item.person_handle)
                    profile_handles.append(item.person_handle)
                    is_primary = True
            grouped[item.generation].append(
                PersonOccurrence(
                    occurrence_id=item.occurrence_id,
                    person_handle=item.person_handle,
                    generation=item.generation,
                    family_handle=item.family_handle,
                    branch_handles=item.branch_handles,
                    roles=item.roles,
                    lineage_paths=item.lineage_paths,
                    profile_anchor=profile_anchor,
                    is_primary_profile=is_primary,
                )
            )
        generation_numbers = sorted(
            grouped, reverse=(part == "ancestry")
        )
        ordered_parts[part] = tuple(
            Generation(number, tuple(grouped[number])) for number in generation_numbers
        )

    ordered_sections = sorted(
        family_sections.values(),
        key=lambda section: (
            0 if section.part == "ancestry" else 1,
            -section.generation if section.part == "ancestry" else section.generation,
            section.family_handle,
        ),
    )
    family_section_records = tuple(
        FamilySection(
            family_handle=section.family_handle,
            part=section.part,
            generation=section.generation,
            branch_handles=tuple(
                sorted(section.branch_handles, key=lambda handle: (root_order.get(handle, 99), handle))
            ),
            roles=tuple(sorted(section.roles)),
        )
        for section in ordered_sections
    )
    return Genealogy(
        ancestry=GenealogyPart("ancestry", ordered_parts["ancestry"]),
        descent=GenealogyPart("descent", ordered_parts["descent"]),
        family_sections=family_section_records,
        profile_handles=tuple(profile_handles),
        diagnostics=tuple(diagnostics.values()),
    )


def _build_ancestry(
    roots: tuple[str, str],
    limit: int | None,
    people: dict[str, Person],
    families: dict[str, Family],
    add_occurrence,
    add_family_section,
    add_diagnostic,
) -> None:
    queue = deque((root, 0, root, (root,)) for root in dict.fromkeys(roots))
    processed: set[tuple[str, int, str, tuple[str, ...]]] = set()
    while queue:
        handle, depth, branch, path = queue.popleft()
        state = handle, depth, branch, path
        if state in processed:
            continue
        processed.add(state)
        person = people.get(handle)
        if person is None:
            add_diagnostic(
                "missing_traversal_person", "person", handle,
                "A genealogy link points to a person missing from the snapshot.",
            )
            continue

        if depth > 0:
            for family_handle in person.family_handles:
                family = families.get(family_handle)
                if family is None:
                    add_diagnostic(
                        "missing_traversal_family", "family", family_handle,
                        "A genealogy link points to a family missing from the snapshot.",
                    )
                    continue
                add_family_section("ancestry", family_handle, -depth, branch, "ancestor_union")
                for partner in _partners(family):
                    if partner.handle != handle:
                        add_occurrence(
                            "ancestry", partner.handle, -depth, family_handle, branch, "partner"
                        )

        if limit is not None and depth >= limit:
            continue
        for family_handle in person.parent_family_handles:
            family = families.get(family_handle)
            if family is None:
                add_diagnostic(
                    "missing_traversal_family", "family", family_handle,
                    "A genealogy link points to a family missing from the snapshot.",
                )
                continue
            parent_generation = -(depth + 1)
            add_family_section(
                "ancestry", family_handle, parent_generation, branch, "parent_family"
            )
            if depth > 0:
                for sibling in family.children:
                    if sibling.handle != handle:
                        add_occurrence(
                            "ancestry", sibling.handle, -depth, family_handle, branch, "sibling"
                        )
            child_relation = _child_relationship(family, handle)
            for parent in _partners(family):
                if not _parent_linked(family, child_relation, parent.handle):
                    continue
                next_path = path + (parent.handle,)
                add_occurrence(
                    "ancestry", parent.handle, parent_generation, family_handle,
                    branch, "lineage", next_path,
                )
                if parent.handle in path:
                    add_diagnostic(
                        "genealogy_cycle", "person", parent.handle,
                        "An ancestry cycle was displayed but its repeated path was not expanded.",
                    )
                    continue
                queue.append((parent.handle, depth + 1, branch, next_path))


def _build_descent(
    roots: tuple[str, str],
    limit: int | None,
    central_family_handle: str,
    people: dict[str, Person],
    families: dict[str, Family],
    add_occurrence,
    add_family_section,
    add_diagnostic,
) -> None:
    queue = deque((root, 0, root, (root,)) for root in dict.fromkeys(roots))
    processed: set[tuple[str, int, str, tuple[str, ...]]] = set()
    while queue:
        handle, depth, branch, path = queue.popleft()
        state = handle, depth, branch, path
        if state in processed:
            continue
        processed.add(state)
        person = people.get(handle)
        if person is None:
            add_diagnostic(
                "missing_traversal_person", "person", handle,
                "A genealogy link points to a person missing from the snapshot.",
            )
            continue

        family_handles = list(person.family_handles)
        if depth == 0 and central_family_handle not in family_handles:
            family_handles.append(central_family_handle)
        for family_handle in family_handles:
            family = families.get(family_handle)
            if family is None:
                add_diagnostic(
                    "missing_traversal_family", "family", family_handle,
                    "A genealogy link points to a family missing from the snapshot.",
                )
                continue
            add_family_section("descent", family_handle, depth, branch, "descendant_union")
            for partner in _partners(family):
                if partner.handle != handle:
                    add_occurrence(
                        "descent", partner.handle, depth, family_handle, branch, "partner"
                    )
            if limit is not None and depth >= limit:
                continue
            for child in family.children:
                child_relation = _child_relationship(family, child.handle)
                if not _parent_linked(family, child_relation, handle):
                    continue
                next_path = path + (child.handle,)
                add_occurrence(
                    "descent", child.handle, depth + 1, family_handle,
                    branch, "lineage", next_path,
                )
                if child.handle in path:
                    add_diagnostic(
                        "genealogy_cycle", "person", child.handle,
                        "A descendant cycle was displayed but its repeated path was not expanded.",
                    )
                    continue
                queue.append((child.handle, depth + 1, branch, next_path))


def _eligible_profiles(
    people: dict[str, Person],
    families: dict[str, Family],
    events: dict,
    occurrences: dict[tuple[str, str, int, str | None], _Occurrence],
    family_sections: Iterable[_FamilySection],
) -> set[str]:
    candidate_handles = {occurrence.person_handle for occurrence in occurrences.values()}
    eligible: set[str] = set()
    relevant_families = {
        occurrence.family_handle
        for occurrence in occurrences.values()
        if occurrence.family_handle is not None
    }
    relevant_families.update(section.family_handle for section in family_sections)

    # Contextual siblings do not become traversal roots, but their own unions can
    # contain events that qualify them for a profile.
    contextual_siblings = {
        occurrence.person_handle
        for occurrence in occurrences.values()
        if "sibling" in occurrence.roles
    }
    for handle in contextual_siblings:
        person = people.get(handle)
        if person is not None:
            relevant_families.update(person.family_handles)

    families_by_partner: dict[str, list[Family]] = defaultdict(list)
    for family_handle in sorted(relevant_families):
        family = families.get(family_handle)
        if family is not None:
            for partner in _partners(family):
                families_by_partner[partner.handle].append(family)
    for handle in candidate_handles:
        person = people[handle]
        if person.book_profile_forced or _has_substantive_event(person.links.events, events):
            eligible.add(handle)
            continue
        for family in families_by_partner.get(handle, ()):
            if _has_substantive_event(family.links.events, events):
                eligible.add(handle)
                break
    return eligible


def _has_substantive_event(references: Iterable, events: dict) -> bool:
    for reference in references:
        event = events.get(reference.event_handle)
        if event is None or event.type.strip().casefold() in {"birth", "death"}:
            continue
        date = event.date
        has_date = date is not None and bool(
            date.display or date.sort_value is not None or date.ymd or date.stop_ymd
        )
        links = event.links
        has_attribute = any(
            attribute.value.strip() and not attribute.type.startswith("BOOK_")
            for attribute in links.attributes
        )
        has_content = bool(
            event.description.strip()
            or event.place_handle
            or has_date
            or links.citations
            or links.notes
            or links.media
            or has_attribute
        )
        role = reference.role.strip().casefold()
        if has_content or role not in {"", "unknown", "family"}:
            return True
    return False


def _ordered_occurrences(
    part: str,
    occurrences: dict[tuple[str, str, int, str | None], _Occurrence],
    people: dict[str, Person],
    root_order: dict[str, int],
    events: dict,
) -> tuple[PersonOccurrence, ...]:
    selected = [item for item in occurrences.values() if item.part == part]
    grouped: dict[int, list[_Occurrence]] = defaultdict(list)
    for item in selected:
        grouped[item.generation].append(item)
    generations = sorted(grouped, reverse=(part == "ancestry"))
    result: list[PersonOccurrence] = []
    for generation in generations:
        items = sorted(
            grouped[generation],
            key=lambda item: (
                0 if "central" in item.roles else 1,
                item.family_handle or "",
                min((root_order.get(handle, 99) for handle in item.branch_handles), default=99)
                if "central" in item.roles else 99,
                _birth_sort_key(people[item.person_handle], events),
                _identity_sort_key(people[item.person_handle]),
            ),
        )
        for item in items:
            branches = tuple(
                sorted(item.branch_handles, key=lambda handle: (root_order.get(handle, 99), handle))
            )
            family_part = item.family_handle or "context"
            result.append(
                PersonOccurrence(
                    occurrence_id=(
                        f"{part}:{generation}:{family_part}:{item.person_handle}"
                    ),
                    person_handle=item.person_handle,
                    generation=generation,
                    family_handle=item.family_handle,
                    branch_handles=branches,
                    roles=tuple(sorted(item.roles)),
                    lineage_paths=tuple(sorted(item.lineage_paths)),
                )
            )
    return tuple(result)


def _birth_sort_key(person: Person, events: dict) -> tuple[int, int, int, int]:
    exact_birth_dates = set()
    for reference in person.links.events:
        event = events.get(reference.event_handle)
        if event is None or event.type.strip().casefold() != "birth":
            continue
        date = event.date
        if date is None or date.modifier not in (None, 0) or date.quality not in (None, 0):
            continue
        if date.ymd is None or len(date.ymd) != 3:
            continue
        year, month, day = date.ymd
        if year == 0 or not (1 <= month <= 12 and 1 <= day <= 31):
            continue
        if date.stop_ymd not in (None, date.ymd):
            continue
        exact_birth_dates.add((year, month, day))
    if len(exact_birth_dates) == 1:
        year, month, day = exact_birth_dates.pop()
        return (0, year, month, day)
    return (1, 0, 0, 0)


def _identity_sort_key(person: Person) -> tuple[str, str]:
    return ((person.gramps_id or person.handle).casefold(), person.handle)


def _snapshot_people(snapshot: Snapshot) -> dict[str, Person]:
    people = dict(snapshot.people)
    families = (snapshot.reference_family, *snapshot.families.values())
    for family in families:
        for person in (*_partners(family), *family.children):
            people.setdefault(person.handle, person)
    return people


def _partners(family: Family) -> tuple[Person, ...]:
    return tuple(person for person in (family.father, family.mother) if person is not None)


def _child_relationship(family: Family, person_handle: str):
    return next(
        (item for item in family.child_relationships if item.person_handle == person_handle),
        None,
    )


def _parent_linked(family: Family, child_relationship, parent_handle: str) -> bool:
    if family.father is not None and family.father.handle == parent_handle:
        relation = child_relationship.father_relation if child_relationship is not None else None
    elif family.mother is not None and family.mother.handle == parent_handle:
        relation = child_relationship.mother_relation if child_relationship is not None else None
    else:
        return False
    if relation is False or relation == 0:
        return False
    return not (isinstance(relation, str) and relation.strip().casefold() == "none")
