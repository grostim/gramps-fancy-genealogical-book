# Gramps Web compatibility — static audit — October 1, 2026

## Version and sources reviewed

The latest published API version at the time of this review is Gramps Web API **3.22.3**, published on September 27, 2026 and still marked “Latest” on the releases page on October 1 ([official release](https://github.com/gramps-project/gramps-web-api/releases/tag/v3.22.3), [release list](https://github.com/gramps-project/gramps-web-api/releases)). The reviewed, pinned sources are [`const.py`](https://github.com/gramps-project/gramps-web-api/blob/v3.22.3/gramps_webapi/const.py), [`api/report.py`](https://github.com/gramps-project/gramps-web-api/blob/v3.22.3/gramps_webapi/api/report.py), and [`api/tasks.py`](https://github.com/gramps-project/gramps-web-api/blob/v3.22.3/gramps_webapi/api/tasks.py). The official user guide says the server exposes installed reports and delivers generated files to the browser ([Reports guide](https://www.grampsweb.org/user-guide/reports/)).

An additional check of the public, unversioned `master` branch was updated on October 1 against commit `d21f64171ceb7900a41e4a62aec13cd7cf5465df`, dated September 30. The reviewed sources are pinned to that commit: [`const.py`](https://github.com/gramps-project/gramps-web-api/blob/d21f64171ceb7900a41e4a62aec13cd7cf5465df/gramps_webapi/const.py), [`api/report.py`](https://github.com/gramps-project/gramps-web-api/blob/d21f64171ceb7900a41e4a62aec13cd7cf5465df/gramps_webapi/api/report.py), and [`api/tasks.py`](https://github.com/gramps-project/gramps-web-api/blob/d21f64171ceb7900a41e4a62aec13cd7cf5465df/gramps_webapi/api/tasks.py). It confirms the same blockers as API 3.22.3: filtering through `REPORT_DEFAULTS`, the absence of `.zip` in `MIME_TYPES`, a server-imposed path via `of` under `REPORT_DIR`, and a `generate_report` task that passes no progress callback to `run_report`. This check of `master` is indicative and does not replace the audit pinned to the published release.

## Compatibility gaps found

- `REPORT_DEFAULTS` depends on available libraries: with GTK it allows `CATEGORY_TEXT` and `CATEGORY_DRAW`, plus `CATEGORY_GRAPHVIZ` when Graphviz is installed; without PyGObject, only `CATEGORY_TEXT` is configured. `CATEGORY_WEB` is absent in every case. `get_reports()` filters reports against this list, and `run_report()` rejects unsupported categories with HTTP 404.
- The `MIME_TYPES` dictionary includes `.html`, but not `.zip`. Report generation checks this dictionary before launching a report, so API 3.22.3 cannot return a ZIP archive through this endpoint.
- The API creates a unique path under `REPORT_DIR` and passes it to the report through the standard `of` option. The add-on currently writes to the path received through its custom `destination` option instead of using this server-provided target.
- `generate_report` is an asynchronous task, but it is not bound to the Celery task instance and passes no progress callback to `run_report`. It returns file metadata when generation completes. Other API tasks can publish a `PROGRESS` state; that does not make such progress available for reports today.

These gaps prevent the current integration from satisfying T-01 and AC-22 on API 3.22.3. Reusing the Desktop report engine does not by itself provide compatibility: the server API filters the categories and file types it exposes.

## Privacy behavior already implemented by the add-on

The add-on declares `privacy_acknowledged` as an unchecked-by-default `BooleanOption` and resets it to false when loading prior option values. The report refuses to proceed without confirmation, before reading the database snapshot or creating an output. The registered report description and the option help text provide the warning. This establishes the add-on-side Desktop/CLI behavior; it does not prove that a Web UI can display, translate, or pass the checkbox correctly. The current API filters out the report before that step. See [`GrampsFancyBookOptions.py`](../gramps60/GrampsFancyBook/GrampsFancyBookOptions.py), [`GrampsFancyBook.py`](../gramps60/GrampsFancyBook/GrampsFancyBook.py), and [`GrampsFancyBook.gpr.py`](../gramps60/GrampsFancyBook/GrampsFancyBook.gpr.py).

## Environment and scope

This is an audit of versioned official source, not a running Gramps Web validation. The Mac has the Docker client but no Docker daemon, Docker Compose, Docker Desktop, Colima, or Podman; no Web instance was started.

The add-on must not be advertised as Web-compatible in this state. The next step requires supported Gramps Web handling for `CATEGORY_WEB` reports, ZIP archives, and generated files inside `REPORT_DIR`, or a maintained server adapter providing the same guarantees. Then test report discovery, options, privacy acknowledgement, PDF/ZIP downloads, and task status against a pinned API version. Detailed progress must be part of the contract discussion because `generate_report` does not currently provide it.
