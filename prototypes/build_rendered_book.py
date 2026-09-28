"""Generate a multi-page synthetic book through the production LaTeX renderer."""

from __future__ import annotations

import os
from pathlib import Path

from gramps_fancy_book.domain import (
    BookModel, Citation, DateValue, EditorialBook, EditorialCitationCall,
    EditorialCitationEntry, EditorialFamilyNotice, EditorialProfile, Event,
    EventReference, Family, FamilySection, Genealogy, GenealogyPart, Generation,
    Note, Person, PersonOccurrence, Place, Repository, RepositoryReference, Source, Url,
)
from gramps_fancy_book.renderers.latex import render_latex


def build_model() -> BookModel:
    father = Person(handle="person-father", name="Émile Exemple", gramps_id="I0001")
    mother = Person(handle="person-mother", name="Jeanne Fictive", gramps_id="I0002")
    child = Person(handle="person-child", name="Camille Exemple", gramps_id="I0003")
    family = Family(
        handle="family-central", father=father, mother=mother, children=(child,),
        gramps_id="F0001",
    )
    place = Place(handle="place-example", name="Saint-Exemple, département fictif")

    events = {
        "event-union": Event(
            handle="event-union", gramps_id="E0001", type="Marriage",
            description="Union du couple central", date=DateValue(display="1901"),
            place_handle=place.handle,
        )
    }
    event_refs = []
    event_target_ids = []
    for index in range(1, 81):
        handle = f"event-profile-{index:03d}"
        events[handle] = Event(
            handle=handle, gramps_id=f"E{index + 1:04d}",
            type="Residence" if index % 3 else "Occupation",
            description=(
                f"Événement biographique {index:03d} — "
                "description fictive conservée dans son contexte documentaire."
            ),
            date=DateValue(display=str(1880 + index)),
            place_handle=place.handle,
        )
        event_refs.append(EventReference(event_handle=handle))
        event_target_ids.append(f"profile-event-{index:03d}")

    note_text = "\n\n".join(
        f"Paragraphe {index:02d}. Cette note fictive qualifie le contexte, "
        "les limites de la source et la prudence nécessaire dans son interprétation. "
        "Les détails restent lisibles lorsque la fiche se poursuit sur plusieurs pages. "
        "Émile et Jeanne sont des personnes imaginaires ; aucune donnée réelle n'est utilisée."
        for index in range(1, 31)
    )
    note = Note(
        handle="note-long", gramps_id="N0001", text=note_text, type=24,
        is_publishable=True,
    )

    repository = Repository(
        handle="repository-1", gramps_id="R0001",
        name="Dépôt fictif des archives communales",
        urls=(Url(
            "https://example.org/archives/registre/parish/fictitious-long-reference",
            "Catalogue en ligne",
        ),),
    )
    source = Source(
        handle="source-1", gramps_id="S0001",
        title="Registre fictif de la commune",
        author="Service imaginaire des archives",
        repository_refs=(RepositoryReference(
            repository_handle=repository.handle, call_number="Registre 1, folio 42",
        ),),
    )
    citation = Citation(
        handle="citation-1", gramps_id="C0001", source_handle=source.handle,
        page="folio 42",
        urls=(Url(
            "https://example.org/archives/registre/fictif/folio-0042?view=full&lang=fr",
            "Image du registre",
        ),),
    )
    profile_id = "profile-father"
    call = EditorialCitationCall(
        call_id="call-profile-source", citation_handle=citation.handle,
        context_id=profile_id, owner_type="person", owner_handle=father.handle,
        field_path="profile.sources",
    )
    citation_entry = EditorialCitationEntry(
        entry_id="citation-entry-1", citation_handle=citation.handle,
        source_handle=source.handle, repository_refs=source.repository_refs,
        calls=(call,),
    )
    profile = EditorialProfile(
        profile_id=profile_id, person_handle=father.handle,
        primary_occurrence_id="occurrence-father",
        note_handles=(note.handle,), event_refs=tuple(event_refs),
        citation_call_ids=(call.call_id,), note_target_ids=("note-long-target",),
        event_target_ids=tuple(event_target_ids),
    )
    notice = EditorialFamilyNotice(
        notice_id="notice-central", family_handle=family.handle,
        primary_section_id="family-section-central",
        event_refs=(EventReference(event_handle="event-union"),),
        event_target_ids=("notice-event-union",),
    )

    father_occurrence = PersonOccurrence(
        occurrence_id="occurrence-father", person_handle=father.handle,
        generation=0, family_handle=family.handle, is_primary_profile=True,
    )
    mother_occurrence = PersonOccurrence(
        occurrence_id="occurrence-mother", person_handle=mother.handle,
        generation=0, family_handle=family.handle,
    )
    child_occurrence = PersonOccurrence(
        occurrence_id="occurrence-child", person_handle=child.handle,
        generation=1, family_handle=family.handle,
    )
    family_section = FamilySection(
        family_handle=family.handle, part="descent", generation=1,
        section_id="family-section-central",
        partner_occurrence_ids=(
            father_occurrence.occurrence_id, mother_occurrence.occurrence_id,
        ),
        child_occurrence_ids=(child_occurrence.occurrence_id,),
    )
    genealogy = Genealogy(
        ancestry=GenealogyPart(
            name="ancestry",
            generations=(Generation(
                number=0, occurrences=(father_occurrence, mother_occurrence),
            ),),
        ),
        descent=GenealogyPart(
            name="descent",
            generations=(Generation(number=1, occurrences=(child_occurrence,)),),
        ),
        family_sections=(family_section,), profile_handles=(father.handle,),
    )

    return BookModel(
        reference_family=family, people=[father, mother, child],
        families={family.handle: family}, events=events, places={place.handle: place},
        notes={note.handle: note}, citations={citation.handle: citation},
        sources={source.handle: source}, repositories={repository.handle: repository},
        genealogy=genealogy,
        editorial_book=EditorialBook(
            family_notices=(notice,), profiles=(profile,),
            citation_entries=(citation_entry,),
        ),
    )


def main() -> None:
    default_output = (
        Path(__file__).resolve().parents[1] / ".work" / "latex-spike"
        / "rendered-book.tex"
    )
    output = Path(os.environ.get("LATEX_RENDERED_BOOK_OUTPUT", default_output))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_latex(build_model()), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
