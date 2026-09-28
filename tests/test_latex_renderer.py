from gramps_fancy_book.domain import (
    BookModel,
    Citation,
    DateValue,
    EditorialBook,
    EditorialCitationCall,
    EditorialCitationEntry,
    EditorialProfile,
    Event,
    EventReference,
    Family,
    Note,
    Person,
    Place,
    Repository,
    RepositoryReference,
    Source,
    Url,
)
from gramps_fancy_book.renderers.latex import render_latex


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
        urls=(Url("https://example.org/archive?folio=1&format=full", "record_&"),),
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

    rendered = render_latex(model)

    assert r"\textbackslash{}input\{owned\}" in rendered
    assert r"\input{owned}" not in rendered
    assert r"50\% value\_a \&" in rendered
    assert r"Place\_\&\_One" in rendered
    assert r"Source \textbackslash{}input\{owned\} \#1\_50\%" in rendered
    assert r"Repository\_\&" in rendered
    assert r"R\_1\&" in rendered
    assert r"\url{https://example.org/archive?folio=1&format=full}" in rendered
    assert r"(record\_\&)" in rendered
