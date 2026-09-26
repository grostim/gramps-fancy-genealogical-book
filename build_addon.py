#!/usr/bin/env python3
"""Build a Gramps 6 add-on archive from the maintained source package."""

from __future__ import annotations

import shutil
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
PLUGIN_SOURCE = ROOT / "gramps60" / "GrampsFancyBook"
PACKAGE_SOURCE = ROOT / "src" / "gramps_fancy_book"
ARCHIVE = ROOT / "gramps60" / "download" / "GrampsFancyBook.addon.tgz"


def main() -> None:
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        staging = Path(temporary) / "GrampsFancyBook"
        shutil.copytree(PLUGIN_SOURCE, staging)
        shutil.copytree(PACKAGE_SOURCE, staging / "gramps_fancy_book")
        for cache in staging.rglob("__pycache__"):
            shutil.rmtree(cache)
        for bytecode in staging.rglob("*.pyc"):
            bytecode.unlink()
        with tarfile.open(ARCHIVE, "w:gz") as archive:
            archive.add(staging, arcname="GrampsFancyBook")
    print(f"Built {ARCHIVE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
