"""Pure helpers for media crop geometry and derivative cache identities."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from .domain import Media

Region = tuple[int | float, int | float, int | float, int | float]
PixelBox = tuple[int, int, int, int]
RASTER_DERIVATIVE_POLICY_VERSION = "raster-png-exif-transpose-covering-pixels-v1"


@dataclass(frozen=True)
class RasterDerivative:
    cache_key: str
    content: bytes
    width: int
    height: int
    mime_type: str = "image/png"


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


def resolve_media_path(database: object, media_path: str) -> str:
    """Resolve a Gramps media path using the active database's media directory."""
    try:
        from gramps.gen.utils.file import media_path_full
    except ImportError as error:
        raise RuntimeError("Gramps is required to resolve database media paths.") from error
    return media_path_full(database, media_path)


def read_local_media(database: object, media: Media) -> bytes:
    """Read an eligible local Gramps media file without fetching external URLs."""
    if media.is_excluded:
        raise ValueError("Media marked BOOK_EXCLUDE cannot be read for publication.")
    resolved_path = resolve_media_path(database, media.path)
    if resolved_path.startswith(("http://", "https://")):
        raise ValueError("Remote media is not downloaded for book generation.")
    return Path(resolved_path).read_bytes()


def prepare_media_derivative(
    database: object, media: Media, rectangle: Region | None
) -> RasterDerivative:
    """Read and prepare one eligible raster reference from the active Gramps DB."""
    if media.is_excluded:
        raise ValueError("Media marked BOOK_EXCLUDE cannot be published.")
    if media.mime_type and not media.mime_type.casefold().startswith("image/"):
        raise ValueError("Only raster images can be prepared by this helper.")
    return prepare_raster_derivative(read_local_media(database, media), rectangle)


def prepare_raster_derivative(
    source_content: bytes, rectangle: Region | None
) -> RasterDerivative:
    """Orient, crop and losslessly encode a raster image as PNG.

    Pillow is imported only when image processing is requested. PDF rasterization
    and non-raster media policies belong to the caller.
    """
    try:
        from PIL import Image, ImageOps
    except ImportError as error:
        raise RuntimeError("Pillow is required to prepare raster media.") from error

    with BytesIO(source_content) as source_stream:
        with Image.open(source_stream) as opened:
            oriented = ImageOps.exif_transpose(opened)
            with oriented:
                box = pixel_region(oriented.size, rectangle)
                with oriented.crop(box) as cropped:
                    image_to_save = cropped
                    converted = None
                    if cropped.mode not in {"1", "L", "LA", "P", "RGB", "RGBA"}:
                        converted = cropped.convert(
                            "RGBA" if "A" in cropped.getbands() else "RGB"
                        )
                        image_to_save = converted
                    try:
                        with BytesIO() as output:
                            save_options = {"format": "PNG"}
                            icc_profile = oriented.info.get("icc_profile")
                            if isinstance(icc_profile, bytes):
                                save_options["icc_profile"] = icc_profile
                            image_to_save.save(output, **save_options)
                            content = output.getvalue()
                        width, height = image_to_save.size
                    finally:
                        if converted is not None:
                            converted.close()

    return RasterDerivative(
        cache_key=derivative_cache_key(
            source_content,
            rectangle,
            RASTER_DERIVATIVE_POLICY_VERSION,
        ),
        content=content,
        width=width,
        height=height,
    )


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
