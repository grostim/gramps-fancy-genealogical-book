"""Run veraPDF UA-2 checks; an explicit option permits only missing identification.

The permitted metadata defect is a documented baseline, not a conformance claim.
Raw reports survive failures. Human accessibility qualification remains separate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET


def audit(pdf: Path, executable: str, directory: Path, allow_missing: bool) -> dict:
    pdf = pdf.resolve(strict=True)
    directory.mkdir(parents=True, exist_ok=True)
    # Each invocation gets a new directory: never reuse an earlier successful report.
    report = directory / "report.xml"
    with report.open("xb") as stdout, (directory / "stderr.log").open("xb") as stderr:
        process = subprocess.run(
            [executable, "--flavour", "ua2", "--format", "xml", str(pdf)],
            stdout=stdout, stderr=stderr, timeout=180, check=False,
        )
    if process.returncode not in (0, 1):
        raise ValueError(f"veraPDF failed with exit code {process.returncode}")
    root = ET.parse(report).getroot()
    jobs = root.findall("./jobs/job")
    summary = root.find("batchSummary")
    if len(jobs) != 1 or summary is None or summary.get("totalJobs") != "1":
        raise ValueError("Expected exactly one complete veraPDF job")
    for key in ("failedToParse", "encrypted", "outOfMemory", "veraExceptions"):
        if summary.get(key) != "0":
            raise ValueError(f"veraPDF batch error: {key}={summary.get(key)}")
    item = jobs[0].find("item")
    if (
        item is None or Path(item.findtext("name", "")).resolve() != pdf
        or int(item.get("size", "-1")) != pdf.stat().st_size
    ):
        raise ValueError("veraPDF report does not identify the requested PDF")
    validation = jobs[0].find("validationReport")
    if (
        validation is None or validation.get("jobEndStatus") != "normal"
        or validation.get("profileName") != "PDF/UA-2 + Tagged PDF validation profile"
    ):
        raise ValueError("Missing normal UA-2 validation report")
    details = validation.find("details")
    if details is None:
        raise ValueError("Missing validation details")
    counts = {key: int(details.attrib[key]) for key in (
        "passedRules", "failedRules", "passedChecks", "failedChecks",
    )}
    rules = details.findall("rule")
    if validation.get("isCompliant") not in ("true", "false"):
        raise ValueError("Missing veraPDF compliance status")
    compliant = validation.get("isCompliant") == "true"
    if (
        counts["passedRules"] <= 0 or counts["passedChecks"] <= 0
        or any(value < 0 for value in counts.values())
        or counts["failedRules"] != len(rules)
        or compliant != (counts["failedRules"] == counts["failedChecks"] == 0)
        or process.returncode != (0 if compliant else 1)
    ):
        raise ValueError("Inconsistent or empty veraPDF results")
    failed_rules = [{**rule.attrib, "test": rule.findtext("test"),
                     "description": rule.findtext("description")} for rule in rules]
    permitted = (
        allow_missing and len(rules) == 1 and counts["failedChecks"] == 1
        and rules[0].get("specification") == "ISO 14289-2:2024"
        and rules[0].get("clause") == "5" and rules[0].get("testNumber") == "1"
        and rules[0].get("status") == "failed" and rules[0].get("failedChecks") == "1"
        and rules[0].findtext("object") == "MainXMPPackage"
        and rules[0].findtext("test") == "containsPDFUAIdentification == true"
    )
    result = {
        "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "validator_build": [x.attrib for x in root.findall("./buildInformation/releaseDetails")],
        "is_compliant": compliant, "reported_counts": counts,
        "failed_rules": failed_rules, "allow_missing_identification": allow_missing,
        "known_missing_identification_permitted": permitted,
        "accepted_automated_baseline": compliant or permitted,
        "human_accessibility_qualified": False,
        "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
    }
    (directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def controls(pdf: Path, executable: str, directory: Path) -> list[str]:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import NameObject

    def clone() -> PdfWriter:
        writer = PdfWriter(clone_from=pdf)
        writer.pdf_header = PdfReader(pdf).pdf_header
        return writer

    intact = directory / "intact.pdf"
    clone().write(intact)
    if not audit(intact, executable, directory / "intact", True)["accepted_automated_baseline"]:
        raise ValueError("Intact PDF clone failed the automated baseline")
    rejected = []
    for corruption in ("missing_language", "missing_figure_alt"):
        writer = clone()
        if corruption == "missing_language":
            del writer.root_object[NameObject("/Lang")]
        else:
            pending = [writer.root_object["/StructTreeRoot"]]
            found = False
            while pending:
                node = pending.pop()
                if hasattr(node, "get_object"):
                    node = node.get_object()
                if isinstance(node, (list, tuple)):
                    pending.extend(node)
                elif isinstance(node, dict):
                    if node.get("/S") == "/Figure":
                        del node[NameObject("/Alt")]
                        found = True
                        break
                    if "/K" in node:
                        pending.append(node["/K"])
            if not found:
                raise ValueError("Figure corruption requires a Figure element")
        output = directory / f"{corruption}.pdf"
        writer.write(output)
        result = audit(output, executable, directory / corruption, True)
        if result["accepted_automated_baseline"]:
            raise ValueError(f"veraPDF baseline accepted corruption: {corruption}")
        rejected.append(corruption)
    return rejected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--verapdf", default="verapdf")
    parser.add_argument("--report-directory", required=True, type=Path)
    parser.add_argument("--allow-missing-identification", action="store_true")
    parser.add_argument("--negative-controls", action="store_true")
    args = parser.parse_args()
    result = audit(args.pdf, args.verapdf, args.report_directory, args.allow_missing_identification)
    if args.negative_controls and result["accepted_automated_baseline"]:
        result["rejected_corruptions"] = controls(
            args.pdf, args.verapdf, args.report_directory,
        )
        (args.report_directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["accepted_automated_baseline"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
