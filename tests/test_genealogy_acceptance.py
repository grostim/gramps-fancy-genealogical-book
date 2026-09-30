from gramps_fancy_book.conventions import BOOK_PROFILE
from gramps_fancy_book.domain import (
    Attribute,
    ChildRelationship,
    DateValue,
    Event,
    EventReference,
    Family,
    ObjectLinks,
    Person,
    Snapshot,
)
from gramps_fancy_book.normalization import build_book_model
from gramps_fancy_book.renderers.latex import render_latex


def _person(
    handle,
    *,
    family_handles=(),
    parent_family_handles=(),
    event_refs=(),
    attributes=(),
):
    return Person(
        handle=handle,
        name=handle,
        gramps_id=handle.upper(),
        family_handles=tuple(family_handles),
        parent_family_handles=tuple(parent_family_handles),
        links=ObjectLinks(
            events=tuple(event_refs),
            attributes=tuple(attributes),
        ),
    )


def _family(
    handle,
    father,
    mother,
    children=(),
    *,
    relations=None,
    event_refs=(),
):
    relations = relations or {}
    child_relationships = tuple(
        ChildRelationship(
            person_handle=child.handle,
            father_relation=relations.get(child.handle, ("Birth", "Birth"))[0],
            mother_relation=relations.get(child.handle, ("Birth", "Birth"))[1],
            order=index,
        )
        for index, child in enumerate(children)
    )
    return Family(
        handle=handle,
        father=father,
        mother=mother,
        children=tuple(children),
        child_relationships=child_relationships,
        links=ObjectLinks(events=tuple(event_refs)),
    )


def _snapshot(reference_family, families, people, events=None):
    return Snapshot(
        reference_family=reference_family,
        families={family.handle: family for family in families},
        people={person.handle: person for person in people},
        events=events or {},
    )


def _event_ref(handle, role="Primary"):
    return EventReference(event_handle=handle, role=role)


def _all_occurrences(genealogy):
    return tuple(
        occurrence
        for part in (genealogy.ancestry, genealogy.descent)
        for generation in part.generations
        for occurrence in generation.occurrences
    )


def _occurrences_in(genealogy, part):
    return tuple(
        occurrence
        for generation in getattr(genealogy, part).generations
        for occurrence in generation.occurrences
    )


