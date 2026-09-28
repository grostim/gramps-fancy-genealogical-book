"""Write a self-contained static HTML book archive."""

from __future__ import annotations

import os
import re
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from ..domain import BookModel
from .html import render_html

_CACHE_KEY = re.compile(r"^[0-9a-f]{64}$")


def write_html_archive(
    model: BookModel,
    destination: str | Path,
    *,
    media_asset_directory: str | Path | None = None,
    overwrite: bool = False,
) -> Path:
    """Write ``index.html`` and its approved PNG derivatives to a ZIP archive.

    ``media_asset_directory`` must be the staging directory produced by
    ``prepare_editorial_media`` or the installed model media directory. Original
    Gramps media paths are never read or copied by this function.
    """
    if not str(destination).strip():
        raise ValueError("Select an HTML ZIP output file.")
    output = Path(destination)
    if output.suffix.casefold() != ".zip":
        raise ValueError("The HTML archive destination must end in .zip.")
    if not output.parent.is_dir():
        raise FileNotFoundError(f"Output directory does not exist: {output.parent}")
    if output.is_dir():
        raise ValueError("The HTML archive destination cannot be a directory.")
    if output.is_symlink():
        raise ValueError("The HTML archive destination cannot be a symbolic link.")
    if (output.exists() or output.is_symlink()) and not overwrite:
        raise FileExistsError(output)

    assets = _media_assets(model, media_asset_directory)
    html = render_html(model, include_media=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=output.parent,
            prefix=".book-html-",
            suffix=".zip",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
        with zipfile.ZipFile(
            temporary,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            _write_entry(archive, "index.html", html.encode("utf-8"))
            for name, content in sorted(assets.items()):
                _write_entry(archive, name, content)
        if overwrite:
            os.replace(temporary, output)
        else:
            os.link(temporary, output)
            temporary.unlink()
    except FileExistsError:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise
    except Exception:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise
    return output


def _media_assets(
    model: BookModel,
    media_asset_directory: str | Path | None,
) -> dict[str, bytes]:
    reproduced = [
        artifact
        for artifact in model.media_artifacts
        if artifact.action == "reproduce"
    ]
    if not reproduced:
        return {}
    if media_asset_directory is None:
        raise ValueError("A media asset directory is required for this book.")
    root = Path(media_asset_directory)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("The media asset directory must be an existing real directory.")
    root = root.resolve(strict=True)

    assets = {}
    for artifact in reproduced:
        cache_key = artifact.cache_key
        asset_path = artifact.asset_path
        if (
            not isinstance(cache_key, str)
            or _CACHE_KEY.fullmatch(cache_key) is None
            or not isinstance(asset_path, str)
        ):
            raise ValueError("A reproduced media artifact has an invalid asset path.")
        relative = PurePosixPath(asset_path)
        if (
            relative.is_absolute()
            or len(relative.parts) != 2
            or relative.parts[0] in {".", ".."}
            or relative.parts[1] != f"{cache_key}.png"
            or any(char in asset_path for char in "\\{}%#\n\r\0")
        ):
            raise ValueError("A reproduced media artifact has an unsafe asset path.")
        source = root / f"{cache_key}.png"
        if source.is_symlink() or not source.is_file():
            raise FileNotFoundError(f"Required media asset is missing: {cache_key}.png")
        if source.resolve(strict=True).parent != root:
            raise ValueError("A media asset resolves outside its asset directory.")
        assets.setdefault(f"media/{cache_key}.png", source.read_bytes())
    return assets


def _write_entry(archive: zipfile.ZipFile, name: str, content: bytes) -> None:
    entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    entry.compress_type = zipfile.ZIP_DEFLATED
    entry.external_attr = 0o100644 << 16
    entry.create_system = 3
    archive.writestr(entry, content)
