import re
from types import SimpleNamespace

from gramps_fancy_book.domain import Family, Person
from gramps_fancy_book.renderers.html import render_html


def test_renders_shared_parts_with_stable_navigation_and_escaped_text():
    p0 = Person("p0", "Ada & <img src=x onerror=alert(1)>")
    p1 = Person("p1", "Benoît Exemple")
    child = Person("child", "Camille Exemple")
    family = Family(
        handle="f0",
        gramps_id="F0001",
        father=p0,
        mother=p1,
        children=(child,),
    )

    p0_occurrence = SimpleNamespace(
        occurrence_id="ancestry:0:f0:p0",
        person_handle="p0",
        generation=0,
        branch_handles=("p0",),
        family_section_ids=("family:ancestry:0:f0",),
        primary_occurrence_id="ancestry:0:f0:p0",
        is_primary_profile=True,
    )
    p1_occurrence = SimpleNamespace(
        occurrence_id="ancestry:0:f0:p1",
        person_handle="p1",
        generation=0,
        branch_handles=("p1",),
        family_section_ids=("family:ancestry:0:f0",),
        primary_occurrence_id="ancestry:0:f0:p1",
        is_primary_profile=False,
    )
    child_occurrence = SimpleNamespace(
        occurrence_id="descent:1:f0:child",
        person_handle="child",
        generation=1,
        branch_handles=("p0",),
        family_section_ids=(),
        primary_occurrence_id="descent:1:f0:child",
        is_primary_profile=False,
    )
    family_section = SimpleNamespace(
        family_handle="f0",
        section_id="family:ancestry:0:f0",
        partner_occurrence_ids=(
            p0_occurrence.occurrence_id,
            p1_occurrence.occurrence_id,
        ),
        child_occurrence_ids=(child_occurrence.occurrence_id,),
        parent_child_links=(
            SimpleNamespace(
                parent_occurrence_id=p0_occurrence.occurrence_id,
                child_occurrence_id=child_occurrence.occurrence_id,
                relationship_type="Adopted",
            ),
        ),
    )
    genealogy = SimpleNamespace(
        ancestry=SimpleNamespace(
            generations=(
                SimpleNamespace(
                    number=0,
                    occurrences=(p0_occurrence, p1_occurrence),
                ),
            ),
        ),
        descent=SimpleNamespace(
            generations=(
                SimpleNamespace(
                    number=0,
                    occurrences=(
                        SimpleNamespace(
                            occurrence_id="descent:0:f0:p0",
                            person_handle="p0",
                            generation=0,
                            branch_handles=("p0",),
                            family_section_ids=(),
                            primary_occurrence_id=p0_occurrence.occurrence_id,
                            is_primary_profile=False,
                        ),
                        SimpleNamespace(
                            occurrence_id="descent:0:f0:p1",
                            person_handle="p1",
                            generation=0,
                            branch_handles=("p1",),
                            family_section_ids=(),
                            primary_occurrence_id=p1_occurrence.occurrence_id,
                            is_primary_profile=False,
                        ),
                    ),
                ),
                SimpleNamespace(number=1, occurrences=(child_occurrence,)),
            ),
        ),
        family_sections=(family_section,),
    )
    profile = SimpleNamespace(
        profile_id="person:p0",
        person_handle="p0",
        primary_occurrence_id=p0_occurrence.occurrence_id,
        portrait=None,
        event_refs=(),
        event_target_ids=(),
        note_handles=(),
        note_target_ids=(),
        citation_call_ids=("call-1",),
    )
    family_notice = SimpleNamespace(
        notice_id="family-notice:f0",
        family_handle="f0",
        family_section_ids=(family_section.section_id,),
        event_refs=(),
        event_target_ids=(),
        note_handles=(),
        note_target_ids=(),
        citation_call_ids=(),
    )
    call = SimpleNamespace(
        call_id="call-1",
        context_id=profile.profile_id,
        owner_type="profile",
        owner_handle="p0",
    )
    citation_entry = SimpleNamespace(
        entry_id="citation-entry:c1",
        citation_handle="c1",
        source_handle=None,
        repository_refs=(),
        calls=(call,),
    )
    person_index_entry = SimpleNamespace(
        entry_id="person-index:p0",
        display_name=p0.name,
        target_id=profile.profile_id,
        alternate_names=(),
    )
    parts = (
        SimpleNamespace(part_id="cover", kind="cover"),
        SimpleNamespace(
            part_id="contents",
            kind="table_of_contents",
            part_ids=("ancestry", "descent", "appendix", "index"),
        ),
        SimpleNamespace(
            part_id="ancestry",
            kind="ancestry",
            family_notice_ids=(family_notice.notice_id,),
        ),
        SimpleNamespace(part_id="descent", kind="descent", family_notice_ids=()),
        SimpleNamespace(
            part_id="appendix",
            kind="documentary_appendix",
            citation_entry_ids=(citation_entry.entry_id,),
        ),
        SimpleNamespace(
            part_id="index",
            kind="person_index",
            person_index_entry_ids=(person_index_entry.entry_id,),
        ),
    )
    editorial_book = SimpleNamespace(
        parts=parts,
        profiles=(profile,),
        family_notices=(family_notice,),
        front_matter_notes=(),
        citation_entries=(citation_entry,),
        person_index=(person_index_entry,),
    )
    model = SimpleNamespace(
        reference_family=family,
        people=[p0, p1, child],
        families={"f0": family},
        genealogy=genealogy,
        editorial_book=editorial_book,
        notes={},
        events={},
        places={},
        citations={},
        sources={},
        repositories={},
    )

    rendered = render_html(model)

    assert '<html lang="fr">' in rendered
    assert '<a href="#ancestry">Ascendance</a>' in rendered
    assert 'id="family-notice:f0"' in rendered
    assert 'id="family:ancestry:0:f0"' in rendered
    assert 'id="person:p0"' in rendered
    assert 'id="citation-entry:c1"' in rendered
    assert 'id="generation:descent:0"' in rendered
    assert 'href="#generation:descent:1"' in rendered
    assert 'href="#descent:0:f0:p0"' in rendered
    assert 'href="#person:p0"' in rendered
    assert "Branche :" in rendered
    assert "filiation : Adopted" in rendered
    assert "Ada &amp; &lt;img src=x onerror=alert(1)&gt;" in rendered
    assert "<img src=x" not in rendered

    ids = re.findall(r'\bid="([^"]+)"', rendered)
    assert len(ids) == len(set(ids))
    targets = set(ids)
    links = re.findall(r'href="#([^"]+)"', rendered)
    assert set(links) <= targets


def test_renders_a_minimal_model_without_editorial_book():
    family = Family(
        handle="f0",
        gramps_id="F0001",
        father=Person("p0", "Ada Exemple"),
        mother=Person("p1", "Benoît Exemple"),
    )
    model = SimpleNamespace(
        reference_family=family,
        people=[family.father, family.mother],
        families={family.handle: family},
        editorial_book=None,
        genealogy=None,
    )

    rendered = render_html(model)

    assert "F0001" in rendered
    assert "Ada Exemple et Benoît Exemple" in rendered
    assert "2 personnes dans le modèle intermédiaire." in rendered