def test_central_couple_starts_ancestry_and_descent_links_back_to_it():
    p0 = _person("p0", family_handles=("f0",))
    p1 = _person("p1", family_handles=("f0",))
    child = _person("child", parent_family_handles=("f0",))
    central = _family("f0", p0, p1, (child,))
    model = build_book_model(_snapshot(central, (central,), (p0, p1, child)))

    ancestry_generations = model.genealogy.ancestry.generations
    assert ancestry_generations[0].number == 0
    ancestry_couple = ancestry_generations[0].occurrences
    assert [item.person_handle for item in ancestry_couple] == ["p0", "p1"]
    assert all("central" in item.roles for item in ancestry_couple)
    ancestry_ids = {item.person_handle: item.occurrence_id for item in ancestry_couple}

    descent_zero = next(
        generation
        for generation in model.genealogy.descent.generations
        if generation.number == 0
    )
    assert [item.person_handle for item in descent_zero.occurrences] == ["p0", "p1"]
    assert {
        item.person_handle: item.primary_occurrence_id
        for item in descent_zero.occurrences
    } == ancestry_ids

    central_section = next(
        section
        for section in model.genealogy.family_sections
        if section.family_handle == "f0" and section.part == "ancestry"
    )
    assert [
        next(
            item.person_handle
            for item in ancestry_couple
            if item.occurrence_id == target_id
        )
        for target_id in central_section.partner_occurrence_ids
    ] == ["p0", "p1"]
    descent_one = next(
        generation
        for generation in model.genealogy.descent.generations
        if generation.number == 1
    )
    assert set(central_section.child_occurrence_ids) == {
        item.occurrence_id for item in descent_one.occurrences
    }

    rendered = render_latex(model)
    ancestry_start = rendered.index(r"\section*{Ancestry}")
    descent_start = rendered.index(r"\section*{Descent}", ancestry_start)
    connections_start = rendered.index(r"\section*{Family connections}", descent_start)
    ancestry_text = rendered[ancestry_start:descent_start]
    ancestry_generation_target = "target-" + "generation:ancestry:0".encode().hex()
    assert r"\textbf{Browse generations}" in ancestry_text
    assert (
        f"\\item \\hyperlink{{{ancestry_generation_target}}}{{Generation 0}}"
        in ancestry_text
    )
    assert f"\\hypertarget{{{ancestry_generation_target}}}" in ancestry_text
    assert ancestry_text.index(r"\hypertarget{") < ancestry_text.index(
        r"\subsection*{Generation 0}"
    )
    generation_zero_text = ancestry_text.split(
        r"\subsection*{Generation 0}", 1
    )[1].split(r"\end{itemize}", 1)[0]
    assert generation_zero_text.index("p0") < generation_zero_text.index("p1")

    descent_text = rendered[descent_start:connections_start]
    assert r"\subsection*{Generation 1}" in descent_text
    descent_generation_target = "target-" + "generation:descent:1".encode().hex()
    assert (
        f"\\item \\hyperlink{{{descent_generation_target}}}{{Generation 1}}"
        in descent_text
    )
    assert f"\\hypertarget{{{descent_generation_target}}}" in descent_text
    assert any(
        r"\hypertarget{" in line and "child" in line
        for line in descent_text.splitlines()
    )
    connection_text = rendered[connections_start:]
    parent_child_lines = [
        line
        for line in connection_text.splitlines()
        if "child" in line and "to$" in line
    ]
    for parent in ("p0", "p1"):
        assert any(
            parent in line and r"\hyperlink{" in line
            for line in parent_child_lines
        ), parent_child_lines


def test_other_union_descendant_uses_both_family_contexts_but_one_person_entry():
    p0 = _person("p0", family_handles=("f0", "f1"))
    p1 = _person("p1", family_handles=("f0",))
    other_partner = _person("other-partner", family_handles=("f1",))
    shared_child = _person(
        "shared-child",
        parent_family_handles=("f0", "f1"),
        attributes=(Attribute(BOOK_PROFILE, "YES"),),
    )
    central = _family("f0", p0, p1, (shared_child,))
    other_union = _family("f1", p0, other_partner, (shared_child,))
    model = build_book_model(
        _snapshot(
            central,
            (central, other_union),
            (p0, p1, other_partner, shared_child),
        )
    )

    child_occurrences = [
        occurrence
        for occurrence in _occurrences_in(model.genealogy, "descent")
        if occurrence.person_handle == "shared-child" and occurrence.generation == 1
    ]
    assert {occurrence.family_handle for occurrence in child_occurrences} == {"f0", "f1"}
    assert len(child_occurrences) == 2

    other_section = next(
        section
        for section in model.genealogy.family_sections
        if section.family_handle == "f1" and section.part == "descent"
    )
    assert set(other_section.child_occurrence_ids) == {
        occurrence.occurrence_id
        for occurrence in child_occurrences
        if occurrence.family_handle == "f1"
    }
    index_entries = [
        entry
        for entry in model.editorial_book.person_index
        if entry.person_handle == "shared-child"
    ]
    assert len(index_entries) == 1
    assert set(index_entries[0].occurrence_ids) == {
        occurrence.occurrence_id for occurrence in child_occurrences
    }
    assert model.genealogy.profile_handles.count("shared-child") == 1

    rendered = render_latex(model)
    assert rendered.count(r"\subsection*{shared-child}") == 1
    assert "other-partner" in rendered
    person_index = rendered.split(r"\section*{Person index}", 1)[1]
    assert person_index.count("shared-child") == 1


