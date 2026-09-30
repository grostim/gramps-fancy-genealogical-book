from gramps_fancy_book.domain import (
    BookModel,
    Citation,
    DateValue,
    EditorialBook,
    EditorialCitationCall,
    EditorialCitationEntry,
    EditorialMediaArtifact,
    EditorialMediaPlacement,
    EditorialMediaUse,
    EditorialProfile,
    Event,
    EventReference,
    Family,
    FamilySection,
    Genealogy,
    GenealogyPart,
    Generation,
    Media,
    MediaReference,
    Note,
    Person,
    PersonOccurrence,
    Place,
    Repository,
    RepositoryReference,
    Source,
    Url,
)
from gramps_fancy_book.renderers.latex import render_latex
from gramps_fancy_book.renderers.latex_notes import render_latex_note


def test_renderer_escapes_model_text_and_keeps_urls_usable():
    person = Person(
        handle="person-1",
        name=r"Émile \input{owned}_&",
        gramps_id="I0001",
    )
    family = Family(handle="family-1", father=person, gramps_id="F0001")
    event = Event(
        handle="event-1",
        gramps_id="E0001",
        type="Birth",
        description=r"Event \input{owned} 50% value_a &",
        date=DateValue(display="about 1900"),
        place_handle="place-1",
    )
    place = Place(handle="place-1", name=r"Place_&_One")
    note = Note(
        handle="note-1",
        text=r"Literal command: \input{owned}; percent 50%; key value_a & #",
        type=24,
        is_publishable=True,
    )
    citation = Citation(
        handle="citation-1",
        gramps_id="C0001",
        source_handle="source-1",
        page="page_1&2",
        urls=(
            Url(
                "https://example.org/archive%2Fdocument?folio=1&format=full#record",
                "record_&",
            ),
        ),
    )
    source = Source(
        handle="source-1",
        gramps_id="S0001",
        title=r"Source \input{owned} #1_50%",
        author="Author_&",
        publication_info="Edition_50%",
    )
    repository = Repository(handle="repository-1", name="Repository_&")
    repository_reference = RepositoryReference(
        repository_handle=repository.handle,
        call_number="R_1&",
    )
    profile = EditorialProfile(
        profile_id="profile-1",
        person_handle=person.handle,
        note_handles=(note.handle,),
        event_refs=(EventReference(event_handle=event.handle, role="Role_&"),),
        citation_call_ids=("call-1",),
        note_target_ids=("note-target",),
        event_target_ids=("event-target",),
    )
    call = EditorialCitationCall(
        call_id="call-1",
        citation_handle=citation.handle,
        context_id=profile.profile_id,
        owner_type="person",
        owner_handle=person.handle,
        field_path="profile.name",
    )
    entry = EditorialCitationEntry(
        entry_id="citation-entry-1",
        citation_handle=citation.handle,
        source_handle=source.handle,
        repository_refs=(repository_reference,),
        calls=(call,),
    )
    model = BookModel(
        reference_family=family,
        people=[person],
        families={family.handle: family},
        events={event.handle: event},
        places={place.handle: place},
        notes={note.handle: note},
        citations={citation.handle: citation},
        sources={source.handle: source},
        repositories={repository.handle: repository},
        editorial_book=EditorialBook(
            profiles=(profile,),
            citation_entries=(entry,),
        ),
    )

    rendered = render_latex(
        model, gramps_type_labels={("event", "Birth"): "Naissance"}
    )

    assert r"\textbackslash{}input\{owned\}" in rendered
    assert r"\input{owned}" not in rendered
    assert r"50\% value\_a \&" in rendered
    assert r"Place\_\&\_One" in rendered
    assert "Naissance" in rendered
    assert "Birth" not in rendered
    assert r"Source \textbackslash{}input\{owned\} \#1\_50\%" in rendered
    assert r"Repository\_\&" in rendered
    assert r"R\_1\&" in rendered
    assert (
        r"\newcommand{\bookurl}[3]{\href{#1}{{\useOriginalUrlSetting\nolinkurl{#2}}\nolinkurl{#3}}}"
        in rendered
    )
    assert (
        r"\tagpdfsetup{role/new-attribute={gfb-strikethrough}{/O/Layout/TextDecorationType/LineThrough}}"
        in rendered
    )
    assert r"\tagstructbegin{tag=Span,attribute-class={gfb-strikethrough}}" in rendered
    assert (
        r"\bookurl{https://example.org/archive\%2Fdocument?folio=1&format=full\#record}"
        r"{https://example.org}{/archive\%2Fdocument?folio=1&format=full\#record}"
        in rendered
    )
    assert r"(record\_\&)" in rendered


