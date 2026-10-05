"""Compile the print renderer into an atomically installed PDF book."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath

from ..domain import BookModel
from .html_archive import _media_asset_paths
from .latex import render_latex

_MAX_PASSES = 5
_PASS_TIMEOUT_SECONDS = 120
_TOTAL_COMPILATION_TIMEOUT_SECONDS = 180
_EXTENDED_PASS_TIMEOUT_SECONDS = 600
_EXTENDED_TOTAL_COMPILATION_TIMEOUT_SECONDS = 1800
_LAYOUT_WARNING = re.compile(
    r"Reference .*undefined|There were undefined references|"
    r"Label\(s\) may have changed|Overfull \\[hv]box"
)
_TAGGING_METADATA = re.compile(
    r"(\\DocumentMetadata\{[^}\r\n]*?\btagging=)on(?=[,}])"
)
_HYPERREF_PACKAGE = re.compile(
    r"(?P<prefix>\\usepackage)(?:\[(?P<options>[^\]\r\n]*)\])?"
    r"(?P<suffix>\{hyperref\})"
)


def _hyperref_draft_declaration(match: re.Match[str]) -> str:
    options = [
        option.strip()
        for option in (match.group("options") or "").split(",")
        if option.strip()
        and option.split("=", 1)[0].strip().casefold() not in {"draft", "final"}
    ]
    option_string = ",".join(("draft", *options))
    return f"{match.group('prefix')}[{option_string}]{match.group('suffix')}"


class LatexCompilerUnavailable(RuntimeError):
    """Raised when LuaLaTeX is not installed or not discoverable."""


class LatexCompilationError(RuntimeError):
    """Raised when PDF compilation or cross-reference convergence fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def validate_latex_pdf_destination(
    destination: str | Path, *, overwrite: bool = False
) -> Path:
    """Validate a PDF destination before media preparation or compilation."""
    if not str(destination).strip():
        raise ValueError("Select a PDF output file.")
    output = Path(destination).expanduser()
    if output.suffix.casefold() != ".pdf":
        raise ValueError("The PDF destination must end in .pdf.")
    if not output.parent.is_dir():
        raise FileNotFoundError(f"Output directory does not exist: {output.parent}")
    if output.is_dir():
        raise ValueError("The PDF destination cannot be a directory.")
    if output.is_symlink():
        raise ValueError("The PDF destination cannot be a symbolic link.")
    if output.exists() and not overwrite:
        raise FileExistsError(output)
    return output


def write_latex_pdf(
    model: BookModel,
    destination: str | Path,
    *,
    media_asset_directory: str | Path | None = None,
    gramps_type_labels: dict[tuple[str, str], str] | None = None,
    overwrite: bool = False,
    extended_compilation: bool = False,
) -> Path:
    """Compile the shared LaTeX renderer and atomically install its PDF.

    Only prepared, approved PNG derivatives are copied into the temporary build
    directory. Source Gramps media paths are never read or copied here.
    """
    output = validate_latex_pdf_destination(destination, overwrite=overwrite)
    compiler = _find_lualatex()
    if compiler is None:
        raise LatexCompilerUnavailable(
            "LuaLaTeX (lualatex) was not found on PATH or in the standard "
            "macOS TeX location."
        )

    assets = _media_asset_paths(model, media_asset_directory)
    source = render_latex(model, gramps_type_labels=gramps_type_labels)
    with tempfile.TemporaryDirectory(
        prefix=".book-pdf-", dir=output.parent
    ) as temporary:
        work_directory = Path(temporary)
        (work_directory / "book.tex").write_text(source, encoding="utf-8")
        for name, asset_source in sorted(assets.items()):
            relative = PurePosixPath(name)
            asset = work_directory.joinpath(*relative.parts)
            asset.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(asset_source, asset)

        if extended_compilation:
            _compile_latex(
                compiler,
                work_directory,
                pass_timeout_seconds=_EXTENDED_PASS_TIMEOUT_SECONDS,
                total_timeout_seconds=_EXTENDED_TOTAL_COMPILATION_TIMEOUT_SECONDS,
            )
        else:
            _compile_latex(compiler, work_directory)
        compiled_pdf = work_directory / "book.pdf"
        if not compiled_pdf.is_file() or compiled_pdf.is_symlink():
            raise LatexCompilationError("missing_pdf")

        if overwrite:
            os.replace(compiled_pdf, output)
        else:
            # This link is atomic and fails if another process created the target.
            os.link(compiled_pdf, output)
    return output


