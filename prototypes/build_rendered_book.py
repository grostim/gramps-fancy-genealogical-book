"""Generate a multi-page synthetic book through the production LaTeX renderer."""

from __future__ import annotations

import hashlib
import os
import struct
import zlib
from pathlib import Path

from gramps_fancy_book.domain import (
    BookModel,
    Citation,
    DateValue,
    Diagnostic,
    EditorialBook,
    EditorialCitationCall,
    EditorialCitationEntry,
    EditorialFamilyNotice,
    EditorialMediaArtifact,
    EditorialMediaPlacement,
    EditorialMediaUse,
    EditorialNavigationTarget,
    EditorialPersonIndexEntry,
    EditorialPortrait,
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


def _synthetic_portrait_png() -> bytes:
    width, height = 120, 160
    pixels = bytearray()
    for y in range(height):
        pixels.append(0)
        for x in range(width):
            face = (x - 60) ** 2 + (y - 52) ** 2 <= 24 ** 2
            neck = 48 <= x <= 72 and 74 <= y <= 105
            shoulders = ((x - 60) / 56) ** 2 + ((y - 148) / 66) ** 2 <= 1
            shade = 105 if face else 135 if neck or shoulders else 242
            pixels.extend((shade, shade, shade))

    def chunk(kind: bytes, payload: bytes) -> bytes:
        body = kind + payload
        return (
            struct.pack(">I", len(payload))
            + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(pixels))
        + chunk(b"IEND", b"")
    )


SYNTHETIC_PORTRAIT_PNG = _synthetic_portrait_png()
SYNTHETIC_PORTRAIT_KEY = hashlib.sha256(SYNTHETIC_PORTRAIT_PNG).hexdigest()
SYNTHETIC_PORTRAIT_PATH = "media/" + SYNTHETIC_PORTRAIT_KEY + ".png"


def build_model() -> BookModel:
    father = Person(handle="person-father", name="Émile Exemple", gramps_id="I0001")
    mother = Person(handle="person-mother", name="Jeanne Fictive", gramps_id="I0002")
    child = Person(handle="person-child", name="Camille Exemple", gramps_id="I0003")
    family = Family(
        handle="family-central", father=father, mother=mother, children=(child,),
        gramps_id="F0001",
    )
    place = Place(handle="place-example", name="Saint-Exemple, département fictif")

    portrait_reference = MediaReference(
        media_handle="media-photo",
        rectangle=(0, 0, 100, 100),
    )
    portrait = EditorialPortrait(
        person_handle=father.handle,
        media_ref=portrait_reference,
        caption="Portrait synthétique de recette — personne fictive",
    )
    unavailable_reference = MediaReference(media_handle="media-unavailable")

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
        media_refs=(portrait_reference, unavailable_reference),
        calls=(call,),
    )
    profile = EditorialProfile(
        profile_id=profile_id, person_handle=father.handle,
        primary_occurrence_id="occurrence-father",
        note_handles=(note.handle,), event_refs=tuple(event_refs), portrait=portrait,
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
        media={
            "media-photo": Media(
                handle="media-photo",
                description="Portrait synthétique — illustration fictive",
                mime_type="image/png",
            ),
            "media-unavailable": Media(
                handle="media-unavailable",
                description="Justificatif synthétique sans dérivé",
                mime_type="image/png",
            ),
        },
        diagnostics=[
            Diagnostic(
                code="MEDIA_DERIVATIVE_FAILED",
                severity="warning",
                object_type="media",
                handle="media-unavailable",
                message="Fixture: no raster derivative is supplied for this media.",
                context="citation:citation-entry-1",
            )
        ],
        media_artifacts=[
            EditorialMediaArtifact(
                media_handle="media-photo",
                rectangle=portrait_reference.rectangle,
                action="reproduce",
                context_ids=("profile:profile-father", "citation:citation-entry-1"),
                citation_handles=(citation.handle,),
                cache_key=SYNTHETIC_PORTRAIT_KEY,
                asset_path=SYNTHETIC_PORTRAIT_PATH,
                mime_type="image/png",
                width=120,
                height=160,
                dpi=150,
            ),
            EditorialMediaArtifact(
                media_handle="media-unavailable",
                rectangle=unavailable_reference.rectangle,
                action="failed",
                context_ids=("citation:citation-entry-1",),
                citation_handles=(citation.handle,),
                diagnostic_code="MEDIA_DERIVATIVE_FAILED",
            ),
        ],
        genealogy=genealogy,
        editorial_book=EditorialBook(
            family_notices=(notice,),
            profiles=(profile,),
            citation_entries=(citation_entry,),
            media_placements=(
                EditorialMediaPlacement(
                    placement_id="featured-portrait",
                    media_handle="media-photo",
                    caption=portrait.caption,
                    is_featured=True,
                    uses=(
                        EditorialMediaUse(
                            context_type="profile",
                            context_id=profile_id,
                            media_ref=portrait_reference,
                        ),
                        EditorialMediaUse(
                            context_type="citation",
                            context_id=citation_entry.entry_id,
                            media_ref=portrait_reference,
                            citation_handles=(citation.handle,),
                        ),
                    ),
                ),
                EditorialMediaPlacement(
                    placement_id="citation-without-derivative",
                    media_handle="media-unavailable",
                    caption="Justificatif synthétique sans dérivé",
                    uses=(
                        EditorialMediaUse(
                            context_type="citation",
                            context_id=citation_entry.entry_id,
                            media_ref=unavailable_reference,
                            citation_handles=(citation.handle,),
                        ),
                    ),
                ),
            ),
            cover_portraits=(portrait,),
            navigation_targets=(
                EditorialNavigationTarget(
                    target_id=father_occurrence.occurrence_id,
                    target_type="person-occurrence",
                    object_id=father.handle,
                ),
                EditorialNavigationTarget(
                    target_id=mother_occurrence.occurrence_id,
                    target_type="person-occurrence",
                    object_id=mother.handle,
                ),
            ),
            person_index=(
                EditorialPersonIndexEntry(
                    entry_id="person-index-father",
                    person_handle=father.handle,
                    display_name=father.name,
                    target_id=father_occurrence.occurrence_id,
                    occurrence_ids=(father_occurrence.occurrence_id,),
                    profile_id=profile_id,
                ),
                EditorialPersonIndexEntry(
                    entry_id="person-index-mother",
                    person_handle=mother.handle,
                    display_name=mother.name,
                    target_id=mother_occurrence.occurrence_id,
                    occurrence_ids=(mother_occurrence.occurrence_id,),
                ),
            ),
        ),
    )


