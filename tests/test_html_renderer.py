import re
import zipfile
from types import SimpleNamespace

from gramps_fancy_book.domain import (
    Citation,
    EditorialMediaArtifact,
    EditorialMediaPlacement,
    EditorialMediaUse,
    Family,
    Media,
    MediaReference,
    Person,
    Repository,
    RepositoryReference,
    Source,
    Url,
)
from gramps_fancy_book.renderers.html import render_html
from gramps_fancy_book.renderers.html_archive import write_html_archive


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
    repository_reference = RepositoryReference(
        repository_handle="r1",
        call_number="3 E 12",
    )
    citation_entry = SimpleNamespace(
        entry_id="citation-entry:c1",
        citation_handle="c1",
        source_handle="s1",
        repository_refs=(repository_reference,),
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
        citations={
            "c1": Citation(
                handle="c1",
                gramps_id="C0001",
                source_handle="s1",
                urls=(Url("javascript:alert(1)", description="Unsafe URL"),),
            )
        },
        sources={
            "s1": Source(
                handle="s1",
                gramps_id="S0001",
                title="Registre paroissial",
                author="Archives fictives",
                abbreviation="Registre",
                urls=(
                    Url(
                        "https://example.invalid/source?record=one&image=two",
                        description="Notice de la source",
                    ),
                ),
            )
        },
        repositories={
            "r1": Repository(
                handle="r1",
                gramps_id="R0001",
                name="Dépôt municipal fictif",
                urls=(
                    Url(
                        "https://example.invalid/shared-document?id=42&view=scan",
                        description="Document partagé fictif",
                    ),
                ),
            )
        },
    )

    rendered = render_html(model)

    assert '<html lang="fr">' in rendered
    assert '<a href="#ancestry">Ascendance</a>' in rendered
    assert 'id="family-notice:f0"' in rendered
    assert 'id="family:ancestry:0:f0"' in rendered
    assert 'id="person:p0"' in rendered
    assert 'id="citation-entry:c1"' in rendered
    assert "C0001" in rendered
    assert "S0001" in rendered
    assert 'href="https://example.invalid/source?record=one&amp;image=two"' in rendered
    assert (
        'href="https://example.invalid/shared-document?id=42&amp;view=scan"'
        in rendered
    )
    assert "javascript:alert(1)" not in rendered
    assert 'id="generation:descent:0"' in rendered
    assert 'href="#generation:descent:1"' in rendered
    assert 'href="#descent:0:f0:p0"' in rendered
    assert 'href="#person:p0"' in rendered
    assert "Branche :" in rendered
    assert (
        "filiation : Ada &amp; &lt;img src=x onerror=alert(1)&gt; : Adopted"
        in rendered
    )
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


def test_renders_shared_citation_media_once_in_the_html_archive(tmp_path):
    cache_key = "a" * 64
    first_entry_id = "citation-entry:c1"
    second_entry_id = "citation-entry:c2"
    first_reference = MediaReference(media_handle="m1")
    second_reference = MediaReference(media_handle="m1")
    first_entry = SimpleNamespace(
        entry_id=first_entry_id,
        citation_handle="c1",
        source_handle=None,
        repository_refs=(),
        media_refs=(first_reference,),
        calls=(),
    )
    second_entry = SimpleNamespace(
        entry_id=second_entry_id,
        citation_handle="c2",
        source_handle=None,
        repository_refs=(),
        media_refs=(second_reference,),
        calls=(),
    )
    placement = EditorialMediaPlacement(
        placement_id="media:m1",
        media_handle="m1",
        uses=(
            EditorialMediaUse("citation", first_entry_id, first_reference),
            EditorialMediaUse("citation", second_entry_id, second_reference),
        ),
    )
    parts = (
        SimpleNamespace(part_id="cover", kind="cover"),
        SimpleNamespace(
            part_id="contents",
            kind="table_of_contents",
            part_ids=("appendix",),
        ),
        SimpleNamespace(
            part_id="appendix",
            kind="documentary_appendix",
            citation_entry_ids=(first_entry_id, second_entry_id),
        ),
    )
    model = SimpleNamespace(
        reference_family=Family(
            handle="f0",
            gramps_id="F0001",
            father=None,
            mother=None,
            children=(),
        ),
        people=[],
        families={},
        genealogy=None,
        editorial_book=SimpleNamespace(
            parts=parts,
            profiles=(),
            family_notices=(),
            front_matter_notes=(),
            citation_entries=(first_entry, second_entry),
            media_placements=(placement,),
            cover_portraits=(),
            person_index=(),
        ),
        notes={},
        events={},
        places={},
        citations={},
        sources={},
        repositories={},
        media={"m1": Media("m1", description="Document partagé")},
        media_artifacts=[
            EditorialMediaArtifact(
                media_handle="m1",
                rectangle=None,
                action="reproduce",
                cache_key=cache_key,
                asset_path=f"media/{cache_key}.png",
                width=10,
                height=10,
            )
        ],
    )

    rendered = render_html(model, include_media=True)

    assert rendered.count(f'<img src="media/{cache_key}.png"') == 1
    assert rendered.count(f'id="media-{cache_key}"') == 1
    assert rendered.count(f'href="#media-{cache_key}"') == 1
    first_article = rendered.split(f'id="{first_entry_id}"', 1)[1].split(
        "</article>", 1
    )[0]
    second_article = rendered.split(f'id="{second_entry_id}"', 1)[1].split(
        "</article>", 1
    )[0]
    assert f'id="media-{cache_key}"' in first_article
    assert f'href="#media-{cache_key}"' in second_article

    staged_media = tmp_path / "staged-media"
    staged_media.mkdir()
    (staged_media / f"{cache_key}.png").write_bytes(b"test image payload")
    archive_path = write_html_archive(
        model,
        tmp_path / "book.zip",
        media_asset_directory=staged_media,
    )

    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        assert archive.namelist() == ["index.html", f"media/{cache_key}.png"]
        archived_html = archive.read("index.html").decode("utf-8")
    assert archived_html.count(f'<img src="media/{cache_key}.png"') == 1
    assert archived_html.count(f'href="#media-{cache_key}"') == 1
