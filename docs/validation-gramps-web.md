# Gramps Web compatibility — static audit — September 29, 2026

## Version and sources reviewed

The latest published API version at the time of this audit is Gramps Web API **3.22.3** ([official release](https://github.com/gramps-project/gramps-web-api/releases/tag/v3.22.3)). The reviewed files are [`const.py` at v3.22.3](https://github.com/gramps-project/gramps-web-api/blob/v3.22.3/gramps_webapi/const.py) and its [`api/report.py`](https://github.com/gramps-project/gramps-web-api/blob/v3.22.3/gramps_webapi/api/report.py). The official user guide says the server exposes installed reports and delivers generated files to the browser ([Reports guide](https://www.grampsweb.org/user-guide/reports/)).

## Compatibility gaps found

- `REPORT_DEFAULTS` allows `CATEGORY_TEXT` and `CATEGORY_DRAW`, plus `CATEGORY_GRAPHVIZ` when Graphviz is available; `CATEGORY_WEB` is absent. The `get_reports()` function therefore hides the current report, which registers as `CATEGORY_WEB`. `run_report()` also rejects a category missing from that table with HTTP 404.
- The `MIME_TYPES` dictionary does not declare `.zip`. Even if the report were listed, the generation endpoint cannot create a ZIP response under its current output-type contract.
- The API chooses an `of` path under `REPORT_DIR`, then expects a file matching the selected extension and MIME type. The add-on currently writes to the path supplied through its custom `destination` option instead of that server-managed path.

These three gaps prevent the current integration from satisfying T-01 and AC-22 on API 3.22.3. Reusing the Desktop report engine does not by itself provide compatibility: the server API filters the categories and file types it exposes.

## Environment and scope

This is an audit of versioned official source, not a running Gramps Web validation. The Mac has the Docker client but no Docker daemon, Docker Compose, Docker Desktop, Colima, or Podman; no Web instance was started. The repository and private mockups were not modified for this audit.

The add-on must not be advertised as Web-compatible in this state. The next step requires supported Gramps Web handling for `CATEGORY_WEB` reports, ZIP archives, and generated files inside `REPORT_DIR`, or a maintained server adapter providing the same guarantees. Then test report discovery, options, privacy acknowledgement, PDF/ZIP downloads, and task progress/logging against a pinned API version.
