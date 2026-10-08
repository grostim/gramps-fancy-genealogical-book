"""Measure synthetic snapshot-to-book performance without family data."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import platform
import random
import sys
import tempfile
import threading
import time
import tracemalloc
from collections import deque
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
# Benchmark the checkout being measured even when the virtualenv contains an
# older, non-editable installation of the package.
sys.path.insert(0, str(SOURCE))

from gramps_fancy_book.conventions import BOOK_PROFILE  # noqa: E402
from gramps_fancy_book.domain import (  # noqa: E402
    Attribute,
    ChildRelationship,
    Citation,
    DateValue,
    EditorialMediaArtifact,
    Event,
    EventReference,
    Family,
    Media,
    MediaReference,
    Note,
    ObjectLinks,
    Person,
    Place,
    Repository,
    RepositoryReference,
    Snapshot,
    Source,
    Url,
)
from gramps_fancy_book.normalization import build_book_model  # noqa: E402
from gramps_fancy_book.renderers.html import render_html  # noqa: E402
from gramps_fancy_book.renderers.html_archive import write_html_archive  # noqa: E402
from gramps_fancy_book.renderers.latex import render_latex  # noqa: E402

_MEDIA_INTERVAL = 10
_DEFAULT_PORTRAIT_SIZE = (96, 72)
_MAX_SYNTHETIC_PORTRAIT_PIXELS = 24_000_000
_MAX_SYNTHETIC_MEDIA_SOURCE_BYTES = 256 * 1024 * 1024
_TEMPORARY_WORKSPACE_SAMPLE_SECONDS = 0.1
_COMPILER_RSS_SAMPLE_SECONDS = 0.1
_COMPILER_PROCESS_NAMES = {"lualatex", "luahbtex", "luatex"}


class _TemporaryWorkspaceMonitor:
    """Sample the logical size of files in a temporary benchmark workspace."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._stop = threading.Event()
        self._peak_bytes = 0
        self._thread = threading.Thread(target=self._sample_until_stopped, daemon=True)

    @property
    def peak_bytes(self) -> int:
        return self._peak_bytes

    def __enter__(self) -> _TemporaryWorkspaceMonitor:
        self._sample()
        self._thread.start()
        return self

    def __exit__(self, *_exception_info: object) -> None:
        self._stop.set()
        self._thread.join()
        self._sample()

    def _sample_until_stopped(self) -> None:
        while not self._stop.wait(_TEMPORARY_WORKSPACE_SAMPLE_SECONDS):
            self._sample()

    def _sample(self) -> None:
        total_bytes = 0
        pending = [self._root]
        while pending:
            directory = pending.pop()
            try:
                entries = os.scandir(directory)
            except OSError:
                continue
            with entries:
                for entry in entries:
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            pending.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            total_bytes += entry.stat(follow_symlinks=False).st_size
                    except OSError:
                        continue
        self._peak_bytes = max(self._peak_bytes, total_bytes)


class _CompilerRssMonitor:
    """Sample the peak RSS of LuaTeX descendants during PDF compilation."""

    def __init__(self, root_pid: int) -> None:
        try:
            import psutil
        except ImportError:
            self._psutil = None
        else:
            self._psutil = psutil
        self._root = self._psutil.Process(root_pid) if self._psutil else None
        self._stop = threading.Event()
        self._sample_count = 0
        self._compiler_process_count = 0
        self._peak_rss_bytes = 0
        self._thread = threading.Thread(target=self._sample_until_stopped, daemon=True)

    def __enter__(self) -> _CompilerRssMonitor:
        self._sample()
        if self._root is not None:
            self._thread.start()
        return self

    def __exit__(self, *_exception_info: object) -> None:
        if self._root is not None:
            self._stop.set()
            self._thread.join()
            self._sample()

    def as_dict(self) -> dict[str, object]:
        if self._psutil is None:
            status = "psutil_unavailable"
        elif self._compiler_process_count == 0:
            status = "compiler_process_not_observed"
        else:
            status = "sampled"
        return {
            "compiler_rss_status": status,
            "compiler_peak_rss_bytes": (
                self._peak_rss_bytes if self._compiler_process_count else None
            ),
            "rss_sample_count": self._sample_count,
            "compiler_rss_sample_interval_ms": int(
                _COMPILER_RSS_SAMPLE_SECONDS * 1000
            ),
        }

    def _sample_until_stopped(self) -> None:
        while not self._stop.wait(_COMPILER_RSS_SAMPLE_SECONDS):
            self._sample()

    def _sample(self) -> None:
        if self._root is None:
            return
        self._sample_count += 1
        try:
            children = self._root.children(recursive=True)
        except (
            self._psutil.AccessDenied,
            self._psutil.NoSuchProcess,
            self._psutil.ZombieProcess,
        ):
            return
        for process in children:
            try:
                names = {
                    Path(process.name()).stem.casefold(),
                    Path(process.exe()).stem.casefold(),
                }
                if not names.intersection(_COMPILER_PROCESS_NAMES):
                    continue
                rss_bytes = process.memory_info().rss
            except (
                self._psutil.AccessDenied,
                self._psutil.NoSuchProcess,
                self._psutil.ZombieProcess,
            ):
                continue
            self._compiler_process_count += 1
            self._peak_rss_bytes = max(self._peak_rss_bytes, rss_bytes)


