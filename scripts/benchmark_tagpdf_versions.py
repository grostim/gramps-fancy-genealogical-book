"""Compare complete tagged builds with installed and isolated tagpdf packages.

Requires the project media dependencies, psutil, pypdf and Poppler. Outputs are
retained in a new directory. The audit covers text, structure, destinations and
link ownership; it is not a PDF/UA conformance or screen-reader assessment.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import statistics
import subprocess
import sys
import time
import unicodedata
from collections import Counter
from pathlib import Path

import benchmark_book as fixture
from pypdf import PdfReader

from gramps_fancy_book.normalization import build_book_model
from gramps_fancy_book.renderers.html_archive import _media_asset_paths
from gramps_fancy_book.renderers.latex import render_latex
from gramps_fancy_book.renderers.latex_pdf import _compile_latex, _find_lualatex


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def _reference(value: object) -> tuple[int, int] | None:
    reference = getattr(value, "indirect_reference", value)
    if hasattr(reference, "idnum"):
        return reference.idnum, reference.generation
    return None


def audit(pdf: Path) -> dict[str, object]:
    """Check each link's ParentTree owner against its actual OBJR reference."""
    reader = PdfReader(pdf)
    root = reader.root_object
    structure = root["/StructTreeRoot"]
    role_map = structure.get("/RoleMap") or {}

    def role(tag: object) -> str:
        seen = set()
        while tag in role_map:
            if tag in seen:
                raise AssertionError("Cyclic role map")
            seen.add(tag)
            tag = role_map[tag]
        return str(tag)

    parent_tree = {}
    pending = [structure["/ParentTree"]]
    while pending:
        node = pending.pop().get_object()
        numbers = node.get("/Nums", [])
        assert len(numbers) % 2 == 0
        for index in range(0, len(numbers), 2):
            key = int(numbers[index])
            assert key not in parent_tree, "Duplicate ParentTree key"
            parent_tree[key] = numbers[index + 1]
        pending.extend(node.get("/Kids", []))

    counts: Counter[str] = Counter()
    owners: dict[tuple[int, int], list[tuple[int, int] | None]] = {}
    shape = []
    missing_alt = 0
    pending = [(structure.get("/K"), None, False)]
    while pending:
        raw, owner, closing = pending.pop()
        if closing:
            shape.append("end")
            continue
        node = raw.get_object() if hasattr(raw, "get_object") else raw
        if isinstance(node, (list, tuple)):
            pending.extend((child, owner, False) for child in reversed(node))
        elif isinstance(node, dict):
            if "/S" in node:
                tag = role(node["/S"])
                counts[tag] += 1
                owner = _reference(raw)
                alt = str(node.get("/Alt", ""))
                missing_alt += int(tag == "/Figure" and not alt.strip())
                shape.append((tag, alt))
                pending.append((None, None, True))
            if node.get("/Type") == "/OBJR":
                annotation = _reference(node.get("/Obj"))
                assert annotation is not None, "OBJR has no indirect annotation"
                owners.setdefault(annotation, []).append(owner)
            pending.append((node.get("/K"), owner, False))

    destinations = reader.named_destinations
    destination_pages = {
        str(name): reader.get_destination_page_number(destination)
        for name, destination in destinations.items()
    }
    assert all(page is not None and page >= 0 for page in destination_pages.values())
    signatures = []
    mismatches = 0
    for page_index, page in enumerate(reader.pages):
        for raw in page.get("/Annots", []):
            annotation = raw.get_object()
            if annotation.get("/Subtype") != "/Link":
                continue
            key = annotation.get("/StructParent")
            owner = parent_tree.get(int(key)) if key is not None else None
            valid = (
                owner is not None
                and role(owner.get_object().get("/S")) == "/Link"
                and owners.get(_reference(raw)) == [_reference(owner)]
            )
            mismatches += int(not valid)
            action = annotation.get("/A") or {}
            target = annotation.get("/Dest", action.get("/D"))
            if target is not None:
                assert isinstance(target, str), "Unexpected non-named internal link"
                assert str(target) in destination_pages, "Unresolved internal link"
            signatures.append((
                page_index, str(annotation.get("/Contents", "")),
                str(target) if target is not None else None,
                destination_pages.get(str(target)), str(action.get("/URI", "")),
                [float(value) for value in annotation.get("/Rect", [])],
            ))
    text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
    normalized_text = unicodedata.normalize("NFC", " ".join(text.split()))
    marked = bool((root.get("/MarkInfo") or {}).get("/Marked"))
    assert marked and reader.pdf_header == "%PDF-2.0"
    assert not mismatches and not missing_alt
    return {
        "pages": len(reader.pages), "marked": marked, "language": str(root.get("/Lang")),
        "structure_elements": sum(counts.values()), "role_counts": dict(counts),
        "named_destinations": len(destination_pages),
        "figures_without_alt": missing_alt, "link_annotations": len(signatures),
        "parenttree_objr_mismatches": mismatches,
        "structure_shape_sha256": _digest(shape),
        "destination_pages_sha256": _digest(destination_pages),
        "link_signatures_sha256": _digest(signatures),
        "text_nfc_sha256": hashlib.sha256(normalized_text.encode()).hexdigest(),
    }


def _package_paths(compiler: Path) -> dict[str, str]:
    kpsewhich = compiler.parent / "kpsewhich"
    return {
        "sty": subprocess.check_output([str(kpsewhich), "tagpdf.sty"], text=True).strip(),
        "lua": subprocess.check_output(
            [str(kpsewhich), "--format=lua", "tagpdf.lua"], text=True,
        ).strip(),
    }


