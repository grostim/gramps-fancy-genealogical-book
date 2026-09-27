"""Pure-Python genealogy traversal over a normalized Gramps snapshot."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field, replace
from typing import Iterable

from .domain import (
    Diagnostic,
    Family,
    FamilySection,
    Genealogy,
    GenealogyPart,
    Generation,
    ParentChildLink,
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
    parts_occurrences = {
        part: _ordered_occurrences(part, occurrences, people, root_order, snapshot.events)
        for part in ("ancestry", "descent")
    }
    primary_occurrence_ids: dict[str, str] = {}
    for part in ("ancestry", "descent"):
        for item in parts_occurrences[part]:
            primary_occurrence_ids.setdefault(item.person_handle, item.occurrence_id)

    ordered_parts: dict[str, tuple[Generation, ...]] = {}
    primary_profiles: set[str] = set()
    profile_handles: list[str] = []
    for part in ("ancestry", "descent"):
        ordered = parts_occurrences[part]
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
                    primary_occurrence_id=primary_occurrence_ids[item.person_handle],
                )
            )
        generation_numbers = sorted(
            grouped, reverse=(part == "ancestry")
        )
        ordered_parts[part] = tuple(
            Generation(number, tuple(grouped[number])) for number in generation_numbers
        )

    lineage_path_positions: dict[tuple[str, tuple[str, ...]], int] = {}
    for part, generations in ordered_parts.items():
        for generation in generations:
            for position, occurrence in enumerate(generation.occurrences):
                for path in occurrence.lineage_paths:
                    key = part, path
                    lineage_path_positions[key] = min(
                        position, lineage_path_positions.get(key, position)
                    )

    section_source_order: dict[
        tuple[str, str, int], list[tuple[tuple[int, ...], int]]
    ] = defaultdict(list)
    for part, generations in ordered_parts.items():
        for generation in generations:
            for occurrence in generation.occurrences:
                if "lineage" not in occurrence.roles and "central" not in occurrence.roles:
                    continue
                person = people.get(occurrence.person_handle)
                if person is None:
                    continue
                path_keys = [
                    _lineage_path_order_key(path, part, root_order, lineage_path_positions)
                    for path in occurrence.lineage_paths
                ]
                if not path_keys:
                    path_keys = [
                        (root_order.get(branch, 99),)
                        for branch in occurrence.branch_handles
                    ]
                path_key = min(path_keys, default=(99,))
                for union_position, family_handle in enumerate(person.family_handles):
                    section_source_order[(part, family_handle, occurrence.generation)].append(
                        (path_key, union_position)
                    )
                if part == "ancestry":
                    for union_position, family_handle in enumerate(person.parent_family_handles):
                        section_source_order[
                            (part, family_handle, occurrence.generation - 1)
                        ].append((path_key, union_position))

    ordered_sections = sorted(
        family_sections.values(),
        key=lambda section: _family_section_order_key(
            section,
            section_source_order,
            root_order,
        ),
    )
    family_section_records, occurrence_section_ids = _link_family_sections(
        ordered_sections,
        families,
        ordered_parts,
        central_family.handle,
        root_order,
    )
    ordered_parts = {
        part: tuple(
            Generation(
                generation.number,
                tuple(
                    replace(
                        occurrence,
                        family_section_ids=tuple(
                            occurrence_section_ids.get(occurrence.occurrence_id, ())
                        ),
                    )
                    for occurrence in generation.occurrences
                ),
            )
            for generation in generations
        )
        for part, generations in ordered_parts.items()
    }
    return Genealogy(
        ancestry=GenealogyPart("ancestry", ordered_parts["ancestry"]),
        descent=GenealogyPart("descent", ordered_parts["descent"]),
        family_sections=family_section_records,
        profile_handles=tuple(profile_handles),
        diagnostics=tuple(diagnostics.values()),
    )


def _family_section_order_key(
    section: _FamilySection,
    section_source_order: dict[
        tuple[str, str, int], list[tuple[tuple[int, ...], int]]
    ],
    root_order: dict[str, int],
) -> tuple[int, int, tuple[int, ...], int, str]:
    """Order family sections by comparable lineage paths and source unions."""
    ancestry = section.part == "ancestry"
    fallback_path = min(
        (root_order.get(branch, 99),) for branch in section.branch_handles
    ) if section.branch_handles else (99,)
    path_position, union_position = min(
        section_source_order.get(
            (section.part, section.family_handle, section.generation),
            [(fallback_path, 1_000_000)],
        )
    )
    return (
        0 if ancestry else 1,
        -section.generation if ancestry else section.generation,
        path_position,
        union_position,
        section.family_handle,
    )


def _lineage_path_order_key(
    path: tuple[str, ...],
    part: str,
    root_order: dict[str, int],
    path_positions: dict[tuple[str, tuple[str, ...]], int],
) -> tuple[int, ...]:
    """Return a branch-comparable key using each occurrence's local generation order."""
    if not path:
        return (99,)
    return (
        root_order.get(path[0], 99),
        *(
            path_positions.get((part, path[:length]), 1_000_000)
            for length in range(2, len(path) + 1)
        ),
    )


