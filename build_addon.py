"""Build a deterministic Gramps 6 archive from explicitly selected project files."""

from __future__ import annotations

import gzip
import io
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "gramps60" / "download" / "GrampsFancyBook.addon.tgz"


def build_addon(destination: Path = ARCHIVE) -> Path:
    plugin = ROOT / "gramps60" / "GrampsFancyBook"
    package = ROOT / "src" / "gramps_fancy_book"
    files = {path.name: path for path in plugin.glob("*.py")}
    files["MANIFEST"] = plugin / "MANIFEST"
    files.update(
        {
            "gramps_fancy_book/" + path.relative_to(package).as_posix(): path
            for path in package.rglob("*.py")
        }
    )
    # Runtime caches, local trees, exports and development tools are never bundled.
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, filename="", mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as tar:
                for name, path in sorted(files.items()):
                    payload = path.read_bytes()
                    info = tarfile.TarInfo("GrampsFancyBook/" + name)
                    info.size = len(payload)
                    info.mode = 0o644
                    info.mtime = 0
                    tar.addfile(info, io.BytesIO(payload))
    return destination


if __name__ == "__main__":
    print(f"Built {build_addon()}")
