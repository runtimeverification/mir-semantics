#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WRAPPER_DIR="$ROOT_DIR/deps/.stable-mir-json"

if ! command -v nix >/dev/null 2>&1; then
  exit 0
fi

zlib_path="$(nix eval --raw nixpkgs#zlib.outPath 2>/dev/null || true)"
if [[ -z "$zlib_path" ]]; then
  exit 0
fi

for wrapper in "$WRAPPER_DIR/debug.sh" "$WRAPPER_DIR/release.sh"; do
  [[ -f "$wrapper" ]] || continue

  if grep -q "$zlib_path/lib" "$wrapper"; then
    continue
  fi

  tmp_file="${wrapper}.tmp"
  awk -v prefix="$zlib_path/lib" '
    /^export LD_LIBRARY_PATH=/ {
      sub(/^export LD_LIBRARY_PATH=/, "export LD_LIBRARY_PATH=" prefix ":")
      print
      next
    }
    { print }
  ' "$wrapper" > "$tmp_file"
  mv "$tmp_file" "$wrapper"
  chmod +x "$wrapper"
done
