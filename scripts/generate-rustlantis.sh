#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMIT="$(tr -d '[:space:]' < "$ROOT_DIR/deps/rustlantis_release")"
OUT_DIR="$ROOT_DIR/kmir/src/tests/integration/data/rustlantis"
PROFILE="small"
COUNT=""
SEED_START=0
CALL_SYNTAX=v4
WITH_SMIR=0
CONFIG_OVERRIDE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    --profile)
      PROFILE="$2"
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
    --config)
      CONFIG_OVERRIDE="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

case "$PROFILE" in
  small)
    DEFAULT_COUNT=20
    ;;
  medium)
    DEFAULT_COUNT=20
    ;;
  large)
    DEFAULT_COUNT=10
    ;;
  *)
    echo "Unsupported profile: $PROFILE (expected: small|medium|large)" >&2
    exit 1
    ;;
esac

if [[ -z "$COUNT" ]]; then
  COUNT="$DEFAULT_COUNT"
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

repo="$TMP_DIR/rustlantis"
git init -q "$repo"
git -C "$repo" remote add origin https://github.com/cbeuw/rustlantis.git
git -C "$repo" fetch --depth 1 origin "$COMMIT"
git -C "$repo" checkout -q FETCH_HEAD

cp "$repo/config.toml.example" "$repo/config.toml"

python3 - "$repo/config.toml" "$PROFILE" <<'PY'
from pathlib import Path
import re
import sys

config_path = Path(sys.argv[1])
profile = sys.argv[2]

profiles = {
    'small': {
        'bb_max_len': '4',
        'max_switch_targets': '2',
        'max_bb_count': '4',
        'max_bb_count_hard': '8',
        'max_fn_count': '2',
        'max_args_count': '3',
        'var_dump_chance': '0.15',
        'tuple_max_len': '2',
        'array_max_len': '2',
        'struct_max_fields': '2',
        'adt_max_variants': '2',
        'composite_count': '6',
        'adt_count': '2',
    },
    'medium': {
        'bb_max_len': '16',
        'max_switch_targets': '6',
        'max_bb_count': '20',
        'max_bb_count_hard': '40',
        'max_fn_count': '10',
        'max_args_count': '8',
        'var_dump_chance': '0.45',
        'tuple_max_len': '4',
        'array_max_len': '6',
        'struct_max_fields': '6',
        'adt_max_variants': '4',
        'composite_count': '40',
        'adt_count': '6',
    },
    'large': {
        'bb_max_len': '32',
        'max_switch_targets': '8',
        'max_bb_count': '50',
        'max_bb_count_hard': '100',
        'max_fn_count': '20',
        'max_args_count': '12',
        'var_dump_chance': '0.5',
        'tuple_max_len': '4',
        'array_max_len': '8',
        'struct_max_fields': '8',
        'adt_max_variants': '4',
        'composite_count': '64',
        'adt_count': '8',
    },
}

overrides = profiles[profile]
lines = config_path.read_text().splitlines()
updated: list[str] = []
for line in lines:
    stripped = line.strip()
    replaced = False
    for key, value in overrides.items():
        if re.match(rf'^{re.escape(key)}\s*=\s*', stripped):
            updated.append(f'{key} = {value}')
            replaced = True
            break
    if not replaced:
        updated.append(line)

config_path.write_text('\n'.join(updated) + '\n')
PY

if [[ -n "$CONFIG_OVERRIDE" ]]; then
  if [[ ! -f "$CONFIG_OVERRIDE" ]]; then
    echo "Config override file not found: $CONFIG_OVERRIDE" >&2
    exit 1
  fi

  python3 - "$repo/config.toml" "$CONFIG_OVERRIDE" <<'PY'
from pathlib import Path
import re
import sys

base_path = Path(sys.argv[1])
override_path = Path(sys.argv[2])

override_assignments: dict[str, str] = {}
for raw in override_path.read_text().splitlines():
    line = raw.strip()
    if not line or line.startswith('#') or line.startswith('['):
        continue
    if '=' not in line:
        continue
    key, value = line.split('=', 1)
    key = key.strip()
    if key:
        override_assignments[key] = value.strip()

if not override_assignments:
    raise SystemExit(0)

base_lines = base_path.read_text().splitlines()
output: list[str] = []
seen: set[str] = set()
for raw in base_lines:
    stripped = raw.strip()
    if stripped.startswith('['):
        output.append(raw)
        continue

    replaced = False
    for key, value in override_assignments.items():
        if re.match(rf'^{re.escape(key)}\s*=\s*', stripped):
            output.append(f'{key} = {value}')
            seen.add(key)
            replaced = True
            break

    if not replaced:
        output.append(raw)

insertion_index = 0
for index, raw in enumerate(output):
    if raw.strip().startswith('['):
        insertion_index = index
        break
else:
    insertion_index = len(output)

missing = [f'{key} = {value}' for key, value in override_assignments.items() if key not in seen]
if missing:
    output[insertion_index:insertion_index] = missing

base_path.write_text('\n'.join(output) + '\n')
PY
fi

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
echo "  profile: $PROFILE"
echo "  output dir: $OUT_DIR"
echo "  generated .rs files: $(find "$OUT_DIR" -type f -name '*.rs' | wc -l | tr -d ' ')"
