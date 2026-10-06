"""Build a deterministic Gramps 6 archive from explicitly selected project files."""

from __future__ import annotations

import gzip
import io
import re
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
        language_pattern = r"[A-Za-z]{2,3}(?:[_-][A-Za-z0-9]{2,8})*(?:@[A-Za-z0-9]+)?"
        if not re.fullmatch(language_pattern, language):
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


def _validate_version_consistency(plugin: Path) -> None:
    """Keep the Python package, Gramps registration, and gettext catalogs aligned."""
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    project_section = re.search(
        r"(?ms)^\[project\][ \t]*\n(?P<section>.*?)(?=^\[|\Z)",
        pyproject,
    )
    version_matches = (
        re.findall(
            r'(?m)^version\s*=\s*["\']([^"\']+)["\']\s*$',
            project_section["section"],
        )
        if project_section
        else []
    )
    if len(version_matches) != 1:
        raise RuntimeError("Expected one project version in pyproject.toml.")
    project_version = version_matches[0]

    registration = (plugin / "GrampsFancyBook.gpr.py").read_text(encoding="utf-8")
    registration_versions = re.findall(
        r'(?m)^\s*version\s*=\s*["\']([^"\']+)["\']\s*,\s*(?:#.*)?$',
        registration,
    )
    if registration_versions != [project_version]:
        raise RuntimeError(
            "Gramps registration version must match pyproject.toml "
            f"({project_version!r}; found {registration_versions!r})."
        )

    catalogs = sorted((plugin / "po").glob("*.po")) + sorted(
        (plugin / "po").glob("*.pot")
    )
    for catalog in catalogs:
        headers = [
            line
            for line in catalog.read_text(encoding="utf-8").splitlines()
            if line.startswith('"Project-Id-Version: ')
        ]
        if len(headers) != 1:
            raise RuntimeError(f"Expected one Project-Id-Version header in {catalog.name}.")
        value = headers[0].removeprefix('"Project-Id-Version: ').removesuffix(r'\n"')
        _, separator, catalog_version = value.rpartition(" ")
        if not separator or catalog_version != project_version:
            raise RuntimeError(
                f"Translation catalog {catalog.name} must use project version "
                f"{project_version!r}; found {catalog_version!r}."
            )


def build_addon(destination: Path = ARCHIVE) -> Path:
    plugin = ROOT / "gramps60" / "GrampsFancyBook"
    package = ROOT / "src" / "gramps_fancy_book"
    _validate_version_consistency(plugin)

    # Build catalogs in temporary storage so generated .mo files stay out of Git.
    with tempfile.TemporaryDirectory(prefix="gramps-fancy-book-build-") as temporary:
        files = {path.name: path for path in plugin.glob("*.py")}
        files["MANIFEST"] = plugin / "MANIFEST"
        files["LICENSE"] = ROOT / "LICENSE"
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
