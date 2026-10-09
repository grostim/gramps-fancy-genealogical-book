"""Check figure attributes in renderer PDFs; this is not a PDF/UA assessment.

Renderer figures occupy one page inside positive page margins. This check
validates their recorded Layout/BBox attributes, not the painted image pixels.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, FloatObject, NameObject


def _object(value):
    return value.get_object() if hasattr(value, "get_object") else value


def _reference(value):
    reference = getattr(value, "indirect_reference", value)
    if hasattr(reference, "idnum"):
        return reference.idnum, reference.generation
    return None


def _figures(reader: PdfReader | PdfWriter):
    structure = reader.root_object["/StructTreeRoot"]
    roles = structure.get("/RoleMap") or {}
    pending = [structure.get("/K")]
    while pending:
        node = _object(pending.pop())
        if isinstance(node, (list, tuple)):
            pending.extend(reversed(node))
        elif isinstance(node, dict):
            role = node.get("/S")
            seen = set()
            while role in roles:
                if role in seen:
                    raise ValueError("Cyclic structure role map")
                seen.add(role)
                role = roles[role]
            if role == "/Figure":
                yield node
            pending.append(node.get("/K"))


def _layout_attributes(figure, class_map):
    """Resolve direct attributes and named attribute classes, ignoring revisions."""
    pending = [figure.get("/A")]
    classes = _object(figure.get("/C"))
    if isinstance(classes, str):
        classes = [classes]
    for name in classes or []:
        if isinstance(name, str):
            if name not in class_map:
                raise ValueError(f"Missing figure attribute class: {name}")
            pending.append(class_map[name])
    while pending:
        node = _object(pending.pop())
        if isinstance(node, (list, tuple)):
            pending.extend(node)
        elif isinstance(node, dict) and node.get("/O") == "/Layout":
            yield node


def _figure_pages(figure):
    pages = set()
    pending = [(figure, None)]
    while pending:
        raw, inherited = pending.pop()
        node = _object(raw)
        if isinstance(node, (list, tuple)):
            pending.extend((child, inherited) for child in node)
        elif isinstance(node, dict):
            page = _reference(node.get("/Pg")) or inherited
            if node.get("/Type") == "/MCR" or node.get("/MCID") is not None:
                if page is None:
                    raise ValueError("Figure marked content has no page")
                pages.add(page)
            pending.append((node.get("/K"), page))
        elif isinstance(node, int) and inherited is not None:
            pages.add(inherited)
    return pages


def audit(pdf: Path) -> dict[str, object]:
    reader = PdfReader(pdf)
    class_map = reader.root_object["/StructTreeRoot"].get("/ClassMap") or {}
    page_numbers = {_reference(page): number for number, page in enumerate(reader.pages)}
    records = []
    for figure in _figures(reader):
        boxes = [
            _object(attributes["/BBox"])
            for attributes in _layout_attributes(figure, class_map)
            if "/BBox" in attributes
        ]
        if len(boxes) != 1 or len(boxes[0]) != 4:
            raise ValueError("Each renderer figure requires one four-coordinate Layout/BBox")
        box = [float(value) for value in boxes[0]]
        if not all(math.isfinite(value) for value in box):
            raise ValueError("Figure BBox coordinates must be finite")
        x0, y0, x1, y1 = box
        if not (0 < x0 < x1 and 0 < y0 < y1):
            raise ValueError("Figure BBox must have positive origin, width and height")
        pages = _figure_pages(figure)
        if len(pages) != 1 or not pages <= page_numbers.keys():
            raise ValueError("Each renderer figure must reference exactly one existing page")
        page_number = page_numbers[next(iter(pages))]
        page = reader.pages[page_number]
        bounds = [float(value) for value in page.mediabox]
        if x0 < bounds[0] or y0 < bounds[1] or x1 > bounds[2] + 0.01 or y1 > bounds[3] + 0.01:
            raise ValueError("Figure BBox lies outside its page")
        records.append({
            "page": page_number + 1, "alt": str(figure.get("/Alt", "")), "bbox": box,
        })
    if not records:
        raise ValueError("Figure geometry control requires at least one figure")
    return {
        "pages": len(reader.pages), "figures": len(records),
        "geometry_sha256": hashlib.sha256(
            json.dumps(records, sort_keys=True).encode()
        ).hexdigest(),
        "scope": "recorded figure attributes; not painted-image or PDF/UA validation",
    }


def negative_controls(source: Path) -> list[str]:
    expected = audit(source)
    rejected = []
    with tempfile.TemporaryDirectory(prefix="gfb-figure-geometry-controls-") as directory:
        target = Path(directory) / "control.pdf"
        for corruption in (
            "intact", "class_attributes", "missing_bbox", "zero_origin", "zero_width",
        ):
            writer = PdfWriter(clone_from=source)
            writer.pdf_header = PdfReader(source).pdf_header
            # PdfWriter exposes the same root/page interface used by traversal.
            figure = next(_figures(writer))
            class_map = writer.root_object["/StructTreeRoot"].get("/ClassMap") or {}
            attributes = next(
                value for value in _layout_attributes(figure, class_map) if "/BBox" in value
            )
            box = [float(value) for value in attributes["/BBox"]]
            if corruption == "class_attributes":
                structure = writer.root_object["/StructTreeRoot"]
                if "/ClassMap" not in structure:
                    structure[NameObject("/ClassMap")] = DictionaryObject()
                name = NameObject("/GeometryControl")
                structure["/ClassMap"][name] = attributes
                figure[NameObject("/C")] = name
                figure.pop(NameObject("/A"), None)
            elif corruption == "missing_bbox":
                del attributes[NameObject("/BBox")]
            elif corruption == "zero_origin":
                attributes[NameObject("/BBox")] = ArrayObject([
                    FloatObject(value) for value in (0, 0, box[2] - box[0], box[3] - box[1])
                ])
            elif corruption == "zero_width":
                attributes[NameObject("/BBox")] = ArrayObject([
                    FloatObject(value) for value in (box[0], box[1], box[0], box[3])
                ])
            writer.write(target)
            if corruption in {"intact", "class_attributes"}:
                if audit(target) != expected:
                    raise ValueError(f"Clone {corruption} must preserve figure geometry")
                continue
            try:
                audit(target)
            except ValueError:
                rejected.append(corruption)
            else:
                raise ValueError(f"Figure audit accepted corruption: {corruption}")
    return rejected


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--negative-controls", action="store_true")
    args = parser.parse_args()
    result = {
        "pdf_sha256": hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
        "audit": audit(args.pdf),
    }
    if args.reference is not None:
        if result["audit"] != audit(args.reference):
            raise ValueError("Recorded figure geometry differs from the reference PDF")
        result["reference_match"] = True
    if args.negative_controls:
        result["rejected_corruptions"] = negative_controls(args.pdf)
        result["validated_clones"] = ["intact", "class_attributes"]
    print(json.dumps(result, indent=2))
