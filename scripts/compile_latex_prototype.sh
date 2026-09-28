#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work_dir="${LATEX_WORK_DIR:-${repo_root}/.work/latex-spike}"
mkdir -p "$work_dir"
work_dir="$(cd "$work_dir" && pwd)"

LAYOUT_SPIKE_OUTPUT="$work_dir/layout-spike.tex" \
  python3 "$repo_root/prototypes/build_layout.py"

cd "$work_dir"
previous_fingerprint=""
stable=0
for pass in 1 2 3 4 5; do
  lualatex \
    -no-shell-escape \
    -interaction=nonstopmode \
    -halt-on-error \
    -file-line-error \
    layout-spike.tex >"lualatex-pass-${pass}.stdout.log" 2>&1

  files=(layout-spike.aux)
  [[ ! -f layout-spike.toc ]] || files+=(layout-spike.toc)
  [[ ! -f layout-spike.out ]] || files+=(layout-spike.out)
  fingerprint="$(sha256sum "${files[@]}" | sha256sum)"
  if [[ -n "$previous_fingerprint" && "$fingerprint" == "$previous_fingerprint" ]]; then
    stable=1
    break
  fi
  previous_fingerprint="$fingerprint"
done

if [[ "$stable" != "1" ]]; then
  echo "LuaLaTeX references did not stabilize within five passes." >&2
  exit 1
fi

if grep -Eq 'Reference .*undefined|There were undefined references|Label\(s\) may have changed' layout-spike.log; then
  echo "LuaLaTeX reported unresolved or unstable references." >&2
  exit 1
fi

printf 'LuaLaTeX references stabilized after %s passes.\n' "$pass"
printf 'PDF: %s/layout-spike.pdf\n' "$work_dir"
