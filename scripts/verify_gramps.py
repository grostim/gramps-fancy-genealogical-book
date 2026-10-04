"""Exercise the built add-on with real Gramps and an isolated, synthetic database.

Usage: python scripts/verify_gramps.py --gramps /path/to/gramps [--addon-archive /path/to/addon.tgz]
"""

from __future__ import annotations

import argparse
import copy
import gzip
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import uuid
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ID = "gramps_fancy_genealogical_book"
AC03_OTHER_PARTNER = "AC03_OTHER_UNION_PARTNER"
AC03_OTHER_CHILD = "AC03_OTHER_UNION_CHILD"
AC05_SHARED_ANCESTOR = "AC05_ANC"
AC05_PARENT_PARTNER = "AC05_P1"
AC05_OTHER_PARTNER = "AC05_P2"
AC06_SIBLING = "AC06_UNC"
AC06_PARTNER = "AC06_MAT"
AC06_UNEXPANDED_CHILD = "AC06_COUS"
AC07_UNFORCED_SPOUSE = "AC07_UNFORCED_SPOUSE"
AC07_FORCED_SPOUSE = "AC07_FORCED_SPOUSE"
AC08_FAMILY_EVENT_PARTNER = "AC08_FAMILY_EVENT_PARTNER"
AC08_FAMILY_EVENT_DETAIL = "AC08_FAMILY_EVENT_DETAIL"
AC13_MEDIA_FILENAME = "ac13-excluded-featured.png"
AC13_MEDIA_DESCRIPTION = "AC13_EXCLUDED_FEATURED_MARKER"
AC13_CITATION_PAGE = "AC13_EXCLUDED_CITATION_MARKER"
AC14_SHARED_PAGE = "AC14SHAREDREFERENCE"
AC14_SECOND_PAGE = "AC14SECONDCITATION"
AC18_UNCITED_EVENT = "AC18UNCITEDFACT"
AC18_SOURCE_TITLE = "AC18SOURCEWITHOUTREPOSITORY"
AC18_SOURCE_AUTHOR = "AC18AUTHORDETAIL"
AC18_SOURCE_PUBLICATION = "AC18PUBLICATIONDETAIL"
AC18_CITATION_PAGE = "AC18PAGE"
F0_EDITORIAL_ROLE_TEXT = {
    "BOOK_TITLE": "T02_TITLE_F0_MARKER",
    "BOOK_SUBTITLE": "T02_SUBTITLE_F0_MARKER",
    "BOOK_INTRODUCTION": "T02_INTRODUCTION_F0_MARKER",
    "BOOK_DEDICATION": "T02_DEDICATION_F0_MARKER",
    "BOOK_AUTHOR": "T02_AUTHOR_F0_MARKER",
    "BOOK_PUBLICATION_DATE": "T02_PUBLICATION_DATE_F0_MARKER",
}
F0_EDITORIAL_INVALID_TEXT = {
    "duplicate": "T02_IGNORED_DUPLICATE_TITLE",
    "ambiguous": "T02_IGNORED_AMBIGUOUS_ROLES",
    "unpublished": "T02_IGNORED_UNPUBLISHED_ROLE",
}


def _qualified_name(root: ET.Element, name: str) -> str:
    namespace = root.tag[1:].split("}", 1)[0] if root.tag.startswith("{") else ""
    return f"{{{namespace}}}{name}" if namespace else name


def _children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in element if child.tag.rsplit("}", 1)[-1] == name]


def _text_content(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join(part.strip() for part in element.itertext() if part.strip())


def _html_citation_numbers(html: str) -> dict[str, int]:
    numbers: dict[str, int] = {}
    for entry_id, body in re.findall(
        r'<article class="citation-entry" id="([^"]+)">(.*?)</article>',
        html,
        flags=re.DOTALL,
    ):
        match = re.search(r'class="citation-number">\[(\d+)\]', body)
        if match is not None:
            numbers[entry_id] = int(match.group(1))
    return numbers


def _pdf_text(path: Path) -> str:
    import pypdfium2 as pdfium

    document = pdfium.PdfDocument(str(path))
    pages = []
    for page in document:
        text_page = page.get_textpage()
        pages.append(text_page.get_text_range())
        text_page.close()
        page.close()
    document.close()
    return "\n".join(pages)


def _pdf_section_between_headings(
    text: str, heading: str, next_heading: str | None = None
) -> str:
    heading_matches = list(
        re.finditer(rf"(?m)^{re.escape(heading)}\s*$", text)
    )
    if len(heading_matches) != 1:
        raise AssertionError(
            f"Expected one standalone PDF heading {heading!r}; "
            f"found {len(heading_matches)}."
        )
    start = heading_matches[0].end()
    if next_heading is None:
        return text[start:]
    next_heading_matches = list(
        re.finditer(
            rf"(?m)^{re.escape(next_heading)}\s*$",
            text[start:],
        )
    )
    if len(next_heading_matches) != 1:
        raise AssertionError(
            f"Expected one standalone PDF heading {next_heading!r} "
            f"after {heading!r}; found {len(next_heading_matches)}."
        )
    return text[start : start + next_heading_matches[0].start()]


def _pdf_citation_number(text: str, detail_marker: str) -> int:
    entry = _pdf_citation_entry(text, detail_marker)
    match = re.search(r"(?m)^\s*— \[(\d+)\] ", entry)
    if match is None:
        raise AssertionError(f"No citation heading precedes {detail_marker} in the PDF.")
    return int(match.group(1))


def _pdf_citation_entry(text: str, detail_marker: str) -> str:
    marker_position = text.index(detail_marker)
    headings = list(
        re.finditer(r"(?m)^\s*— \[(\d+)\] ", text)
    )
    preceding = [heading for heading in headings if heading.start() < marker_position]
    if not preceding:
        raise AssertionError(f"No citation heading precedes {detail_marker} in the PDF.")
    current = preceding[-1]
    following = next(
        (heading for heading in headings if heading.start() > marker_position),
        None,
    )
    end = following.start() if following is not None else len(text)
    return text[current.start() : end]


def _insert_event_attribute(root: ET.Element, event: ET.Element, name: str, value: str) -> None:
    for attribute in _children(event, "attribute"):
        if attribute.get("type") == name:
            event.remove(attribute)
    trailing_reference_tags = {"noteref", "citationref", "mediaref", "tagref"}
    index = next(
        (
            position
            for position, child in enumerate(event)
            if child.tag.rsplit("}", 1)[-1] in trailing_reference_tags
        ),
        len(event),
    )
    event.insert(
        index,
        ET.Element(
            _qualified_name(root, "attribute"),
            {"type": name, "value": value},
        ),
    )


def _add_same_fact_birth_version(
    root: ET.Element, events: ET.Element, person: ET.Element
) -> tuple[str, str]:
    event_items = _children(events, "event")

    def event_type(event: ET.Element) -> str:
        return _text_content(next(iter(_children(event, "type")), None))

    birth = next((event for event in event_items if event_type(event) == "Birth"), None)
    marriage = next((event for event in event_items if event_type(event) == "Marriage"), None)
    if birth is None or marriage is None:
        raise AssertionError("Native fixture needs a Birth and Marriage event.")

    date_value = next(
        (
            item
            for item in birth
            if item.tag.rsplit("}", 1)[-1] in {"dateval", "daterange", "datespan", "datestr"}
        ),
        None,
    )
    if date_value is None:
        raise AssertionError("Native fixture Birth event needs a Gramps date element.")
    source_place = next(iter(_children(marriage, "place")), None)
    place_handle = source_place.get("hlink") if source_place is not None else None
    if not place_handle:
        raise AssertionError("Native fixture Marriage event needs a place reference.")

    birth_handle = birth.get("handle")
    birth_ref = next(
        (
            reference
            for reference in _children(person, "eventref")
            if reference.get("hlink") == birth_handle
        ),
        None,
    )
    if not birth_handle or birth_ref is None:
        raise AssertionError("Native fixture person needs a reference to the Birth event.")

    used_ids = {event.get("id") for event in event_items}
    event_number = 1
    while f"E{event_number:04d}" in used_ids:
        event_number += 1
    second_birth = copy.deepcopy(birth)
    second_handle = f"_{uuid.uuid4().hex}"
    second_birth.set("handle", second_handle)
    second_birth.set("id", f"E{event_number:04d}")
    second_date = next(
        item
        for item in second_birth
        if item.tag.rsplit("}", 1)[-1] in {"dateval", "daterange", "datespan", "datestr"}
    )
    second_date_index = list(second_birth).index(second_date)
    second_birth.remove(second_date)
    second_birth.insert(
        second_date_index,
        ET.Element(
            _qualified_name(root, "dateval"),
            {"val": "2000-01-01"},
        ),
    )
    second_place = next(iter(_children(second_birth, "place")), None)
    if second_place is None:
        second_place = ET.Element(_qualified_name(root, "place"))
        second_birth.insert(
            next(
                (
                    position
                    for position, child in enumerate(second_birth)
                    if child.tag.rsplit("}", 1)[-1] in {"description", "attribute", "noteref", "citationref", "mediaref", "tagref"}
                ),
                len(second_birth),
            ),
            second_place,
        )
    second_place.set("hlink", place_handle)

    fact_id = "AC19-birth-of-I0001"
    _insert_event_attribute(root, birth, "BOOK_FACT_ID", fact_id)
    _insert_event_attribute(root, second_birth, "BOOK_FACT_ID", fact_id)
    events.append(second_birth)

    second_ref = copy.deepcopy(birth_ref)
    second_ref.set("hlink", second_handle)
    person.insert(list(person).index(birth_ref) + 1, second_ref)
    return birth_handle, second_handle


def _apply_ac14_shared_citation(root: ET.Element, events: ET.Element) -> None:
    """Make Birth cite twice and Profession reuse its first citation."""
    event_items = _children(events, "event")

    def event_type(event: ET.Element) -> str:
        return _text_content(next(iter(_children(event, "type")), None))

    birth = next((item for item in event_items if event_type(item) == "Birth"), None)
    profession = next(
        (item for item in event_items if event_type(item) == "Profession"),
        None,
    )
    if birth is None or profession is None:
        raise AssertionError("Native AC-14 fixture needs Birth and Profession events.")

    birth_refs = _children(birth, "citationref")
    profession_refs = _children(profession, "citationref")
    if len(birth_refs) != 1 or len(profession_refs) != 1:
        raise AssertionError(
            "Native AC-14 Birth and Profession events must each start with one citation."
        )
    shared_handle = birth_refs[0].get("hlink")
    additional_handle = profession_refs[0].get("hlink")
    if not shared_handle or not additional_handle or shared_handle == additional_handle:
        raise AssertionError("Native AC-14 fixture needs two distinct source citations.")

    profession_refs[0].set("hlink", shared_handle)
    birth.append(
        ET.Element(
            _qualified_name(root, "citationref"),
            {"hlink": additional_handle},
        )
    )
    citations = _section(root, "citations")
    pages_by_handle = {
        shared_handle: AC14_SHARED_PAGE,
        additional_handle: AC14_SECOND_PAGE,
    }
    for citation in _children(citations, "citation"):
        handle = citation.get("handle")
        if handle not in pages_by_handle:
            continue
        page = next(iter(_children(citation, "page")), None)
        if page is None:
            raise AssertionError(f"Native AC-14 citation {handle} has no page field.")
        page.text = pages_by_handle[handle]


def _apply_ac18_missing_references(root: ET.Element, events: ET.Element) -> None:
    """Keep an uncited marriage and add a detailed citation with no repository."""
    event_items = _children(events, "event")

    def event_type(event: ET.Element) -> str:
        return _text_content(next(iter(_children(event, "type")), None))

    marriage = next((item for item in event_items if event_type(item) == "Marriage"), None)
    profession = next(
        (item for item in event_items if event_type(item) == "Profession"),
        None,
    )
    if marriage is None or profession is None:
        raise AssertionError("Native AC-18 fixture needs Marriage and Profession events.")

    marriage_citations = _children(marriage, "citationref")
    if not marriage_citations:
        raise AssertionError("Native AC-18 fixture needs an initially cited Marriage event.")
    for reference in marriage_citations:
        marriage.remove(reference)

    description = next(iter(_children(marriage, "description")), None)
    if description is None:
        event_type_element = next(iter(_children(marriage, "type")), None)
        description = ET.Element(_qualified_name(root, "description"))
        insert_at = (
            list(marriage).index(event_type_element) + 1
            if event_type_element is not None
            else 0
        )
        marriage.insert(insert_at, description)
    description.text = AC18_UNCITED_EVENT

    sources = _section(root, "sources")
    source_items = _children(sources, "source")
    original_source = next(
        (item for item in source_items if item.get("id") == "S0001"),
        None,
    )
    if original_source is None:
        raise AssertionError("Native AC-18 fixture needs source S0001 to copy its details.")

    source = copy.deepcopy(original_source)
    source_handle = f"_{uuid.uuid4().hex}"
    source_ids = {item.get("id") for item in source_items}
    source_number = 1
    while f"S{source_number:04d}" in source_ids:
        source_number += 1
    source.set("handle", source_handle)
    source.set("id", f"S{source_number:04d}")
    for child in list(source):
        if child.tag.rsplit("}", 1)[-1] in {"reporef", "url"}:
            source.remove(child)
    source_fields = {
        "stitle": AC18_SOURCE_TITLE,
        "sauthor": AC18_SOURCE_AUTHOR,
        "spubinfo": AC18_SOURCE_PUBLICATION,
        "sabbrev": "",
    }
    for name, value in source_fields.items():
        element = next((item for item in _children(source, name)), None)
        if element is None:
            element = ET.SubElement(source, _qualified_name(root, name))
        element.text = value
    sources.append(source)

    citations = _section(root, "citations")
    citation_items = _children(citations, "citation")
    citation_ids = {item.get("id") for item in citation_items}
    citation_number = 0
    while f"C{citation_number:04d}" in citation_ids:
        citation_number += 1
    citation_handle = f"_{uuid.uuid4().hex}"
    citation = ET.SubElement(
        citations,
        _qualified_name(root, "citation"),
        {"handle": citation_handle, "change": "0", "id": f"C{citation_number:04d}"},
    )
    ET.SubElement(
        citation,
        _qualified_name(root, "sourceref"),
        {"hlink": source_handle},
    )
    ET.SubElement(citation, _qualified_name(root, "page")).text = AC18_CITATION_PAGE
    ET.SubElement(
        profession,
        _qualified_name(root, "citationref"),
        {"hlink": citation_handle},
    )


def _section(root: ET.Element, name: str) -> ET.Element:
    existing = next(iter(_children(root, name)), None)
    if existing is not None:
        return existing
    section = ET.Element(_qualified_name(root, name))
    if name == "notes":
        index = next(
            (
                position
                for position, child in enumerate(root)
                if child.tag.rsplit("}", 1)[-1] in {"bookmarks", "namemaps"}
            ),
            len(root),
        )
    else:
        data_sections = {
            "events",
            "people",
            "families",
            "citations",
            "sources",
            "places",
            "objects",
            "repositories",
            "notes",
            "bookmarks",
            "namemaps",
        }
        index = next(
            (
                position
                for position, child in enumerate(root)
                if child.tag.rsplit("}", 1)[-1] in data_sections
            ),
            len(root),
        )
    root.insert(index, section)
    return section


def _create_media_fixture(work: Path) -> None:
    """Write the synthetic portrait referenced by the GEDCOM fixture."""
    from PIL import Image

    media_path = work / "media" / "portrait.jpg"
    media_path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (10, 10), color=(90, 130, 170)).save(media_path, format="JPEG")
    Image.new("RGB", (16, 12), color=(210, 40, 90)).save(
        media_path.parent / AC13_MEDIA_FILENAME, format="PNG"
    )
    for filename, page_count in (
        ("ac16-single-unlinked.pdf", 1),
        ("ac16-multipage-unlinked.pdf", 2),
        ("ac16-single-linked.pdf", 1),
        ("ac16-multipage-linked.pdf", 2),
    ):
        (media_path.parent / filename).write_bytes(_blank_pdf(page_count))


