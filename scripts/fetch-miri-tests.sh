#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMIT="$(tr -d '[:space:]' < "$ROOT_DIR/deps/miri_release")"
DEST_BASE="$ROOT_DIR/kmir/src/tests/integration/data"
DEST_PASS="$DEST_BASE/miri-pass"
DEST_FAIL="$DEST_BASE/miri-fail"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

repo="$TMP_DIR/miri"
git init -q "$repo"
git -C "$repo" remote add origin https://github.com/rust-lang/miri.git
git -C "$repo" fetch --depth 1 origin "$COMMIT"
git -C "$repo" checkout -q FETCH_HEAD

rm -rf "$DEST_PASS" "$DEST_FAIL"
mkdir -p "$DEST_PASS" "$DEST_FAIL"

rsync -a --delete "$repo/tests/pass/" "$DEST_PASS/"
rsync -a --delete "$repo/tests/fail/" "$DEST_FAIL/"

echo "Fetched Miri tests at $COMMIT"
echo "  miri-pass .rs files: $(find "$DEST_PASS" -type f -name '*.rs' | wc -l | tr -d ' ')"
echo "  miri-fail .rs files: $(find "$DEST_FAIL" -type f -name '*.rs' | wc -l | tr -d ' ')"
