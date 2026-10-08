"""Benchmark the book pipeline with public, openly licensed portrait JPEGs.

The family fixture is synthetic. Image files are downloaded to a temporary
directory (or read from ``--media-dir``) and are never added to the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import replace
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
MANIFEST_PATH = ROOT / "docs" / "fixtures" / "wellcome-open-portraits-cc-by.json"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SOURCE))

import scripts.benchmark_book as benchmark_book  # noqa: E402
from gramps_fancy_book.renderers import latex_pdf  # noqa: E402


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _load_manifest() -> tuple[dict[str, object], bytes]:
    raw = MANIFEST_PATH.read_bytes()
    manifest = json.loads(raw)
    items = manifest.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError(f"No images listed in {MANIFEST_PATH}.")
    for item in items:
        parsed = urlparse(str(item["download_url"]))
        if parsed.scheme != "https" or parsed.hostname != "iiif.wellcomecollection.org":
            raise ValueError(f"Unexpected image host in manifest: {parsed.netloc}")
        if item.get("license_id") != "cc-by":
            raise ValueError(f"Image is not marked CC BY: {item.get('image_id')}")
        if Path(str(item["local_file"])).name != item["local_file"]:
            raise ValueError(f"Unsafe local filename: {item['local_file']}")
    return manifest, raw


def _prepare_images(
    manifest: dict[str, object], directory: Path
) -> tuple[list[dict[str, object]], dict[str, Path], int, float]:
    from PIL import Image

    items = manifest["items"]
    assert isinstance(items, list)
    directory.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    total_bytes = 0
    started = time.perf_counter()
    for item in items:
        filename = str(item["local_file"])
        path = directory / filename
        if not path.exists():
            request = Request(
                str(item["download_url"]),
                headers={"User-Agent": "Gramps-Fancy-Book-open-media-benchmark"},
            )
            with urlopen(request, timeout=60) as response:
                content = response.read()
            path.write_bytes(content)
        content = path.read_bytes()
        if len(content) != int(item["bytes"]):
            raise ValueError(f"Unexpected byte count for {filename}.")
        if _sha256(content) != item["sha256"]:
            raise ValueError(f"SHA-256 mismatch for {filename}.")
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            if image.format != "JPEG" or image.size != (
                int(item["width"]),
                int(item["height"]),
            ):
                raise ValueError(f"Unexpected JPEG dimensions for {filename}.")
        paths[filename] = path
        total_bytes += len(content)
    return items, paths, total_bytes, time.perf_counter() - started


def _compiler_version() -> str | None:
    compiler = shutil.which("lualatex")
    if compiler is None:
        return None
    result = subprocess.run(
        [compiler, "--version"], capture_output=True, text=True, check=False
    )
    return result.stdout.splitlines()[0] if result.stdout else None


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the JSON report to this path instead of stdout.",
    )
    parser.add_argument(
        "--media-dir",
        type=Path,
        help="Reuse verified JPEGs from this directory; missing files are downloaded.",
    )
    parser.add_argument(
        "--pdf-output-dir",
        type=Path,
        help="Optionally preserve one compiled PDF per repetition in this directory.",
    )
    parser.add_argument(
        "--failure-dir",
        type=Path,
        help="Preserve LaTeX source and log files when a PDF compilation fails.",
    )
    parser.add_argument(
        "--max-derived-side-px",
        type=int,
        help=(
            "Diagnostic only: downsample prepared PNG derivatives so their longest "
            "side is at most this many pixels; source JPEGs remain unchanged."
        ),
    )
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions must be at least 1")
    if args.max_derived_side_px is not None and args.max_derived_side_px < 1:
        parser.error("--max-derived-side-px must be at least 1")
    return args


def main() -> int:
    args = _parse_args()
    manifest, raw_manifest = _load_manifest()
    manifest_items = manifest["items"]
    assert isinstance(manifest_items, list)

    if args.media_dir is None:
        with tempfile.TemporaryDirectory(prefix="gfb-open-portraits-") as folder:
            items, image_paths, source_bytes, acquisition_seconds = _prepare_images(
                manifest, Path(folder)
            )
            report = _run_benchmark(
                args,
                manifest,
                raw_manifest,
                items,
                image_paths,
                source_bytes,
                acquisition_seconds,
            )
    else:
        items, image_paths, source_bytes, acquisition_seconds = _prepare_images(
            manifest, args.media_dir
        )
        report = _run_benchmark(
            args,
            manifest,
            raw_manifest,
            items,
            image_paths,
            source_bytes,
            acquisition_seconds,
        )

    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output is None:
        print(serialized, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    return int(
        any(
            run.get("pdf", {}).get("status") != "compiled"
            for run in report["cases"]
        )
    )


def _run_benchmark(
    args: argparse.Namespace,
    manifest: dict[str, object],
    raw_manifest: bytes,
    items: list[dict[str, object]],
    image_paths: dict[str, Path],
    source_bytes: int,
    acquisition_seconds: float,
) -> dict[str, object]:
    original_snapshot = benchmark_book.synthetic_branching_snapshot
    original_photo = benchmark_book._synthetic_photo
    original_writer = latex_pdf.write_latex_pdf
    original_compile = latex_pdf._compile_latex
    from gramps_fancy_book import media as media_module

    original_prepare_raster = media_module.prepare_raster_derivative
    derivative_png_bytes: dict[str, int] = {}
    active_repeat = 0
    source_hash = _sha256(raw_manifest)
    maximum_width = max(int(item["width"]) for item in items)

    if args.max_derived_side_px is not None:
        from PIL import Image

        max_side = args.max_derived_side_px

        def prepare_with_pixel_limit(source_content, rectangle, *, dpi=None):
            derivative = original_prepare_raster(
                source_content,
                rectangle,
                dpi=dpi,
            )
            with Image.open(BytesIO(derivative.content)) as image:
                image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
                save_options = {"format": "PNG"}
                if derivative.dpi is not None:
                    save_options["dpi"] = (derivative.dpi, derivative.dpi)
                icc_profile = image.info.get("icc_profile")
                if isinstance(icc_profile, bytes):
                    save_options["icc_profile"] = icc_profile
                with BytesIO() as stream:
                    image.save(stream, **save_options)
                    content = stream.getvalue()
                cache_key = hashlib.sha256(
                    f"{derivative.cache_key}:max-side:{max_side}".encode("ascii")
                ).hexdigest()
                derivative_png_bytes[cache_key] = len(content)
                return replace(
                    derivative,
                    cache_key=cache_key,
                    content=content,
                    width=image.width,
                    height=image.height,
                )

        media_module.prepare_raster_derivative = prepare_with_pixel_limit

    def placeholder_photo(seed: int, size: tuple[int, int], *, profile: str) -> bytes:
        del seed, size, profile
        return b""

    def snapshot_with_open_photos(
        descendant_couples: int,
        *,
        include_media: bool = False,
        portrait_size: tuple[int, int] = (1, 1),
        portrait_profile: str = "random",
    ):
        del include_media, portrait_size, portrait_profile
        snapshot, _ = original_snapshot(
            descendant_couples,
            include_media=True,
            portrait_size=(1, 1),
            portrait_profile="random",
        )
        handles = list(snapshot.media)
        if len(handles) != len(items):
            raise ValueError(
                f"Expected {len(items)} media records, got {len(handles)}."
            )
        sources: dict[str, bytes] = {}
        for index, handle in enumerate(handles):
            item = items[index]
            path = image_paths[str(item["local_file"])]
            content = path.read_bytes()
            old = snapshot.media[handle]
            attribution = (
                f"{item['title']} — {item['credit']} (CC BY 4.0)"
            )
            snapshot.media[handle] = replace(
                old,
                path=f"photos/{handle}.jpg",
                mime_type="image/jpeg",
                checksum=_sha256(content),
                description=attribution,
            )
            sources[handle] = content
        return snapshot, sources

    def writer_with_optional_copy(model, pdf_path: Path, **kwargs):
        result = original_writer(model, pdf_path, **kwargs)
        if args.pdf_output_dir is not None:
            args.pdf_output_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(
                pdf_path,
                args.pdf_output_dir / f"wellcome-open-portraits-run-{active_repeat}.pdf",
            )
        return result

    def compile_with_failure_capture(compiler, work_directory: Path, **kwargs):
        try:
            return original_compile(compiler, work_directory, **kwargs)
        except Exception:
            if args.failure_dir is not None:
                failure = args.failure_dir / f"run-{active_repeat}"
                failure.mkdir(parents=True, exist_ok=True)
                for filename in ("book.log", "book.tex"):
                    source = work_directory / filename
                    if source.exists():
                        shutil.copyfile(source, failure / filename)
            raise

    benchmark_book.synthetic_branching_snapshot = snapshot_with_open_photos
    benchmark_book._synthetic_photo = placeholder_photo
    latex_pdf.write_latex_pdf = writer_with_optional_copy
    latex_pdf._compile_latex = compile_with_failure_capture
    try:
        runs = []
        for active_repeat in range(1, args.repetitions + 1):
            run = benchmark_book.benchmark(
                100,
                shape="branching",
                include_media=True,
                portrait_size=(1, 1),
                portrait_profile="random",
                compile_pdf=True,
                extended_pdf_compilation=True,
            )
            run["portrait_size"] = f"variable; maximum width {maximum_width} px"
            run["portrait_profile"] = (
                "wellcome-cc-by-4.0-archival-jpeg"
                if args.max_derived_side_px is None
                else (
                    "wellcome-cc-by-4.0-archival-jpeg-derived-max-side-"
                    f"{args.max_derived_side_px}px"
                )
            )
            run["source_manifest_sha256"] = source_hash
            run["repeat"] = active_repeat
            runs.append(run)
    finally:
        benchmark_book.synthetic_branching_snapshot = original_snapshot
        benchmark_book._synthetic_photo = original_photo
        latex_pdf.write_latex_pdf = original_writer
        latex_pdf._compile_latex = original_compile
        media_module.prepare_raster_derivative = original_prepare_raster

    metric_names = (
        "fixture_seconds",
        "model_seconds",
        "media_prepare_seconds",
        "json_seconds",
        "html_seconds",
        "latex_seconds",
        "html_zip_seconds",
        "media_source_bytes",
        "fixture_heap_bytes",
        "fixture_peak_heap_bytes",
        "peak_additional_heap_bytes",
        "peak_total_heap_bytes",
        "json_bytes",
        "html_bytes",
        "latex_bytes",
        "html_zip_bytes",
        "temporary_workspace_peak_bytes",
    )
    medians = {
        name: statistics.median(float(run[name]) for run in runs)
        for name in metric_names
    }
    medians["pdf_seconds"] = statistics.median(
        float(run["pdf"]["seconds"]) for run in runs
    )
    medians["pdf_bytes"] = statistics.median(
        int(run["pdf"]["bytes"]) for run in runs
    )
    medians["compiler_peak_rss_bytes"] = statistics.median(
        int(run["pdf"]["compiler_peak_rss_bytes"]) for run in runs
    )
    report = {
        "date": datetime.now(UTC).date().isoformat(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "lualatex": _compiler_version(),
        },
        "fixture": {
            "shape": "branching",
            "descendant_couples": 100,
            "family_data": "fully synthetic; no private family data used",
        },
        "source": {
            "publisher": manifest.get("source"),
            "query": manifest.get("query"),
            "license": "CC BY 4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "manifest": str(MANIFEST_PATH.relative_to(ROOT)),
            "manifest_sha256": source_hash,
            "image_count": len(items),
            "total_bytes": source_bytes,
            "maximum_width_px": maximum_width,
            "acquisition_seconds": round(acquisition_seconds, 6),
            "image_files_committed": False,
            "attribution": "Each PDF caption includes the catalogue title, credit, and CC BY 4.0.",
        },
        "method": {
            "benchmark": "Production snapshot-to-book pipeline; N=100; three independent fixture builds by default.",
            "pdf_compilation": "Extended convergent LuaLaTeX compilation; no diagnostic source changes.",
            "placeholder_media": "Synthetic image payloads are stubbed out; snapshot media records are replaced before model building with checksum-verified JPEGs.",
            "image_transform": "Images were requested from Wellcome IIIF at 1600 px maximum width; the largest returned JPEG is 1601 px wide.",
            "compiler_rss_sampling": "100 ms; shorter peaks may be missed.",
            "temporary_workspace_sampling": "100 ms; shorter peaks may be missed.",
            "python_heap": "tracemalloc; excludes native allocations and child processes.",
            "download_time_included_in_benchmarks": False,
        },
        "cases": runs,
        "medians": medians,
    }
    if args.max_derived_side_px is not None:
        report["derivative_variant"] = {
            "policy": (
                "Diagnostic only: resize the prepared, cropped image derivative "
                "with Pillow LANCZOS and store it as lossless PNG. Original JPEG "
                "sources are unchanged."
            ),
            "maximum_side_px": args.max_derived_side_px,
            "unique_derivative_png_bytes": sum(derivative_png_bytes.values()),
        }
        report["method"]["image_transform"] += (
            " The diagnostic option then downsamples the cropped PNG derivative "
            f"to a {args.max_derived_side_px} px maximum side."
        )
    return report


if __name__ == "__main__":
    raise SystemExit(main())