def _blank_pdf(page_count: int) -> bytes:
    """Create a minimal, deterministic PDF without adding a test dependency."""
    page_objects = list(range(3, 3 + page_count))
    kids = " ".join(f"{number} 0 R" for number in page_objects)
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {page_count} >>".encode(),
    ]
    objects.extend(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 72 72] /Resources << >> >>"
        for _ in page_objects
    )

    document = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, content in enumerate(objects, start=1):
        offsets.append(len(document))
        document.extend(f"{number} 0 obj\n".encode())
        document.extend(content)
        document.extend(b"\nendobj\n")

    xref_offset = len(document)
    document.extend(f"xref\n0 {len(offsets)}\n".encode())
    document.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        document.extend(f"{offset:010d} 00000 n \n".encode())
    document.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode()
    )
    return bytes(document)


def _add_ac13_excluded_featured_media(
    root: ET.Element,
    person: ET.Element,
    objects: ET.Element,
    citations: ET.Element,
    tags: ET.Element,
    work: Path,
) -> None:
    """Attach a synthetic, cited media object carrying both AC-13 tags."""
    tag_handles: dict[str, str] = {}
    for name in ("BOOK_EXCLUDE", "BOOK_FEATURED"):
        tag = next(
            (item for item in _children(tags, "tag") if item.get("name") == name),
            None,
        )
        if tag is None:
            handle = f"_{uuid.uuid4().hex}"
            tag = ET.SubElement(
                tags,
                _qualified_name(root, "tag"),
                {
                    "handle": handle,
                    "change": "0",
                    "name": name,
                    "color": "#000000000000",
                    "priority": "0",
                },
            )
        else:
            handle = tag.get("handle", "")
        if not handle:
            raise AssertionError(f"Native Gramps tag {name} has no handle.")
        tag_handles[name] = handle

    citation_ids = {
        item.get("id") for item in _children(citations, "citation")
    }
    citation_number = 1
    while f"C{citation_number:04d}" in citation_ids:
        citation_number += 1
    source_reference = next(
        (
            child
            for item in _children(citations, "citation")
            for child in _children(item, "sourceref")
        ),
        None,
    )
    source_handle = source_reference.get("hlink") if source_reference is not None else None
    if not source_handle:
        raise AssertionError("Native Gramps fixture has no source for its AC-13 citation.")
    citation_handle = f"_{uuid.uuid4().hex}"
    citation = ET.SubElement(
        citations,
        _qualified_name(root, "citation"),
        {
            "handle": citation_handle,
            "change": "0",
            "id": f"C{citation_number:04d}",
        },
    )
    ET.SubElement(
        citation,
        _qualified_name(root, "sourceref"),
        {"hlink": source_handle},
    )
    ET.SubElement(citation, _qualified_name(root, "page")).text = AC13_CITATION_PAGE

    media_ids = {item.get("id") for item in _children(objects, "object")}
    media_number = 1
    while f"M{media_number:04d}" in media_ids:
        media_number += 1
    media_handle = f"_{uuid.uuid4().hex}"
    media = ET.SubElement(
        objects,
        _qualified_name(root, "object"),
        {
            "handle": media_handle,
            "change": "0",
            "id": f"M{media_number:04d}",
        },
    )
    ET.SubElement(
        media,
        _qualified_name(root, "file"),
        {
            "src": str((work / "media" / AC13_MEDIA_FILENAME).resolve()),
            "mime": "image/png",
            "description": AC13_MEDIA_DESCRIPTION,
        },
    )
    for name in ("BOOK_EXCLUDE", "BOOK_FEATURED"):
        ET.SubElement(
            media,
            _qualified_name(root, "tagref"),
            {"hlink": tag_handles[name]},
        )
    media_reference = ET.SubElement(
        person,
        _qualified_name(root, "objref"),
        {"hlink": media_handle},
    )
    ET.SubElement(
        media_reference,
        _qualified_name(root, "citationref"),
        {"hlink": citation_handle},
    )


def _add_f0_editorial_notes(
    root: ET.Element,
    family: ET.Element,
    notes: ET.Element,
    tags: ET.Element,
    publication_tag_handle: str,
) -> None:
    """Add native notes that cover every F0 role and malformed-note diagnostics."""
    role_tags: dict[str, str] = {}
    for role in F0_EDITORIAL_ROLE_TEXT:
        handle = f"_{uuid.uuid4().hex}"
        ET.SubElement(
            tags,
            _qualified_name(root, "tag"),
            {
                "handle": handle,
                "change": "0",
                "name": role,
                "color": "#000000000000",
                "priority": "0",
            },
        )
        role_tags[role] = handle

    existing_ids = {item.get("id") for item in _children(notes, "note")}

    def add_note(
        text: str,
        roles: tuple[str, ...],
        *,
        publishable: bool = True,
    ) -> str:
        number = 1
        while f"N{number:04d}" in existing_ids:
            number += 1
        note_id = f"N{number:04d}"
        existing_ids.add(note_id)
        handle = f"_{uuid.uuid4().hex}"
        note = ET.SubElement(
            notes,
            _qualified_name(root, "note"),
            {
                "handle": handle,
                "change": "0",
                "id": note_id,
                "type": "General",
            },
        )
        ET.SubElement(note, _qualified_name(root, "text")).text = text
        if publishable:
            ET.SubElement(
                note,
                _qualified_name(root, "tagref"),
                {"hlink": publication_tag_handle},
            )
        for role in roles:
            ET.SubElement(
                note,
                _qualified_name(root, "tagref"),
                {"hlink": role_tags[role]},
            )
        ET.SubElement(family, _qualified_name(root, "noteref"), {"hlink": handle})
        return handle

    for role, text in F0_EDITORIAL_ROLE_TEXT.items():
        add_note(text, (role,))

    add_note(
        F0_EDITORIAL_INVALID_TEXT["duplicate"],
        ("BOOK_TITLE",),
    )
    add_note(
        F0_EDITORIAL_INVALID_TEXT["ambiguous"],
        ("BOOK_DEDICATION", "BOOK_INTRODUCTION"),
    )
    add_note(
        F0_EDITORIAL_INVALID_TEXT["unpublished"],
        ("BOOK_AUTHOR",),
        publishable=False,
    )
    add_note("   ", ("BOOK_SUBTITLE",))


def _set_t04_parentage_case(
    family: ET.Element,
    child: ET.Element,
) -> None:
    """Exercise a typed parent link and an explicit None link in native Gramps XML."""
    child_handle = child.get("handle")
    if not child_handle:
        raise AssertionError("Native T-04 fixture child has no Gramps handle.")
    child_ref = next(
        (
            item
            for item in _children(family, "childref")
            if item.get("hlink") == child_handle
        ),
        None,
    )
    if child_ref is None:
        raise AssertionError("Native T-04 fixture family has no reference to its child.")

    # F0001 is imported from the small GEDCOM fixture: frel is I0001's link,
    # and mrel is I0002's. Reimport through Gramps below to exercise its API.
    child_ref.set("frel", "Adopted")
    child_ref.set("mrel", "None")


def _add_person_family_ref(
    root: ET.Element,
    person: ET.Element,
    ref_type: str,
    family_handle: str,
) -> None:
    """Insert a reciprocal person-to-family reference in Gramps XML order."""
    if ref_type not in {"childof", "parentin"}:
        raise ValueError(f"Unsupported person-family reference {ref_type!r}.")
    if any(
        item.get("hlink") == family_handle
        for item in _children(person, ref_type)
    ):
        raise AssertionError(
            f"Native fixture already has a {ref_type} reference to {family_handle}."
        )

    order = (
        "gender",
        "name",
        "eventref",
        "lds_ord",
        "objref",
        "address",
        "attribute",
        "url",
        "childof",
        "parentin",
        "personref",
        "noteref",
        "citationref",
        "tagref",
    )
    target_rank = order.index(ref_type)
    insert_at = next(
        (
            index
            for index, item in enumerate(person)
            if item.tag.rsplit("}", 1)[-1] in order
            and order.index(item.tag.rsplit("}", 1)[-1]) > target_rank
        ),
        len(person),
    )
    person.insert(
        insert_at,
        ET.Element(
            _qualified_name(root, ref_type),
            {"hlink": family_handle},
        ),
    )


def _add_t04_foster_parent_family(
    root: ET.Element,
    family: ET.Element,
    child: ET.Element,
    father: ET.Element,
) -> None:
    """Connect I0001 to a single-parent family with an explicit Foster link."""
    family_handle = family.get("handle")
    child_handle = child.get("handle")
    father_handle = father.get("handle")
    if not family_handle or not child_handle or not father_handle:
        raise AssertionError("Native T-04 foster-family fixture has a missing handle.")
    family_father = next(iter(_children(family, "father")), None)
    if family_father is None or family_father.get("hlink") != father_handle:
        raise AssertionError("Native T-04 foster family must contain only its known father.")
    if _children(family, "mother"):
        raise AssertionError("Native T-04 foster family unexpectedly has a mother.")
    if any(
        item.get("hlink") == child_handle
        for item in _children(family, "childref")
    ):
        raise AssertionError("Native T-04 foster family already references its child.")

    child_ref = ET.Element(
        _qualified_name(root, "childref"),
        {"hlink": child_handle, "frel": "Foster"},
    )
    family_trailing_refs = {"attribute", "noteref", "citationref", "tagref"}
    family_index = next(
        (
            index
            for index, item in enumerate(family)
            if item.tag.rsplit("}", 1)[-1] in family_trailing_refs
        ),
        len(family),
    )
    family.insert(family_index, child_ref)

    _add_person_family_ref(root, child, "childof", family_handle)


def _add_ac03_other_union(
    root: ET.Element,
    people: ET.Element,
    families: ET.Element,
    reference_parent: ET.Element,
) -> None:
    """Add a native second union and a profile-eligible child of the F0 parent."""
    existing_person_ids = {item.get("id") for item in _children(people, "person")}
    existing_family_ids = {
        item.get("id") for item in _children(families, "family")
    }
    if {"I0005", "I0006"}.intersection(existing_person_ids):
        raise AssertionError("Native AC-03 fixture person IDs I0005/I0006 already exist.")
    if "F0003" in existing_family_ids:
        raise AssertionError("Native AC-03 fixture family F0003 already exists.")
    parent_handle = reference_parent.get("handle")
    if not parent_handle:
        raise AssertionError("Native AC-03 reference parent has no Gramps handle.")

    family_handle = f"_{uuid.uuid4().hex}"
    partner_handle = f"_{uuid.uuid4().hex}"
    child_handle = f"_{uuid.uuid4().hex}"
    partner = ET.Element(
        _qualified_name(root, "person"),
        {"handle": partner_handle, "change": "0", "id": "I0005"},
    )
    ET.SubElement(partner, _qualified_name(root, "gender")).text = "F"
    partner_name = ET.SubElement(
        partner,
        _qualified_name(root, "name"),
        {"type": "Birth Name"},
    )
    ET.SubElement(
        partner_name,
        _qualified_name(root, "first"),
    ).text = AC03_OTHER_PARTNER
    ET.SubElement(partner_name, _qualified_name(root, "surname")).text = "Synthetic"
    _add_person_family_ref(root, partner, "parentin", family_handle)

    child = ET.Element(
        _qualified_name(root, "person"),
        {"handle": child_handle, "change": "0", "id": "I0006"},
    )
    ET.SubElement(child, _qualified_name(root, "gender")).text = "U"
    child_name = ET.SubElement(
        child,
        _qualified_name(root, "name"),
        {"type": "Birth Name"},
    )
    ET.SubElement(child_name, _qualified_name(root, "first")).text = AC03_OTHER_CHILD
    ET.SubElement(child_name, _qualified_name(root, "surname")).text = "Synthetic"
    ET.SubElement(
        child,
        _qualified_name(root, "attribute"),
        {"type": "BOOK_PROFILE", "value": "YES"},
    )
    _add_person_family_ref(root, child, "childof", family_handle)

    family = ET.Element(
        _qualified_name(root, "family"),
        {"handle": family_handle, "change": "0", "id": "F0003"},
    )
    ET.SubElement(
        family,
        _qualified_name(root, "father"),
        {"hlink": parent_handle},
    )
    ET.SubElement(
        family,
        _qualified_name(root, "mother"),
        {"hlink": partner_handle},
    )
    ET.SubElement(
        family,
        _qualified_name(root, "childref"),
        {"hlink": child_handle, "frel": "Birth", "mrel": "Birth"},
    )
    _add_person_family_ref(root, reference_parent, "parentin", family_handle)
    people.extend((partner, child))
    families.append(family)


