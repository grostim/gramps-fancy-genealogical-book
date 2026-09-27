"""Publish an intermediate model without exposing a partially written file."""

import json
import os
import tempfile
from pathlib import Path

from .domain import BookModel


def write_model_json(model: BookModel, destination: str | Path, *, overwrite=False) -> Path:
    if not str(destination).strip():
        raise ValueError("Select a JSON output file.")
    output = Path(destination).expanduser()
    if output.suffix.lower() != ".json":
        raise ValueError("The output file must use the .json extension.")
    payload = json.dumps(model.to_dict(), ensure_ascii=False, indent=2) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=output.parent, prefix=".book-model-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
        if overwrite:
            os.replace(temporary, output)
        else:
            # Linking is atomic and fails if another process created the destination.
            os.link(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return output