def build_sparse_model() -> BookModel:
    father = Person(handle="sparse-father", name="Alexandre Sobre", gramps_id="I0101")
    mother = Person(handle="sparse-mother", name="Louise Discrète", gramps_id="I0102")
    family = Family(
        handle="sparse-family",
        father=father,
        mother=mother,
        gramps_id="F0101",
    )
    father_occurrence = PersonOccurrence(
        occurrence_id="sparse-occurrence-father",
        person_handle=father.handle,
        generation=0,
        family_handle=family.handle,
    )
    mother_occurrence = PersonOccurrence(
        occurrence_id="sparse-occurrence-mother",
        person_handle=mother.handle,
        generation=0,
        family_handle=family.handle,
    )
    family_section = FamilySection(
        family_handle=family.handle,
        part="descent",
        generation=1,
        section_id="sparse-family-section",
        partner_occurrence_ids=(
            father_occurrence.occurrence_id,
            mother_occurrence.occurrence_id,
        ),
    )
    genealogy = Genealogy(
        ancestry=GenealogyPart(
            name="ancestry",
            generations=(Generation(
                number=0,
                occurrences=(father_occurrence, mother_occurrence),
            ),),
        ),
        descent=GenealogyPart(name="descent"),
        family_sections=(family_section,),
    )
    return BookModel(
        reference_family=family,
        people=[father, mother],
        families={family.handle: family},
        genealogy=genealogy,
        editorial_book=EditorialBook(),
    )


def main() -> None:
    default_output = (
        Path(__file__).resolve().parents[1] / ".work" / "latex-spike"
        / "rendered-book.tex"
    )
    sparse_default = default_output.with_name("rendered-sparse-book.tex")
    output = Path(os.environ.get("LATEX_RENDERED_BOOK_OUTPUT", default_output))
    sparse_output = Path(os.environ.get("LATEX_SPARSE_BOOK_OUTPUT", sparse_default))
    output.parent.mkdir(parents=True, exist_ok=True)
    sparse_output.parent.mkdir(parents=True, exist_ok=True)
    media_asset = output.parent / SYNTHETIC_PORTRAIT_PATH
    media_asset.parent.mkdir(parents=True, exist_ok=True)
    media_asset.write_bytes(SYNTHETIC_PORTRAIT_PNG)
    output.write_text(render_latex(build_model()), encoding="utf-8")
    sparse_output.write_text(render_latex(build_sparse_model()), encoding="utf-8")
    print(output)
    print(sparse_output)


if __name__ == "__main__":
    main()
