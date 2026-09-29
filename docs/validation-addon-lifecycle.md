# Add-on package lifecycle validation — September 29, 2026

## Environment and method

- Gramps Desktop 6.0.8 on macOS 27.0 arm64, using its embedded Python 3.13.2.
- Source `main` at commit `106eae276871238b0dd2c373cae5879e7f600119`; add-on registration version `0.9.0`.
- Archive rebuilt with `build_addon.py`: SHA-256 `e99fbe4c9c19c5817c95c97f7ada6020c2a66473445095815dc6e186a63de366`.
- A temporary `GRAMPSHOME` profile was used without opening a personal family tree. Mistune 3.3.4 was installed only into that profile’s library directory. The synthetic GEDCOM and its one-pixel portrait were copied into the temporary directory; Gramps reported `No errors detected` on import.

## Results

| Step | Check | Result |
| --- | --- | --- |
| Install | Extract the archive into the profile, then export an HTML ZIP from the CLI | Gramps discovers the report; the ZIP passes integrity validation and contains `index.html` (2,450 bytes). |
| Reinstall | Replace the complete `GrampsFancyBook/` directory with the same archive built at version `0.9.0`, then export PDF | A new Gramps process discovers the report; the output begins with the `%PDF-` signature (27,971 bytes). |
| Remove | Delete only the installed add-on directory and invoke the report again | Gramps returns `Unknown report name` and creates no output file. |

The temporary profile, dependency, ZIP, and PDF were removed when the check ended. The built archives and output artifacts contain no real family data.

## Scope and limitations

The replacement exercised here reinstalls the same `0.9.0` version; it does not prove an upgrade between two versions. The historical `0.8.0` source at commit `a8c3797`, rebuilt for this check, fails to load under Gramps 6.0.8: its `.gpr.py` calls `get_addon_translator(__file__)`, but Gramps does not inject `__file__` into this registration context. It is therefore not a valid upgrade baseline for this matrix. There is currently no version published in GitHub Releases.

This check used the CLI binary in the Desktop application bundle. It does not qualify the graphical add-on manager, an upgrade between versions, or Gramps Web. Manual steps are in [Build and install](../README.md#build-and-install).
