"""Build a deterministic Gramps 6 archive from explicitly selected project files."""

from __future__ import annotations

import gzip
import io
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "gramps60" / "download" / "GrampsFancyBook.addon.tgz"


def _compile_translations(plugin: Path, build_directory: Path) -> dict[str, Path]:
    """Compile addon PO files into the Gramps message-catalog layout."""
    sources = sorted((plugin / "po").glob("*-local.po"))
    if not sources:
        return {}

    msgfmt = shutil.which("msgfmt")
    if msgfmt is None:
        raise RuntimeError(
            "GNU gettext's msgfmt is required to build the translated add-on. "
            "Install gettext and make msgfmt available on PATH."
        )

    compiled: dict[str, Path] = {}
    for source in sources:
        language = source.name.removesuffix("-local.po")
        if not language:
            raise ValueError(f"Invalid translation catalog filename: {source.name}")

        relative_path = Path("locale") / language / "LC_MESSAGES" / "addon.mo"
        destination = build_directory / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                msgfmt,
                "--check",
                "--check-format",
                "--output-file",
                str(destination),
                str(source),
            ],
            check=True,
        )
        compiled[relative_path.as_posix()] = destination
    return compiled


def build_addon(destination: Path = ARCHIVE) -> Path:
    plugin = ROOT / "gramps60" / "GrampsFancyBook"
    package = ROOT / "src" / "gramps_fancy_book"

    # Build catalogs in temporary storage so generated .mo files stay out of Git.
    with tempfile.TemporaryDirectory(prefix="gramps-fancy-book-build-") as temporary:
        files = {path.name: path for path in plugin.glob("*.py")}
        files["MANIFEST"] = plugin / "MANIFEST"
        files.update(
            {
                "gramps_fancy_book/" + path.relative_to(package).as_posix(): path
                for path in package.rglob("*.py")
            }
        )
        files.update(_compile_translations(plugin, Path(temporary)))

        # Runtime caches, local trees, exports and development tools are never bundled.
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as raw:
            with gzip.GzipFile(fileobj=raw, filename="", mode="wb", mtime=0) as compressed:
                with tarfile.open(
                    fileobj=compressed,
                    mode="w",
                    format=tarfile.USTAR_FORMAT,
                ) as tar:
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
