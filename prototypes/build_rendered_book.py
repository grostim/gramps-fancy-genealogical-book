"""Generate a multi-page synthetic book through the production LaTeX renderer."""

from __future__ import annotations

import hashlib
import os
import struct
import zlib
from collections.abc import Callable
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


def _encode_synthetic_png(
    width: int,
    height: int,
    shade_at: Callable[[int, int], int],
) -> bytes:
    pixels = bytearray()
    for y in range(height):
        pixels.append(0)
        for x in range(width):
            shade = shade_at(x, y)
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


def _portrait_shade(x: int, y: int) -> int:
    face = (x - 60) ** 2 + (y - 52) ** 2 <= 24 ** 2
    neck = 48 <= x <= 72 and 74 <= y <= 105
    shoulders = ((x - 60) / 56) ** 2 + ((y - 148) / 66) ** 2 <= 1
    return 105 if face else 135 if neck or shoulders else 242


def _featured_photo_shade(x: int, y: int) -> int:
    if x < 12 or y < 12 or x >= 408 or y >= 588:
        return 105
    for center_x, head_y, radius, body_top, shade in (
        (105, 188, 42, 255, 125),
        (210, 162, 48, 238, 95),
        (315, 188, 42, 255, 145),
    ):
        face = (x - center_x) ** 2 + (y - head_y) ** 2 <= radius ** 2
        neck = center_x - 12 <= x <= center_x + 12 and head_y + radius - 4 <= y <= body_top + 20
        shoulders = (
            ((x - center_x) / 92) ** 2 + ((y - 423) / 180) ** 2 <= 1
            and y >= body_top
        )
        if face or neck or shoulders:
            return shade
    return 235


def _document_shade(x: int, y: int) -> int:
    if x < 18 or y < 18 or x >= 462 or y >= 622:
        return 112
    if 66 <= y <= 71 and 56 <= x <= 424:
        return 85
    if 88 <= y <= 91 and 130 <= x <= 350:
        return 120
    for index in range(10):
        line_y = 128 + index * 38
        line_width = 350 - (index % 3) * 42
        if line_y <= y <= line_y + 3 and 56 <= x <= 56 + line_width:
            return 125
    return 246


SYNTHETIC_MEDIA_IMAGES = {
    "portrait": _encode_synthetic_png(120, 160, _portrait_shade),
    "featured": _encode_synthetic_png(420, 600, _featured_photo_shade),
    "document": _encode_synthetic_png(480, 640, _document_shade),
}
SYNTHETIC_MEDIA_KEYS = {
    name: hashlib.sha256(image).hexdigest()
    for name, image in SYNTHETIC_MEDIA_IMAGES.items()
}
SYNTHETIC_MEDIA_PATHS = {
    name: "media/" + key + ".png"
    for name, key in SYNTHETIC_MEDIA_KEYS.items()
}


