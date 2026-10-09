"""Audit renderer PDFs, optionally proving detection of three link corruptions."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from benchmark_tagpdf_versions import audit
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject


def negative_controls(source: Path) -> list[str]:
    expected = audit(source)

    def writer() -> PdfWriter:
        clone = PdfWriter(clone_from=source)
        # PdfWriter defaults to 1.3 even when cloning a PDF 2.0 document.
        clone.pdf_header = PdfReader(source).pdf_header
        return clone

    rejected = []
    with tempfile.TemporaryDirectory(prefix="gfb-pdf-audit-controls-") as directory:
        output = Path(directory) / "control.pdf"
        writer().write(output)
        assert audit(output) == expected, "An intact clone must pass the same audit"
        for corruption in (
            "missing_structparent", "swapped_parenttree_owners", "unresolved_destination",
        ):
            clone = writer()
            links = [
                reference.get_object()
                for page in clone.pages for reference in page.get("/Annots", [])
                if reference.get_object().get("/Subtype") == "/Link"
            ]
            assert len(links) >= 2, "Negative controls require at least two links"
            if corruption == "missing_structparent":
                del links[0][NameObject("/StructParent")]
            elif corruption == "unresolved_destination":
                annotation = next(link for link in links if link.get("/A", {}).get("/D"))
                annotation["/A"][NameObject("/D")] = TextStringObject("missing-destination")
            else:
                keys = [int(link["/StructParent"]) for link in links[:2]]
                locations = {}
                pending = [clone.root_object["/StructTreeRoot"]["/ParentTree"]]
                while pending:
                    node = pending.pop().get_object()
                    numbers = node.get("/Nums", [])
                    for index in range(0, len(numbers), 2):
                        if int(numbers[index]) in keys:
                            locations[int(numbers[index])] = numbers, index + 1
                    pending.extend(node.get("/Kids", []))
                first, a = locations[keys[0]]
                second, b = locations[keys[1]]
                first[a], second[b] = second[b], first[a]
            clone.write(output)
            try:
                audit(output)
            except AssertionError:
                rejected.append(corruption)
            else:
                raise AssertionError(f"Audit accepted corruption: {corruption}")
    return rejected


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--negative-controls", action="store_true")
    args = parser.parse_args()
    result = {"audit": audit(args.pdf)}
    if args.negative_controls:
        result["rejected_corruptions"] = negative_controls(args.pdf)
    print(json.dumps(result, indent=2))
