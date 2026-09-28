"""Local media conversion helpers and derivative cache identities."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Literal

from .domain import Media

Region = tuple[int | float, int | float, int | float, int | float]
PixelBox = tuple[int, int, int, int]
RASTER_DERIVATIVE_POLICY_VERSION = "raster-png-exif-transpose-covering-pixels-v1"
PDF_DERIVATIVE_POLICY_VERSION = "pdfium-png-covering-pixels-v1"
PDF_RASTER_DPI = 300
MAX_PDF_RASTER_PIXELS = 40_000_000
PdfMediaAction = Literal["external-link", "reference-only", "reproduce"]


@dataclass(frozen=True)
class RasterDerivative:
    cache_key: str
    content: bytes
    width: int
    height: int
    mime_type: str = "image/png"


@dataclass(frozen=True)
class PdfMediaResult:
    action: PdfMediaAction
    page_count: int | None
    derivative: RasterDerivative | None = None


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
    database: object,
    media: Media,
    rectangle: Region | None,
    *,
    external_url_available: bool = False,
) -> RasterDerivative | PdfMediaResult:
    """Prepare one eligible image or PDF reference from the active Gramps DB."""
    if media.is_excluded:
        raise ValueError("Media marked BOOK_EXCLUDE cannot be published.")
    media_type = media.mime_type.partition(";")[0].strip().casefold()
    if media_type in {"application/pdf", "application/x-pdf"}:
        return prepare_pdf_media_derivative(
            database,
            media,
            rectangle,
            external_url_available=external_url_available,
        )
    if media_type and not media_type.startswith("image/"):
        raise ValueError("Only raster images can be prepared by this helper.")
    return prepare_raster_derivative(read_local_media(database, media), rectangle)


def pdf_reproduction_action(
    page_count: int | None, external_url_available: bool
) -> PdfMediaAction:
    """Apply the specification's external-link and single-page PDF rules."""
    if external_url_available:
        return "external-link"
    if page_count is None:
        raise ValueError("A page count is required when no external URL is available.")
    if page_count < 1:
        raise ValueError("A readable PDF must contain at least one page.")
    return "reproduce" if page_count == 1 else "reference-only"


def prepare_pdf_media_derivative(
    database: object,
    media: Media,
    rectangle: Region | None,
    *,
    external_url_available: bool,
) -> PdfMediaResult:
    """Rasterize an eligible one-page PDF; leave other PDFs as links/references.

    PDFium and Pillow are loaded only when an unlinked PDF must be inspected or
    reproduced. Multipage PDFs are never embedded. A 300-DPI render above the
    pixel limit is rejected rather than silently reduced in quality.
    """
    if media.is_excluded:
        raise ValueError("Media marked BOOK_EXCLUDE cannot be published.")
    media_type = media.mime_type.partition(";")[0].strip().casefold()
    if media_type not in {"application/pdf", "application/x-pdf"}:
        raise ValueError("PDF processing requires a PDF media record.")

    if external_url_available:
        return PdfMediaResult(action="external-link", page_count=None)

    try:
        import pypdfium2 as pdfium
    except ImportError as error:
        raise RuntimeError("pypdfium2 is required to inspect and prepare PDF media.") from error

    source_content = read_local_media(database, media)
    pdf = pdfium.PdfDocument(source_content)
    try:
        page_count = len(pdf)
        action = pdf_reproduction_action(page_count, external_url_available=False)
        if action != "reproduce":
            return PdfMediaResult(action=action, page_count=page_count)

        page = pdf[0]
        try:
            width_points, height_points = page.get_size()
            if (
                not math.isfinite(width_points)
                or not math.isfinite(height_points)
                or width_points <= 0
                or height_points <= 0
            ):
                raise ValueError("The PDF page has invalid dimensions.")
            scale = PDF_RASTER_DPI / 72
            pixel_width = math.ceil(width_points * scale)
            pixel_height = math.ceil(height_points * scale)
            if pixel_width * pixel_height > MAX_PDF_RASTER_PIXELS:
                raise ValueError(
                    "The PDF page is too large to rasterize at the required 300 DPI."
                )

            bitmap = page.render(scale=scale)
            try:
                try:
                    rendered_view = bitmap.to_pil()
                except ImportError as error:
                    raise RuntimeError("Pillow is required to prepare PDF media.") from error
                try:
                    rendered_image = rendered_view.copy()
                finally:
                    rendered_view.close()
                try:
                    with BytesIO() as rendered_png:
                        rendered_image.save(rendered_png, format="PNG")
                        raster_content = rendered_png.getvalue()
                finally:
                    rendered_image.close()
            finally:
                bitmap.close()
        finally:
            page.close()
    finally:
        pdf.close()

    raster = prepare_raster_derivative(raster_content, rectangle)
    return PdfMediaResult(
        action="reproduce",
        page_count=page_count,
        derivative=RasterDerivative(
            cache_key=derivative_cache_key(
                source_content,
                rectangle,
                f"{PDF_DERIVATIVE_POLICY_VERSION}-dpi-{PDF_RASTER_DPI}",
            ),
            content=raster.content,
            width=raster.width,
            height=raster.height,
        ),
    )


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