def test_explicit_adoptive_and_foster_parentage_keeps_types_and_excludes_none_links():
    p0 = _person("p0", parent_family_handles=("f-adoptive", "f-foster"))
    p1 = _person("p1")
    adoptive_father = _person("adoptive-father", family_handles=("f-adoptive",))
    adoptive_mother = _person("adoptive-mother", family_handles=("f-adoptive",))
    foster_father = _person("foster-father", family_handles=("f-foster",))
    foster_mother = _person("foster-mother", family_handles=("f-foster",))
    central = _family("f0", p0, p1)
    adoptive = _family(
        "f-adoptive",
        adoptive_father,
        adoptive_mother,
        (p0,),
        relations={"p0": ("Adopted", "None")},
    )
    foster = _family(
        "f-foster",
        foster_father,
        foster_mother,
        (p0,),
        relations={"p0": ("Foster", "None")},
    )
    model = build_book_model(
        _snapshot(
            central,
            (central, adoptive, foster),
            (
                p0,
                p1,
                adoptive_father,
                adoptive_mother,
                foster_father,
                foster_mother,
            ),
        )
    )

    lineage_parent_handles = {
        occurrence.person_handle
        for occurrence in _occurrences_in(model.genealogy, "ancestry")
        if occurrence.generation == -1 and "lineage" in occurrence.roles
    }
    assert lineage_parent_handles == {"adoptive-father", "foster-father"}

    occurrences_by_id = {
        occurrence.occurrence_id: occurrence
        for occurrence in _occurrences_in(model.genealogy, "ancestry")
    }
    for family_handle, parent_handle, relationship_type in (
        ("f-adoptive", "adoptive-father", "Adopted"),
        ("f-foster", "foster-father", "Foster"),
    ):
        section = next(
            section
            for section in model.genealogy.family_sections
            if section.family_handle == family_handle and section.part == "ancestry"
        )
        assert {
            occurrences_by_id[link.parent_occurrence_id].person_handle
            for link in section.parent_child_links
        } == {parent_handle}
        assert {
            link.relationship_type for link in section.parent_child_links
        } == {relationship_type}

    rendered = render_latex(model)
    assert "(Adopted)" in rendered
    assert "(Foster)" in rendered
    assert "(None)" not in rendered


def test_implex_creates_one_profile_and_cycle_paths_stop_expanding():
    p0 = _person("p0", family_handles=("f0", "f-cycle"), parent_family_handles=("f-p0",))
    p1 = _person("p1", family_handles=("f0",), parent_family_handles=("f-p1",))
    shared_ancestor = _person(
        "shared-ancestor",
        family_handles=("f-p0", "f-p1"),
        parent_family_handles=("f-cycle",),
        attributes=(Attribute(BOOK_PROFILE, "YES"),),
    )
    spouse_a = _person("spouse-a", family_handles=("f-p0", "f-cycle"))
    spouse_b = _person("spouse-b", family_handles=("f-p1",))
    central = _family("f0", p0, p1)
    p0_parents = _family("f-p0", shared_ancestor, spouse_a, (p0,))
    p1_parents = _family("f-p1", shared_ancestor, spouse_b, (p1,))
    cycle_family = _family("f-cycle", p0, spouse_a, (shared_ancestor,))
    model = build_book_model(
        _snapshot(
            central,
            (central, p0_parents, p1_parents, cycle_family),
            (p0, p1, shared_ancestor, spouse_a, spouse_b),
        )
    )

    ancestor_occurrences = [
        occurrence
        for occurrence in _occurrences_in(model.genealogy, "ancestry")
        if occurrence.person_handle == "shared-ancestor" and occurrence.generation == -1
    ]
    assert {occurrence.branch_handles[0] for occurrence in ancestor_occurrences} == {"p0", "p1"}

    index_entries = [
        entry
        for entry in model.editorial_book.person_index
        if entry.person_handle == "shared-ancestor"
    ]
    profiles = [
        profile
        for profile in model.editorial_book.profiles
        if profile.person_handle == "shared-ancestor"
    ]
    assert len(index_entries) == 1
    assert len(index_entries[0].occurrence_ids) >= 2
    assert len(profiles) == 1
    shared_occurrences = [
        occurrence
        for occurrence in _all_occurrences(model.genealogy)
        if occurrence.person_handle == "shared-ancestor"
    ]
    assert sum(occurrence.is_primary_profile for occurrence in shared_occurrences) == 1
    assert any(
        diagnostic.code == "genealogy_cycle"
        for diagnostic in model.genealogy.diagnostics
    )

    rendered = render_latex(model)
    assert rendered.count(r"\subsection*{shared-ancestor}") == 1
    assert "first appearance in the genealogy" in rendered


