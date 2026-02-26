#!/usr/bin/env bash
set -xeuo pipefail

# Kup relies on cachix registry k-framework-binary.
CACHE="k-framework-binary"
OWNER_REPO="$(git remote get-url origin | sed -E 's#(git@github.com:|https://github.com/)##; s#\.git$##')"
REV="$(git rev-parse HEAD)"
# Get the output of the nix build for kmir.
OUT="$(nix build --no-link --json ".#kmir" | jq -r '.[0].outputs.out')"
KEY="github:${OWNER_REPO}/${REV}#kmir"

SUMMARY="${GITHUB_STEP_SUMMARY:-/dev/stdout}"

{
  echo "## Cachix Publish Summary"
  echo "CACHE: $CACHE"
  echo "OUT: $OUT"
  echo "KEY: $KEY"
} >> "$SUMMARY"

# Verify the Push
HASH="$(basename "$OUT" | cut -d- -f1)"
PUSH_STATUS="$(curl -sS -o /dev/null -w '%{http_code}' "https://${CACHE}.cachix.org/${HASH}.narinfo")" || true
echo "push-http: ${PUSH_STATUS}" >> "$SUMMARY"
if [ "$PUSH_STATUS" -ne 200 ]; then
  echo "push-http: push-failed" >> "$SUMMARY"
  exit 1
fi

# Verify the Pin
if curl -fsSL "https://app.cachix.org/api/v1/cache/${CACHE}/pin" | jq -e --arg k "$KEY" 'any(.[]; .name == $k)' > /dev/null; then
  echo "pin-status: pin-ok" >> "$SUMMARY"
  exit 0
else
  echo "pin-status: pin-missing" >> "$SUMMARY"
  exit 1
fi
