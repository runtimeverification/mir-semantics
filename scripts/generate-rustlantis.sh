#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMIT="$(tr -d '[:space:]' < "$ROOT_DIR/deps/rustlantis_release")"
OUT_DIR="$ROOT_DIR/kmir/src/tests/integration/data/rustlantis"
COUNT=10
SEED_START=0
CALL_SYNTAX=v4
WITH_SMIR=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    --count)
      COUNT="$2"
      shift 2
      ;;
    --seed-start)
      SEED_START="$2"
      shift 2
      ;;
    --call-syntax)
      CALL_SYNTAX="$2"
      shift 2
      ;;
    --with-smir)
      WITH_SMIR=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

repo="$TMP_DIR/rustlantis"
git init -q "$repo"
git -C "$repo" remote add origin https://github.com/cbeuw/rustlantis.git
git -C "$repo" fetch --depth 1 origin "$COMMIT"
git -C "$repo" checkout -q FETCH_HEAD

cp "$repo/config.toml.example" "$repo/config.toml"

if cargo +nightly --version >/dev/null 2>&1; then
  cargo +nightly build --manifest-path "$repo/Cargo.toml" -p generate --release
else
  cargo build --manifest-path "$repo/Cargo.toml" -p generate --release
fi

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

for ((i = 0; i < COUNT; i++)); do
  seed=$((SEED_START + i))
  out_file="$OUT_DIR/seed-${seed}.rs"
  (
    cd "$repo"
    target/release/generate --call-syntax "$CALL_SYNTAX" "$seed"
  ) > "$out_file"
done

if [[ "$WITH_SMIR" -eq 1 ]]; then
  SMIR_TOOL=""
  if [[ -x "$ROOT_DIR/deps/.stable-mir-json/release.sh" ]]; then
    SMIR_TOOL="$ROOT_DIR/deps/.stable-mir-json/release.sh"
  elif [[ -x "$ROOT_DIR/deps/.stable-mir-json/debug.sh" ]]; then
    SMIR_TOOL="$ROOT_DIR/deps/.stable-mir-json/debug.sh"
  elif command -v stable_mir_json >/dev/null 2>&1; then
    SMIR_TOOL="$(command -v stable_mir_json)"
  else
    echo "No stable_mir_json executable found; skipping .smir.json generation" >&2
  fi

  if [[ -n "$SMIR_TOOL" ]]; then
    for src in "$OUT_DIR"/*.rs; do
      "$SMIR_TOOL" -Zno-codegen --out-dir "$OUT_DIR" "$src"
    done
  fi
fi

echo "Generated Rustlantis corpus at commit $COMMIT"
echo "  output dir: $OUT_DIR"
echo "  generated .rs files: $(find "$OUT_DIR" -type f -name '*.rs' | wc -l | tr -d ' ')"