def _add_ac05_implex_and_cycle(
    root: ET.Element,
    people: ET.Element,
    families: ET.Element,
    reference_parent: ET.Element,
    reference_partner: ET.Element,
) -> None:
    """Add a shared ancestor on both central branches and a bounded ancestry cycle."""
    existing_person_ids = {item.get("id") for item in _children(people, "person")}
    existing_family_ids = {
        item.get("id") for item in _children(families, "family")
    }
    person_ids = {"I0007", "I0008", "I0009"}
    family_ids = {"F0004", "F0005", "F0006"}
    if person_ids.intersection(existing_person_ids):
        raise AssertionError("Native AC-05 fixture person IDs I0007/I0008/I0009 already exist.")
    if family_ids.intersection(existing_family_ids):
        raise AssertionError("Native AC-05 fixture family IDs F0004/F0005/F0006 already exist.")

    handles = {gramps_id: f"_{uuid.uuid4().hex}" for gramps_id in person_ids}
    names = {
        "I0007": (AC05_SHARED_ANCESTOR, "U", True),
        "I0008": (AC05_PARENT_PARTNER, "U", False),
        "I0009": (AC05_OTHER_PARTNER, "U", False),
    }
    added_people = {}
    for gramps_id in ("I0007", "I0008", "I0009"):
        first_name, gender, profile_eligible = names[gramps_id]
        person = ET.Element(
            _qualified_name(root, "person"),
            {"handle": handles[gramps_id], "change": "0", "id": gramps_id},
        )
        ET.SubElement(person, _qualified_name(root, "gender")).text = gender
        name = ET.SubElement(
            person,
            _qualified_name(root, "name"),
            {"type": "Birth Name"},
        )
        ET.SubElement(name, _qualified_name(root, "first")).text = first_name
        ET.SubElement(name, _qualified_name(root, "surname")).text = "Synthetic"
        if profile_eligible:
            ET.SubElement(
                person,
                _qualified_name(root, "attribute"),
                {"type": "BOOK_PROFILE", "value": "YES"},
            )
        added_people[gramps_id] = person

    reference_parent_handle = reference_parent.get("handle")
    reference_partner_handle = reference_partner.get("handle")
    shared_ancestor_handle = handles["I0007"]
    parent_partner_handle = handles["I0008"]
    other_partner_handle = handles["I0009"]
    if not reference_parent_handle or not reference_partner_handle:
        raise AssertionError("Native AC-05 central couple is missing a Gramps handle.")
    people_by_handle = {
        person.get("handle"): person
        for person in (*_children(people, "person"), *added_people.values())
        if person.get("handle")
    }
    if (
        people_by_handle.get(reference_parent_handle) is not reference_parent
        or people_by_handle.get(reference_partner_handle) is not reference_partner
    ):
        raise AssertionError("Native AC-05 central couple is absent from the fixture.")

    family_specs = (
        ("F0004", shared_ancestor_handle, parent_partner_handle, reference_parent_handle),
        ("F0005", shared_ancestor_handle, other_partner_handle, reference_partner_handle),
        ("F0006", reference_parent_handle, parent_partner_handle, shared_ancestor_handle),
    )
    added_families = []
    for gramps_id, father_handle, mother_handle, child_handle in family_specs:
        family_handle = f"_{uuid.uuid4().hex}"
        family = ET.Element(
            _qualified_name(root, "family"),
            {"handle": family_handle, "change": "0", "id": gramps_id},
        )
        ET.SubElement(
            family,
            _qualified_name(root, "father"),
            {"hlink": father_handle},
        )
        ET.SubElement(
            family,
            _qualified_name(root, "mother"),
            {"hlink": mother_handle},
        )
        ET.SubElement(
            family,
            _qualified_name(root, "childref"),
            {"hlink": child_handle, "frel": "Birth", "mrel": "Birth"},
        )
        _add_person_family_ref(
            root, people_by_handle[father_handle], "parentin", family_handle
        )
        _add_person_family_ref(
            root, people_by_handle[mother_handle], "parentin", family_handle
        )
        _add_person_family_ref(
            root, people_by_handle[child_handle], "childof", family_handle
        )
        added_families.append(family)

    people.extend(added_people.values())
    families.extend(added_families)


def _add_ac06_sibling_without_descendants(
    root: ET.Element,
    people: ET.Element,
    families: ET.Element,
) -> None:
    """Add an eligible sibling to an ancestor family with an unexpanded child."""
    existing_person_ids = {item.get("id") for item in _children(people, "person")}
    existing_family_ids = {
        item.get("id") for item in _children(families, "family")
    }
    person_ids = {"I0010", "I0011", "I0012", "I0013", "I0014"}
    if person_ids.intersection(existing_person_ids):
        raise AssertionError("Native AC-06 fixture person IDs I0010-I0014 already exist.")
    if {"F0007", "F0008"}.intersection(existing_family_ids):
        raise AssertionError("Native AC-06 fixture family IDs F0007/F0008 already exist.")

    ancestor = next(
        (
            item
            for item in _children(people, "person")
            if item.get("id") == "I0009"
        ),
        None,
    )
    if ancestor is None or not ancestor.get("handle"):
        raise AssertionError("Native AC-06 fixture is missing ancestor I0009.")

    uncle_handle, parent_a_handle, parent_b_handle, partner_handle, cousin_handle = (
        f"_{uuid.uuid4().hex}" for _ in range(5)
    )
    added_people = {}
    for gramps_id, handle, first_name, gender in (
        ("I0010", uncle_handle, AC06_SIBLING, "M"),
        ("I0011", parent_a_handle, "AC06_GPA", "M"),
        ("I0012", parent_b_handle, "AC06_GMA", "F"),
        ("I0013", partner_handle, AC06_PARTNER, "F"),
        ("I0014", cousin_handle, AC06_UNEXPANDED_CHILD, "U"),
    ):
        person = ET.Element(
            _qualified_name(root, "person"),
            {"handle": handle, "change": "0", "id": gramps_id},
        )
        ET.SubElement(person, _qualified_name(root, "gender")).text = gender
        name = ET.SubElement(
            person,
            _qualified_name(root, "name"),
            {"type": "Birth Name"},
        )
        ET.SubElement(name, _qualified_name(root, "first")).text = first_name
        ET.SubElement(name, _qualified_name(root, "surname")).text = "Synthetic"
        if gramps_id == "I0010":
            ET.SubElement(
                person,
                _qualified_name(root, "attribute"),
                {"type": "BOOK_PROFILE", "value": "YES"},
            )
        added_people[gramps_id] = person

    ancestor_family_handle = f"_{uuid.uuid4().hex}"
    ancestor_family = ET.Element(
        _qualified_name(root, "family"),
        {"handle": ancestor_family_handle, "change": "0", "id": "F0007"},
    )
    ET.SubElement(
        ancestor_family,
        _qualified_name(root, "father"),
        {"hlink": parent_a_handle},
    )
    ET.SubElement(
        ancestor_family,
        _qualified_name(root, "mother"),
        {"hlink": parent_b_handle},
    )
    for child_handle in (ancestor.get("handle"), uncle_handle):
        ET.SubElement(
            ancestor_family,
            _qualified_name(root, "childref"),
            {"hlink": child_handle, "frel": "Birth", "mrel": "Birth"},
        )
    _add_person_family_ref(
        root,
        added_people["I0010"],
        "childof",
        ancestor_family_handle,
    )
    _add_person_family_ref(root, ancestor, "childof", ancestor_family_handle)
    _add_person_family_ref(root, added_people["I0011"], "parentin", ancestor_family_handle)
    _add_person_family_ref(root, added_people["I0012"], "parentin", ancestor_family_handle)

    child_family_handle = f"_{uuid.uuid4().hex}"
    child_family = ET.Element(
        _qualified_name(root, "family"),
        {"handle": child_family_handle, "change": "0", "id": "F0008"},
    )
    ET.SubElement(
        child_family,
        _qualified_name(root, "father"),
        {"hlink": uncle_handle},
    )
    ET.SubElement(
        child_family,
        _qualified_name(root, "mother"),
        {"hlink": partner_handle},
    )
    ET.SubElement(
        child_family,
        _qualified_name(root, "childref"),
        {"hlink": cousin_handle, "frel": "Birth", "mrel": "Birth"},
    )
    _add_person_family_ref(root, added_people["I0010"], "parentin", child_family_handle)
    _add_person_family_ref(root, added_people["I0013"], "parentin", child_family_handle)
    _add_person_family_ref(root, added_people["I0014"], "childof", child_family_handle)

    people.extend(added_people.values())
    families.append(ancestor_family)
    families.append(child_family)


def _add_ac07_spouse_eligibility(
    root: ET.Element,
    people: ET.Element,
    families: ET.Element,
    events: ET.Element,
    reference_parent: ET.Element,
) -> None:
    """Add two spouse-only unions that differ only by BOOK_PROFILE=YES."""
    person_ids = {"I0015", "I0016"}
    family_ids = {"F0009", "F0010"}
    existing_person_ids = {item.get("id") for item in _children(people, "person")}
    existing_family_ids = {item.get("id") for item in _children(families, "family")}
    if person_ids.intersection(existing_person_ids):
        raise AssertionError("Native AC-07 fixture person IDs I0015/I0016 already exist.")
    if family_ids.intersection(existing_family_ids):
        raise AssertionError("Native AC-07 fixture family IDs F0009/F0010 already exist.")

    def event_type(event: ET.Element) -> str:
        return _text_content(next(iter(_children(event, "type")), None))

    templates = {
        event_type(event): event
        for event in _children(events, "event")
        if event_type(event) in {"Birth", "Death"}
    }
    if "Birth" not in templates:
        raise AssertionError("Native AC-07 fixture requires a Birth event template.")
    if "Death" not in templates:
        death_template = copy.deepcopy(templates["Birth"])
        death_type = next(iter(_children(death_template, "type")), None)
        if death_type is None:
            raise AssertionError("Native AC-07 Birth event template has no type.")
        death_type.text = "Death"
        templates["Death"] = death_template

    used_event_ids = {
        item.get("id")
        for item in _children(events, "event")
        if item.get("id")
    }
    next_event_number = max(
        (
            int(event_id[1:])
            for event_id in used_event_ids
            if event_id.startswith("E") and event_id[1:].isdigit()
        ),
        default=0,
    ) + 1

    def clone_life_event(kind: str) -> str:
        nonlocal next_event_number
        cloned = copy.deepcopy(templates[kind])
        handle = f"_{uuid.uuid4().hex}"
        event_id = f"E{next_event_number:04d}"
        while event_id in used_event_ids:
            next_event_number += 1
            event_id = f"E{next_event_number:04d}"
        next_event_number += 1
        used_event_ids.add(event_id)
        cloned.set("handle", handle)
        cloned.set("id", event_id)
        cloned.set("change", "0")
        date = next(
            (
                item
                for item in cloned
                if item.tag.rsplit("}", 1)[-1]
                in {"dateval", "daterange", "datespan", "datestr"}
            ),
            None,
        )
        event_type_node = next(iter(_children(cloned, "type")), None)
        if date is None or event_type_node is None:
            raise AssertionError(f"Native {kind} event template is incomplete.")
        if kind == "Death":
            date_index = list(cloned).index(date)
            cloned.remove(date)
            date = ET.Element(
                _qualified_name(root, "dateval"),
                {"val": "1970-01-01"},
            )
            cloned.insert(date_index, date)
        for child in list(cloned):
            if child is not date and child is not event_type_node:
                cloned.remove(child)
        events.append(cloned)
        return handle

    parent_handle = reference_parent.get("handle")
    if not parent_handle:
        raise AssertionError("Native AC-07 reference parent has no Gramps handle.")
    added_people = []
    added_families = []
    for gramps_id, first_name, family_id, force_profile in (
        ("I0015", AC07_UNFORCED_SPOUSE, "F0009", False),
        ("I0016", AC07_FORCED_SPOUSE, "F0010", True),
    ):
        partner_handle = f"_{uuid.uuid4().hex}"
        family_handle = f"_{uuid.uuid4().hex}"
        partner = ET.Element(
            _qualified_name(root, "person"),
            {"handle": partner_handle, "change": "0", "id": gramps_id},
        )
        ET.SubElement(partner, _qualified_name(root, "gender")).text = "U"
        name = ET.SubElement(
            partner,
            _qualified_name(root, "name"),
            {"type": "Birth Name"},
        )
        ET.SubElement(name, _qualified_name(root, "first")).text = first_name
        ET.SubElement(name, _qualified_name(root, "surname")).text = "Synthetic"
        for kind in ("Birth", "Death"):
            event_handle = clone_life_event(kind)
            ET.SubElement(
                partner,
                _qualified_name(root, "eventref"),
                {"hlink": event_handle, "role": "Primary"},
            )
        if force_profile:
            ET.SubElement(
                partner,
                _qualified_name(root, "attribute"),
                {"type": "BOOK_PROFILE", "value": "YES"},
            )
        _add_person_family_ref(root, partner, "parentin", family_handle)
        _add_person_family_ref(root, reference_parent, "parentin", family_handle)

        family = ET.Element(
            _qualified_name(root, "family"),
            {"handle": family_handle, "change": "0", "id": family_id},
        )
        ET.SubElement(
            family,
            _qualified_name(root, "father"),
            {"hlink": parent_handle},
        )
        ET.SubElement(
            family,
            _qualified_name(root, "mother"),
            {"hlink": partner_handle},
        )
        added_people.append(partner)
        added_families.append(family)

    people.extend(added_people)
    families.extend(added_families)