def synthetic_wide_snapshot(descendant_couples: int) -> Snapshot:
    """Create a central couple with many children and one union per child."""
    if descendant_couples < 0:
        raise ValueError("The number of descendant couples cannot be negative.")

    central_handle = "family-central"
    father = Person(
        handle="person-central-father",
        name="Alex Exemple",
        gramps_id="I000001",
        family_handles=(central_handle,),
        links=ObjectLinks(attributes=(Attribute(BOOK_PROFILE, "YES"),)),
    )
    mother = Person(
        handle="person-central-mother",
        name="Camille Exemple",
        gramps_id="I000002",
        family_handles=(central_handle,),
        links=ObjectLinks(attributes=(Attribute(BOOK_PROFILE, "YES"),)),
    )
    children: list[Person] = []
    people = {father.handle: father, mother.handle: mother}
    families: dict[str, Family] = {}

    for index in range(descendant_couples):
        child_handle = f"person-child-{index:06d}"
        partner_handle = f"person-partner-{index:06d}"
        union_handle = f"family-union-{index:06d}"
        child = Person(
            handle=child_handle,
            name=f"Descendant {index:06d}",
            gramps_id=f"I{index + 3:06d}",
            family_handles=(union_handle,),
            parent_family_handles=(central_handle,),
            links=ObjectLinks(attributes=(Attribute(BOOK_PROFILE, "YES"),)),
        )
        partner = Person(
            handle=partner_handle,
            name=f"Partner {index:06d}",
            gramps_id=f"I{index + descendant_couples + 3:06d}",
            family_handles=(union_handle,),
            links=ObjectLinks(attributes=(Attribute(BOOK_PROFILE, "YES"),)),
        )
        children.append(child)
        people[child.handle] = child
        people[partner.handle] = partner
        families[union_handle] = Family(
            handle=union_handle,
            gramps_id=f"F{index + 2:06d}",
            father=child,
            mother=partner,
            relationship="Married",
        )

    reference_family = Family(
        handle=central_handle,
        gramps_id="F0001",
        father=father,
        mother=mother,
        children=tuple(children),
        relationship="Married",
    )
    return Snapshot(
        reference_family=reference_family,
        families=families,
        people=people,
    )


