"""Measure the Gramps report's real database extraction on synthetic GEDCOM trees.

The reported adapter time is instrumented inside the isolated add-on copy. The
end-to-end time and resident-memory peak include Gramps startup, GEDCOM import,
snapshot extraction, model construction, and JSON serialization.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "gramps60" / "download" / "GrampsFancyBook.addon.tgz"
PLUGIN_ID = "gramps_fancy_genealogical_book"
_BENCHMARK_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c636000020000050001a5f645400000000049454e44ae426082"
)
ADAPTER_CALL = """            snapshot = adapter.read_snapshot_by_gramps_id(
                gramps_id,
                max_ancestor_depth=max_ancestor_depth,
                max_descendant_depth=max_descendant_depth,
            )
"""
MODEL_CALL = """            model = build_book_model(
                snapshot,
                max_ancestor_depth=max_ancestor_depth,
                max_descendant_depth=max_descendant_depth,
            )
"""


def _synthetic_gedcom(descendant_couples: int, scenario: str = "branching") -> str:
    """Build a fictional Gramps tree for one extraction performance scenario."""
    people: list[dict[str, object]] = []
    families: list[dict[str, object]] = []
    notes: list[tuple[str, str]] = []

    def add_person(given: str, surname: str, sex: str, generation: int) -> dict[str, object]:
        person = {
            "id": f"I{len(people) + 1:04d}",
            "given": given,
            "surname": surname,
            "sex": sex,
            "generation": generation,
            "parent_family": None,
            "spouse_families": [],
            "note": None,
        }
        people.append(person)
        return person

    def add_family(father: dict[str, object], mother: dict[str, object], generation: int) -> dict[str, object]:
        family = {
            "id": f"F{len(families) + 1:04d}",
            "father": father,
            "mother": mother,
            "children": [],
            "generation": generation,
            "note": None,
        }
        families.append(family)
        father["spouse_families"].append(family["id"])
        mother["spouse_families"].append(family["id"])
        return family

    first = add_person("Alex", "Exemple", "M", 0)
    second = add_person("Camille", "Exemple", "F", 0)
    central_family = add_family(first, second, 0)
    queue = deque([central_family])
    descendant_number = 0
    descendants: list[dict[str, object]] = []

    if scenario == "ancestors":
        # N successive ancestor unions, split between the two central partners.
        # One parent in each new union continues the line, keeping the graph deep
        # without making its size exponential.
        focuses = [first, second]
        for index in range(descendant_couples):
            side = index % 2
            generation = -(index // 2 + 1)
            father = add_person(f"Ancestor {index * 2 + 1:06d}", "Fictif", "M", generation)
            mother = add_person(f"Ancestor {index * 2 + 2:06d}", "Fictif", "F", generation)
            family = add_family(father, mother, generation)
            child = focuses[side]
            family["children"].append(child)
            child["parent_family"] = family["id"]
            focuses[side] = father
    elif scenario in {"branching", "multiple-unions", "pedigree-collapse", "media"}:
        while descendant_number < descendant_couples:
            parent_family = queue.popleft()
            for _ in range(2):
                if descendant_number >= descendant_couples:
                    break
                descendant_number += 1
                generation = int(parent_family["generation"]) + 1
                descendant_sex = "M" if descendant_number % 2 else "F"
                descendant = add_person(
                    f"Descendant {descendant_number:06d}",
                    "Fictif",
                    descendant_sex,
                    generation,
                )
                descendants.append(descendant)
                partner = add_person(
                    f"Partner {descendant_number:06d}",
                    "Fictif",
                    "F" if descendant_sex == "M" else "M",
                    generation,
                )
                parent_family["children"].append(descendant)
                descendant["parent_family"] = parent_family["id"]
                father, mother = (
                    (descendant, partner)
                    if descendant_sex == "M"
                    else (partner, descendant)
                )
                queue.append(add_family(father, mother, generation))
        if scenario == "multiple-unions":
            for index, descendant in enumerate(descendants, start=1):
                sex = "F" if descendant["sex"] == "M" else "M"
                spouse = add_person(
                    f"Second partner {index:06d}", "Fictif", sex,
                    int(descendant["generation"]),
                )
                add_family(descendant, spouse, int(descendant["generation"]))
        elif scenario == "pedigree-collapse":
            # Add a scaled number of cousin unions to the bounded descendant
            # tree. The cousins are children of siblings in separate families.
            family_by_id = {family["id"]: family for family in families}
            cousin_groups: dict[
                tuple[int, str], dict[str, list[dict[str, object]]]
            ] = {}
            for descendant in descendants:
                parent_family = family_by_id.get(descendant["parent_family"])
                if parent_family is None:
                    continue
                shared_ancestor_families = {
                    parent["parent_family"]
                    for parent in (parent_family["father"], parent_family["mother"])
                    if parent["parent_family"]
                }
                for ancestor_family_id in shared_ancestor_families:
                    family_groups = cousin_groups.setdefault(
                        (int(descendant["generation"]), str(ancestor_family_id)), {}
                    )
                    family_groups.setdefault(parent_family["id"], []).append(descendant)

            cousin_pairs = []
            target_pairs = descendant_couples // 5
            for (_, ancestor_family_id), family_groups in sorted(cousin_groups.items()):
                family_ids = sorted(family_groups)
                for left_index in range(0, len(family_ids) - 1, 2):
                    left_candidates = family_groups[family_ids[left_index]]
                    right_candidates = family_groups[family_ids[left_index + 1]]
                    for left in left_candidates:
                        right = next(
                            (
                                candidate
                                for candidate in right_candidates
                                if candidate["sex"] != left["sex"]
                            ),
                            None,
                        )
                        if right is not None:
                            cousin_pairs.append((left, right, int(left["generation"])))
                            right_candidates.remove(right)
                            break
                    if len(cousin_pairs) >= target_pairs:
                        break
                if len(cousin_pairs) >= target_pairs:
                    break
            if len(cousin_pairs) != target_pairs:
                raise RuntimeError(
                    f"Could not construct {target_pairs} cousin unions; "
                    f"constructed {len(cousin_pairs)}."
                )
            for index, (cousin_a, cousin_b, generation) in enumerate(cousin_pairs, start=1):
                father, mother = (
                    (cousin_a, cousin_b)
                    if cousin_a["sex"] == "M"
                    else (cousin_b, cousin_a)
                )
                family = add_family(father, mother, generation)
                child = add_person(f"Collapsed line {index:06d}", "Fictif", "F", generation + 1)
                family["children"].append(child)
                child["parent_family"] = family["id"]
    else:
        raise ValueError(f"Unknown synthetic scenario: {scenario}")

    for index, person in enumerate(people, start=1):
        if index % 12 == 0:
            note_id = f"N{len(notes) + 1:04d}"
            person["note"] = note_id
            notes.append((note_id, f"Synthetic publication note for person {index:06d}."))
    for index, family in enumerate(families, start=1):
        if index % 10 == 0:
            note_id = f"N{len(notes) + 1:04d}"
            family["note"] = note_id
            notes.append((note_id, f"Synthetic family note for family {index:06d}."))

    lines = [
        "0 HEAD",
        "1 SOUR GRAMPS_FANCY_BOOK_BENCHMARK",
        "1 GEDC",
        "2 VERS 5.5.1",
        "2 FORM LINEAGE-LINKED",
        "1 CHAR UTF-8",
    ]
    media_number = 0
    for index, person in enumerate(people, start=1):
        birth_year = 1650 + index % 300
        lines.extend(
            [
                f"0 @{person['id']}@ INDI",
                f"1 NAME {person['given']} /{person['surname']}/",
                f"1 SEX {person['sex']}",
                "1 BIRT",
                f"2 DATE {birth_year}",
                f"2 PLAC Town {index % 25 + 1:02d}, Example County",
                "2 SOUR @S0001@",
                f"3 PAGE Birth register folio {index:06d}",
            ]
        )
        if scenario == "media" and index % 10 == 0:
            media_number += 1
            lines.append(f"1 OBJE @M{media_number:06d}@")
        if person["parent_family"]:
            lines.append(f"1 FAMC @{person['parent_family']}@")
        for family_id in person["spouse_families"]:
            lines.append(f"1 FAMS @{family_id}@")
        if person["note"]:
            lines.append(f"1 NOTE @{person['note']}@")

    for index, family in enumerate(families, start=1):
        marriage_year = 1670 + index % 300
        lines.extend(
            [
                f"0 @{family['id']}@ FAM",
                f"1 HUSB @{family['father']['id']}@",
                f"1 WIFE @{family['mother']['id']}@",
            ]
        )
        lines.extend(f"1 CHIL @{child['id']}@" for child in family["children"])
        lines.extend(
            [
                "1 MARR",
                f"2 DATE {marriage_year}",
                f"2 PLAC Town {index % 25 + 1:02d}, Example County",
                "2 SOUR @S0001@",
                f"3 PAGE Marriage register folio {index:06d}",
            ]
        )
        if family["note"]:
            lines.append(f"1 NOTE @{family['note']}@")

    for index in range(1, media_number + 1):
        lines.extend(
            [
                f"0 @M{index:06d}@ OBJE",
                f"1 FILE benchmark-media/media-{index:06d}.png",
                "2 FORM png",
                f"1 TITL Synthetic benchmark image {index:06d}",
            ]
        )

    lines.extend(
        [
            "0 @S0001@ SOUR",
            "1 TITL Synthetic parish registers",
            "1 AUTH Example Archives",
            "1 PUBL Performance fixture; no real family data",
            "1 REPO @R0001@",
            "2 CALN BENCHMARK",
            "2 MEDI BOOK",
            "0 @R0001@ REPO",
            "1 NAME Synthetic municipal archive",
        ]
    )
    for note_id, note_text in notes:
        lines.extend([f"0 @{note_id}@ NOTE", f"1 CONT {note_text}"])
    lines.append("0 TRLR")
    return "\n".join(lines) + "\n"


def _expected_counts(size: int, scenario: str) -> dict[str, int]:
    if scenario in {"branching", "media"}:
        people, families = 2 + 2 * size, 1 + size
    elif scenario == "ancestors":
        people, families = 2 + 2 * size, 1 + size
    elif scenario == "multiple-unions":
        people, families = 2 + 3 * size, 1 + 2 * size
    else:  # pedigree-collapse
        collapse_unions = size // 5
        people, families = 2 + 2 * size + collapse_unions, 1 + size + collapse_unions
    expected = {
        "people": people,
        "families": families,
        "events": people + families,
        "citations": people + families,
        "media": people // 10 if scenario == "media" else 0,
    }
    return expected


def _mistune_source() -> Path:
    spec = importlib.util.find_spec("mistune")
    if spec is None:
        raise RuntimeError(
            "Install mistune in the Python environment running this script; "
            "the module is copied into the isolated Gramps profile."
        )
    if spec.submodule_search_locations:
        return Path(next(iter(spec.submodule_search_locations)))
    if spec.origin:
        return Path(spec.origin).parent
    raise RuntimeError("Could not locate the mistune Python package.")


def _install_isolated_addon(profile: Path, mistune: Path) -> Path:
    plugin_home = profile / "gramps" / "gramps60" / "plugins"
    plugin_home.mkdir(parents=True)
    with tarfile.open(ADDON) as archive:
        archive.extractall(plugin_home, filter="data")

    plugin = plugin_home / "GrampsFancyBook"
    shutil.copytree(mistune, plugin_home / "lib" / "mistune")
    report = plugin / "GrampsFancyBook.py"
    source = report.read_text(encoding="utf-8")
    if source.count(ADAPTER_CALL) != 1 or source.count(MODEL_CALL) != 1:
        raise RuntimeError("The packaged report structure changed; update the benchmark hook.")
    source = source.replace(
        "import tempfile\n",
        "import json\nimport tempfile\nimport time\n",
        1,
    )
    source = source.replace(
        ADAPTER_CALL,
        """            _benchmark_adapter_started = time.perf_counter()
            snapshot = adapter.read_snapshot_by_gramps_id(
                gramps_id,
                max_ancestor_depth=max_ancestor_depth,
                max_descendant_depth=max_descendant_depth,
            )
            _benchmark_adapter_seconds = time.perf_counter() - _benchmark_adapter_started