def compare(candidate: Path, work: Path, couples: int, pairs: int) -> None:
    if work.exists():
        raise FileExistsError("Use a new output directory to retain every run.")
    compiler_name = _find_lualatex()
    if compiler_name is None:
        raise RuntimeError("LuaLaTeX is required")
    compiler = Path(compiler_name).absolute()
    candidate = candidate.resolve()
    for name in ("tagpdf.sty", "tagpdf.lua"):
        if not (candidate / name).is_file():
            raise FileNotFoundError(candidate / name)
    work.mkdir(parents=True)
    wrapper = work / "lualatex-recorder"
    wrapper.write_text(f'#!/bin/sh\nexec {shlex.quote(str(compiler))} -recorder "$@"\n')
    wrapper.chmod(0o755)
    snapshot, media = fixture.synthetic_branching_snapshot(couples, include_media=True)
    model = build_book_model(snapshot)
    fixture._prepare_synthetic_media(model, media, work / "media")
    source = render_latex(model)
    report = {
        "descendant_couples": couples, "pairs": pairs, "runs": [],
        "python": sys.version, "platform": platform.platform(),
        "benchmark_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "fixture_generator_sha256": hashlib.sha256(Path(fixture.__file__).read_bytes()).hexdigest(),
        "renderer_source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "model_sha256": _digest(model.to_dict()),
        "instrumentation": "compiler recorder only; production source unchanged",
        "scope": "complete converged builds; synthetic 96x72 portraits; not PDF/UA",
    }
    previous = {key: os.environ.get(key) for key in ("TEXINPUTS", "LUAINPUTS")}
    (work / "benchmark-source.py").write_bytes(Path(__file__).read_bytes())
    (work / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    try:
        for pair in range(1, pairs + 1):
            order = ("installed", "candidate") if pair % 2 else ("candidate", "installed")
            pair_audits = []
            for variant in order:
                for key in previous:
                    if variant == "candidate":
                        os.environ[key] = str(candidate) + "//:"
                    else:
                        os.environ.pop(key, None)
                paths = _package_paths(compiler)
                if variant == "candidate":
                    assert all(Path(path).resolve().parent == candidate for path in paths.values())
                run_directory = work / f"pair-{pair}-{variant}"
                run_directory.mkdir()
                (run_directory / "book.tex").write_text(source)
                for relative, asset in _media_asset_paths(model, work / "media").items():
                    destination = run_directory / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(asset, destination)
                print(json.dumps({"event": "start", "pair": pair, "variant": variant}), flush=True)
                gc.collect()
                start = time.perf_counter()
                try:
                    with fixture._CompilerRssMonitor(os.getpid()) as monitor:
                        _compile_latex(str(wrapper), run_directory,
                                       pass_timeout_seconds=600, total_timeout_seconds=1800)
                except Exception as error:
                    failure = {
                        "pair": pair, "variant": variant, "status": "compile_failed",
                        "seconds": time.perf_counter() - start,
                        "error": str(error), "artifact_directory": str(run_directory),
                        "package_paths": paths, **monitor.as_dict(),
                    }
                    report["runs"].append(failure)
                    report["status"] = "failed; retained compiler artifacts"
                    (work / "results.json").write_text(json.dumps(report, indent=2) + "\n")
                    raise
                elapsed = time.perf_counter() - start
                log = (run_directory / "book.log").read_text(errors="replace")
                sty_version = re.search(r"Package: tagpdf [0-9-]+ v(\S+)", log)
                lua_version = re.search(r"Lua module: tagpdf [0-9-]+ v(\S+)", log)
                assert sty_version and lua_version and sty_version[1] == lua_version[1]
                assert (run_directory / "book.tex").read_text() == source
                loaded = {
                    line[6:] for line in (run_directory / "book.fls").read_text().splitlines()
                    if line.startswith("INPUT ") and Path(line[6:]).name.startswith("tagpdf")
                }
                assert paths["sty"] in loaded and paths["lua"] in loaded
                if variant == "candidate":
                    # Namespace data can be supplied by latex-lab or the TeX
                    # distribution rather than by the candidate archive.
                    assert all(
                        Path(path).resolve().parent == candidate for path in loaded
                        if (candidate / Path(path).name).is_file()
                    )
                pdf = run_directory / "book.pdf"
                result = {
                    "pair": pair, "variant": variant, "seconds": elapsed,
                    "pdf_bytes": pdf.stat().st_size, "pdf_path": str(pdf),
                    "package_paths": paths,
                    "actual_package_version": sty_version[1],
                    "actual_lua_module_version": lua_version[1],
                    "package_sha256": {
                        kind: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                        for kind, path in paths.items()
                    },
                    "loaded_tagpdf_files": sorted(loaded),
                    "loaded_tagpdf_sha256": {
                        path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                        for path in sorted(loaded)
                    },
                    **monitor.as_dict(), "audit": audit(pdf),
                }
                report["runs"].append(result)
                pair_audits.append(result["audit"])
                (work / "results.json").write_text(json.dumps(report, indent=2) + "\n")
                print(json.dumps({"event": "complete", **result}), flush=True)
            assert pair_audits[0] == pair_audits[1], "PDF audits differ within a pair"
        report["median_seconds"] = {
            variant: statistics.median(run["seconds"] for run in report["runs"]
                                       if run["variant"] == variant)
            for variant in ("installed", "candidate")
        }
        report["status"] = "complete; all paired audits match"
        (work / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", required=True, type=Path)
    parser.add_argument("--work-directory", required=True, type=Path)
    parser.add_argument("--descendant-couples", type=int, default=1000)
    parser.add_argument("--pairs", type=int, default=3)
    args = parser.parse_args()
    if args.pairs < 1 or args.descendant_couples < 1:
        parser.error("pairs and descendant-couples must be positive")
    compare(args.candidate_root, args.work_directory, args.descendant_couples, args.pairs)