def synthetic_branching_snapshot(
    descendant_couples: int,
    *,
    include_media: bool = False,
    portrait_size: tuple[int, int] = _DEFAULT_PORTRAIT_SIZE,
    portrait_profile: str = "random",
) -> tuple[Snapshot, dict[str, bytes]]:
    """Create a bounded binary descendant tree with editorial records.

    Each couple has up to two children, each child has a partner and a family
    record, and records include dated events, citations, repositories, places
    and publishable notes. When requested, every tenth person has a synthetic
    portrait with a crop region. Portrait dimensions are configurable so the
    media pipeline can also be measured with larger source images.
    """
    if descendant_couples < 0:
        raise ValueError("The number of descendant couples cannot be negative.")

    people: dict[str, Person] = {}
    families: dict[str, Family] = {}
    events: dict[str, Event] = {}
    places: dict[str, Place] = {}
    notes: dict[str, Note] = {}
    citations: dict[str, Citation] = {}
    sources: dict[str, Source] = {}
    repositories = {
        "repository-city": Repository(
            handle="repository-city",
            gramps_id="R0001",
            name="Dépôt municipal synthétique",
            urls=(Url("https://archives.example.test"),),
        )
    }
    media: dict[str, Media] = {}
    media_sources: dict[str, bytes] = {}
    repository_reference = RepositoryReference(
        repository_handle="repository-city",
        call_number="series-test",
        media_type="Book",
    )
    fact_number = 0
    person_number = 0

    def source_for(fact_index: int) -> str:
        source_number = fact_index // 25
        source_handle = f"source-{source_number:05d}"
        if source_handle not in sources:
            sources[source_handle] = Source(
                handle=source_handle,
                gramps_id=f"S{source_number + 1:06d}",
                title=f"Registre synthétique {source_number + 1:05d}",
                author="Atelier de données fictives",
                publication_info="Édition de recette",
                repository_refs=(
                    replace(
                        repository_reference,
                        call_number=f"series-test/{source_number + 1:05d}",
                    ),
                ),
                urls=(
                    Url(
                        f"https://archives.example.test/register/{source_number + 1}"
                    ),
                ),
            )
        return source_handle

    def add_fact(
        event_type: str,
        *,
        media_reference: MediaReference | None = None,
    ) -> tuple[EventReference, str]:
        nonlocal fact_number
        fact_number += 1
        index = fact_number
        event_handle = f"event-{index:07d}"
        citation_handle = f"citation-{index:07d}"
        place_number = index % 20
        place_handle = f"place-{place_number:03d}"
        year = 1700 + index % 300
        places.setdefault(
            place_handle,
            Place(
                handle=place_handle,
                gramps_id=f"P{place_number + 1:04d}",
                name=f"Ville synthétique {place_number + 1:02d}",
                title=f"Commune de recette {place_number + 1:02d}",
            ),
        )
        source_handle = source_for(index)
        media_links = (
            (media_reference,) if media_reference is not None else ()
        )
        citations[citation_handle] = Citation(
            handle=citation_handle,
            gramps_id=f"C{index:07d}",
            source_handle=source_handle,
            page=f"folio {index:04d}",
            date=DateValue(display=str(year), sort_value=year * 10000),
            urls=(
                Url(
                    f"https://archives.example.test/item/{index}",
                    description="Notice numérisée",
                ),
            ),
            links=ObjectLinks(media=media_links),
        )
        events[event_handle] = Event(
            handle=event_handle,
            gramps_id=f"E{index:07d}",
            type=event_type,
            description=f"{event_type} fictif, référence {index:04d}",
            date=DateValue(
                display=f"{year}",
                sort_value=year * 10000,
                ymd=(year, 1, 1),
            ),
            place_handle=place_handle,
            links=ObjectLinks(citations=(citation_handle,)),
        )
        return (
            EventReference(event_handle=event_handle, role="Primary", order=0),
            citation_handle,
        )

    def add_person(
        label: str,
        *,
        family_handles: tuple[str, ...],
        parent_family_handles: tuple[str, ...] = (),
    ) -> Person:
        nonlocal person_number
        person_number += 1
        index = person_number
        handle = f"person-{index:07d}"
        media_reference = None
        if include_media and index % _MEDIA_INTERVAL == 0:
            media_handle = f"media-{index:07d}"
            media_reference = MediaReference(
                media_handle=media_handle,
                rectangle=(5 + index % 16, 5 + index % 12, 94, 94),
                order=0,
            )
            photo = _synthetic_photo(index, portrait_size, profile=portrait_profile)
            media[media_handle] = Media(
                handle=media_handle,
                gramps_id=f"M{index:07d}",
                path=f"photos/{media_handle}.png",
                description=f"Portrait synthétique {index:04d}",
                mime_type="image/png",
                checksum=hashlib.sha256(photo).hexdigest(),
                is_featured=index % 50 == 0,
            )
            media_sources[media_handle] = photo

        event_reference, citation_handle = add_fact(
            "Birth", media_reference=media_reference
        )
        person_notes: tuple[str, ...] = ()
        if index % 12 == 0:
            note_handle = f"note-person-{index:07d}"
            notes[note_handle] = Note(
                handle=note_handle,
                gramps_id=f"N{index:07d}",
                text=(
                    f"Note biographique fictive pour {label}. "
                    "Texte de recette répété sur plusieurs lignes."
                ),
                is_publishable=True,
                links=ObjectLinks(citations=(citation_handle,)),
            )
            person_notes = (note_handle,)
        person = Person(
            handle=handle,
            name=label,
            gramps_id=f"I{index:07d}",
            family_handles=family_handles,
            parent_family_handles=parent_family_handles,
            links=ObjectLinks(
                attributes=(Attribute(BOOK_PROFILE, "YES"),),
                events=(event_reference,),
                notes=person_notes,
                media=((media_reference,) if media_reference is not None else ()),
            ),
        )
        people[handle] = person
        return person

    def add_family(
        handle: str,
        gramps_id: str,
        father: Person,
        mother: Person,
    ) -> Family:
        event_reference, citation_handle = add_fact(
            "Marriage",
            media_reference=father.links.media[0] if father.links.media else None,
        )
        family_notes: tuple[str, ...] = ()
        if len(families) % 10 == 0:
            note_handle = f"note-family-{len(families):07d}"
            notes[note_handle] = Note(
                handle=note_handle,
                gramps_id=f"N{len(families):07d}",
                text=f"Note familiale synthétique pour {gramps_id}.",
                is_publishable=True,
                links=ObjectLinks(citations=(citation_handle,)),
            )
            family_notes = (note_handle,)
        return Family(
            handle=handle,
            gramps_id=gramps_id,
            father=father,
            mother=mother,
            relationship="Married",
            links=ObjectLinks(
                events=(event_reference,),
                notes=family_notes,
                media=father.links.media,
            ),
        )

    central_handle = "family-central"
    central_father = add_person(
        "Alex Exemple",
        family_handles=(central_handle,),
    )
    central_mother = add_person(
        "Camille Exemple",
        family_handles=(central_handle,),
    )
    root = add_family(
        central_handle,
        "F0001",
        central_father,
        central_mother,
    )
    families[central_handle] = root

    queue = deque([root])
    remaining = descendant_couples
    couple_number = 0
    while queue and remaining:
        parent_family = queue.popleft()
        children: list[Person] = []
        relationships: list[ChildRelationship] = []
        child_count = min(2, remaining)
        for child_index in range(child_count):
            union_handle = f"family-union-{couple_number:07d}"
            child = add_person(
                f"Descendant {couple_number + 1:07d}",
                family_handles=(union_handle,),
                parent_family_handles=(parent_family.handle,),
            )
            partner = add_person(
                f"Partner {couple_number + 1:07d}",
                family_handles=(union_handle,),
            )
            children.append(child)
            relationships.append(
                ChildRelationship(
                    person_handle=child.handle,
                    father_relation="Birth",
                    mother_relation="Birth",
                    order=child_index,
                )
            )
            union = add_family(
                union_handle,
                f"F{couple_number + 2:06d}",
                child,
                partner,
            )
            families[union_handle] = union
            queue.append(union)
            couple_number += 1
            remaining -= 1
        families[parent_family.handle] = replace(
            parent_family,
            children=tuple(children),
            child_relationships=tuple(relationships),
        )

    reference_family = families[central_handle]
    return (
        Snapshot(
            reference_family=reference_family,
            families=families,
            people=people,
            events=events,
            places=places,
            notes=notes,
            citations=citations,
            sources=sources,
            repositories=repositories,
            media=media,
        ),
        media_sources,
    )