def test_ancestral_sibling_is_documented_without_expanding_the_siblings_family():
    p0 = _person("p0", family_handles=("f0",), parent_family_handles=("f-parents",))
    p1 = _person("p1", family_handles=("f0",))
    grandparent_a = _person("grandparent-a", family_handles=("f-parents",))
    grandparent_b = _person("grandparent-b", family_handles=("f-parents",))
    occupation = Event(
        handle="uncle-occupation",
        type="Occupation",
        description="Charpentier",
    )
    uncle = _person(
        "uncle",
        family_handles=("f-uncle",),
        parent_family_handles=("f-parents",),
        event_refs=(_event_ref("uncle-occupation"),),
    )
    uncle_partner = _person("uncle-partner", family_handles=("f-uncle",))
    cousin = _person("cousin", parent_family_handles=("f-uncle",))
    central = _family("f0", p0, p1)
    parent_family = _family(
        "f-parents",
        grandparent_a,
        grandparent_b,
        (p0, uncle),
    )
    uncle_family = _family("f-uncle", uncle, uncle_partner, (cousin,))
    model = build_book_model(
        _snapshot(
            central,
            (central, parent_family, uncle_family),
            (
                p0,
                p1,
                grandparent_a,
                grandparent_b,
                uncle,
                uncle_partner,
                cousin,
            ),
            events={"uncle-occupation": occupation},
        )
    )

    uncle_occurrences = [
        occurrence
        for occurrence in _occurrences_in(model.genealogy, "ancestry")
        if occurrence.person_handle == "uncle"
    ]
    assert len(uncle_occurrences) == 1
    assert "sibling" in uncle_occurrences[0].roles
    assert "uncle" in model.genealogy.profile_handles
    assert all(
        occurrence.person_handle != "cousin"
        for occurrence in _all_occurrences(model.genealogy)
    )

    parent_section = next(
        section
        for section in model.genealogy.family_sections
        if section.family_handle == "f-parents" and section.part == "ancestry"
    )
    assert uncle_occurrences[0].occurrence_id in parent_section.child_occurrence_ids

    rendered = render_latex(model)
    assert r"\subsection*{uncle}" in rendered
    assert "cousin" not in rendered


def _spouse_book(force_profile=False, family_event=False):
    p0 = _person("p0", family_handles=("f0", "f-other-union"))
    p1 = _person("p1", family_handles=("f0",))
    spouse = _person(
        "spouse",
        family_handles=("f-other-union",),
        event_refs=(_event_ref("birth"), _event_ref("death")),
        attributes=(Attribute(BOOK_PROFILE, "YES"),) if force_profile else (),
    )
    central = _family("f0", p0, p1)
    other_union = _family(
        "f-other-union",
        p0,
        spouse,
        event_refs=(_event_ref("marriage", "Family"),) if family_event else (),
    )
    events = {
        "birth": Event(
            handle="birth",
            type="Birth",
            date=DateValue(display="1900"),
        ),
        "death": Event(
            handle="death",
            type="Death",
            date=DateValue(display="1970"),
        ),
    }
    if family_event:
        events["marriage"] = Event(
            handle="marriage",
            type="Marriage",
            description="Union célébrée",
            date=DateValue(display="1920"),
        )
    return _snapshot(central, (central, other_union), (p0, p1, spouse), events)