def _add_ac08_family_event_eligibility(
    root: ET.Element,
    people: ET.Element,
    families: ET.Element,
    events: ET.Element,
    reference_parent: ET.Element,
) -> None:
    """Add a spouse qualified only by a marriage recorded on the family."""
    if any(item.get("id") == "I0017" for item in _children(people, "person")):
        raise AssertionError("Native AC-08 fixture person ID I0017 already exists.")
    if any(item.get("id") == "F0011" for item in _children(families, "family")):
        raise AssertionError("Native AC-08 fixture family ID F0011 already exists.")

    def event_type(event: ET.Element) -> str:
        return _text_content(next(iter(_children(event, "type")), None))

    templates = {
        event_type(event): event
        for event in _children(events, "event")
        if event_type(event) in {"Birth", "Death", "Marriage"}
    }
    if "Birth" not in templates or "Marriage" not in templates:
        raise AssertionError("Native AC-08 fixture requires Birth and Marriage templates.")
    if "Death" not in templates:
        death_template = copy.deepcopy(templates["Birth"])
        death_type = next(iter(_children(death_template, "type")), None)
        if death_type is None:
            raise AssertionError("Native AC-08 Birth event template has no type.")
        death_type.text = "Death"
        templates["Death"] = death_template

    used_event_ids = {
        item.get("id")
        for item in _children(events, "event")
        if item.get("id")
    }
    next_event_number = max(
        (
            int(event_id[1:])
            for event_id in used_event_ids
            if event_id.startswith("E") and event_id[1:].isdigit()
        ),
        default=0,
    ) + 1

    def allocate_event(kind: str) -> ET.Element:
        nonlocal next_event_number
        cloned = copy.deepcopy(templates[kind])
        handle = f"_{uuid.uuid4().hex}"
        event_id = f"E{next_event_number:04d}"
        while event_id in used_event_ids:
            next_event_number += 1
            event_id = f"E{next_event_number:04d}"
        next_event_number += 1
        used_event_ids.add(event_id)
        cloned.set("handle", handle)
        cloned.set("id", event_id)
        cloned.set("change", "0")
        type_node = next(iter(_children(cloned, "type")), None)
        if type_node is None:
            raise AssertionError(f"Native AC-08 {kind} event template has no type.")
        for child in list(cloned):
            if child is not type_node:
                cloned.remove(child)
        if kind == "Marriage":
            ET.SubElement(cloned, _qualified_name(root, "description")).text = (
                AC08_FAMILY_EVENT_DETAIL
            )
        else:
            date = next(
                (
                    child
                    for child in templates[kind]
                    if child.tag.rsplit("}", 1)[-1]
                    in {"dateval", "daterange", "datespan", "datestr"}
                ),
                None,
            )
            if date is not None:
                cloned.insert(list(cloned).index(type_node) + 1, copy.deepcopy(date))
        events.append(cloned)
        return cloned

    parent_handle = reference_parent.get("handle")
    if not parent_handle:
        raise AssertionError("Native AC-08 reference parent has no Gramps handle.")

    partner_handle = f"_{uuid.uuid4().hex}"
    family_handle = f"_{uuid.uuid4().hex}"
    partner = ET.Element(
        _qualified_name(root, "person"),
        {"handle": partner_handle, "change": "0", "id": "I0017"},
    )
    ET.SubElement(partner, _qualified_name(root, "gender")).text = "U"
    name = ET.SubElement(
        partner,
        _qualified_name(root, "name"),
        {"type": "Birth Name"},
    )
    ET.SubElement(name, _qualified_name(root, "first")).text = AC08_FAMILY_EVENT_PARTNER
    ET.SubElement(name, _qualified_name(root, "surname")).text = "Synthetic"
    for kind in ("Birth", "Death"):
        life_event = allocate_event(kind)
        ET.SubElement(
            partner,
            _qualified_name(root, "eventref"),
            {"hlink": life_event.get("handle", ""), "role": "Primary"},
        )
    _add_person_family_ref(root, partner, "parentin", family_handle)
    _add_person_family_ref(root, reference_parent, "parentin", family_handle)

    family = ET.Element(
        _qualified_name(root, "family"),
        {"handle": family_handle, "change": "0", "id": "F0011"},
    )
    ET.SubElement(family, _qualified_name(root, "father"), {"hlink": parent_handle})
    ET.SubElement(family, _qualified_name(root, "mother"), {"hlink": partner_handle})
    marriage = allocate_event("Marriage")
    ET.SubElement(
        family,
        _qualified_name(root, "eventref"),
        {"hlink": marriage.get("handle", ""), "role": "Family"},
    )
    people.append(partner)
    families.append(family)


def _install_mistune_dependency(plugins: Path) -> None:
    """Install the runner's Mistune copy into this isolated Gramps profile."""
    spec = importlib.util.find_spec("mistune")
    if spec is None or not spec.submodule_search_locations:
        raise AssertionError("Install the project dependencies before Gramps integration.")
    source = Path(next(iter(spec.submodule_search_locations)))
    target = plugins / "lib" / "mistune"
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )


def _install_optional_media_dependencies(plugins: Path) -> None:
    """Expose the runner's Pillow/PDFium packages to the isolated Gramps profile."""
    for package in ("PIL", "pypdfium2", "pypdfium2_cfg", "pypdfium2_raw"):
        spec = importlib.util.find_spec(package)
        if spec is None or not spec.submodule_search_locations:
            raise AssertionError(
                f"Install the project media extra before Gramps integration ({package})."
            )
        source = Path(next(iter(spec.submodule_search_locations)))
        shutil.copytree(
            source,
            plugins / "lib" / package,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )


def _set_birth_month_day(root: ET.Element, events: ET.Element) -> None:
    """Give the fixture a structured date that exercises localized month names."""
    birth = next(
        (item for item in _children(events, "event") if item.get("id") == "E0000"),
        None,
    )
    if birth is None:
        raise AssertionError("Gramps XML export is missing the fixture birth event E0000.")
    date_elements = [
        item
        for item in birth
        if item.tag.rsplit("}", 1)[-1]
        in {"daterange", "datespan", "dateval", "datestr"}
    ]
    if not date_elements:
        raise AssertionError("Fixture birth event E0000 has no Gramps date element.")
    date_index = list(birth).index(date_elements[0])
    for item in date_elements:
        birth.remove(item)
    birth.insert(
        date_index,
        ET.Element(
            _qualified_name(root, "dateval"),
            {"val": "1900-03-14", "type": "about"},
        ),
    )


def _native_fixture(executable: str, env: dict[str, str], work: Path) -> Path:
    """Round-trip GEDCOM through Gramps, then add native Gramps XML fields."""
    gedcom = work / "reference-family.ged"
    gedcom.write_bytes((ROOT / "tests/fixtures/reference-family.ged").read_bytes())
    fixture = work / "reference-family-native.gramps"
    result = subprocess.run(
        [
            executable,
            "-i",
            str(gedcom),
            "-e",
            str(fixture),
        ],
        env=env,
        cwd=work,
        text=True,
        capture_output=True,
        timeout=90,
    )
    log = result.stdout + result.stderr
    if result.returncode or "Traceback" in log or not fixture.is_file():
        raise AssertionError(log or "Gramps did not export the native XML fixture.")

    raw = fixture.read_bytes()
    compressed = raw.startswith(b"\x1f\x8b")
    xml = gzip.decompress(raw) if compressed else raw
    root = ET.fromstring(xml)
    namespace = root.tag[1:].split("}", 1)[0] if root.tag.startswith("{") else ""
    if namespace:
        ET.register_namespace("", namespace)

    people = next(iter(_children(root, "people")), None)
    families = _section(root, "families")
    events = next(iter(_children(root, "events")), None)
    objects = next(iter(_children(root, "objects")), None)
    notes = _section(root, "notes")
    tags = _section(root, "tags")
    if people is None or events is None or objects is None:
        raise AssertionError("Gramps XML export is missing people, events or media objects.")

    person = next(
        (
            item
            for item in _children(people, "person")
            if item.get("id") == "I0001"
        ),
        None,
    )
    child = next(
        (
            item
            for item in _children(people, "person")
            if item.get("id") == "I0003"
        ),
        None,
    )
    single_parent = next(
        (
            item
            for item in _children(people, "person")
            if item.get("id") == "I0004"
        ),
        None,
    )
    reference_partner = next(
        (
            item
            for item in _children(people, "person")
            if item.get("id") == "I0002"
        ),
        None,
    )
    family = next(
        (
            item
            for item in _children(families, "family")
            if item.get("id") == "F0001"
        ),
        None,
    )
    single_parent_family = next(
        (
            item
            for item in _children(families, "family")
            if item.get("id") == "F0002"
        ),
        None,
    )
    media = next(
        (
            item
            for item in _children(objects, "object")
            if item.get("id") == "M0001"
        ),
        None,
    )
    if (
        person is None
        or child is None
        or single_parent is None
        or reference_partner is None
        or family is None
        or single_parent_family is None
        or media is None
    ):
        raise AssertionError(
            "Gramps XML export is missing fixture people I0001/I0002/I0003/I0004, "
            "families F0001/F0002 or media M0001."
        )

    _set_t04_parentage_case(family, child)
    _add_t04_foster_parent_family(root, single_parent_family, person, single_parent)
    _add_ac03_other_union(root, people, families, person)
    _add_ac05_implex_and_cycle(
        root, people, families, person, reference_partner
    )
    _add_ac06_sibling_without_descendants(root, people, families)
    _add_ac07_spouse_eligibility(root, people, families, events, person)
    _add_ac08_family_event_eligibility(root, people, families, events, person)
    _set_birth_month_day(root, events)
    _add_same_fact_birth_version(root, events, person)
    _apply_ac14_shared_citation(root, events)

    marriage = next(
        (item for item in _children(events, "event") if item.get("id") == "E0002"),
        None,
    )
    if marriage is None:
        raise AssertionError("Gramps XML export is missing the fixture marriage event.")
    marriage_date = next(
        (
            item
            for item in marriage
            if item.tag.rsplit("}", 1)[-1] in {"daterange", "datespan", "dateval", "datestr"}
        ),
        None,
    )
    if marriage_date is None:
        raise AssertionError("Gramps XML export is missing the fixture marriage date.")
    date_index = list(marriage).index(marriage_date)
    marriage.remove(marriage_date)
    marriage.insert(
        date_index,
        ET.Element(
            _qualified_name(root, "datestr"),
            {"val": "Entre l’hiver 1924 et le printemps 1925"},
        ),
    )

    media_file = next(
        (item for item in _children(media, "file") if item.get("src")),
        None,
    )
    if media_file is None:
        raise AssertionError("Gramps XML export is missing M0001's file path.")
    media_file.set("src", str((work / "media" / "portrait.jpg").resolve()))

    media_handle = media.get("handle")
    media_ref = next(
        (
            item for item in _children(person, "objref")
            if item.get("hlink") == media_handle
        ),
        None,
    )
    if not media_handle or media_ref is None:
        raise AssertionError("Gramps XML export is missing I0001's native media reference.")

    ET.SubElement(
        person,
        _qualified_name(root, "attribute"),
        {"type": "BOOK_PROFILE", "value": "YES"},
    )
    rectangle = {
        "corner1_x": "10",
        "corner1_y": "20",
        "corner2_x": "90",
        "corner2_y": "80",
    }
    ET.SubElement(media_ref, _qualified_name(root, "region"), rectangle)

    citations = _section(root, "citations")
    citation_by_id = {
        item.get("id"): item for item in _children(citations, "citation")
    }
    if not {"C0000", "C0001"} <= citation_by_id.keys():
        raise AssertionError("Gramps XML export is missing citations C0000 or C0001.")
    sources = _section(root, "sources")
    source = next(
        (item for item in _children(sources, "source") if item.get("id") == "S0001"),
        None,
    )
    if source is None:
        raise AssertionError("Gramps XML export is missing source S0001.")
    linked_source = copy.deepcopy(source)
    linked_source_handle = f"_{uuid.uuid4().hex}"
    linked_source.set("handle", linked_source_handle)
    linked_source.set("id", "S0002")
    source_ref = next(
        (
            child
            for child in citation_by_id["C0001"]
            if child.tag.rsplit("}", 1)[-1] == "sourceref"
        ),
        None,
    )
    if source_ref is None:
        raise AssertionError("Citation C0001 is missing its native source reference.")
    source_ref.set("hlink", linked_source_handle)
    repository_ref = next(
        (
            child
            for child in linked_source
            if child.tag.rsplit("}", 1)[-1] == "reporef"
        ),
        None,
    )
    if repository_ref is None:
        raise AssertionError("Source S0001 is missing its native repository reference.")
    repositories = _section(root, "repositories")
    repository = next(
        (
            item
            for item in _children(repositories, "repository")
            if item.get("handle") == repository_ref.get("hlink")
        ),
        None,
    )
    if repository is None:
        raise AssertionError("Source S0001 references a missing repository.")
    linked_repository = copy.deepcopy(repository)
    linked_repository_handle = f"_{uuid.uuid4().hex}"
    linked_repository.set("handle", linked_repository_handle)
    linked_repository.set("id", "R0002")
    repository_ref.set("hlink", linked_repository_handle)
    ET.SubElement(
        linked_repository,
        _qualified_name(root, "url"),
        {"href": "https://example.org/ac16-citation", "type": "Web Home"},
    )
    repositories.append(linked_repository)
    sources.append(linked_source)
    pdf_cases = (
        ("M0002", "C0000", "ac16-single-unlinked.pdf"),
        ("M0003", "C0000", "ac16-multipage-unlinked.pdf"),
        ("M0004", "C0001", "ac16-single-linked.pdf"),
        ("M0005", "C0001", "ac16-multipage-linked.pdf"),
    )
    for media_id, citation_id, filename in pdf_cases:
        pdf_handle = f"_{uuid.uuid4().hex}"
        pdf_media = ET.SubElement(
            objects,
            _qualified_name(root, "object"),
            {"handle": pdf_handle, "change": "0", "id": media_id},
        )
        ET.SubElement(
            pdf_media,
            _qualified_name(root, "file"),
            {
                "src": str((work / "media" / filename).resolve()),
                "mime": "application/pdf",
                "description": filename.removesuffix(".pdf"),
            },
        )
        citation = citation_by_id[citation_id]
        ET.SubElement(
            citation,
            _qualified_name(root, "objref"),
            {"hlink": pdf_handle},
        )

    _add_ac13_excluded_featured_media(
        root,
        person,
        objects,
        citations,
        tags,
        work,
    )
    _apply_ac18_missing_references(root, events)

    tag_handle = f"_{uuid.uuid4().hex}"
    ET.SubElement(
        tags,
        _qualified_name(root, "tag"),
        {
            "handle": tag_handle,
            "change": "0",
            "name": "BOOK_PUBLICATION",
            "color": "#000000000000",
            "priority": "0",
        },
    )

    existing_note_ids = {item.get("id") for item in _children(notes, "note")}
    note_number = 1
    while f"N{note_number:04d}" in existing_note_ids:
        note_number += 1
    note_handle = f"_{uuid.uuid4().hex}"
    note = ET.SubElement(
        notes,
        _qualified_name(root, "note"),
        {
            "handle": note_handle,
            "change": "0",
            "id": f"N{note_number:04d}",
            "type": "General",
        },
    )
    note_text = "Note de publication native en gras et en italique."
    ET.SubElement(note, _qualified_name(root, "text")).text = note_text
    for style_name, fragment in (("bold", "gras"), ("italic", "italique")):
        style = ET.SubElement(
            note,
            _qualified_name(root, "style"),
            {"name": style_name},
        )
        start = note_text.index(fragment)
        ET.SubElement(
            style,
            _qualified_name(root, "range"),
            {"start": str(start), "end": str(start + len(fragment))},
        )
    ET.SubElement(note, _qualified_name(root, "tagref"), {"hlink": tag_handle})
    ET.SubElement(person, _qualified_name(root, "noteref"), {"hlink": note_handle})
    ET.SubElement(family, _qualified_name(root, "noteref"), {"hlink": note_handle})

    _add_f0_editorial_notes(root, family, notes, tags, tag_handle)

    updated = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    fixture.write_bytes(gzip.compress(updated, mtime=0) if compressed else updated)
    return fixture


