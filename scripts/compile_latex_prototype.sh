#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work_dir="${LATEX_WORK_DIR:-${repo_root}/.work/latex-spike}"
mkdir -p "$work_dir"
work_dir="$(cd "$work_dir" && pwd)"

LAYOUT_SPIKE_OUTPUT="$work_dir/layout-spike.tex" \
  python3 "$repo_root/prototypes/build_layout.py"

for document in rendered-book.tex rendered-sparse-book.tex; do
  if [[ ! -f "$work_dir/$document" ]]; then
    echo "The production-rendered book fixture is missing: $work_dir/$document" >&2
    exit 1
  fi
done

cd "$work_dir"

compile_document() {
  local document_name="$1"
  local previous_fingerprint=""
  local stable=0
  local pass
  local extension
  local fingerprint
  local files

  for pass in 1 2 3 4 5; do
    lualatex \
      -no-shell-escape \
      -interaction=nonstopmode \
      -halt-on-error \
      -file-line-error \
      "$document_name.tex" >"lualatex-${document_name}-pass-${pass}.stdout.log" 2>&1

    files=("$document_name.aux")
    for extension in toc out; do
      [[ ! -f "$document_name.$extension" ]] || files+=("$document_name.$extension")
    done
    fingerprint="$(sha256sum "${files[@]}" | sha256sum)"
    if [[ -n "$previous_fingerprint" && "$fingerprint" == "$previous_fingerprint" ]]; then
      stable=1
      break
    fi
    previous_fingerprint="$fingerprint"
  done

  if [[ "$stable" != "1" ]]; then
    echo "LuaLaTeX references in $document_name.tex did not stabilize within five passes." >&2
    return 1
  fi

  if grep -Eq 'Reference .*undefined|There were undefined references|Label\(s\) may have changed|Overfull \\[hv]box' "$document_name.log"; then
    echo "LuaLaTeX reported unresolved references, unstable references, or overfull boxes in $document_name.tex." >&2
    return 1
  fi

  printf 'LuaLaTeX references stabilized for %s after %s passes.\n' "$document_name" "$pass"
  printf 'PDF: %s/%s.pdf\n' "$work_dir" "$document_name"
}

compile_document "layout-spike"
compile_document "rendered-book"
compile_document "rendered-sparse-book"