def _find_lualatex() -> str | None:
    """Find LuaLaTeX on PATH or through the standard macOS TeX symlink."""
    compiler = shutil.which("lualatex")
    if compiler is not None:
        return compiler
    if sys.platform == "darwin":
        macos_compiler = Path("/Library/TeX/texbin/lualatex")
        if macos_compiler.is_file() and os.access(macos_compiler, os.X_OK):
            return str(macos_compiler)
    return None


def _compile_latex(
    compiler: str,
    work_directory: Path,
    *,
    pass_timeout_seconds: int = _PASS_TIMEOUT_SECONDS,
    total_timeout_seconds: int = _TOTAL_COMPILATION_TIMEOUT_SECONDS,
) -> None:
    previous_fingerprint = None
    stable = False
    deadline = time.monotonic() + total_timeout_seconds
    for _pass_number in range(1, _MAX_PASSES + 1):
        remaining_seconds = deadline - time.monotonic()
        if remaining_seconds <= 0:
            raise LatexCompilationError("timeout")
        original_source = None
        if _pass_number == 1:
            # The first PDF is discarded; defer tagging and hyperlink work to later passes.
            source_path = work_directory / "book.tex"
            original_source = source_path.read_text(encoding="utf-8")
            untagged_source, replacements = _TAGGING_METADATA.subn(
                r"\1off", original_source, count=1
            )
            if replacements != 1:
                raise LatexCompilationError("missing_tagging_metadata")
            first_pass_source, replacements = _HYPERREF_PACKAGE.subn(
                _hyperref_draft_declaration, untagged_source, count=1
            )
            if replacements != 1:
                raise LatexCompilationError("missing_hyperref_package")
            source_path.write_text(first_pass_source, encoding="utf-8")
        try:
            result = subprocess.run(
                [
                    compiler,
                    "-no-shell-escape",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-file-line-error",
                    "book.tex",
                ],
                cwd=work_directory,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                check=False,
                timeout=min(pass_timeout_seconds, remaining_seconds),
            )
        except subprocess.TimeoutExpired as error:
            raise LatexCompilationError("timeout") from error
        except OSError as error:
            raise LatexCompilerUnavailable(
                "LuaLaTeX could not be started."
            ) from error
        finally:
            if original_source is not None:
                source_path.write_text(original_source, encoding="utf-8")

        if result.returncode:
            raise LatexCompilationError("compile")

        fingerprint = _auxiliary_fingerprint(work_directory)
        if fingerprint is None:
            raise LatexCompilationError("missing_auxiliary_files")
        if previous_fingerprint is not None and fingerprint == previous_fingerprint:
            stable = True
            break
        previous_fingerprint = fingerprint

    if not stable:
        raise LatexCompilationError("references_unstable")

    log_path = work_directory / "book.log"
    if not log_path.is_file():
        raise LatexCompilationError("missing_log")
    log = log_path.read_text(encoding="utf-8", errors="replace")
    if _LAYOUT_WARNING.search(log):
        raise LatexCompilationError("layout_warnings")


def _auxiliary_fingerprint(work_directory: Path) -> bytes | None:
    digest = hashlib.sha256()
    present = False
    for suffix in ("aux", "toc", "out"):
        path = work_directory / f"book.{suffix}"
        if not path.is_file():
            continue
        present = True
        digest.update(path.name.encode("ascii"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.digest() if present else None
