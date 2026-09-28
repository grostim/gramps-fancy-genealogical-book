"""Exercise the built add-on with real Gramps and an isolated, synthetic database.

Usage: python scripts/verify_gramps.py --gramps /path/to/gramps
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ID = "gramps_fancy_genealogical_book"


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
                    str(ROOT / "tests/fixtures/reference-family.ged"),
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
        assert model["reference_family"]["gramps_id"] == "F0001"
        assert [person["gramps_id"] for person in model["people"]] == ["I0001", "I0002", "I0003"]
        assert "Émile" in model["people"][0]["name"]
        assert model["reference_family"]["handle"] != "F0001"
        assert model["metadata"]["BOOK_SCHEMA_VERSION"] == "0.7"
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
        assert media["path"] == "media/portrait.jpg"
        assert "portrait" in media["description"].lower()
        assert model["people"][0]["links"]["media"][0]["media_handle"] == media["handle"]
        # The GEDCOM references a portrait file not shipped with this fixture.
        # Its recoverable derivative warning is expected; unrelated diagnostics are not.
        assert all(
            diagnostic["code"] == "MEDIA_DERIVATIVE_FAILED"
            and diagnostic["object_type"] == "media"
            and diagnostic["handle"] == media["handle"]
            for diagnostic in model["diagnostics"]
        )
        assert model["privacy"]["contains_private_data"] is False
        print("PASS: installed add-on, rich Gramps snapshot, uncertain dates, sources and repositories")

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
        assert "Output file already exists" in log, log
        assert output.read_bytes() == original
        print("PASS: invalid/empty selection and existing-output protection")

        output.write_text("previous export", encoding="utf-8")
        log = report("F0001", output, overwrite=True)
        assert json.loads(output.read_text())["reference_family"]["gramps_id"] == "F0001", log
        print("PASS: explicit replacement")

        for destination in (None, work / "missing" / "file.json", work / "not-json.pdf"):
            log = report("F0001", destination)
            assert "Book model export failed" in log, log
            if destination is not None:
                assert not destination.exists()
        assert not list(work.glob(".book-model-*"))
        print("PASS: missing, unavailable and invalid destinations; temporary-file cleanup")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gramps", default="gramps", help="Gramps 6 executable")
    verify(parser.parse_args().gramps)
