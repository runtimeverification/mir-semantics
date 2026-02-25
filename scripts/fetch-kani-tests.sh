#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMIT="$(tr -d '[:space:]' < "$ROOT_DIR/deps/kani_release")"
DEST_DIR="$ROOT_DIR/kmir/src/tests/integration/data/kani"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

repo="$TMP_DIR/kani"
git init -q "$repo"
git -C "$repo" remote add origin https://github.com/model-checking/kani.git
git -C "$repo" fetch --depth 1 origin "$COMMIT"
git -C "$repo" checkout -q FETCH_HEAD

rm -rf "$DEST_DIR"
mkdir -p "$DEST_DIR"

rsync -a --delete "$repo/tests/kani/" "$DEST_DIR/"

echo "Fetched Kani tests at $COMMIT"
echo "  kani .rs files: $(find "$DEST_DIR" -type f -name '*.rs' | wc -l | tr -d ' ')"