def _link_family_sections(
    ordered_sections: list[_FamilySection],
    families: dict[str, Family],
    ordered_parts: dict[str, tuple[Generation, ...]],
    central_family_handle: str,
    root_order: dict[str, int],
) -> tuple[tuple[FamilySection, ...], dict[str, tuple[str, ...]]]:
    """Connect family sections to the in-scope partner and child occurrences."""
    occurrences_by_context: dict[tuple[str, int, str], list[PersonOccurrence]] = defaultdict(list)
    for part, generations in ordered_parts.items():
        for generation in generations:
            for occurrence in generation.occurrences:
                occurrences_by_context[(part, generation.number, occurrence.person_handle)].append(
                    occurrence
                )

    section_records: list[FamilySection] = []
    section_ids_by_occurrence: dict[str, list[str]] = defaultdict(list)
    for section in ordered_sections:
        family = families[section.family_handle]
        section_id = f"family:{section.part}:{section.generation}:{section.family_handle}"
        partners_by_handle: dict[str, list[PersonOccurrence]] = defaultdict(list)
        section_branches = section.branch_handles
        for partner in _partners(family):
            for occurrence in occurrences_by_context.get(
                (section.part, section.generation, partner.handle), ()
            ):
                is_context_member = occurrence.family_handle == family.handle or bool(
                    {"lineage", "central"}.intersection(occurrence.roles)
                )
                if is_context_member and section_branches.intersection(occurrence.branch_handles):
                    partners_by_handle[partner.handle].append(occurrence)

        partner_occurrences = [
            occurrence
            for partner in _partners(family)
            for occurrence in partners_by_handle.get(partner.handle, ())
        ]
        child_part = (
            "descent"
            if section.part == "ancestry"
            and section.family_handle == central_family_handle
            and section.generation == 0
            and "central" in section.roles
            else section.part
        )
        child_generation = section.generation + 1
        child_occurrences: list[PersonOccurrence] = []
        parent_child_links: list[ParentChildLink] = []
        seen_child_ids: set[str] = set()
        seen_links: set[tuple[str, str]] = set()
        for child in family.children:
            child_relation = _child_relationship(family, child.handle)
            linked_parents = tuple(
                (
                    partner.handle,
                    _parent_relationship(family, child_relation, partner.handle),
                )
                for partner in _partners(family)
                if _parent_linked(family, child_relation, partner.handle)
            )
            if not linked_parents:
                continue
            candidates = [
                occurrence
                for occurrence in occurrences_by_context.get(
                    (child_part, child_generation, child.handle), ()
                )
                if section_branches.intersection(occurrence.branch_handles)
                and (
                    occurrence.family_handle == family.handle
                    or "lineage" in occurrence.roles
                    or "central" in occurrence.roles
                    or "sibling" in occurrence.roles
                )
            ]
            for occurrence in candidates:
                if occurrence.occurrence_id not in seen_child_ids:
                    seen_child_ids.add(occurrence.occurrence_id)
                    child_occurrences.append(occurrence)
            for parent_handle, relationship_type in linked_parents:
                for parent in partners_by_handle.get(parent_handle, ()):
                    for occurrence in candidates:
                        link_key = parent.occurrence_id, occurrence.occurrence_id
                        if link_key not in seen_links:
                            seen_links.add(link_key)
                            parent_child_links.append(
                                ParentChildLink(
                                    parent_occurrence_id=parent.occurrence_id,
                                    child_occurrence_id=occurrence.occurrence_id,
                                    relationship_type=relationship_type,
                                )
                            )

        partner_ids = tuple(dict.fromkeys(item.occurrence_id for item in partner_occurrences))
        child_ids = tuple(item.occurrence_id for item in child_occurrences)
        for occurrence_id in (*partner_ids, *child_ids):
            section_ids_by_occurrence[occurrence_id].append(section_id)
        section_records.append(
            FamilySection(
                family_handle=section.family_handle,
                part=section.part,
                generation=section.generation,
                branch_handles=tuple(
                    sorted(
                        section_branches,
                        key=lambda handle: (root_order.get(handle, 99), handle),
                    )
                ),
                roles=tuple(sorted(section.roles)),
                section_id=section_id,
                partner_occurrence_ids=partner_ids,
                child_occurrence_ids=child_ids,
                parent_child_links=tuple(parent_child_links),
            )
        )

    return tuple(section_records), {
        occurrence_id: tuple(dict.fromkeys(section_ids))
        for occurrence_id, section_ids in section_ids_by_occurrence.items()
    }


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
                for child in family.children:
                    relationship = _child_relationship(family, child.handle)
                    if (
                        child.handle == path[-2]
                        or not _parent_linked(family, relationship, handle)
                    ):
                        continue
                    add_occurrence(
                        "ancestry", child.handle, 1 - depth, family_handle, branch, "sibling"
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
            if family_handle != central_family_handle:
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

    # Contextual siblings and partners do not become traversal roots, but their
    # own unions can contain events that qualify them for a profile.
    contextual_people = {
        occurrence.person_handle
        for occurrence in occurrences.values()
        if {"sibling", "partner"} & occurrence.roles
    }
    for handle in contextual_people:
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
    path_positions: dict[tuple[str, ...], int] = {}
    for generation in generations:
        items = sorted(
            grouped[generation],
            key=lambda item: (
                0 if "central" in item.roles else 1,
                _branch_hierarchy_key(item, part, people, root_order, path_positions),
                item.family_handle or "",
                _birth_sort_key(people[item.person_handle], events),
                _identity_sort_key(people[item.person_handle]),
            ),
        )
        for position, item in enumerate(items):
            for path in item.lineage_paths:
                path_positions[path] = min(path_positions.get(path, position), position)
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


def _branch_hierarchy_key(
    occurrence: _Occurrence,
    part: str,
    people: dict[str, Person],
    root_order: dict[str, int],
    path_positions: dict[tuple[str, ...], int],
) -> tuple[int, int]:
    """Order lineage occurrences by displayed parent, then source union order."""
    keys = []
    for path in occurrence.lineage_paths:
        if not path:
            continue
        if len(path) == 1:
            keys.append((root_order.get(path[0], 99), -1))
            continue

        parent_path = path[:-1]
        parent_position = path_positions.get(
            parent_path, 1_000_000 + root_order.get(path[0], 99)
        )
        parent = people.get(path[-2])
        if parent is None:
            union_handles = ()
        elif part == "descent":
            union_handles = parent.family_handles
        else:
            union_handles = parent.parent_family_handles
        try:
            union_position = union_handles.index(occurrence.family_handle)
        except ValueError:
            union_position = len(union_handles)
        keys.append((parent_position, union_position))

    if keys:
        return min(keys)
    branch_position = min(
        (root_order.get(handle, 99) for handle in occurrence.branch_handles),
        default=99,
    )
    return branch_position, 99


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


def _parent_relationship(family: Family, child_relationship, parent_handle: str):
    if family.father is not None and family.father.handle == parent_handle:
        return child_relationship.father_relation if child_relationship is not None else None
    if family.mother is not None and family.mother.handle == parent_handle:
        return child_relationship.mother_relation if child_relationship is not None else None
    return None


def _parent_linked(family: Family, child_relationship, parent_handle: str) -> bool:
    if parent_handle not in {partner.handle for partner in _partners(family)}:
        return False
    relation = _parent_relationship(family, child_relationship, parent_handle)
    if relation is False:
        return False
    return not (isinstance(relation, str) and relation.strip().casefold() == "none")
