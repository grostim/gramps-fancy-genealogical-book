"""Publish the intermediate model and its content-addressed media assets."""

import contextlib
import json
import os
import shutil
import tempfile
from collections.abc import Iterator
from pathlib import Path

from .domain import BookModel


@contextlib.contextmanager
def media_asset_staging_directory(
    destination: str | Path, *, overwrite: bool = False
) -> Iterator[Path]:
    """Create a same-filesystem staging directory for an export's PNG assets."""
    output = _model_json_path(destination)
    if not output.parent.is_dir():
        raise FileNotFoundError(f"Output directory does not exist: {output.parent}")
    if output.is_dir():
        raise ValueError("The JSON destination cannot be a directory.")
    if output.exists() and not overwrite:
        raise FileExistsError(output)
    asset_directory = output.with_name(media_asset_directory_name(output))
    if (asset_directory.exists() or asset_directory.is_symlink()) and not overwrite:
        raise FileExistsError(asset_directory)
    with tempfile.TemporaryDirectory(prefix=".book-media-stage-", dir=output.parent) as temporary:
        yield Path(temporary)


def write_model_json(
    model: BookModel,
    destination: str | Path,
    *,
    overwrite: bool = False,
    media_asset_staging: str | Path | None = None,
) -> Path:
    if not str(destination).strip():
        raise ValueError("Select a JSON output file.")
    output = _model_json_path(destination)
    if not output.parent.is_dir():
        raise FileNotFoundError(f"Output directory does not exist: {output.parent}")
    if output.is_dir():
        raise ValueError("The JSON destination cannot be a directory.")
    if output.exists() and not overwrite:
        raise FileExistsError(output)

    stage = Path(media_asset_staging) if media_asset_staging is not None else None
    if stage is None and any(item.asset_path for item in model.media_artifacts):
        raise ValueError("Media assets need a staging directory before JSON export.")
    if stage is not None:
        _validate_media_manifest(
            model, stage, media_asset_directory_name(output), output.parent
        )

    payload = json.dumps(model.to_dict(), ensure_ascii=False, indent=2) + "\n"
    temporary = None
    backup = None
    assets_installed = False
    asset_directory = output.with_name(media_asset_directory_name(output))
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=output.parent, prefix=".book-model-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)

        if stage is not None:
            backup, assets_installed = _install_media_assets(
                stage, asset_directory, overwrite=overwrite
            )
        if overwrite:
            os.replace(temporary, output)
        else:
            # Linking is atomic and fails if another process created the destination.
            os.link(temporary, output)
    except Exception:
        if assets_installed:
            _remove_path(asset_directory)
        if backup is not None and (backup.exists() or backup.is_symlink()):
            os.replace(backup, asset_directory)
        raise
    else:
        if backup is not None:
            _remove_path(backup)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return output


def media_asset_directory_name(destination: str | Path) -> str:
    return f"{_model_json_path(destination).stem}_media"


def _model_json_path(destination: str | Path) -> Path:
    if not str(destination).strip():
        raise ValueError("Select a JSON output file.")
    output = Path(destination).expanduser()
    if output.suffix.lower() != ".json":
        raise ValueError("The output file must use the .json extension.")
    return output


def _validate_media_manifest(
    model: BookModel,
    stage: Path,
    asset_directory_name: str,
    output_parent: Path,
) -> None:
    if not stage.is_dir() or stage.is_symlink():
        raise ValueError("The media asset staging path must be an existing directory.")
    if stage.parent.resolve() != output_parent.resolve():
        raise ValueError("Media assets must be staged beside the JSON output.")
    for artifact in model.media_artifacts:
        if artifact.action != "reproduce":
            continue
        if not artifact.cache_key or not artifact.asset_path:
            raise ValueError("A reproduced media artifact needs a cache key and path.")
        if (
            len(artifact.cache_key) != 64
            or any(char not in "0123456789abcdef" for char in artifact.cache_key)
            or artifact.asset_path != f"{asset_directory_name}/{artifact.cache_key}.png"
            or not (stage / f"{artifact.cache_key}.png").is_file()
        ):
            raise ValueError("A referenced media asset is missing from the staging directory.")


def _install_media_assets(
    stage: Path, asset_directory: Path, *, overwrite: bool
) -> tuple[Path | None, bool]:
    has_assets = any(stage.iterdir())
    if not has_assets and not overwrite:
        if asset_directory.exists() or asset_directory.is_symlink():
            raise FileExistsError(asset_directory)
        return None, False

    backup = None
    if asset_directory.exists() or asset_directory.is_symlink():
        if not overwrite:
            raise FileExistsError(asset_directory)
        backup = Path(
            tempfile.mkdtemp(
                prefix=f".{asset_directory.name}-backup-", dir=asset_directory.parent
            )
        )
        backup.rmdir()
        os.replace(asset_directory, backup)

    if not has_assets:
        return backup, False

    try:
        os.replace(stage, asset_directory)
    except Exception:
        if backup is not None:
            os.replace(backup, asset_directory)
        raise
    return backup, True


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.exists():
        shutil.rmtree(path)
