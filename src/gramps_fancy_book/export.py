"""Publish the intermediate model, consistency report and media assets."""

import contextlib
import json
import os
import shutil
import tempfile
from collections.abc import Iterator, Mapping
from pathlib import Path

from .domain import BookModel


@contextlib.contextmanager
def media_asset_staging_directory(
    destination: str | Path,
    *,
    overwrite: bool = False,
    include_consistency_report: bool = False,
) -> Iterator[Path]:
    """Create a same-filesystem staging directory for an export's PNG assets."""
    output = _model_json_path(destination)
    if not output.parent.is_dir():
        raise FileNotFoundError(f"Output directory does not exist: {output.parent}")
    if output.is_dir():
        raise ValueError("The JSON destination cannot be a directory.")
    report_output = consistency_report_path(output) if include_consistency_report else None
    if not overwrite:
        if _path_exists(output):
            raise FileExistsError(output)
        if report_output is not None and _path_exists(report_output):
            raise FileExistsError(report_output)
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
    consistency_report: Mapping[str, object] | None = None,
) -> Path:
    if not str(destination).strip():
        raise ValueError("Select a JSON output file.")
    output = _model_json_path(destination)
    if not output.parent.is_dir():
        raise FileNotFoundError(f"Output directory does not exist: {output.parent}")
    if output.is_dir():
        raise ValueError("The JSON destination cannot be a directory.")
    report_output = consistency_report_path(output) if consistency_report is not None else None
    if report_output is not None and report_output.is_dir():
        raise ValueError("The consistency report destination cannot be a directory.")
    if not overwrite:
        if _path_exists(output):
            raise FileExistsError(output)
        if report_output is not None and _path_exists(report_output):
            raise FileExistsError(report_output)

    stage = Path(media_asset_staging) if media_asset_staging is not None else None
    if stage is None and any(item.asset_path for item in model.media_artifacts):
        raise ValueError("Media assets need a staging directory before JSON export.")
    if stage is not None:
        _validate_media_manifest(
            model, stage, media_asset_directory_name(output), output.parent
        )

    payload = json.dumps(model.to_dict(), ensure_ascii=False, indent=2) + "\n"
    report_payload = (
        json.dumps(consistency_report, ensure_ascii=False, indent=2) + "\n"
        if consistency_report is not None
        else None
    )
    temporary_model = None
    temporary_report = None
    media_backup = None
    assets_installed = False
    file_backups: dict[Path, Path] = {}
    installed_files: set[Path] = set()
    asset_directory = output.with_name(media_asset_directory_name(output))
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=output.parent, prefix=".book-model-", delete=False
        ) as stream:
            temporary_model = Path(stream.name)
            stream.write(payload)
        if report_payload is not None:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=output.parent,
                prefix=".book-consistency-",
                delete=False,
            ) as stream:
                temporary_report = Path(stream.name)
                stream.write(report_payload)

        if overwrite:
            for target in (report_output, output):
                if target is not None and _path_exists(target):
                    if target.is_dir():
                        raise ValueError(f"Output destination cannot be a directory: {target}")
                    file_backups[target] = _move_to_backup(target)

        if stage is not None:
            media_backup, assets_installed = _install_media_assets(
                stage, asset_directory, overwrite=overwrite
            )

        # Install the report first; the model JSON remains the bundle's last commit marker.
        if temporary_report is not None and report_output is not None:
            _install_file(temporary_report, report_output, overwrite)
            installed_files.add(report_output)
        _install_file(temporary_model, output, overwrite)
        installed_files.add(output)
    except Exception:
        for target in installed_files:
            _remove_path(target)
        for target, backup in file_backups.items():
            if _path_exists(backup):
                os.replace(backup, target)
        if assets_installed:
            _remove_path(asset_directory)
        if media_backup is not None and _path_exists(media_backup):
            os.replace(media_backup, asset_directory)
        raise
    else:
        for backup in file_backups.values():
            _remove_path(backup)
        if media_backup is not None:
            _remove_path(media_backup)
    finally:
        if temporary_model is not None:
            temporary_model.unlink(missing_ok=True)
        if temporary_report is not None:
            temporary_report.unlink(missing_ok=True)
    return output


def consistency_report_path(destination: str | Path) -> Path:
    """Return the companion control-report path for a model JSON destination."""
    output = _model_json_path(destination)
    return output.with_name(f"{output.stem}_consistency.json")


def _path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _move_to_backup(path: Path) -> Path:
    with tempfile.NamedTemporaryFile(
        dir=path.parent, prefix=f".{path.name}-backup-", delete=False
    ) as stream:
        backup = Path(stream.name)
    backup.unlink()
    os.replace(path, backup)
    return backup


def _install_file(temporary: Path, destination: Path, overwrite: bool) -> None:
    if overwrite:
        os.replace(temporary, destination)
    else:
        # Linking is atomic and fails if another process created the destination.
        os.link(temporary, destination)


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
