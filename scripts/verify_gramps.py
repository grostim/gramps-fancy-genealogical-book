"""Exercise the built add-on with real Gramps and an isolated, synthetic database.

Usage: python scripts/verify_gramps.py --gramps /path/to/gramps
"""

from __future__ import annotations

import argparse
import copy
import gzip
import json
import os
import subprocess
import tarfile
import tempfile
import uuid
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ID = "gramps_fancy_genealogical_book"


def _qualified_name(root: ET.Element, name: str) -> str:
    namespace = root.tag[1:].split("}", 1)[0] if root.tag.startswith("{") else ""
    return f"{{{namespace}}}{name}" if namespace else name


def _children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in element if child.tag.rsplit("}", 1)[-1] == name]


def _text_content(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join(part.strip() for part in element.itertext() if part.strip())


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
            {"val": "1910-01-01"},
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
    media = next(
        (
            item
            for item in _children(objects, "object")
            if item.get("id") == "M0001"
        ),
        None,
    )
    if person is None or media is None:
        raise AssertionError("Gramps XML export is missing fixture person I0001 or media M0001.")

    _add_same_fact_birth_version(root, events, person)

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
    ET.SubElement(
        note,
        _qualified_name(root, "text"),
    ).text = "Note de publication du fixture natif."
    ET.SubElement(note, _qualified_name(root, "tagref"), {"hlink": tag_handle})
    ET.SubElement(person, _qualified_name(root, "noteref"), {"hlink": note_handle})

    updated = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    fixture.write_bytes(gzip.compress(updated, mtime=0) if compressed else updated)
    return fixture


def verify(executable: str) -> None:
    with tempfile.TemporaryDirectory(prefix="fancy-book-integration-") as directory:
        work = Path(directory)
        env = os.environ.copy()
        env.update(GRAMPSHOME=str(work), XDG_CACHE_HOME=str(work / "cache"), LANGUAGE="en")
        # Import only the installed add-on, never a development PYTHONPATH.
        env.pop("PYTHONPATH", None)
        plugins = work / "gramps" / "gramps60" / "plugins"
        plugins.mkdir(parents=True)
        with tarfile.open(ROOT / "gramps60/download/GrampsFancyBook.addon.tgz") as archive:
            archive.extractall(plugins, filter="data")

        _create_media_fixture(work)
        native_fixture = _native_fixture(executable, env, work)

        def report(family: str, output: Path | None, *, overwrite=False) -> str:
            options = f"name={PLUGIN_ID},reference_family={family}"
            if output is not None:
                options += f",destination={output}"
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
        assert {event["date"]["ymd"][0] for event in birth_fact_events} == {1900, 1910}
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
        assert [person["gramps_id"] for person in model["people"]] == ["I0001", "I0002", "I0003"]
        assert "Émile" in model["people"][0]["name"]
        assert model["reference_family"]["handle"] != "F0001"
        assert model["metadata"]["BOOK_SCHEMA_VERSION"] == "0.8"
        assert model["reference_family"]["handle"] in model["families"]
        assert model["reference_family"]["child_relationships"][0]["father_relation"] == "Birth"
        assert model["reference_family"]["child_relationships"][0]["mother_relation"] == "Birth"
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
        assert len(model["citations"]) == 3
        assert len(model["sources"]) == 1
        source = next(iter(model["sources"].values()))
        assert len(source["repository_refs"]) == 1
        assert len(model["repositories"]) == 1
        assert len(model["media"]) == 1
        media = next(iter(model["media"].values()))
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
        assert publishable_note["text"] == "Note de publication du fixture natif."
        assert any(
            model["tags"][handle]["name"] == "BOOK_PUBLICATION"
            for handle in publishable_note["links"]["tag_handles"]
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
            assert "Book model export failed" in log, log
            assert output.read_bytes() == original
        log = report("F0001", output)
        assert "Output file or media folder already exists" in log, log
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
        assert len(list(media_output.glob("*.png"))) == 1
        print("PASS: explicit replacement of JSON and media assets")

        for destination in (None, work / "missing" / "file.json", work / "not-json.pdf"):
            log = report("F0001", destination)
            assert "Book model export failed" in log, log
            if destination is not None:
                assert not destination.exists()
        assert not list(work.glob(".book-model-*"))
        assert not list(work.glob(".book-media-stage-*"))
        print("PASS: missing, unavailable and invalid destinations; temporary-file cleanup")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gramps", default="gramps", help="Gramps 6 executable")
    verify(parser.parse_args().gramps)