def test_birth_and_death_only_spouse_is_mentioned_but_book_profile_can_force_a_profile():
    unforced = build_book_model(_spouse_book())
    assert "spouse" not in unforced.genealogy.profile_handles
    assert not any(
        profile.person_handle == "spouse"
        for profile in unforced.editorial_book.profiles
    )
    spouse_occurrence = next(
        occurrence
        for occurrence in _occurrences_in(unforced.genealogy, "descent")
        if occurrence.person_handle == "spouse"
    )
    assert spouse_occurrence.generation == 0
    assert "partner" in spouse_occurrence.roles

    forced = build_book_model(_spouse_book(force_profile=True))
    assert "spouse" in forced.genealogy.profile_handles
    assert sum(
        occurrence.is_primary_profile
        for occurrence in _all_occurrences(forced.genealogy)
        if occurrence.person_handle == "spouse"
    ) == 1

    unforced_render = render_latex(unforced)
    forced_render = render_latex(forced)
    assert "spouse" in unforced_render
    assert r"\subsection*{spouse}" not in unforced_render
    assert r"\subsection*{spouse}" in forced_render


def test_family_event_qualifies_partner_but_stays_in_family_notice():
    model = build_book_model(_spouse_book(family_event=True))
    spouse_profile = next(
        profile
        for profile in model.editorial_book.profiles
        if profile.person_handle == "spouse"
    )
    assert "spouse" in model.genealogy.profile_handles
    assert all(reference.event_handle != "marriage" for reference in spouse_profile.event_refs)

    family_notice = next(
        notice
        for notice in model.editorial_book.family_notices
        if notice.family_handle == "f-other-union"
    )
    assert [reference.event_handle for reference in family_notice.event_refs] == ["marriage"]

    rendered = render_latex(model)
    assert rendered.count("Union célébrée") == 1
    notice_section = rendered.split(r"\section*{Family notices}", 1)[1].split(
        r"\section*{Person profiles}", 1
    )[0]
    assert "Union célébrée" in notice_section
    profile_section = rendered.split(r"\section*{Person profiles}", 1)[1]
    assert "Union célébrée" not in profile_section


def test_single_parent_family_section_has_only_the_recorded_parent():
    p0 = _person("p0", family_handles=("f0", "f-single"))
    p1 = _person("p1", family_handles=("f0",))
    child = _person("child", parent_family_handles=("f-single",))
    central = _family("f0", p0, p1)
    single_parent = _family(
        "f-single",
        p0,
        None,
        (child,),
        relations={"child": ("Birth", None)},
    )
    model = build_book_model(
        _snapshot(central, (central, single_parent), (p0, p1, child))
    )

    section = next(
        section
        for section in model.genealogy.family_sections
        if section.family_handle == "f-single" and section.part == "descent"
    )
    assert len(section.partner_occurrence_ids) == 1
    assert len(section.child_occurrence_ids) == 1
    link = section.parent_child_links[0]
    assert link.relationship_type == "Birth"
    assert not any(
        diagnostic.code.startswith("missing_traversal")
        for diagnostic in model.genealogy.diagnostics
    )

    rendered = render_latex(model)
    connection_section = rendered.split(r"\section*{Family connections}", 1)[1]
    section_label = f"(descent, generation {section.generation})"
    assert any(
        section_label in line and "}{p0}" in line and "p1" not in line
        for line in connection_section.splitlines()
    )
    assert any(
        "p0}" in line and "$\\to$" in line and "child" in line and "(Birth)" in line
        for line in connection_section.splitlines()
    )


