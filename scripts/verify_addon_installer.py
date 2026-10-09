"""Exercise Gramps' native archive installer in a disposable profile.

Run with the Python interpreter that has Gramps installed. This checks the
backend used by Plugin Manager; it does not qualify the graphical interaction.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import tarfile
import tempfile
from pathlib import Path


def _archive_files(path: Path) -> dict[str, bytes]:
    with tarfile.open(path) as archive:
        files = {}
        for member in archive.getmembers():
            name = Path(member.name)
            if (
                not member.isfile()
                or name.is_absolute()
                or ".." in name.parts
                or name.parts[0] != "GrampsFancyBook"
            ):
                raise AssertionError(f"Unexpected archive member: {member.name}")
            if member.name in files:
                raise AssertionError(f"Duplicate archive member: {member.name}")
            payload = archive.extractfile(member)
            assert payload is not None
            files[member.name] = payload.read()
        if "GrampsFancyBook/GrampsFancyBook.gpr.py" not in files:
            raise AssertionError("Archive has no Gramps registration file.")
        return files


def _check_installed(plugins: Path, expected: dict[str, bytes]) -> None:
    actual = {
        path.relative_to(plugins).as_posix(): path.read_bytes()
        for path in (plugins / "GrampsFancyBook").rglob("*")
        if path.is_file()
    }
    if actual != expected:
        raise AssertionError("Installed files do not match the archive exactly.")


def verify(archive_path: Path) -> dict[str, object]:
    """Install, reinstall and reject an incompatible target using native Gramps."""
    if any(name == "gramps" or name.startswith("gramps.") for name in sys.modules):
        raise RuntimeError("Run in a fresh Python process before importing Gramps.")
    expected = _archive_files(archive_path)
    previous = {key: os.environ.get(key) for key in ("GRAMPSHOME", "XDG_CACHE_HOME")}
    with tempfile.TemporaryDirectory(prefix="gfb-native-installer-") as directory:
        work = Path(directory)
        os.environ["GRAMPSHOME"] = str(work)
        os.environ["XDG_CACHE_HOME"] = str(work / "cache")
        try:
            # Gramps computes USER_PLUGINS at import time: set isolation first.
            from gramps.gen.const import USER_PLUGINS, VERSION_TUPLE
            from gramps.gen.plug.utils import load_addon_file

            plugins = Path(USER_PLUGINS)
            if not plugins.resolve().is_relative_to(work.resolve()):
                raise AssertionError("Gramps did not select the disposable profile.")
            plugins.mkdir(parents=True, exist_ok=True)
            messages: list[str] = []
            if not load_addon_file(str(archive_path.resolve()), messages.append):
                raise AssertionError("Native installation refused: " + "".join(messages))
            _check_installed(plugins, expected)

            # Reinstallation must restore an existing file, not merely accept
            # the registration and leave the previous bytes untouched.
            manifest = plugins / "GrampsFancyBook" / "MANIFEST"
            manifest.write_bytes(b"deliberately changed in the disposable profile\n")
            if not load_addon_file(str(archive_path.resolve()), messages.append):
                raise AssertionError("Native same-version reinstallation refused.")
            _check_installed(plugins, expected)

            incompatible = work / "incompatible.addon.tgz"
            with tarfile.open(incompatible, "w:gz") as archive:
                for name, payload in expected.items():
                    if name.endswith(".gpr.py"):
                        target = f'gramps_target_version="{VERSION_TUPLE[0]}.{VERSION_TUPLE[1]}"'
                        text = payload.decode("utf-8")
                        if text.count(target) != 1:
                            raise AssertionError("Expected one native Gramps target.")
                        payload = text.replace(target, 'gramps_target_version="99.0"').encode()
                    member = tarfile.TarInfo(name)
                    member.size = len(payload)
                    archive.addfile(member, io.BytesIO(payload))
            if load_addon_file(str(incompatible), messages.append):
                raise AssertionError("Native installer accepted an incompatible target.")
            _check_installed(plugins, expected)
            return {
                "gramps_version": ".".join(map(str, VERSION_TUPLE)),
                "python_version": sys.version,
                "archive_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
                "archive_members": len(expected),
                "installation_matches_archive": True,
                "same_version_reinstallation_restores_files": True,
                "incompatible_target_rejected_without_changes": True,
                "scope": "native installer backend; GUI interaction not assessed",
            }
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--addon-archive", type=Path, required=True)
    parser.add_argument("--output-record", type=Path)
    arguments = parser.parse_args()
    record = verify(arguments.addon_archive)
    text = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    if arguments.output_record is not None:
        arguments.output_record.write_text(text, encoding="utf-8")
    print(text)