def verify(
    executable: str,
    *,
    pdf_output: str | Path | None = None,
    lualatex: str | Path | None = None,
    addon_archive: str | Path | None = None,
) -> None:
    with tempfile.TemporaryDirectory(prefix="fancy-book-integration-") as directory:
        work = Path(directory)
        env = os.environ.copy()
        env.update(GRAMPSHOME=str(work), XDG_CACHE_HOME=str(work / "cache"), LANGUAGE="en")
        preferences = work / "gramps" / "gramps60" / "gramps.ini"
        preferences.parent.mkdir(parents=True, exist_ok=True)
        preferences.write_text("[preferences]\ndate-format=2\n", encoding="utf-8")
        if lualatex is not None:
            compiler = Path(lualatex).expanduser()
            if not compiler.is_file():
                raise FileNotFoundError(f"LuaLaTeX executable was not found: {compiler}")
            env["PATH"] = f"{compiler.absolute().parent}{os.pathsep}{env.get('PATH', '')}"
        # Install the add-on and declared dependency in this profile, never from a source PYTHONPATH.
        env.pop("PYTHONPATH", None)
        plugins = work / "gramps" / "gramps60" / "plugins"
        plugins.mkdir(parents=True)
        archive_path = (
            Path(addon_archive).expanduser()
            if addon_archive is not None
            else ROOT / "gramps60/download/GrampsFancyBook.addon.tgz"
        )
        with tarfile.open(archive_path) as archive:
            archive.extractall(plugins, filter="data")
        _install_mistune_dependency(plugins)
        _install_optional_media_dependencies(plugins)

        _create_media_fixture(work)
        native_fixture = _native_fixture(executable, env, work)

        def report(
            family: str,
            output: Path | None,
            *,
            output_format: str = "json_snapshot",
            book_language: str | None = None,
            overwrite=False,
        ) -> str:
            options = (
                f"name={PLUGIN_ID},reference_family={family},"
                f"output_format={output_format},privacy_acknowledged=True"
            )
            if output is not None:
                options += f",destination={output}"
            if book_language is not None:
                options += f",book_language={book_language}"
            if overwrite:
                options += ",overwrite=True"
            result = subprocess.run(
                [
                    executable,
                    "-i",
                    str(native_fixture),
                    "-a",
                    "report",
                    "-p",
                    options,
                ],
                env=env,
                cwd=work,
                text=True,
                capture_output=True,
                timeout=90,
            )
            log = result.stdout + result.stderr
            # Gramps can return 0 even when a report failed. Verify the output and logs.
            if result.returncode or "Traceback" in log or "Unknown report name" in log:
                raise AssertionError(log)
            return log

        output = work / "family.json"
        log = report("F0001", output)
        if not output.exists():
            raise AssertionError(log)
        model = json.loads(output.read_text(encoding="utf-8"))

        localized_models = {}
        for language in ("en", "fr"):
            localized_output = work / f"family-{language}.json"
            log = report("F0001", localized_output, book_language=language)
            if not localized_output.exists():
                raise AssertionError(log)
            localized_models[language] = json.loads(
                localized_output.read_text(encoding="utf-8")
            )
        localized_birth_dates = {}
        for language, localized_model in localized_models.items():
            birth = next(
                event
                for event in localized_model["events"].values()
                if event["gramps_id"] == "E0000"
            )
            localized_birth_dates[language] = birth["date"]
            assert localized_model["metadata"]["BOOK_LANGUAGE"] == language
        english_date = localized_birth_dates["en"]
        french_date = localized_birth_dates["fr"]
        assert "march" in english_date["display"].casefold(), english_date
        assert "mars" in french_date["display"].casefold(), french_date
        assert english_date["ymd"] == [1900, 3, 14]
        assert french_date["ymd"] == [1900, 3, 14]
        assert english_date["raw"] == french_date["raw"]
        assert english_date["range"] == french_date["range"]

        localized_marriage_dates = {}
        for language, localized_model in localized_models.items():
            marriage = next(
                event
                for event in localized_model["events"].values()
                if event["type"] == "Marriage"
            )
            localized_marriage_dates[language] = marriage["date"]
        expected_free_text_date = "Entre l’hiver 1924 et le printemps 1925"
        english_marriage_date = localized_marriage_dates["en"]
        french_marriage_date = localized_marriage_dates["fr"]
        assert english_marriage_date["display"] == expected_free_text_date
        assert french_marriage_date["display"] == expected_free_text_date
        assert english_marriage_date["raw"] == french_marriage_date["raw"]
        print(
            "PASS: month names in structured dates follow the book language; raw dates and free text stay unchanged"
        )

        consistency_path = output.with_name("family_consistency.json")
        if not consistency_path.is_file():
            raise AssertionError("The export is missing its consistency companion JSON.")
        consistency = json.loads(consistency_path.read_text(encoding="utf-8"))
        birth_events = [
            event for event in model["events"].values() if event["type"] == "Birth"
        ]
        assert len(birth_events) >= 2, (birth_events, model["diagnostics"])
        birth_fact_events = [
            event
            for event in birth_events
            if any(
                attribute["type"] == "BOOK_FACT_ID"
                and attribute["value"] == "AC19-birth-of-I0001"
                for attribute in event["links"]["attributes"]
            )
        ]
        assert len(birth_fact_events) == 2, birth_fact_events
        assert {event["date"]["ymd"][0] for event in birth_fact_events} == {1900, 2000}
        assert len({event["place_handle"] for event in birth_fact_events}) == 2
        assert consistency["scope"]["compared_groups"] == 1
        assert consistency["groups"][0]["book_fact_id"] == "AC19-birth-of-I0001"
        assert set(consistency["groups"][0]["event_handles"]) == {
            event["handle"] for event in birth_fact_events
        }
        actual_findings = {
            (finding["field"], finding["classification"])
            for finding in consistency["findings"]
        }
        expected_findings = {
            ("date", "confirmed_conflict"),
            ("place", "review_required"),
        }
        assert actual_findings == expected_findings, {
            "actual_findings": actual_findings,
            "groups": consistency["groups"],
            "findings": consistency["findings"],
        }
        book_conflict_codes = {
            "disjoint_event_date_ranges",
            "different_event_place_references",
        }
        assert not any(
            diagnostic["code"] in book_conflict_codes
            for diagnostic in model["diagnostics"]
        )
        print(
            "PASS: AC-19 native BOOK_FACT_ID, separate date/place report, "
            "and unchanged book diagnostics"
        )

        assert model["reference_family"]["gramps_id"] == "F0001"
        assert {person["gramps_id"] for person in model["people"]} == {
            "I0001",
            "I0002",
            "I0003",
            "I0004",
            "I0005",
            "I0006",
            "I0007",
            "I0008",
            "I0009",
            "I0010",
            "I0011",
            "I0012",
            "I0013",
            "I0014",
            "I0015",
            "I0016",
            "I0017",
        }
        assert "Émile" in model["people"][0]["name"]
        assert model["reference_family"]["handle"] != "F0001"
        assert model["metadata"]["BOOK_SCHEMA_VERSION"] == "0.8"
        assert model["reference_family"]["handle"] in model["families"]
        reference_family = model["reference_family"]
        child_relationship = reference_family["child_relationships"][0]
        assert child_relationship["father_relation"] == "Adopted"
        assert child_relationship["mother_relation"] == "None"
        family_sections = model["genealogy"]["family_sections"]
        central_section = next(
            section
            for section in family_sections
            if section["family_handle"] == reference_family["handle"]
            and section["part"] == "ancestry"
            and "central" in section["roles"]
        )
        central_partner_handles = [
            reference_family["father"]["handle"],
            reference_family["mother"]["handle"],
        ]
        ancestry_generation_zero = next(
            generation
            for generation in model["genealogy"]["ancestry"]["generations"]
            if generation["number"] == 0
        )
        central_ancestry_occurrences = [
            occurrence
            for occurrence in ancestry_generation_zero["occurrences"]
            if "central" in occurrence["roles"]
        ]
        assert [
            occurrence["person_handle"] for occurrence in central_ancestry_occurrences
        ] == central_partner_handles
        ancestry_occurrence_ids = {
            occurrence["person_handle"]: occurrence["occurrence_id"]
            for occurrence in central_ancestry_occurrences
        }
        assert set(central_section["partner_occurrence_ids"]) == set(
            ancestry_occurrence_ids.values()
        )
        descent_generation_zero = next(
            generation
            for generation in model["genealogy"]["descent"]["generations"]
            if generation["number"] == 0
        )
        central_descent_occurrences = [
            occurrence
            for occurrence in descent_generation_zero["occurrences"]
            if occurrence["person_handle"] in central_partner_handles
        ]
        assert len(central_descent_occurrences) == 2
        assert {
            occurrence["person_handle"]: occurrence["primary_occurrence_id"]
            for occurrence in central_descent_occurrences
        } == ancestry_occurrence_ids
        print(
            "PASS: AC-01 native central partners start ancestry generation zero "
            "and descent occurrences point back to them"
        )
        occurrences_by_id = {}
        for part in ("ancestry", "descent"):
            for generation in model["genealogy"][part]["generations"]:
                occurrences_by_id.update(
                    (item["occurrence_id"], item)
                    for item in generation["occurrences"]
                )
        parent_child_links = central_section["parent_child_links"]
        assert len(parent_child_links) == 1, parent_child_links
        parent_child_link = parent_child_links[0]
        assert parent_child_link["relationship_type"] == "Adopted"
        assert (
            occurrences_by_id[parent_child_link["parent_occurrence_id"]]["person_handle"]
            == reference_family["father"]["handle"]
        )
        assert (
            occurrences_by_id[parent_child_link["child_occurrence_id"]]["person_handle"]
            == child_relationship["person_handle"]
        )
        foster_family = next(
            family
            for family in model["families"].values()
            if family["gramps_id"] == "F0002"
        )
        assert foster_family["mother"] is None
        foster_relationship = foster_family["child_relationships"][0]
        assert foster_relationship["father_relation"] == "Foster"
        foster_section = next(
            section
            for section in family_sections
            if section["family_handle"] == foster_family["handle"]
            and section["part"] == "ancestry"
        )
        assert len(foster_section["partner_occurrence_ids"]) == 1
        assert len(foster_section["child_occurrence_ids"]) == 1
        foster_links = foster_section["parent_child_links"]
        assert len(foster_links) == 1, foster_links
        assert foster_links[0]["relationship_type"] == "Foster"
        assert (
            occurrences_by_id[foster_links[0]["parent_occurrence_id"]]["person_handle"]
            == foster_family["father"]["handle"]
        )
        assert (
            occurrences_by_id[foster_links[0]["child_occurrence_id"]]["person_handle"]
            == foster_relationship["person_handle"]
        )
        assert len(foster_section["partner_occurrence_ids"]) == 1
        assert (
            occurrences_by_id[foster_section["partner_occurrence_ids"][0]][
                "person_handle"
            ]
            == foster_family["father"]["handle"]
        )
        other_union = next(
            family
            for family in model["families"].values()
            if family["gramps_id"] == "F0003"
        )
        other_union_child_handle = other_union["child_relationships"][0]["person_handle"]
        other_union_section = next(
            section
            for section in family_sections
            if section["family_handle"] == other_union["handle"]
            and section["part"] == "descent"
        )
        other_child_occurrences = [
            item
            for generation in model["genealogy"]["descent"]["generations"]
            for item in generation["occurrences"]
            if item["person_handle"] == other_union_child_handle
        ]
        assert len(other_child_occurrences) == 1, other_child_occurrences
        assert other_child_occurrences[0]["generation"] == 1
        assert other_child_occurrences[0]["family_handle"] == other_union["handle"]
        assert other_union_section["child_occurrence_ids"] == [
            other_child_occurrences[0]["occurrence_id"]
        ]
        assert len(other_union_section["partner_occurrence_ids"]) == 2
        assert {
            link["relationship_type"]
            for link in other_union_section["parent_child_links"]
        } == {"Birth"}
        assert model["genealogy"]["profile_handles"].count(
            other_union_child_handle
        ) == 1
        assert sum(
            profile["person_handle"] == other_union_child_handle
            for profile in model["editorial_book"]["profiles"]
        ) == 1
        shared_ancestor = next(
            person for person in model["people"]
            if person["gramps_id"] == "I0007"
        )
        shared_ancestor_handle = shared_ancestor["handle"]
        shared_ancestor_occurrences = [
            occurrence
            for generation in model["genealogy"]["ancestry"]["generations"]
            for occurrence in generation["occurrences"]
            if occurrence["person_handle"] == shared_ancestor_handle
        ]
        shared_ancestor_branch_occurrences = [
            occurrence
            for occurrence in shared_ancestor_occurrences
            if occurrence["generation"] == -1
        ]
        assert {
            occurrence["branch_handles"][0]
            for occurrence in shared_ancestor_branch_occurrences
        } == {reference_family["father"]["handle"], reference_family["mother"]["handle"]}
        assert len(shared_ancestor_branch_occurrences) == 2
        assert model["genealogy"]["profile_handles"].count(
            shared_ancestor_handle
        ) == 1
        shared_ancestor_profiles = [
            profile
            for profile in model["editorial_book"]["profiles"]
            if profile["person_handle"] == shared_ancestor_handle
        ]
        assert len(shared_ancestor_profiles) == 1
        assert sum(
            occurrence["is_primary_profile"]
            for occurrence in shared_ancestor_occurrences
        ) == 1
        shared_ancestor_index_entries = [
            entry
            for entry in model["editorial_book"]["person_index"]
            if entry["person_handle"] == shared_ancestor_handle
        ]
        assert len(shared_ancestor_index_entries) == 1
        assert len(shared_ancestor_index_entries[0]["occurrence_ids"]) >= 2
        assert any(
            diagnostic["code"] == "genealogy_cycle"
            and diagnostic["handle"] == reference_family["father"]["handle"]
            for diagnostic in model["diagnostics"]
        )
        ancestry_paths = [
            path
            for generation in model["genealogy"]["ancestry"]["generations"]
            for occurrence in generation["occurrences"]
            for path in occurrence["lineage_paths"]
        ]
        assert max(map(len, ancestry_paths)) == 4
        ac06_sibling = next(
            person for person in model["people"]
            if person["gramps_id"] == "I0010"
        )
        ac06_sibling_handle = ac06_sibling["handle"]
        ac06_child = next(
            person for person in model["people"]
            if person["gramps_id"] == "I0014"
        )
        ac06_sibling_occurrences = [
            occurrence
            for generation in model["genealogy"]["ancestry"]["generations"]
            for occurrence in generation["occurrences"]
            if occurrence["person_handle"] == ac06_sibling_handle
        ]
        ac06_sibling_parent_generation_occurrences = [
            occurrence
            for occurrence in ac06_sibling_occurrences
            if occurrence["generation"] == -1
        ]
        assert len(ac06_sibling_parent_generation_occurrences) == 1, (
            ac06_sibling_occurrences
        )
        ac06_sibling_occurrence = ac06_sibling_parent_generation_occurrences[0]
        assert all(
            "sibling" in occurrence["roles"]
            for occurrence in ac06_sibling_occurrences
        )
        assert all(
            occurrence["person_handle"] != ac06_child["handle"]
            for occurrence in occurrences_by_id.values()
        )
        ac06_child_family = next(
            family
            for family in model["families"].values()
            if family["gramps_id"] == "F0008"
        )
        assert all(
            section["family_handle"] != ac06_child_family["handle"]
            for section in family_sections
        )
        ac06_parent_family = next(
            family
            for family in model["families"].values()
            if family["gramps_id"] == "F0007"
        )
        ac06_sibling_family_section = next(
            section
            for section in family_sections
            if section["family_handle"] == ac06_parent_family["handle"]
            and section["part"] == "ancestry"
        )
        assert (
            ac06_sibling_occurrence["occurrence_id"]
            in ac06_sibling_family_section["child_occurrence_ids"]
        )
        assert model["genealogy"]["profile_handles"].count(
            ac06_sibling_handle
        ) == 1
        ac06_sibling_profiles = [
            profile
            for profile in model["editorial_book"]["profiles"]
            if profile["person_handle"] == ac06_sibling_handle
        ]
        assert len(ac06_sibling_profiles) == 1
        ac06_sibling_index_entries = [
            entry
            for entry in model["editorial_book"]["person_index"]
            if entry["person_handle"] == ac06_sibling_handle
        ]
        assert len(ac06_sibling_index_entries) == 1
        ac07_people = {
            person["gramps_id"]: person
            for person in model["people"]
            if person["gramps_id"] in {"I0015", "I0016"}
        }
        assert set(ac07_people) == {"I0015", "I0016"}
        ac07_occurrences = {}
        for gramps_id, person in ac07_people.items():
            event_types = {
                model["events"][reference["event_handle"]]["type"]
                for reference in person["links"]["events"]
            }
            assert event_types == {"Birth", "Death"}, (gramps_id, event_types)
            occurrences = [
                occurrence
                for generation in model["genealogy"]["descent"]["generations"]
                for occurrence in generation["occurrences"]
                if occurrence["person_handle"] == person["handle"]
            ]
            assert len(occurrences) == 1, (gramps_id, occurrences)
            assert occurrences[0]["generation"] == 0
            assert "partner" in occurrences[0]["roles"]
            ac07_occurrences[gramps_id] = occurrences[0]
        ac07_unforced_handle = ac07_people["I0015"]["handle"]
        ac07_forced_handle = ac07_people["I0016"]["handle"]
        assert ac07_unforced_handle not in model["genealogy"]["profile_handles"]
        assert ac07_forced_handle in model["genealogy"]["profile_handles"]
        ac07_unforced_profiles = [
            profile
            for profile in model["editorial_book"]["profiles"]
            if profile["person_handle"] == ac07_unforced_handle
        ]
        ac07_forced_profiles = [
            profile
            for profile in model["editorial_book"]["profiles"]
            if profile["person_handle"] == ac07_forced_handle
        ]
        assert not ac07_unforced_profiles
        assert len(ac07_forced_profiles) == 1
        for gramps_id, family_id in (("I0015", "F0009"), ("I0016", "F0010")):
            family = next(
                family
                for family in model["families"].values()
                if family["gramps_id"] == family_id
            )
            section = next(
                section
                for section in family_sections
                if section["family_handle"] == family["handle"]
                and section["part"] == "descent"
            )
            assert (
                ac07_occurrences[gramps_id]["occurrence_id"]
                in section["partner_occurrence_ids"]
            )
            assert not section["child_occurrence_ids"]
        ac08_partner = next(
            person for person in model["people"] if person["gramps_id"] == "I0017"
        )
        ac08_event_types = {
            model["events"][reference["event_handle"]]["type"]
            for reference in ac08_partner["links"]["events"]
        }
        assert ac08_event_types == {"Birth", "Death"}, ac08_event_types
        assert not any(
            attribute["type"] == "BOOK_PROFILE"
            for attribute in ac08_partner["links"]["attributes"]
        )
        ac08_family = next(
            family
            for family in model["families"].values()
            if family["gramps_id"] == "F0011"
        )
        assert len(ac08_family["links"]["events"]) == 1
        ac08_marriage_ref = ac08_family["links"]["events"][0]
        assert ac08_marriage_ref["role"] == "Family"
        ac08_marriage = model["events"][ac08_marriage_ref["event_handle"]]
        assert ac08_marriage["type"] == "Marriage"
        assert ac08_marriage["description"] == AC08_FAMILY_EVENT_DETAIL
        assert ac08_partner["handle"] in model["genealogy"]["profile_handles"]
        ac08_profiles = [
            profile
            for profile in model["editorial_book"]["profiles"]
            if profile["person_handle"] == ac08_partner["handle"]
        ]
        assert len(ac08_profiles) == 1
        assert all(
            reference["event_handle"] != ac08_marriage_ref["event_handle"]
            for reference in ac08_profiles[0]["event_refs"]
        )
        ac08_family_notice = next(
            notice
            for notice in model["editorial_book"]["family_notices"]
            if notice["family_handle"] == ac08_family["handle"]
        )
        assert [
            reference["event_handle"] for reference in ac08_family_notice["event_refs"]
        ] == [ac08_marriage_ref["event_handle"]]
        print(
            "PASS: T-04 native Gramps preserves Adopted/Foster/None; traversal "
            "keeps only recorded parent links and the single-parent family"
        )
        print(
            "PASS: AC-09 native single-parent family has exactly one recorded "
            "parent occurrence in the model"
        )
        print(
            "PASS: AC-03 native other-union child is in descent generation 1, "
            "with a family section and one profile"
        )
        print(
            "PASS: AC-05 native Gramps preserves both shared-ancestor branches, "
            "one profile/index entry, and stops the ancestry cycle"
        )
        print(
            "PASS: AC-06 native Gramps shows an eligible ancestor sibling and its "
            "profile without expanding the sibling's child"
        )
        print(
            "PASS: AC-07 native spouse with only Birth/Death stays mention-only; "
            "BOOK_PROFILE=YES creates one profile"
        )
        print(
            "PASS: AC-08 native Marriage family event qualifies its spouse; "
            "event detail remains in the family notice"
        )
        assert {event["type"] for event in model["events"].values()} >= {
            "Birth", "Profession", "Marriage"
        }
        birth = next(event for event in model["events"].values() if event["type"] == "Birth")
        assert birth["date"]["modifier"] == 3
        assert birth["date"]["ymd"][0] == 1900
        assert isinstance(birth["date"]["range"], list)
        assert isinstance(birth["date"]["raw"], list)
        assert birth["place_handle"] in model["places"]
        person_event_types = {
            model["events"][ref["event_handle"]]["type"]
            for ref in model["people"][0]["links"]["events"]
        }
        assert person_event_types >= {"Birth", "Profession"}
        marriage_ref = model["reference_family"]["links"]["events"][0]
        assert marriage_ref["role"] == "Family"
        assert model["events"][marriage_ref["event_handle"]]["type"] == "Marriage"
        print("PASS: T-04 F0 Marriage association retains the Family event role")
        assert len(model["citations"]) == 4
        assert len(model["sources"]) == 3
        source = next(iter(model["sources"].values()))
        assert len(source["repository_refs"]) == 1
        assert len(model["repositories"]) == 2
        assert len(model["media"]) == 6
        ac14_citations_by_page = {
            citation["page"]: citation
            for citation in model["citations"].values()
        }
        shared_citation = ac14_citations_by_page[AC14_SHARED_PAGE]
        second_citation = ac14_citations_by_page[AC14_SECOND_PAGE]
        assert shared_citation["handle"] != second_citation["handle"]
        birth_events = [
            event for event in model["events"].values() if event["type"] == "Birth"
        ]
        birth_with_multiple_citations = next(
            event
            for event in birth_events
            if {
                shared_citation["handle"],
                second_citation["handle"],
            }
            <= set(event["links"]["citations"])
        )
        profession_event = next(
            event
            for event in model["events"].values()
            if event["type"] == "Profession"
        )
        assert shared_citation["handle"] in profession_event["links"]["citations"]
        assert second_citation["handle"] not in profession_event["links"]["citations"]
        assert len(birth_with_multiple_citations["links"]["citations"]) == 2
        editorial_book = model["editorial_book"]
        citation_entries = editorial_book["citation_entries"]
        entries_by_citation = {
            entry["citation_handle"]: entry for entry in citation_entries
        }
        assert len(entries_by_citation) == len(citation_entries)
        shared_entry = entries_by_citation[shared_citation["handle"]]
        second_entry = entries_by_citation[second_citation["handle"]]
        shared_owner_event_types = {
            model["events"][call["owner_handle"]]["type"]
            for call in shared_entry["calls"]
            if call["owner_type"] == "event"
        }
        assert {"Birth", "Profession"} <= shared_owner_event_types
        ac18_citation = next(
            citation
            for citation in model["citations"].values()
            if citation["page"] == AC18_CITATION_PAGE
        )
        ac18_source = model["sources"][ac18_citation["source_handle"]]
        assert ac18_source["title"] == AC18_SOURCE_TITLE
        assert ac18_source["author"] == AC18_SOURCE_AUTHOR
        assert ac18_source["publication_info"] == AC18_SOURCE_PUBLICATION
        assert ac18_source["repository_refs"] == []
        ac18_entry = entries_by_citation[ac18_citation["handle"]]
        assert ac18_entry["source_handle"] == ac18_source["handle"]
        assert ac18_entry["repository_refs"] == []
        assert any(
            model["events"][call["owner_handle"]]["type"] == "Profession"
            for call in ac18_entry["calls"]
            if call["owner_type"] == "event"
        )
        uncited_marriage = next(
            event
            for event in model["events"].values()
            if event["gramps_id"] == "E0002"
        )
        assert uncited_marriage["type"] == "Marriage"
        assert uncited_marriage["description"] == AC18_UNCITED_EVENT
        assert uncited_marriage["links"]["citations"] == []
        family_notice = next(
            notice
            for notice in editorial_book["family_notices"]
            if notice["family_handle"] == model["reference_family"]["handle"]
        )
        uncited_marriage_reference = next(
            reference
            for reference in family_notice["event_refs"]
            if reference["event_handle"] == uncited_marriage["handle"]
        )
        assert uncited_marriage_reference["citations"] == []
        assert family_notice["citation_call_ids"] == []
        f0_role_notes = editorial_book["front_matter_notes"]
        expected_f0_roles = tuple(F0_EDITORIAL_ROLE_TEXT)
        assert tuple(item["role"] for item in f0_role_notes) == expected_f0_roles
        f0_note_handles = {item["note_handle"] for item in f0_role_notes}
        assert all(handle in model["notes"] for handle in f0_note_handles)
        f0_text_by_role = {
            item["role"]: model["notes"][item["note_handle"]]["text"]
            for item in f0_role_notes
        }
        assert f0_text_by_role == F0_EDITORIAL_ROLE_TEXT
        assert not f0_note_handles.intersection(family_notice["note_handles"])
        f0_diagnostic_codes = {
            item["code"]
            for item in model["diagnostics"]
            if item["code"].startswith("F0_EDITORIAL_NOTE_")
        }
        assert f0_diagnostic_codes == {
            "F0_EDITORIAL_NOTE_DUPLICATE_ROLE",
            "F0_EDITORIAL_NOTE_AMBIGUOUS_ROLE",
            "F0_EDITORIAL_NOTE_NOT_PUBLISHABLE",
            "F0_EDITORIAL_NOTE_EMPTY",
        }, model["diagnostics"]
        print(
            "PASS: T-02 native F0 notes select all six roles and diagnose "
            "duplicate, ambiguous, unpublished and empty notes"
        )
        print(
            "PASS: AC-18 native model publishes a Marriage without citations and "
            "keeps a detailed citation whose source has no repository"
        )
        print(
            "PASS: AC-14 native Gramps citations: Birth has two citations and "
            "Profession reuses the same citation as Birth"
        )
        media = next(
            item
            for item in model["media"].values()
            if item["path"] == str((work / "media" / "portrait.jpg").resolve())
        )
        assert media["path"] == str((work / "media" / "portrait.jpg").resolve())
        assert "portrait" in media["description"].lower()
        assert model["people"][0]["links"]["media"][0]["media_handle"] == media["handle"]
        assert model["people"][0]["links"]["media"][0]["rectangle"] == [10, 20, 90, 80]
        assert any(
            attribute["type"] == "BOOK_PROFILE" and attribute["value"] == "YES"
            for attribute in model["people"][0]["links"]["attributes"]
        )
        publishable_note = next(
            (note for note in model["notes"].values() if note["is_publishable"]),
            None,
        )
        assert publishable_note is not None
        assert publishable_note["text"] == "Note de publication native en gras et en italique."
        assert any(
            model["tags"][handle]["name"] == "BOOK_PUBLICATION"
            for handle in publishable_note["links"]["tag_handles"]
        )
        note_handle = publishable_note["handle"]
        assert note_handle in model["people"][0]["links"]["notes"]
        assert note_handle in model["reference_family"]["links"]["notes"]

        media_by_name = {
            Path(item["path"]).name: item for item in model["media"].values()
        }
        expected_pdf_actions = {
            "ac16-single-unlinked.pdf": ("reproduce", 1, True),
            "ac16-multipage-unlinked.pdf": ("reference-only", 2, False),
            "ac16-single-linked.pdf": ("external-link", None, False),
            "ac16-multipage-linked.pdf": ("external-link", None, False),
        }
        artifacts_by_handle = {
            artifact["media_handle"]: artifact for artifact in model["media_artifacts"]
        }
        assert len(artifacts_by_handle) == 5, model["media_artifacts"]
        ac13_media = media_by_name[AC13_MEDIA_FILENAME]
        assert ac13_media["is_excluded"] is True
        assert ac13_media["is_featured"] is True
        ac13_media_handle = ac13_media["handle"]
        assert ac13_media_handle not in artifacts_by_handle
        ac13_citations = [
            citation
            for citation in model["citations"].values()
            if citation["page"] == AC13_CITATION_PAGE
        ]
        assert len(ac13_citations) == 1, ac13_citations
        ac13_citation_handle = ac13_citations[0]["handle"]
        editorial_book = model["editorial_book"]
        assert all(
            placement["media_handle"] != ac13_media_handle
            for placement in editorial_book["media_placements"]
        )
        editorial_media_refs = [
            reference
            for profile in editorial_book["profiles"]
            for reference in profile["media_refs"]
        ]
        editorial_media_refs.extend(
            reference
            for notice in editorial_book["family_notices"]
            for reference in notice["media_refs"]
        )
        editorial_media_refs.extend(
            reference
            for entry in editorial_book["citation_entries"]
            for reference in entry["media_refs"]
        )
        assert all(
            reference["media_handle"] != ac13_media_handle
            for reference in editorial_media_refs
        )
        assert ac13_citation_handle not in {
            entry["citation_handle"] for entry in editorial_book["citation_entries"]
        }
        print(
            "PASS: AC-13 native Gramps media with BOOK_EXCLUDE + BOOK_FEATURED "
            "and its exclusive citation are omitted from the editorial book"
        )
        for filename, (expected_action, expected_pages, has_derivative) in (
            expected_pdf_actions.items()
        ):
            pdf_media = media_by_name[filename]
            artifact = artifacts_by_handle[pdf_media["handle"]]
            assert artifact["action"] == expected_action, (
                filename,
                artifact,
                model["diagnostics"],
            )
            assert artifact["page_count"] == expected_pages, artifact
            assert bool(artifact.get("asset_path")) is has_derivative, artifact
            if expected_action == "reproduce":
                assert artifact["dpi"] == 300, artifact
            if expected_action == "external-link":
                assert artifact["citation_handles"]
                linked_citation = model["citations"][artifact["citation_handles"][0]]
                linked_source = model["sources"][linked_citation["source_handle"]]
                assert any(
                    url["path"] == "https://example.org/ac16-citation"
                    for reference in linked_source["repository_refs"]
                    for url in model["repositories"][reference["repository_handle"]]["urls"]
                ), artifact
        print(
            "PASS: AC-16 native Gramps citation media: single/multipage PDFs with and without URLs"
        )

        html_output = work / "family-shared-note.zip"
        log = report("F0001", html_output, output_format="html_zip")
        if not html_output.is_file():
            raise AssertionError(log or "Gramps did not write the shared-note HTML archive.")
        with zipfile.ZipFile(html_output) as archive:
            if archive.testzip() is not None:
                raise AssertionError("Gramps produced an invalid shared-note HTML archive.")
            html = archive.read("index.html").decode("utf-8")
            archive_names = set(archive.namelist())
        assert '<section class="generation" id="generation:ancestry:0">' in html
        assert '<section class="generation" id="generation:descent:0">' in html
        html_people_by_handle = {
            person["handle"]: person for person in model["people"]
        }
        html_profiles_by_person = {
            profile["person_handle"]: profile
            for profile in editorial_book["profiles"]
        }
        for occurrence in central_ancestry_occurrences:
            occurrence_start = html.index(
                f'<li id="{occurrence["occurrence_id"]}">'
            )
            occurrence_end = html.index("</li>", occurrence_start) + len("</li>")
            occurrence_html = html[occurrence_start:occurrence_end]
            person_name = html_people_by_handle[occurrence["person_handle"]]["name"]
            assert f"<span>{person_name}</span>" in occurrence_html
        for occurrence in central_descent_occurrences:
            occurrence_start = html.index(
                f'<li id="{occurrence["occurrence_id"]}">'
            )
            occurrence_end = html.index("</li>", occurrence_start) + len("</li>")
            occurrence_html = html[occurrence_start:occurrence_end]
            profile = html_profiles_by_person.get(occurrence["person_handle"])
            target = (
                profile["profile_id"]
                if profile is not None
                else occurrence["primary_occurrence_id"]
            )
            assert f'href="#{target}"' in occurrence_html
        print(
            "PASS: AC-01 native HTML starts with both central partners and "
            "links their descent mentions back"
        )
        single_pdf_artifact = artifacts_by_handle[
            media_by_name["ac16-single-unlinked.pdf"]["handle"]
        ]
        assert f"media/{single_pdf_artifact['cache_key']}.png" in archive_names
        assert any(
            filename in html
            for filename in (
                "ac16-single-unlinked",
                "ac16-multipage-unlinked",
                "ac16-single-linked",
                "ac16-multipage-linked",
            )
        ), "The HTML archive does not contain the native citation PDF references."
        assert "https://example.org/ac16-citation" in html
        assert any(label in html for label in ("Adopted", "Adopté"))
        assert "(None)" not in html
        assert AC13_MEDIA_DESCRIPTION not in html
        assert AC13_CITATION_PAGE not in html
        html_citation_numbers = _html_citation_numbers(html)
        assert len(html_citation_numbers) == len(citation_entries)
        shared_entry_id = shared_entry["entry_id"]
        second_entry_id = second_entry["entry_id"]
        assert shared_entry_id in html_citation_numbers
        assert second_entry_id in html_citation_numbers
        assert html_citation_numbers[shared_entry_id] != html_citation_numbers[second_entry_id]
        shared_html_links = re.findall(
            rf'<a href="#{re.escape(shared_entry_id)}">'
            r'<span class="citation-number">\[(\d+)\]</span></a>',
            html,
        )
        assert shared_html_links == [str(html_citation_numbers[shared_entry_id])]
        first_profile = next(
            profile
            for profile in editorial_book["profiles"]
            if profile["person_handle"] == model["people"][0]["handle"]
        )
        profile_match = re.search(
            rf'<section class="person-profile" id="{re.escape(first_profile["profile_id"])}">'
            r"(.*?)</section>",
            html,
            flags=re.DOTALL,
        )
        assert profile_match is not None
        profile_html = profile_match.group(1)
        assert f'href="#{shared_entry_id}"' in profile_html
        assert f'href="#{second_entry_id}"' in profile_html
        assert html.count(AC14_SHARED_PAGE) == 1
        assert html.count(AC14_SECOND_PAGE) == 1
        ac18_entry_match = re.search(
            rf'<article class="citation-entry" id="{re.escape(ac18_entry["entry_id"])}">'
            r"(.*?)</article>",
            html,
            flags=re.DOTALL,
        )
        assert ac18_entry_match is not None
        ac18_entry_html = ac18_entry_match.group(1)
        for marker in (
            AC18_SOURCE_TITLE,
            AC18_SOURCE_AUTHOR,
            AC18_SOURCE_PUBLICATION,
            AC18_CITATION_PAGE,
        ):
            assert html.count(marker) == 1
            assert marker in ac18_entry_html
        assert all(
            marker not in ac18_entry_html
            for marker in ("Dépôt municipal fictif", "R0001", "3 E 12")
        )
        family_notice_match = re.search(
            rf'<article class="family-notice" id="{re.escape(family_notice["notice_id"])}">'
            r"(.*?)</article>",
            html,
            flags=re.DOTALL,
        )
        assert family_notice_match is not None
        family_notice_html = family_notice_match.group(1)
        assert family_notice_html.count(AC18_UNCITED_EVENT) == 1
        assert f'href="#{ac18_entry["entry_id"]}"' not in family_notice_html
        assert 'class="citation-number"' not in family_notice_html
        assert len(
            [name for name in archive_names if name.startswith("media/")]
        ) == 2, archive_names
        for role, marker in F0_EDITORIAL_ROLE_TEXT.items():
            expected_count = 2 if role == "BOOK_TITLE" else 1
            assert html.count(marker) == expected_count, (
                marker,
                html.count(marker),
            )
        assert all(
            marker not in html for marker in F0_EDITORIAL_INVALID_TEXT.values()
        )
        assert html.index(F0_EDITORIAL_ROLE_TEXT["BOOK_DEDICATION"]) < html.index(
            F0_EDITORIAL_ROLE_TEXT["BOOK_INTRODUCTION"]
        )
        ac03_notice = next(
            notice
            for notice in editorial_book["family_notices"]
            if notice["family_handle"] == other_union["handle"]
        )
        ac03_notice_match = re.search(
            rf'<article class="family-notice" id="{re.escape(ac03_notice["notice_id"])}">'
            r"(.*?)</article>",
            html,
            flags=re.DOTALL,
        )
        assert ac03_notice_match is not None
        assert AC03_OTHER_PARTNER in ac03_notice_match.group(1)
        assert AC03_OTHER_CHILD in ac03_notice_match.group(1)
        child_occurrence_target = other_child_occurrences[0]["occurrence_id"]
        assert (
            f'<li id="{child_occurrence_target}"><span>Synthetic, {AC03_OTHER_CHILD}</span>'
            in html
        )
        ac03_profile = next(
            profile
            for profile in editorial_book["profiles"]
            if profile["person_handle"] == other_union_child_handle
        )
        assert html.count(
            f'<section class="person-profile" id="{ac03_profile["profile_id"]}">'
        ) == 1
        shared_ancestor_profile = shared_ancestor_profiles[0]
        assert html.count(
            f'<section class="person-profile" id="{shared_ancestor_profile["profile_id"]}">'
        ) == 1
        for occurrence in shared_ancestor_branch_occurrences:
            occurrence_start = html.index(
                f'<li id="{occurrence["occurrence_id"]}">'
            )
            occurrence_end = html.index("</li>", occurrence_start) + len("</li>")
            occurrence_html = html[occurrence_start:occurrence_end]
            assert f"Synthetic, {AC05_SHARED_ANCESTOR}" in occurrence_html
            if occurrence["is_primary_profile"]:
                assert (
                    f'<section class="person-profile" '
                    f'id="{shared_ancestor_profile["profile_id"]}">'
                ) in occurrence_html
            else:
                assert (
                    f'href="#{shared_ancestor_profile["profile_id"]}"'
                    in occurrence_html
                )
        shared_ancestor_index = shared_ancestor_index_entries[0]
        assert (
            f'<li id="{shared_ancestor_index["entry_id"]}">'
            f'<a href="#{shared_ancestor_profile["profile_id"]}">'
            f"Synthetic, {AC05_SHARED_ANCESTOR}</a></li>"
        ) in html
        ac06_sibling_profile = ac06_sibling_profiles[0]
        assert html.count(
            f'<section class="person-profile" id="{ac06_sibling_profile["profile_id"]}">'
        ) == 1
        assert (
            f'<li id="{ac06_sibling_occurrence["occurrence_id"]}">'
            f"<span>Synthetic, {AC06_SIBLING}</span>"
        ) in html
        assert AC06_UNEXPANDED_CHILD not in html
        ac06_sibling_index = ac06_sibling_index_entries[0]
        ac06_sibling_index_html = (
            f'<li id="{ac06_sibling_index["entry_id"]}">'
            f'<a href="#{ac06_sibling_profile["profile_id"]}">'
            f"Synthetic, {AC06_SIBLING}</a></li>"
        )
        assert html.count(ac06_sibling_index_html) == 1
        print(
            "PASS: AC-06 native HTML includes the eligible sibling and unique "
            "profile/index entry, without the sibling's child"
        )
        ac09_family_notice = next(
            notice
            for notice in editorial_book["family_notices"]
            if notice["family_handle"] == foster_family["handle"]
        )
        ac09_notice_match = re.search(
            rf'<article class="family-notice" id="{re.escape(ac09_family_notice["notice_id"])}">'
            r"(.*?)</article>",
            html,
            flags=re.DOTALL,
        )
        assert ac09_notice_match is not None
        ac09_partner_lists = re.findall(
            r'<ul class="family-partners">(.*?)</ul>',
            ac09_notice_match.group(1),
            flags=re.DOTALL,
        )
        ac09_notice_sections = [
            section
            for section in family_sections
            if section["section_id"] in ac09_family_notice["family_section_ids"]
        ]
        assert len(ac09_partner_lists) == len(ac09_notice_sections), (
            ac09_partner_lists,
            ac09_notice_sections,
        )
        ac09_partner_items = [
            re.findall(
                r'<li><a href="#([^"]+)">([^<]+)</a></li>',
                partner_list,
            )
            for partner_list in ac09_partner_lists
        ]
        assert all(len(items) == 1 for items in ac09_partner_items), ac09_partner_items
        ac09_parent_name = next(
            person["name"]
            for person in model["people"]
            if person["handle"] == foster_family["father"]["handle"]
        )
        expected_ac09_partner_occurrences = {
            occurrence_id
            for section in ac09_notice_sections
            for occurrence_id in section["partner_occurrence_ids"]
        }
        assert all(
            len(section["partner_occurrence_ids"]) == 1
            for section in ac09_notice_sections
        )
        assert {
            items[0][0]
            for items in ac09_partner_items
        } == expected_ac09_partner_occurrences
        assert all(
            items[0][1] == ac09_parent_name for items in ac09_partner_items
        )
        print(
            "PASS: AC-09 native HTML family notice lists only the one recorded "
            "parent"
        )
        assert f"Synthetic, {AC07_UNFORCED_SPOUSE}" in html
        assert f"Synthetic, {AC07_FORCED_SPOUSE}" in html
        assert html.count('<section class="person-profile"') == len(
            editorial_book["profiles"]
        )
        ac07_forced_profile = ac07_forced_profiles[0]
        assert html.count(
            f'<section class="person-profile" id="{ac07_forced_profile["profile_id"]}">'
        ) == 1
        for family_id, spouse_marker in (
            ("F0009", AC07_UNFORCED_SPOUSE),
            ("F0010", AC07_FORCED_SPOUSE),
        ):
            family = next(
                family
                for family in model["families"].values()
                if family["gramps_id"] == family_id
            )
            notice = next(
                notice
                for notice in editorial_book["family_notices"]
                if notice["family_handle"] == family["handle"]
            )
            notice_match = re.search(
                rf'<article class="family-notice" id="{re.escape(notice["notice_id"])}">'
                r"(.*?)</article>",
                html,
                flags=re.DOTALL,
            )
            assert notice_match is not None
            assert f"Synthetic, {spouse_marker}" in notice_match.group(1)
        print(
            "PASS: AC-07 native HTML family notices mention each spouse and only "
            "BOOK_PROFILE=YES creates a profile"
        )
        ac08_profile = ac08_profiles[0]
        ac08_profile_html = (
            f'<section class="person-profile" id="{ac08_profile["profile_id"]}">'
        )
        assert html.count(ac08_profile_html) == 1
        ac08_profile_start = html.index(ac08_profile_html)
        ac08_profile_end = html.index("</section>", ac08_profile_start)
        assert AC08_FAMILY_EVENT_DETAIL not in html[
            ac08_profile_start:ac08_profile_end
        ]
        ac08_notice_match = re.search(
            rf'<article class="family-notice" id="{re.escape(ac08_family_notice["notice_id"])}">'
            r"(.*?)</article>",
            html,
            flags=re.DOTALL,
        )
        assert ac08_notice_match is not None
        assert f"Synthetic, {AC08_FAMILY_EVENT_PARTNER}" in ac08_notice_match.group(1)
        assert ac08_notice_match.group(1).count(AC08_FAMILY_EVENT_DETAIL) == 1
        assert html.count(AC08_FAMILY_EVENT_DETAIL) == 1
        print(
            "PASS: AC-08 native HTML creates one spouse profile and renders the "
            "Marriage detail only in its family notice"
        )
        rendered_note_nodes = [
            (target, body)
            for target, body in re.findall(
                r'<div id="([^"]+)" class="note-text">(.*?)</div>',
                html,
                flags=re.DOTALL,
            )
            if "Note de publication native en " in body
        ]
        assert len(rendered_note_nodes) == 2, rendered_note_nodes
        assert len({target for target, _ in rendered_note_nodes}) == 2, rendered_note_nodes
        assert all("<strong>gras</strong>" in body for _, body in rendered_note_nodes)
        assert all("<em>italique</em>" in body for _, body in rendered_note_nodes)
        print(
            "PASS: AC-14 native HTML uses one appendix entry per Citation, "
            "reuses its number, and keeps both references on the two-citation fact"
        )
        print(
            "PASS: AC-18 native HTML keeps the uncited Marriage visible and renders "
            "source details without inventing a repository"
        )
        print(
            "PASS: AC-10 native BOOK_PUBLICATION note shared by person and family, "
            "with distinct HTML targets and native bold/italic styles"
        )
        # The synthetic media file is read through Gramps' database media path,
        # cropped using the recorded rectangle, and installed beside the JSON.
        artifact = next(
            item for item in model["media_artifacts"] if item["media_handle"] == media["handle"]
        )
        assert artifact["action"] == "reproduce", (artifact, model["diagnostics"])
        assert artifact["asset_path"].startswith("family_media/")
        with Image.open(work / artifact["asset_path"]) as derivative:
            assert derivative.format == "PNG"
            assert derivative.size == (8, 6)
        assert not any(
            diagnostic["code"] == "MEDIA_DERIVATIVE_FAILED"
            and diagnostic["handle"] == media["handle"]
            for diagnostic in model["diagnostics"]
        )
        assert model["privacy"]["contains_private_data"] is False
        print(
            "PASS: native Gramps XML, synthetic media crop, rich snapshot, sources and repositories"
        )

        single = work / "single.json"
        log = report("F0002", single)
        assert "two known partners" in log, log
        assert not single.exists()
        print("PASS: incomplete reference couple rejected without output (AC-02)")

        original = output.read_bytes()
        for family in ("F9999", "", "F0002"):
            log = report(family, output, overwrite=True)
            assert "Book generation failed" in log, log
            assert output.read_bytes() == original
        log = report("F0001", output)
        assert "Output already exists" in log, log
        assert output.read_bytes() == original
        print("PASS: invalid/empty selection and existing-output protection")

        media_output = work / "family_media"
        stale_asset = media_output / "stale.txt"
        stale_asset.write_text("old media output", encoding="utf-8")
        output.write_text("previous export", encoding="utf-8")
        log = report("F0001", output, overwrite=True)
        assert json.loads(output.read_text())["reference_family"]["gramps_id"] == "F0001", log
        assert media_output.is_dir()
        assert not stale_asset.exists()
        assert len(list(media_output.glob("*.png"))) == 2
        print("PASS: explicit replacement of JSON and media assets")

        for destination in (None, work / "missing" / "file.json", work / "not-json.pdf"):
            log = report("F0001", destination)
            assert "Book generation failed" in log, log
            if destination is not None:
                assert not destination.exists()
        assert not list(work.glob(".book-model-*"))
        assert not list(work.glob(".book-media-stage-*"))
        print("PASS: missing, unavailable and invalid destinations; temporary-file cleanup")

        if pdf_output is not None:
            destination = Path(pdf_output).expanduser()
            if not destination.is_absolute():
                destination = Path.cwd() / destination
            if destination.exists():
                raise FileExistsError(
                    f"Refusing to validate a pre-existing PDF as fresh output: {destination}"
                )
            destination.parent.mkdir(parents=True, exist_ok=True)
            log = report("F0001", destination, output_format="pdf", book_language="fr")
            if not destination.is_file() or not destination.read_bytes().startswith(b"%PDF-"):
                raise AssertionError(log or "Gramps did not produce a valid PDF output file.")
            rendered_pdf_text = _pdf_text(destination)
            assert any(label in rendered_pdf_text for label in ("Adopted", "Adopté"))
            assert "(None)" not in rendered_pdf_text
            assert rendered_pdf_text.count(AC18_UNCITED_EVENT) == 1
            assert rendered_pdf_text.count(AC18_SOURCE_TITLE) == 1
            assert rendered_pdf_text.count(AC18_SOURCE_AUTHOR) == 1
            assert rendered_pdf_text.count(AC18_SOURCE_PUBLICATION) == 1
            assert rendered_pdf_text.count(AC18_CITATION_PAGE) == 1
            for marker in F0_EDITORIAL_ROLE_TEXT.values():
                assert rendered_pdf_text.count(marker) == 1, marker
            assert all(
                marker not in rendered_pdf_text
                for marker in F0_EDITORIAL_INVALID_TEXT.values()
            )
            assert AC03_OTHER_PARTNER in rendered_pdf_text
            assert AC03_OTHER_CHILD in rendered_pdf_text
            pdf_ancestry = _pdf_section_between_headings(
                rendered_pdf_text, "Ascendance", "Descendance"
            )
            pdf_shared_ancestor_branches = _pdf_section_between_headings(
                pdf_ancestry, "Génération -1", "Génération -2"
            )
            assert pdf_shared_ancestor_branches.count(
                f"Synthetic, {AC06_SIBLING}"
            ) == 1
            assert pdf_shared_ancestor_branches.count(
                f"Synthetic, {AC05_SHARED_ANCESTOR}"
            ) == 2
            for partner_marker in (AC05_PARENT_PARTNER, AC05_OTHER_PARTNER):
                assert re.search(
                    rf"Synthetic, {re.escape(AC05_SHARED_ANCESTOR)}\s+"
                    rf"— Synthetic, {re.escape(partner_marker)}",
                    pdf_shared_ancestor_branches,
                )
            pdf_profiles = _pdf_section_between_headings(
                rendered_pdf_text, "Fiches individuelles", "Annexe documentaire"
            )
            pdf_family_connections = _pdf_section_between_headings(
                rendered_pdf_text, "Liens familiaux", "Notices familiales"
            )
            pdf_family_notices = _pdf_section_between_headings(
                rendered_pdf_text, "Notices familiales", "Fiches individuelles"
            )
            pdf_ancestry_generation_zero = _pdf_section_between_headings(
                pdf_ancestry, "Génération 0", "Génération -1"
            )
            pdf_descent = _pdf_section_between_headings(
                rendered_pdf_text, "Descendance", "Liens familiaux"
            )
            pdf_descent_generation_zero = _pdf_section_between_headings(
                pdf_descent, "Génération 0", "Génération 1"
            )
            central_partner_names = [
                html_people_by_handle[handle]["name"]
                for handle in central_partner_handles
            ]
            for generation_text in (
                pdf_ancestry_generation_zero,
                pdf_descent_generation_zero,
            ):
                occurrence_lines = [
                    line.strip()
                    for line in generation_text.splitlines()
                    if line.strip().startswith("— ")
                ]
                assert occurrence_lines[:2] == [
                    f"— {name}" for name in central_partner_names
                ], occurrence_lines
            central_pdf_family_entries = [
                line.strip()
                for line in pdf_family_connections.splitlines()
                if all(name in line for name in central_partner_names)
                and "(ascendance, génération 0)" in line
            ]
            assert len(central_pdf_family_entries) == 1, central_pdf_family_entries
            print(
                "PASS: AC-01 native PDF opens ancestry and descent generation zero "
                "with the central pair and renders their F0 connection"
            )
            ac09_pdf_parent_entries = [
                line.strip()
                for line in pdf_family_connections.splitlines()
                if "Isolé, Parent" in line
                and "(ascendance, génération -1)" in line
            ]
            assert len(ac09_pdf_parent_entries) == 1, ac09_pdf_parent_entries
            assert ac09_pdf_parent_entries[0].startswith("— Isolé, Parent ")
            assert " et " not in ac09_pdf_parent_entries[0]
            assert pdf_profiles.count(f"Synthetic, {AC06_SIBLING}") == 1
            assert f"Synthetic, {AC07_UNFORCED_SPOUSE}" not in pdf_profiles
            assert pdf_profiles.count(f"Synthetic, {AC07_FORCED_SPOUSE}") == 1
            assert pdf_profiles.count(
                f"Synthetic, {AC08_FAMILY_EVENT_PARTNER}"
            ) == 1
            assert AC08_FAMILY_EVENT_DETAIL not in pdf_profiles
            assert pdf_family_notices.count(AC08_FAMILY_EVENT_DETAIL) == 1
            assert f"Synthetic, {AC08_FAMILY_EVENT_PARTNER}" in pdf_family_notices
            assert rendered_pdf_text.count(AC08_FAMILY_EVENT_DETAIL) == 1
            assert pdf_profiles.count(
                f"Synthetic, {AC05_SHARED_ANCESTOR}"
            ) == 1
            ac07_reference_parent_name = next(
                person["name"]
                for person in model["people"]
                if person["handle"] == reference_family["father"]["handle"]
            )
            ac07_pdf_union_entries = {}
            for spouse_marker in (AC07_UNFORCED_SPOUSE, AC07_FORCED_SPOUSE):
                entries = [
                    line.strip()
                    for line in pdf_family_connections.splitlines()
                    if spouse_marker in line
                    and re.search(r"\(descendance, génération 0\)", line)
                ]
                assert len(entries) == 1, (spouse_marker, entries)
                assert ac07_reference_parent_name in entries[0], entries[0]
                ac07_pdf_union_entries[spouse_marker] = entries[0]
            assert len(set(ac07_pdf_union_entries.values())) == 2
            assert f"Synthetic, {AC07_UNFORCED_SPOUSE}" in rendered_pdf_text
            assert f"Synthetic, {AC07_FORCED_SPOUSE}" in rendered_pdf_text
            pdf_person_index = _pdf_section_between_headings(
                rendered_pdf_text, "Index des personnes"
            )
            assert pdf_person_index.count(
                f"Synthetic, {AC05_SHARED_ANCESTOR}"
            ) == 1
            assert pdf_person_index.count(f"Synthetic, {AC06_SIBLING}") == 1
            assert AC06_UNEXPANDED_CHILD not in rendered_pdf_text
            print(
                "PASS: AC-06 native PDF includes the eligible sibling and unique "
                "profile/index entry, without the sibling's child"
            )
            print(
                "PASS: AC-07 native PDF family connections mention each spouse; "
                "only BOOK_PROFILE=YES receives one profile"
            )
            print(
                "PASS: AC-08 native PDF creates one profile for the spouse; "
                "Marriage detail appears only in family notices"
            )
            print(
                "PASS: AC-09 native PDF family connection contains only the "
                "recorded single parent"
            )
            assert rendered_pdf_text.index(
                F0_EDITORIAL_ROLE_TEXT["BOOK_DEDICATION"]
            ) < rendered_pdf_text.index(
                F0_EDITORIAL_ROLE_TEXT["BOOK_INTRODUCTION"]
            )
            ac18_pdf_entry = _pdf_citation_entry(
                rendered_pdf_text, AC18_CITATION_PAGE
            )
            for marker in (
                AC18_SOURCE_TITLE,
                AC18_SOURCE_AUTHOR,
                AC18_SOURCE_PUBLICATION,
                AC18_CITATION_PAGE,
            ):
                assert marker in ac18_pdf_entry
            assert all(
                marker not in ac18_pdf_entry
                for marker in ("Dépôt municipal fictif", "R0001", "3 E 12")
            )
            assert rendered_pdf_text.count(AC14_SHARED_PAGE) == 1
            assert rendered_pdf_text.count(AC14_SECOND_PAGE) == 1
            shared_pdf_number = _pdf_citation_number(
                rendered_pdf_text, AC14_SHARED_PAGE
            )
            second_pdf_number = _pdf_citation_number(
                rendered_pdf_text, AC14_SECOND_PAGE
            )
            assert shared_pdf_number != second_pdf_number
            profile_sources_sections = list(re.finditer(
                r"(?m)^Sources\s*\n((?:[ \t]*— \[\d+\].*\n)+)",
                rendered_pdf_text,
            ))
            assert profile_sources_sections
            profile_sources = profile_sources_sections[-1]
            profile_source_numbers = {
                int(number)
                for number in re.findall(r"— \[(\d+)\]", profile_sources.group(1))
            }
            assert {shared_pdf_number, second_pdf_number} <= profile_source_numbers
            shared_position = rendered_pdf_text.index(AC14_SHARED_PAGE)
            second_position = rendered_pdf_text.index(AC14_SECOND_PAGE)
            assert shared_position < second_position
            shared_pdf_entry = rendered_pdf_text[shared_position:second_position]
            assert re.search(r"événement\s*:\s*Naissance", shared_pdf_entry)
            assert re.search(r"événement\s*:\s*Profession", shared_pdf_entry)
            print(f"PASS: native Gramps PDF written to {destination}")
            print(
                "PASS: AC-14 PDF maps both citations to distinct numbers, "
                "shows both on the two-citation profile, and reuses the shared entry"
            )
            print(
                "PASS: AC-18 PDF keeps the uncited Marriage visible and renders "
                "source details without inventing a repository"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gramps", default="gramps", help="Gramps 6 executable")
    parser.add_argument(
        "--pdf-output",
        type=Path,
        help="Also compile the native fixture as a PDF at this destination.",
    )
    parser.add_argument(
        "--lualatex",
        type=Path,
        help="Optional LuaLaTeX executable; its directory is prepended to PATH.",
    )
    parser.add_argument(
        "--addon-archive",
        type=Path,
        help="Optional add-on archive; defaults to the built project archive.",
    )
    arguments = parser.parse_args()
    verify(
        arguments.gramps,
        pdf_output=arguments.pdf_output,
        lualatex=arguments.lualatex,
        addon_archive=arguments.addon_archive,
    )