def test_depth_limits_count_parent_child_edges_and_keep_frontier_context():
    p0 = _person(
        "p0",
        family_handles=("f0", "f-second-union"),
        parent_family_handles=("f-parents",),
    )
    p1 = _person("p1", family_handles=("f0",))
    child = _person(
        "child",
        family_handles=("f-child-union",),
        parent_family_handles=("f0",),
    )
    second_partner = _person("second-partner", family_handles=("f-second-union",))
    second_union_child = _person(
        "second-union-child",
        parent_family_handles=("f-second-union",),
    )
    parent_a = _person(
        "parent-a",
        family_handles=("f-parents",),
        parent_family_handles=("f-grandparents",),
    )
    parent_b = _person("parent-b", family_handles=("f-parents",))
    grandparent_a = _person("grandparent-a", family_handles=("f-grandparents",))
    grandparent_b = _person("grandparent-b", family_handles=("f-grandparents",))
    child_partner = _person("child-partner", family_handles=("f-child-union",))
    grandchild = _person("grandchild", parent_family_handles=("f-child-union",))

    central = _family("f0", p0, p1, (child,))
    second_union = _family(
        "f-second-union",
        p0,
        second_partner,
        (second_union_child,),
    )
    parents = _family("f-parents", parent_a, parent_b, (p0,))
    grandparents = _family("f-grandparents", grandparent_a, grandparent_b, (parent_a,))
    child_union = _family("f-child-union", child, child_partner, (grandchild,))
    snapshot = _snapshot(
        central,
        (central, second_union, parents, grandparents, child_union),
        (
            p0,
            p1,
            child,
            second_partner,
            second_union_child,
            parent_a,
            parent_b,
            grandparent_a,
            grandparent_b,
            child_partner,
            grandchild,
        ),
    )

    bounded = build_book_model(
        snapshot,
        max_ancestor_depth=1,
        max_descendant_depth=1,
    )
    bounded_ancestry = _occurrences_in(bounded.genealogy, "ancestry")
    bounded_descent = _occurrences_in(bounded.genealogy, "descent")
    assert any(
        occurrence.person_handle == "parent-a" and occurrence.generation == -1
        for occurrence in bounded_ancestry
    )
    assert all(
        occurrence.person_handle not in {"grandparent-a", "grandparent-b"}
        for occurrence in bounded_ancestry
    )
    assert any(
        occurrence.person_handle == "child" and occurrence.generation == 1
        for occurrence in bounded_descent
    )
    assert any(
        occurrence.person_handle == "second-union-child"
        and occurrence.generation == 1
        for occurrence in bounded_descent
    )
    assert all(
        occurrence.person_handle != "grandchild"
        for occurrence in bounded_descent
    )

    frontier_union = next(
        section
        for section in bounded.genealogy.family_sections
        if section.family_handle == "f-child-union" and section.part == "descent"
    )
    frontier_partners = {
        occurrence.person_handle
        for occurrence in bounded_descent
        if occurrence.occurrence_id in frontier_union.partner_occurrence_ids
    }
    assert frontier_partners == {"child", "child-partner"}
    assert frontier_union.child_occurrence_ids == ()

    zero_depth = build_book_model(snapshot, max_ancestor_depth=0, max_descendant_depth=0)
    zero_occurrences = _all_occurrences(zero_depth.genealogy)
    assert all(
        occurrence.person_handle not in {
            "parent-a",
            "parent-b",
            "child",
            "second-union-child",
            "grandchild",
        }
        for occurrence in zero_occurrences
    )
    assert any(
        occurrence.person_handle == "second-partner" and occurrence.generation == 0
        for occurrence in _occurrences_in(zero_depth.genealogy, "descent")
    )
    zero_union = next(
        section
        for section in zero_depth.genealogy.family_sections
        if section.family_handle == "f-second-union" and section.part == "descent"
    )
    assert zero_union.child_occurrence_ids == ()
