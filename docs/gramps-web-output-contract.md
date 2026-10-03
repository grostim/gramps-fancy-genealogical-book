# Proposal: custom-output reports in Gramps Web

**Status:** local discussion draft; not reviewed or accepted by Gramps Web maintainers.

## Context

Gramps Fancy Genealogical Book registers as a `CATEGORY_WEB` report and generates PDF or HTML ZIP files itself. The static audit of Gramps Web API 3.22.3 found that this report category is filtered out, ZIP is not an accepted result type, and the add-on's custom `destination` option is independent of the server-managed path under `REPORT_DIR`. See the [compatibility audit](validation-gramps-web.md).

The add-on needs to keep its Desktop flow. Gramps Web must provide a supported, safe server contract for installed reports that produce their own files.

As of October 3, 2026, v3.22.3 remains the latest published release. A [fresh pinned audit of `master`](validation-gramps-web.md) at commit `375371f` finds the same gaps, so the proposed contract remains relevant. No issue has been submitted to the maintainers.

## Minimum capability to discuss

1. **Explicit report discovery.** The server can expose an installed report that opts into the custom-output contract, without making every report in a new or existing category runnable by default.
2. **Declared output types.** A report can declare supported extensions and MIME types. The first required results are PDF (`application/pdf`) and ZIP (`application/zip`); the server returns the matching filename and content type.
3. **Server-controlled output path.** The API creates a unique target inside `REPORT_DIR` and passes that target to the report through a documented field. A report cannot choose an arbitrary server path. The server verifies the resulting file and removes temporary output after delivery or failure.
4. **Normal option and privacy handling.** The report's family, depth, and format options appear in the Web UI, are validated server-side, and reach the report unchanged after validation. The Gramps `privacy_acknowledged` checkbox remains unchecked by default; the Web flow presents the warning before generation and requires affirmative confirmation. The contract defines this option's input encoding and guarantees that a missing or false value is never interpreted as true. Without confirmation, generation is refused before any write.
5. **Task status and diagnostics.** Generation uses the normal asynchronous task lifecycle. API 3.22.3 does not pass a progress callback for `generate_report`, so the contract must define either report-supported progress or a clearly presented indeterminate running state. Failures should produce actionable logs without exposing private data or server paths.

The exact extension point is for maintainers to choose. It could be a report capability declaration or another documented adapter; the proposal does not require globally enabling `CATEGORY_WEB` or hard-coding this add-on into the API.

## Acceptance checks for an implementation

Against a pinned Gramps Web API version and a synthetic database:

- An opted-in report appears in report discovery; a report without the capability remains hidden when its category is unsupported.
- Family, depth, and format options are validated server-side; an invalid value is rejected before writing. The UI presents the privacy warning and an unchecked-by-default acknowledgement. A missing or false value is rejected before any write; a true value reaches the add-on with the BooleanOption semantics it expects.
- PDF and ZIP results are generated under `REPORT_DIR`, downloaded with the declared extension and MIME type, and open as valid files.
- A report cannot write outside `REPORT_DIR`, overwrite an unrelated file, or leave partial output after failure.
- The UI exposes pending/running/completed/failed states; it presents progress if the contract provides it, otherwise an indeterminate running state. Failures provide useful diagnostics without private data or internal paths.
- Existing Desktop GUI and CLI generation continue to work without Web-specific settings.

## Decision needed

This draft should be discussed with Gramps Web maintainers before implementation. If they prefer a maintained adapter or a narrower output contract, revise this proposal to match their supported approach. Do not claim Gramps Web compatibility until the runtime acceptance checks pass.