def _synthetic_photo(
    seed: int,
    size: tuple[int, int] = _DEFAULT_PORTRAIT_SIZE,
    *,
    profile: str = "random",
) -> bytes:
    try:
        from io import BytesIO

        from PIL import Image, ImageFilter
    except ImportError as error:
        raise RuntimeError("Portrait benchmarking requires the optional Pillow package.") from error

    width, height = size
    if profile == "smooth":
        low_size = (max(64, width // 16), max(48, height // 16))
        low_pixels = random.Random(seed).randbytes(low_size[0] * low_size[1] * 3)
        with Image.frombytes("RGB", low_size, low_pixels) as low_resolution:
            with low_resolution.resize(size, Image.Resampling.BICUBIC) as upscaled:
                with upscaled.filter(ImageFilter.GaussianBlur(1.2)) as image:
                    with BytesIO() as stream:
                        image.save(stream, format="PNG")
                        return stream.getvalue()
    if profile != "random":
        raise ValueError(f"Unknown synthetic portrait profile: {profile}")

    pixels = random.Random(seed).randbytes(width * height * 3)
    with BytesIO() as stream:
        Image.frombytes("RGB", (width, height), pixels).save(stream, format="PNG")
        return stream.getvalue()


def _prepare_synthetic_media(model, media_sources: dict[str, bytes], asset_directory: Path) -> None:
    from gramps_fancy_book.media import prepare_raster_derivative

    asset_directory.mkdir()
    written_cache_keys: set[str] = set()
    for placement in model.editorial_book.media_placements:
        uses_by_region = {}
        for use in placement.uses:
            uses_by_region.setdefault(use.media_ref.rectangle, []).append(use)
        for rectangle, uses in uses_by_region.items():
            derivative = prepare_raster_derivative(
                media_sources[placement.media_handle],
                rectangle,
            )
            if derivative.cache_key not in written_cache_keys:
                (asset_directory / f"{derivative.cache_key}.png").write_bytes(
                    derivative.content
                )
                written_cache_keys.add(derivative.cache_key)
            model.media_artifacts.append(
                EditorialMediaArtifact(
                    media_handle=placement.media_handle,
                    rectangle=rectangle,
                    action="reproduce",
                    context_ids=tuple(
                        dict.fromkeys(
                            f"{use.context_type}:{use.context_id}" for use in uses
                        )
                    ),
                    citation_handles=tuple(
                        dict.fromkeys(
                            handle
                            for use in uses
                            for handle in (
                                *use.citation_handles,
                                *use.media_ref.citations,
                            )
                        )
                    ),
                    cache_key=derivative.cache_key,
                    asset_path=f"media/{derivative.cache_key}.png",
                    mime_type=derivative.mime_type,
                    width=derivative.width,
                    height=derivative.height,
                    dpi=derivative.dpi,
                )
            )


def benchmark(
    descendant_couples: int,
    *,
    shape: str,
    include_media: bool = False,
    portrait_size: tuple[int, int] = _DEFAULT_PORTRAIT_SIZE,
    portrait_profile: str = "random",
    compile_pdf: bool = False,
    extended_pdf_compilation: bool = False,
) -> dict[str, object]:
    gc.collect()
    tracemalloc.start()
    try:
        start = time.perf_counter()
        if shape == "wide":
            snapshot = synthetic_wide_snapshot(descendant_couples)
            media_sources = {}
        elif shape == "branching":
            snapshot, media_sources = synthetic_branching_snapshot(
                descendant_couples,
                include_media=include_media,
                portrait_size=portrait_size,
                portrait_profile=portrait_profile,
            )
        else:
            raise ValueError(f"Unknown synthetic shape: {shape}")
        fixture_seconds = time.perf_counter() - start
        fixture_heap, fixture_peak_heap = tracemalloc.get_traced_memory()
        tracemalloc.reset_peak()

        start = time.perf_counter()
        model = build_book_model(snapshot)
        model_seconds = time.perf_counter() - start

        with (
            tempfile.TemporaryDirectory(prefix="gramps-book-benchmark-") as folder,
            _TemporaryWorkspaceMonitor(Path(folder)) as temporary_monitor,
        ):
            temporary = Path(folder)
            media_directory = temporary / "media"
            media_seconds = 0.0
            if media_sources:
                start = time.perf_counter()
                _prepare_synthetic_media(model, media_sources, media_directory)
                media_seconds = time.perf_counter() - start

            start = time.perf_counter()
            json_bytes = len(
                json.dumps(
                    model.to_dict(),
                    ensure_ascii=False,
                    separators=(",", ":"),
                ).encode("utf-8")
            )
            json_seconds = time.perf_counter() - start

            start = time.perf_counter()
            html_bytes = len(
                render_html(model, include_media=bool(model.media_artifacts)).encode(
                    "utf-8"
                )
            )
            html_seconds = time.perf_counter() - start

            start = time.perf_counter()
            latex_bytes = len(render_latex(model).encode("utf-8"))
            latex_seconds = time.perf_counter() - start

            archive_path = temporary / "book.zip"
            start = time.perf_counter()
            write_html_archive(
                model,
                archive_path,
                media_asset_directory=media_directory if model.media_artifacts else None,
            )
            archive_seconds = time.perf_counter() - start
            archive_bytes = archive_path.stat().st_size

            pdf_result: dict[str, object] | None = None
            if compile_pdf:
                from gramps_fancy_book.renderers.latex_pdf import (
                    LatexCompilationError,
                    LatexCompilerUnavailable,
                    write_latex_pdf,
                )

                pdf_path = temporary / "book.pdf"
                start = time.perf_counter()
                with _CompilerRssMonitor(os.getpid()) as rss_monitor:
                    try:
                        write_latex_pdf(
                            model,
                            pdf_path,
                            media_asset_directory=(
                                media_directory if model.media_artifacts else None
                            ),
                            extended_compilation=extended_pdf_compilation,
                        )
                    except LatexCompilerUnavailable as error:
                        pdf_result = {"status": "skipped", "reason": str(error)}
                    except LatexCompilationError as error:
                        pdf_result = {
                            "status": "failed",
                            "seconds": round(time.perf_counter() - start, 6),
                            "reason": error.reason,
                        }
                    else:
                        pdf_result = {
                            "status": "compiled",
                            "seconds": round(time.perf_counter() - start, 6),
                            "bytes": pdf_path.stat().st_size,
                        }
                pdf_result.update(rss_monitor.as_dict())

        temporary_workspace_peak_bytes = temporary_monitor.peak_bytes
        _, peak_heap = tracemalloc.get_traced_memory()
        family_count = len(model.families)
        if model.reference_family.handle not in model.families:
            family_count += 1
        result: dict[str, object] = {
            "shape": shape,
            "descendant_couples": descendant_couples,
            "people": len(model.people),
            "families": family_count,
            "events": len(model.events),
            "notes": len(model.notes),
            "citations": len(model.citations),
            "sources": len(model.sources),
            "media": len(model.media),
            "portrait_size": (
                f"{portrait_size[0]}x{portrait_size[1]}" if include_media else None
            ),
            "portrait_profile": portrait_profile if include_media else None,
            "media_source_bytes": sum(map(len, media_sources.values())),
            "family_notices": len(model.editorial_book.family_notices),
            "family_sections": len(model.genealogy.family_sections),
            "profiles": len(model.editorial_book.profiles),
            "media_artifacts": len(model.media_artifacts),
            "fixture_seconds": round(fixture_seconds, 6),
            "model_seconds": round(model_seconds, 6),
            "media_prepare_seconds": round(media_seconds, 6),
            "json_seconds": round(json_seconds, 6),
            "html_seconds": round(html_seconds, 6),
            "latex_seconds": round(latex_seconds, 6),
            "html_zip_seconds": round(archive_seconds, 6),
            "json_bytes": json_bytes,
            "html_bytes": html_bytes,
            "latex_bytes": latex_bytes,
            "html_zip_bytes": archive_bytes,
            "fixture_heap_bytes": fixture_heap,
            "fixture_peak_heap_bytes": fixture_peak_heap,
            "peak_additional_heap_bytes": max(0, peak_heap - fixture_heap),
            "peak_total_heap_bytes": max(fixture_peak_heap, peak_heap),
            "temporary_workspace_peak_bytes": temporary_workspace_peak_bytes,
        }
        if pdf_result is not None:
            result["pdf"] = pdf_result
        return result
    finally:
        tracemalloc.stop()


def _parse_portrait_size(value: str) -> tuple[int, int]:
    try:
        width, height = (int(part) for part in value.lower().split("x"))
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "portrait size must use WIDTHxHEIGHT with positive integers"
        ) from error
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError(
            "portrait dimensions must both be greater than zero"
        )
    if width * height > _MAX_SYNTHETIC_PORTRAIT_PIXELS:
        raise argparse.ArgumentTypeError(
            "a synthetic portrait cannot exceed 24 million pixels"
        )
    return width, height


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--descendant-couples",
        type=int,
        nargs="+",
        default=(10, 100, 1000),
        metavar="N",
        help="number of synthetic child/partner pairs per benchmark case",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="number of complete measurement repetitions",
    )
    parser.add_argument(
        "--shape",
        choices=("wide", "branching", "both"),
        default="both",
        help="compare the original wide fixture with the richer branching fixture",
    )
    parser.add_argument(
        "--with-media",
        action="store_true",
        help="prepare synthetic portrait crops (requires the optional Pillow package)",
    )
    parser.add_argument(
        "--portrait-size",
        type=_parse_portrait_size,
        default=None,
        metavar="WIDTHxHEIGHT",
        help=(
            "synthetic portrait dimensions in pixels (default: 96x72; "
            "requires --with-media)"
        ),
    )
    parser.add_argument(
        "--portrait-profile",
        choices=("random", "smooth"),
        default="random",
        help=(
            "synthetic portrait pixel profile (default: random; smooth uses seeded "
            "low-resolution texture and blur; requires --with-media)"
        ),
    )
    parser.add_argument(
        "--compile-pdf-for",
        type=int,
        metavar="N",
        help="also compile the branching case with N descendant couples through LuaLaTeX",
    )
    parser.add_argument(
        "--extended-pdf-compilation",
        action="store_true",
        help=(
            "use the renderer's extended PDF pass and total timeouts; only applies "
            "with --compile-pdf-for"
        ),
    )
    arguments = parser.parse_args()
    portrait_size = arguments.portrait_size or _DEFAULT_PORTRAIT_SIZE
    if any(count < 0 for count in arguments.descendant_couples):
        parser.error("all descendant-couple counts must be non-negative")
    if arguments.repeat < 1:
        parser.error("--repeat must be at least 1")
    if (
        arguments.compile_pdf_for is not None
        and arguments.compile_pdf_for not in arguments.descendant_couples
    ):
        parser.error("--compile-pdf-for must be one of the requested descendant-couple counts")
    if arguments.with_media and arguments.shape == "wide":
        parser.error("--with-media requires --shape branching or --shape both")
    if arguments.portrait_size is not None and not arguments.with_media:
        parser.error("--portrait-size requires --with-media")
    if arguments.portrait_profile != "random" and not arguments.with_media:
        parser.error("--portrait-profile requires --with-media")
    if arguments.with_media:
        width, height = portrait_size
        largest_source_set = max(
            ((2 * count + 2) // _MEDIA_INTERVAL) * width * height * 3
            for count in arguments.descendant_couples
        )
        if largest_source_set > _MAX_SYNTHETIC_MEDIA_SOURCE_BYTES:
            parser.error(
                "the requested portraits exceed the 256 MiB synthetic source-media "
                "budget; reduce --descendant-couples or --portrait-size"
            )
    if arguments.compile_pdf_for is not None and arguments.shape == "wide":
        parser.error("--compile-pdf-for requires --shape branching or --shape both")
    if arguments.extended_pdf_compilation and arguments.compile_pdf_for is None:
        parser.error("--extended-pdf-compilation requires --compile-pdf-for")

    shapes = (
        ("wide", "branching")
        if arguments.shape == "both"
        else (arguments.shape,)
    )
    cases = []
    for repetition in range(1, arguments.repeat + 1):
        for shape in shapes:
            for count in arguments.descendant_couples:
                result = benchmark(
                    count,
                    shape=shape,
                    include_media=arguments.with_media and shape == "branching",
                    portrait_size=portrait_size,
                    portrait_profile=arguments.portrait_profile,
                    compile_pdf=(
                        arguments.compile_pdf_for == count and shape == "branching"
                    ),
                    extended_pdf_compilation=arguments.extended_pdf_compilation,
                )
                result["repeat"] = repetition
                cases.append(result)
    report = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "memory_metric": (
            "tracemalloc Python heap; excludes native allocations and subprocesses"
        ),
        "pdf_rss_metric": (
            "sampled RSS of LuaTeX compiler processes; 100 ms interval, so shorter "
            "peaks may be missed; requires psutil"
        ),
        "temporary_workspace_metric": (
            "sampled logical file sizes under the benchmark temporary directory; "
            f"sample interval {int(_TEMPORARY_WORKSPACE_SAMPLE_SECONDS * 1000)} ms; "
            "shorter-lived peaks may be missed"
        ),
        "media_enabled": arguments.with_media,
        "portrait_size": (
            f"{portrait_size[0]}x{portrait_size[1]}"
            if arguments.with_media
            else None
        ),
        "portrait_profile": (
            arguments.portrait_profile if arguments.with_media else None
        ),
        "repetitions": arguments.repeat,
        "extended_pdf_compilation": arguments.extended_pdf_compilation,
        "pdf_compile_case": (
            {
                "shape": "branching",
                "descendant_couples": arguments.compile_pdf_for,
            }
            if arguments.compile_pdf_for is not None
            else None
        ),
        "cases": cases,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