def build_model(language: str = "en") -> BookModel:
    father = Person(handle="person-father", name="Émile Exemple", gramps_id="I0001")
    mother = Person(handle="person-mother", name="Jeanne Fictive", gramps_id="I0002")
    child = Person(handle="person-child", name="Camille Exemple", gramps_id="I0003")
    family = Family(
        handle="family-central", father=father, mother=mother, children=(child,),
        gramps_id="F0001",
    )
    place = Place(handle="place-example", name="Saint-Exemple, département fictif")

    portrait_reference = MediaReference(media_handle="media-portrait")
    featured_reference = MediaReference(
        media_handle="media-featured",
        rectangle=(0, 0, 100, 100),
    )
    document_reference = MediaReference(
        media_handle="media-document",
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
    strike_phrase = (
        "Passage barré de recette : Émile et Jeanne, au cœur de la généalogie "
        "fictive, confirment qu’une phrase volontairement longue reste lisible "
        "et conserve ses caractères accentués lorsqu’elle se poursuit sur la "
        "ligne suivante dans le document balisé."
        if language == "fr"
        else "Strikethrough test: Émile and Jeanne's fictional family history "
        "keeps accents readable when this intentionally long phrase wraps onto "
        "the next line in the tagged document."
    )
    strike_note = Note(
        handle="note-strikethrough",
        gramps_id="N0002",
        text=f"~~{strike_phrase}~~",
        type=0,
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
        media_refs=(featured_reference, document_reference, unavailable_reference),
        calls=(call,),
    )
    profile = EditorialProfile(
        profile_id=profile_id, person_handle=father.handle,
        primary_occurrence_id="occurrence-father",
        note_handles=(note.handle, strike_note.handle),
        event_refs=tuple(event_refs),
        media_refs=(featured_reference,),
        portrait=portrait,
        citation_call_ids=(call.call_id,),
        note_target_ids=("note-long-target", "note-strike-target"),
        event_target_ids=tuple(event_target_ids),
    )
    notice = EditorialFamilyNotice(
        notice_id="notice-central", family_handle=family.handle,
        primary_section_id="family-section-central",
        event_refs=(EventReference(event_handle="event-union"),),
        media_refs=(featured_reference,),
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
        notes={note.handle: note, strike_note.handle: strike_note},
        citations={citation.handle: citation},
        sources={source.handle: source}, repositories={repository.handle: repository},
        metadata={"BOOK_LANGUAGE": language},
        media={
            "media-portrait": Media(
                handle="media-portrait",
                path="synthetic/portrait.png",
                description="Portrait synthétique d’Émile Exemple — personne fictive",
                mime_type="image/png",
            ),
            "media-featured": Media(
                handle="media-featured",
                path="synthetic/family-photo.png",
                description="Photographie familiale fictive — pleine page",
                mime_type="image/png",
                is_featured=True,
            ),
            "media-document": Media(
                handle="media-document",
                path="synthetic/register.png",
                description="Extrait de registre synthétique",
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
                media_handle="media-portrait",
                rectangle=portrait_reference.rectangle,
                action="reproduce",
                context_ids=("cover:cover", "profile:profile-father"),
                cache_key=SYNTHETIC_MEDIA_KEYS["portrait"],
                asset_path=SYNTHETIC_MEDIA_PATHS["portrait"],
                mime_type="image/png",
                width=120,
                height=160,
                dpi=150,
            ),
            EditorialMediaArtifact(
                media_handle="media-featured",
                rectangle=featured_reference.rectangle,
                action="reproduce",
                context_ids=(
                    "profile:profile-father",
                    "family_notice:notice-central",
                    "citation:citation-entry-1",
                ),
                citation_handles=(citation.handle,),
                cache_key=SYNTHETIC_MEDIA_KEYS["featured"],
                asset_path=SYNTHETIC_MEDIA_PATHS["featured"],
                mime_type="image/png",
                width=420,
                height=600,
                dpi=150,
            ),
            EditorialMediaArtifact(
                media_handle="media-document",
                rectangle=document_reference.rectangle,
                action="reproduce",
                context_ids=("citation:citation-entry-1",),
                citation_handles=(citation.handle,),
                cache_key=SYNTHETIC_MEDIA_KEYS["document"],
                asset_path=SYNTHETIC_MEDIA_PATHS["document"],
                mime_type="image/png",
                width=480,
                height=640,
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
                    placement_id="media:media-portrait",
                    media_handle="media-portrait",
                    caption=portrait.caption,
                    uses=(
                        EditorialMediaUse(
                            context_type="profile",
                            context_id=profile_id,
                            media_ref=portrait_reference,
                        ),
                        EditorialMediaUse(
                            context_type="cover",
                            context_id="cover",
                            media_ref=portrait_reference,
                        ),
                    ),
                ),
                EditorialMediaPlacement(
                    placement_id="media:media-featured",
                    media_handle="media-featured",
                    caption="Photographie familiale fictive — pleine page",
                    is_featured=True,
                    uses=(
                        EditorialMediaUse(
                            context_type="profile",
                            context_id=profile_id,
                            media_ref=featured_reference,
                        ),
                        EditorialMediaUse(
                            context_type="family_notice",
                            context_id=notice.notice_id,
                            media_ref=featured_reference,
                        ),
                        EditorialMediaUse(
                            context_type="citation",
                            context_id=citation_entry.entry_id,
                            media_ref=featured_reference,
                            citation_handles=(citation.handle,),
                        ),
                    ),
                ),
                EditorialMediaPlacement(
                    placement_id="media:media-document",
                    media_handle="media-document",
                    caption="Extrait de registre synthétique",
                    uses=(
                        EditorialMediaUse(
                            context_type="citation",
                            context_id=citation_entry.entry_id,
                            media_ref=document_reference,
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
    french_default = default_output.with_name("rendered-french-book.tex")
    output = Path(os.environ.get("LATEX_RENDERED_BOOK_OUTPUT", default_output))
    sparse_output = Path(os.environ.get("LATEX_SPARSE_BOOK_OUTPUT", sparse_default))
    french_output = Path(os.environ.get("LATEX_FRENCH_BOOK_OUTPUT", french_default))
    for target in (output, sparse_output, french_output):
        target.parent.mkdir(parents=True, exist_ok=True)
    media_directory = output.parent / "media"
    media_directory.mkdir(parents=True, exist_ok=True)
    for name, image in SYNTHETIC_MEDIA_IMAGES.items():
        media_asset = media_directory / (SYNTHETIC_MEDIA_KEYS[name] + ".png")
        media_asset.write_bytes(image)
    output.write_text(render_latex(build_model()), encoding="utf-8")
    french_output.write_text(
        render_latex(build_model(language="fr")), encoding="utf-8"
    )
    sparse_output.write_text(render_latex(build_sparse_model()), encoding="utf-8")
    print(output)
    print(french_output)
    print(sparse_output)


if __name__ == "__main__":
    main()
