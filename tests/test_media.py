"""Executable media conversion contracts for Pillow and PDFium."""

from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image

from gramps_fancy_book.media import (
    MAX_PDF_RASTER_PIXELS,
    pdf_reproduction_action,
    pixel_region,
    prepare_pdf_derivative,
    prepare_raster_derivative,
)


def _blank_pdf(page_count: int, width_points: int = 72, height_points: int = 72) -> bytes:
    page_objects = list(range(3, 3 + page_count))
    kids = " ".join(f"{number} 0 R" for number in page_objects)
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {page_count} >>".encode(),
    ]
    objects.extend(
        (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width_points} {height_points}] "
            "/Resources << >> >>"
        ).encode()
        for _ in page_objects
    )

    document = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, content in enumerate(objects, start=1):
        offsets.append(len(document))
        document.extend(f"{number} 0 obj\n".encode())
        document.extend(content)
        document.extend(b"\nendobj\n")

    xref_offset = len(document)
    document.extend(f"xref\n0 {len(offsets)}\n".encode())
    document.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        document.extend(f"{offset:010d} 00000 n \n".encode())
    document.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode()
    )
    return bytes(document)


def _png(width: int, height: int) -> bytes:
    with BytesIO() as stream:
        Image.new("RGB", (width, height), (32, 64, 96)).save(stream, format="PNG")
        return stream.getvalue()


def test_pixel_region_rounds_outward_and_rejects_invalid_boxes():
    assert pixel_region((10, 10), (10, 20, 90, 80)) == (1, 2, 9, 8)
    with pytest.raises(ValueError, match="ordered and contained"):
        pixel_region((10, 10), (90, 20, 10, 80))


def test_raster_derivative_crops_to_png():
    derivative = prepare_raster_derivative(_png(10, 10), (10, 20, 90, 80))

    assert (derivative.width, derivative.height) == (8, 6)
    assert derivative.mime_type == "image/png"
    with Image.open(BytesIO(derivative.content)) as output:
        assert output.format == "PNG"
        assert output.size == (8, 6)


def test_unlinked_single_page_pdf_is_cropped_at_300_dpi():
    result = prepare_pdf_derivative(_blank_pdf(1), (0, 0, 50, 50))

    assert result.action == "reproduce"
    assert result.page_count == 1
    assert result.derivative is not None
    assert (result.derivative.width, result.derivative.height) == (150, 150)
    assert result.derivative.dpi == 300
    with Image.open(BytesIO(result.derivative.content)) as output:
        assert output.format == "PNG"
        assert output.size == (150, 150)
        assert all(abs(value - 300) < 1 for value in output.info["dpi"])


def test_multipage_pdf_remains_a_reference_and_external_url_takes_precedence():
    result = prepare_pdf_derivative(_blank_pdf(2), None)

    assert result.action == "reference-only"
    assert result.page_count == 2
    assert result.derivative is None
    assert pdf_reproduction_action(None, external_url_available=True) == "external-link"


def test_pdf_larger_than_pixel_limit_is_rejected_at_required_resolution():
    points = int((MAX_PDF_RASTER_PIXELS**0.5) + 1) * 72 // 300 + 100
    with pytest.raises(ValueError, match="too large"):
        prepare_pdf_derivative(_blank_pdf(1, points, points), None)
