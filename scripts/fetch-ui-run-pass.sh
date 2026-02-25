#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMIT="$(tr -d '[:space:]' < "$ROOT_DIR/deps/rust_release")"
DEST_DIR="$ROOT_DIR/kmir/src/tests/integration/data/ui-run-pass"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

repo="$TMP_DIR/rust"
git init -q "$repo"
git -C "$repo" remote add origin https://github.com/rust-lang/rust.git
git -C "$repo" fetch --depth 1 origin "$COMMIT"
git -C "$repo" checkout -q FETCH_HEAD

UI_ROOT="$repo/tests/ui"
rm -rf "$DEST_DIR"
mkdir -p "$DEST_DIR"

declare -A copied_aux=()
kept=0

while IFS= read -r -d '' src; do
  if ! grep -Eq 'run-pass' "$src"; then
    continue
  fi

  rel="${src#"$UI_ROOT/"}"
  dst="$DEST_DIR/$rel"
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  kept=$((kept + 1))

  src_dir="$(dirname "$src")"
  aux="$src_dir/auxiliary"
  if [[ -d "$aux" ]] && [[ -z "${copied_aux[$src_dir]:-}" ]]; then
    rel_dir="${src_dir#"$UI_ROOT/"}"
    mkdir -p "$DEST_DIR/$rel_dir/auxiliary"
    rsync -a "$aux/" "$DEST_DIR/$rel_dir/auxiliary/"
    copied_aux[$src_dir]=1
  fi
done < <(find "$UI_ROOT" -type f -name '*.rs' -print0)

echo "Fetched rust/ui run-pass tests at $COMMIT"
echo "  ui-run-pass .rs files: $kept"
