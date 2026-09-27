"""Generate synthetic media and demonstrate Gramps percentage coordinates.

Run with a Python environment containing Pillow. Files stay in .work/media-spike.
This development probe is not bundled with the add-on.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def pixel_region(size, rectangle):
    """Convert ordered Gramps percent coordinates into a covering pixel box."""
    width, height = size
    if width <= 0 or height <= 0:
        raise ValueError("Image dimensions must be positive.")
    if rectangle is None:
        return (0, 0, width, height)
    if len(rectangle) != 4 or not all(math.isfinite(value) for value in rectangle):
        raise ValueError("A region needs four finite percentages.")
    left, top, right, bottom = rectangle
    if not (0 <= left < right <= 100 and 0 <= top < bottom <= 100):
        raise ValueError("The region must be ordered and contained within 0–100 percent.")
    return (
        math.floor(left * width / 100),
        math.floor(top * height / 100),
        math.ceil(right * width / 100),
        math.ceil(bottom * height / 100),
    )


def pdf_policy(page_count, external_url):
    if page_count < 1:
        raise ValueError("A readable PDF must contain at least one page.")
    if external_url:
        return "external-link"
    return "reproduce" if page_count == 1 else "reference-only"


def main():
    output = ROOT / ".work" / "media-spike"
    output.mkdir(parents=True, exist_ok=True)
    original = Image.new("RGB", (1200, 800), "white")
    draw = ImageDraw.Draw(original)
    for x in range(0, 1200, 100):
        draw.line((x, 0, x, 799), fill="gray")
    for y in range(0, 800, 100):
        draw.line((0, y, 1199, y), fill="gray")
    draw.text((310, 210), "SYNTHETIC DOCUMENT REGION", fill="black")
    original.save(output / "synthetic-original.png")
    rectangle = (25, 25, 75, 75)
    box = pixel_region(original.size, rectangle)
    cropped = original.crop(box)
    cropped.save(output / "synthetic-region.png")
    source_digest = hashlib.sha256((output / "synthetic-original.png").read_bytes()).hexdigest()
    cache_material = json.dumps(
        {"source": source_digest, "region": rectangle, "policy": "covering-pixels-v1"},
        sort_keys=True,
    ).encode()
    summary = {
        "input_size": original.size,
        "gramps_region_percent": rectangle,
        "pixel_box": box,
        "derived_size": cropped.size,
        "cache_key": hashlib.sha256(cache_material).hexdigest(),
        "pdf_policy": [
            {"pages": pages, "has_url": url, "action": pdf_policy(pages, url)}
            for pages in (1, 2)
            for url in (False, True)
        ],
        "limitations": [
            "No PDF rasterization, EXIF orientation or remote media fetch in this probe.",
            "Different regions remain distinct derivatives; documentary placement must be decided once per media identity.",
            "Invalid regions raise a diagnostic; the editorial fallback remains to be decided.",
        ],
    }
    (output / "result.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
