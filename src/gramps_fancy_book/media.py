"""Local media conversion helpers and derivative cache identities."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from .domain import (
    BookModel,
    Diagnostic,
    EditorialMediaArtifact,
    EditorialMediaUse,
    Media,
)

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
    dpi: int | None = None


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
    if _is_external_url(resolved_path):
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
    media_kind = _media_kind(media)
    if media_kind == "pdf":
        return prepare_pdf_media_derivative(
            database,
            media,
            rectangle,
            external_url_available=external_url_available,
        )
    if media_kind != "raster":
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
    if _media_kind(media) != "pdf":
        raise ValueError("PDF processing requires a PDF media record.")

    if external_url_available:
        return PdfMediaResult(action="external-link", page_count=None)

    return prepare_pdf_derivative(read_local_media(database, media), rectangle)


def prepare_pdf_derivative(
    source_content: bytes, rectangle: Region | None
) -> PdfMediaResult:
    """Inspect and rasterize PDF bytes under the single-page publication rule."""
    try:
        import pypdfium2 as pdfium
    except ImportError as error:
        raise RuntimeError("pypdfium2 is required to inspect and prepare PDF media.") from error

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

    raster = prepare_raster_derivative(raster_content, rectangle, dpi=PDF_RASTER_DPI)
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
            dpi=PDF_RASTER_DPI,
        ),
    )


def _media_kind(media: Media) -> Literal["pdf", "raster", "reference"]:
    media_type = media.mime_type.partition(";")[0].strip().casefold()
    suffix = Path(media.path).suffix.casefold()
    if media_type in {"application/pdf", "application/x-pdf"} or suffix == ".pdf":
        return "pdf"
    if media_type.startswith("image/") or not media_type:
        return "raster"
    return "reference"


def prepare_raster_derivative(
    source_content: bytes, rectangle: Region | None, *, dpi: int | None = None
) -> RasterDerivative:
    """Orient, crop and losslessly encode a raster image as PNG.

    Pillow is imported only when image processing is requested.
    """
    try:
        from PIL import Image, ImageOps
    except ImportError as error:
        raise RuntimeError("Pillow is required to prepare raster media.") from error
    if dpi is not None and dpi <= 0:
        raise ValueError("Output resolution must be a positive number of DPI.")

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
                            if dpi is not None:
                                save_options["dpi"] = (dpi, dpi)
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
        dpi=dpi,
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


def prepare_editorial_media(
    database: object,
    model: BookModel,
    asset_directory_name: str,
    asset_staging_directory: str | Path,
) -> None:
    """Prepare each unique editorial media region and attach its manifest.

    PNG files are written one at a time to the supplied staging directory. The
    book model records relative asset paths and structured diagnostics for the
    JSON export; the caller commits the staged directory beside that export.
    """
    if (
        not asset_directory_name
        or asset_directory_name in {".", ".."}
        or Path(asset_directory_name).name != asset_directory_name
    ):
        raise ValueError("The media asset directory must be a single relative name.")
    staging_directory = Path(asset_staging_directory)
    if not staging_directory.is_dir() or staging_directory.is_symlink():
        raise ValueError("The media asset staging path must be an existing directory.")
    model.media_artifacts = []
    if model.editorial_book is None:
        return

    uses_by_media: dict[
        str, dict[tuple[int | float, ...] | None, list[EditorialMediaUse]]
    ] = {}
    for placement in model.editorial_book.media_placements:
        for use in placement.uses:
            rectangle = use.media_ref.rectangle
            uses_by_media.setdefault(placement.media_handle, {}).setdefault(
                rectangle, []
            ).append(use)

    diagnostics: list[Diagnostic] = []
    written_cache_keys: set[str] = set()

    for media_handle, uses_by_region in uses_by_media.items():
        media = model.media.get(media_handle)
        all_citation_handles = list(media.links.citations) if media is not None else []
        for uses in uses_by_region.values():
            all_citation_handles.extend(_media_citations(uses))
        all_citation_handles = tuple(dict.fromkeys(all_citation_handles))
        if media is None:
            for rectangle, uses in uses_by_region.items():
                _append_media_failure(
                    model,
                    diagnostics,
                    media_handle,
                    rectangle,
                    _media_contexts(uses),
                    _media_citations(uses),
                    "MEDIA_REFERENCE_UNAVAILABLE",
                )
            continue
        if media.is_excluded:
            continue

        external_url_available = any(
            _citation_has_url(model, citation_handle)
            for citation_handle in all_citation_handles
        )
        media_kind = _media_kind(media)
        if media_kind == "pdf" and external_url_available:
            for rectangle, uses in uses_by_region.items():
                model.media_artifacts.append(
                    EditorialMediaArtifact(
                        media_handle=media_handle,
                        rectangle=rectangle,
                        action="external-link",
                        context_ids=_media_contexts(uses),
                        citation_handles=_all_media_citations(media, uses),
                    )
                )
            continue

        if media_kind == "reference":
            action = "external-link" if external_url_available else "reference-only"
            for rectangle, uses in uses_by_region.items():
                model.media_artifacts.append(
                    EditorialMediaArtifact(
                        media_handle=media_handle,
                        rectangle=rectangle,
                        action=action,
                        context_ids=_media_contexts(uses),
                        citation_handles=_all_media_citations(media, uses),
                    )
                )
            continue

        source_content: bytes | None = None
        source_error: Exception | None = None
        try:
            source_content = read_local_media(database, media)
        except Exception as error:
            source_error = error

        for rectangle, uses in uses_by_region.items():
            contexts = _media_contexts(uses)
            citation_handles = _all_media_citations(media, uses)
            if source_error is not None or source_content is None:
                _append_media_failure(
                    model,
                    diagnostics,
                    media_handle,
                    rectangle,
                    contexts,
                    citation_handles,
                    "MEDIA_DERIVATIVE_FAILED",
                )
                continue
            try:
                if media_kind == "pdf":
                    prepared_pdf = prepare_pdf_derivative(source_content, rectangle)
                    if prepared_pdf.derivative is None:
                        model.media_artifacts.append(
                            EditorialMediaArtifact(
                                media_handle=media_handle,
                                rectangle=rectangle,
                                action=prepared_pdf.action,
                                context_ids=contexts,
                                citation_handles=citation_handles,
                                page_count=prepared_pdf.page_count,
                            )
                        )
                        continue
                    derivative = prepared_pdf.derivative
                    page_count = prepared_pdf.page_count
                    action = prepared_pdf.action
                else:
                    derivative = prepare_raster_derivative(source_content, rectangle)
                    page_count = None
                    action = "reproduce"
            except Exception:
                _append_media_failure(
                    model,
                    diagnostics,
                    media_handle,
                    rectangle,
                    contexts,
                    citation_handles,
                    "MEDIA_DERIVATIVE_FAILED",
                )
                continue

            if derivative.cache_key not in written_cache_keys:
                asset_file = staging_directory / f"{derivative.cache_key}.png"
                with asset_file.open("xb") as stream:
                    stream.write(derivative.content)
                written_cache_keys.add(derivative.cache_key)
            model.media_artifacts.append(
                EditorialMediaArtifact(
                    media_handle=media_handle,
                    rectangle=rectangle,
                    action=action,
                    context_ids=contexts,
                    citation_handles=citation_handles,
                    cache_key=derivative.cache_key,
                    asset_path=f"{asset_directory_name}/{derivative.cache_key}.png",
                    mime_type=derivative.mime_type,
                    width=derivative.width,
                    height=derivative.height,
                    dpi=derivative.dpi,
                    page_count=page_count,
                )
            )

    model.diagnostics.extend(item for item in diagnostics if item not in model.diagnostics)


def _media_contexts(uses: list[EditorialMediaUse]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(f"{use.context_type}:{use.context_id}" for use in uses))


def _media_citations(uses: list[EditorialMediaUse]) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            citation_handle
            for use in uses
            for citation_handle in (*use.citation_handles, *use.media_ref.citations)
        )
    )


def _all_media_citations(media: Media, uses: list[EditorialMediaUse]) -> tuple[str, ...]:
    return tuple(dict.fromkeys((*media.links.citations, *_media_citations(uses))))


def _citation_has_url(model: BookModel, citation_handle: str) -> bool:
    citation = model.citations.get(citation_handle)
    if citation is None:
        return False
    if any(_is_external_url(url.path) for url in citation.urls):
        return True
    source = model.sources.get(citation.source_handle or "")
    return bool(source and any(_is_external_url(url.path) for url in source.urls))


def _is_external_url(value: str) -> bool:
    try:
        parsed = urlsplit(value.strip())
    except ValueError:
        return False
    return parsed.scheme.casefold() in {"http", "https"} and bool(parsed.netloc)


def _append_media_failure(
    model: BookModel,
    diagnostics: list[Diagnostic],
    media_handle: str,
    rectangle: tuple[int | float, ...] | None,
    contexts: tuple[str, ...],
    citation_handles: tuple[str, ...],
    diagnostic_code: str,
) -> None:
    diagnostics.append(
        Diagnostic(
            code=diagnostic_code,
            severity="warning",
            object_type="media",
            handle=media_handle,
            message=(
                "Media could not be prepared. Check its Gramps path, crop region, "
                "file format and optional media dependencies."
            ),
            context=contexts[0] if contexts else str(rectangle),
        )
    )
    model.media_artifacts.append(
        EditorialMediaArtifact(
            media_handle=media_handle,
            rectangle=rectangle,
            action="failed",
            context_ids=contexts,
            citation_handles=citation_handles,
            diagnostic_code=diagnostic_code,
        )
    )