def test_latex_strikethrough_notes_keep_text_and_visual_command():
    note = Note(handle="note-strike", text="Avant ~~texte barré~~ après.")

    rendered = render_latex_note(note)

    assert r"Avant \sout{texte barré} après." in rendered
    assert rendered.endswith(r"\par" + "\n")


def test_pdf_renders_shared_citation_media_once_and_links_later_uses():
    cache_key = "a" * 64
    first_entry_id = "citation-entry:c1"
    second_entry_id = "citation-entry:c2"
    first_reference = MediaReference(media_handle="m1")
    second_reference = MediaReference(media_handle="m1")
    first_entry = EditorialCitationEntry(
        entry_id=first_entry_id,
        citation_handle="c1",
        media_refs=(first_reference,),
    )
    second_entry = EditorialCitationEntry(
        entry_id=second_entry_id,
        citation_handle="c2",
        media_refs=(second_reference,),
    )
    placement = EditorialMediaPlacement(
        placement_id="media:m1",
        media_handle="m1",
        caption="Document partagé",
        uses=(
            EditorialMediaUse("citation", first_entry_id, first_reference),
            EditorialMediaUse("citation", second_entry_id, second_reference),
        ),
    )
    model = BookModel(
        reference_family=Family(
            handle="f0",
            gramps_id="F0001",
            father=None,
            mother=None,
            children=(),
        ),
        metadata={"BOOK_LANGUAGE": "fr"},
        media={"m1": Media(handle="m1", description="Document partagé")},
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
        editorial_book=EditorialBook(
            citation_entries=(first_entry, second_entry),
            media_placements=(placement,),
        ),
    )

    rendered = render_latex(model)
    target = "target-" + f"media-{cache_key}".encode().hex()

    assert rendered.startswith(r"\DocumentMetadata{lang=fr-FR,tagging=on}")
    image_command = r"\includegraphics[width=0.6\linewidth,alt={Document partagé}]"
    assert rendered.count(image_command) == 1
    assert rendered.count(f"\\hypertarget{{{target}}}") == 1
    assert rendered.count(f"\\hyperlink{{{target}}}") == 2
    assert "Voir la reproduction :" in rendered
    assert rendered.index(image_command) < rendered.index("Voir la reproduction :")


def test_running_headers_include_section_generation_branch_and_page_number():
    alex = Person(handle="alex", name="Alex Exemple")
    camille = Person(handle="camille", name="Camille Exemple")
    child = Person(handle="child", name="Enfant Exemple")
    family = Family(
        handle="family",
        father=alex,
        mother=camille,
        children=(child,),
    )
    model = BookModel(
        reference_family=family,
        people=[alex, camille, child],
        families={family.handle: family},
        genealogy=Genealogy(
            ancestry=GenealogyPart(
                "ancestry",
                (
                    Generation(
                        0,
                        (
                            PersonOccurrence(
                                "a-alex", "alex", 0, branch_handles=("alex",)
                            ),
                            PersonOccurrence(
                                "a-camille", "camille", 0, branch_handles=("camille",)
                            ),
                        ),
                    ),
                ),
            ),
            descent=GenealogyPart(
                "descent",
                (
                    Generation(
                        0,
                        (
                            PersonOccurrence(
                                "d-alex", "alex", 0, branch_handles=("alex",)
                            ),
                        ),
                    ),
                    Generation(
                        1,
                        (
                            PersonOccurrence(
                                "d-child", "child", 1, branch_handles=("alex",)
                            ),
                        ),
                    ),
                ),
            ),
            family_sections=(
                FamilySection(
                    family_handle="family",
                    part="descent",
                    generation=1,
                    branch_handles=("alex",),
                    section_id="family-section",
                    partner_occurrence_ids=("d-alex",),
                    child_occurrence_ids=("d-child",),
                ),
            ),
        ),
    )

    rendered = render_latex(model)

    assert r"\usepackage{fancyhdr}" in rendered
    assert (
        r"\fancyhead[L]{\parbox[t]{\headwidth}{\footnotesize"
        r"\nouppercase{\leftmark}\hfill\thepage\\[4pt]\nouppercase{\rightmark}}}"
        in rendered
    )
    assert r"\fancyhead[R]{}" in rendered
    assert r"\thepage" in rendered
    assert r"\setlength{\headheight}{30pt}" in rendered
    assert rendered.index(r"\markboth{Contents}{}") < rendered.index(r"\tableofcontents")
    assert r"\markboth{Ancestry}{Generation 0 / Branch: Alex Exemple}" in rendered
    assert r"\markright{Generation 0 / Branch: Camille Exemple}" in rendered
    assert r"\markright{Generation 1 / Branch: Alex Exemple}" in rendered
    assert (
        r"\markboth{Family connections}{Generation 1 / Branch: Alex Exemple}"
        in rendered
    )