""",
        1,
    )
    source = source.replace(
        MODEL_CALL,
        """            _benchmark_model_started = time.perf_counter()
            model = build_book_model(
                snapshot,
                max_ancestor_depth=max_ancestor_depth,
                max_descendant_depth=max_descendant_depth,
            )
            _benchmark_metrics_path = os.environ.get("GFBOOK_BENCHMARK_METRICS")
            if _benchmark_metrics_path:
                with open(_benchmark_metrics_path, "w", encoding="utf-8") as _metrics_file:
                    json.dump(
                        {
                            "adapter_seconds": _benchmark_adapter_seconds,
                            "model_seconds": time.perf_counter() - _benchmark_model_started,
                            "people": len(snapshot.people),
                            "families": len(snapshot.families),
                            "events": len(snapshot.events),
                            "citations": len(snapshot.citations),
                            "notes": len(snapshot.notes),
                            "places": len(snapshot.places),
                            "sources": len(snapshot.sources),
                            "repositories": len(snapshot.repositories),
                            "media": len(snapshot.media),
                        },
                        _metrics_file,
                        sort_keys=True,
                    )
""",
        1,
    )
    report.write_text(source, encoding="utf-8")
    return plugin


def _resident_bytes(stderr: str) -> int | None:
    match = re.search(r"(?m)^\s*(\d+)\s+maximum resident set size\s*$", stderr)
    return int(match.group(1)) if match else None


def _gramps_versions(executable: Path, profile: Path) -> tuple[str | None, str | None]:
    profile.mkdir(parents=True)
    env = os.environ.copy()
    env.update(
        {
            "GRAMPSHOME": str(profile),
            "XDG_CACHE_HOME": str(profile / "cache"),
            "LANGUAGE": "en",
        }
    )
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [str(executable), "--version"],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"Could not read Gramps version:\n{result.stdout}{result.stderr}")
    gramps_match = re.search(r"(?mi)^\s*gramps\s*:\s*(.+)$", result.stdout)
    python_match = re.search(r"(?mi)^\s*python\s*:\s*(.+)$", result.stdout)
    return (
        gramps_match.group(1).strip() if gramps_match else None,
        python_match.group(1).strip() if python_match else None,
    )


def _run_case(
    executable: Path,
    gedcom: Path,
    output_directory: Path,
    scenario: str,
    descendant_couples: int,
    repetition: int,
    mistune: Path,
) -> dict[str, object]:
    profile = output_directory / f"profile-{scenario}-{descendant_couples}-{repetition}"
    profile.mkdir()
    _install_isolated_addon(profile, mistune)
    env = os.environ.copy()
    env.update(
        {
            "GRAMPSHOME": str(profile),
            "XDG_CACHE_HOME": str(profile / "cache"),
            "LANGUAGE": "en",
        }
    )
    env.pop("PYTHONPATH", None)

    destination = output_directory / f"snapshot-{scenario}-{descendant_couples}-{repetition}.json"
    metrics_path = output_directory / f"metrics-{scenario}-{descendant_couples}-{repetition}.json"
    env["GFBOOK_BENCHMARK_METRICS"] = str(metrics_path)
    options = (
        f"name={PLUGIN_ID},reference_family=F0001,"
        "output_format=json_snapshot,privacy_acknowledged=True,"
        f"destination={destination}"
    )
    command = [
        "/usr/bin/time",
        "-l",
        str(executable),
        "-q",
        "-y",
        "-i",
        str(gedcom),
        "-a",
        "report",
        "-p",
        options,
    ]
    started = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=output_directory,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    elapsed = time.perf_counter() - started
    log = result.stdout + result.stderr
    if result.returncode or not destination.is_file() or not metrics_path.is_file():
        raise RuntimeError(
            f"Gramps extraction case N={descendant_couples}, run={repetition} failed.\n"
            f"Exit: {result.returncode}\n{log[-8000:]}"
        )

    model = json.loads(destination.read_text(encoding="utf-8"))
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    if model["reference_family"]["gramps_id"] != "F0001":
        raise RuntimeError("The synthetic reference family was not selected in Gramps.")
    expected_counts = _expected_counts(descendant_couples, scenario)
    actual_counts = {name: metrics[name] for name in expected_counts}
    if actual_counts != expected_counts:
        raise RuntimeError(
            f"Gramps imported unexpected record counts: {actual_counts}; "
            f"expected {expected_counts}."
        )
    return {
        "scenario": scenario,
        "descendant_couples": descendant_couples,
        "repetition": repetition,
        "people": len(model["people"]),
        "families": len(model["families"]),
        "events": len(model["events"]),
        "citations": len(model["citations"]),
        "notes": len(model["notes"]),
        "places": len(model["places"]),
        "sources": len(model["sources"]),
        "repositories": len(model["repositories"]),
        "media": len(model["media"]),
        "adapter_seconds": metrics["adapter_seconds"],
        "model_seconds": metrics["model_seconds"],
        "end_to_end_seconds": elapsed,
        "resident_bytes": _resident_bytes(result.stderr),
        "json_bytes": destination.stat().st_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gramps", type=Path, required=True, help="Gramps 6 CLI executable")
    parser.add_argument(
        "--scenario",
        choices=("branching", "ancestors", "multiple-unions", "pedigree-collapse", "media"),
        nargs="+",
        default=("branching",),
        help="synthetic graph shapes to measure",
    )
    parser.add_argument(
        "--descendant-couples",
        type=int,
        nargs="+",
        default=(10, 100, 1000),
        metavar="N",
        help="scenario size parameter (descendant couples or ancestor families)",
    )
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--output", type=Path, help="optional path for the JSON report")
    arguments = parser.parse_args()
    executable = arguments.gramps.expanduser().resolve()
    if not executable.is_file():
        parser.error(f"Gramps executable does not exist: {executable}")
    if sys.platform != "darwin" or not Path("/usr/bin/time").is_file():
        parser.error("This benchmark currently requires macOS /usr/bin/time -l.")
    if arguments.repeat < 1 or any(count < 0 for count in arguments.descendant_couples):
        parser.error("Repeat count must be positive and descendant counts non-negative.")

    subprocess.run([sys.executable, str(ROOT / "build_addon.py")], cwd=ROOT, check=True)
    mistune = _mistune_source()
    with tempfile.TemporaryDirectory(prefix="gramps-fancy-book-extraction-") as temporary:
        work = Path(temporary)
        gramps_version, gramps_python = _gramps_versions(
            executable,
            work / "version-profile",
        )
        records: list[dict[str, object]] = []
        for scenario in arguments.scenario:
            for count in arguments.descendant_couples:
                scenario_directory = work / scenario
                scenario_directory.mkdir(exist_ok=True)
                gedcom = scenario_directory / f"synthetic-{count}.ged"
                gedcom.write_text(_synthetic_gedcom(count, scenario), encoding="utf-8")
                if scenario == "media":
                    media_directory = scenario_directory / "benchmark-media"
                    media_directory.mkdir(exist_ok=True)
                    for media_number in range(1, _expected_counts(count, scenario)["media"] + 1):
                        (media_directory / f"media-{media_number:06d}.png").write_bytes(
                            _BENCHMARK_PNG
                        )
                for repetition in range(1, arguments.repeat + 1):
                    records.append(
                        _run_case(
                            executable,
                            gedcom,
                            scenario_directory,
                            scenario,
                            count,
                            repetition,
                            mistune,
                        )
                    )

        medians = []
        for scenario in arguments.scenario:
            for count in arguments.descendant_couples:
                cases = [
                    row
                    for row in records
                    if row["scenario"] == scenario and row["descendant_couples"] == count
                ]
                median_row: dict[str, object] = {
                    "scenario": scenario,
                    "descendant_couples": count,
                    "people": cases[0]["people"],
                    "families": cases[0]["families"],
                    "events": cases[0]["events"],
                    "citations": cases[0]["citations"],
                    "notes": cases[0]["notes"],
                    "places": cases[0]["places"],
                    "sources": cases[0]["sources"],
                    "repositories": cases[0]["repositories"],
                    "media": cases[0]["media"],
                }
                for metric in (
                    "adapter_seconds",
                    "model_seconds",
                    "end_to_end_seconds",
                    "resident_bytes",
                    "json_bytes",
                ):
                    values = [case[metric] for case in cases if case[metric] is not None]
                    median_row[metric] = statistics.median(values) if values else None
                medians.append(median_row)

    report = {
        "gramps_executable": str(executable),
        "gramps_version": gramps_version,
        "gramps_python": gramps_python,
        "host_python": sys.version.split()[0],
        "platform": sys.platform,
        "repetitions": arguments.repeat,
        "scenarios": list(arguments.scenario),
        "timing_scope": (
            "adapter_seconds measures GrampsDatabaseAdapter.read_snapshot_by_gramps_id; "
            "end_to_end_seconds and resident_bytes include Gramps startup, GEDCOM import, "
            "adapter extraction, model construction, and JSON export"
        ),
        "medians": medians,
        "runs": records,
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if arguments.output:
        output = arguments.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
        print(output)
    else:
        print(rendered)


if __name__ == "__main__":
    main()
