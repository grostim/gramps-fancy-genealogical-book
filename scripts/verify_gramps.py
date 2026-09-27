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
        print("PASS: installed add-on, family selection, Unicode, Gramps IDs and handles")

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
