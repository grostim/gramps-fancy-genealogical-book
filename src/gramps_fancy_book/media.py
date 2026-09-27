"""Pure helpers for media crop geometry and derivative cache identities."""

from __future__ import annotations

import hashlib
import json
import math

Region = tuple[int | float, int | float, int | float, int | float]
PixelBox = tuple[int, int, int, int]


def pixel_region(
    size: tuple[int, int], rectangle: Region | None
) -> PixelBox:
    """Convert Gramps percentage coordinates into a pixel box covering the region."""
    width, height = size
    if width <= 0 or height <= 0:
        raise ValueError("Image dimensions must be positive.")

    left, top, right, bottom = _normalized_region(rectangle)
    return (
        math.floor(left * width / 100),
        math.floor(top * height / 100),
        math.ceil(right * width / 100),
        math.ceil(bottom * height / 100),
    )


def derivative_cache_key(
    source_content: bytes,
    rectangle: Region | None,
    conversion_policy_version: str,
) -> str:
    """Hash source bytes, normalized crop region, and conversion policy version.

    Bump the policy version whenever orientation handling, output format, or other
    conversion behavior changes.
    """
    if not conversion_policy_version.strip():
        raise ValueError("A conversion policy version is required.")
    source_digest = hashlib.sha256(source_content).hexdigest()
    cache_material = json.dumps(
        {
            "source": source_digest,
            "region": _normalized_region(rectangle),
            "policy": conversion_policy_version,
        },
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(cache_material).hexdigest()


def _normalized_region(rectangle: Region | None) -> tuple[int | float, ...]:
    if rectangle is None:
        return (0, 0, 100, 100)
    if len(rectangle) != 4 or not all(math.isfinite(value) for value in rectangle):
        raise ValueError("A region needs four finite percentages.")

    left, top, right, bottom = rectangle
    if not (0 <= left < right <= 100 and 0 <= top < bottom <= 100):
        raise ValueError("The region must be ordered and contained within 0–100 percent.")
    return tuple(
        int(value) if float(value).is_integer() else float(value)
        for value in (left, top, right, bottom)
    )
