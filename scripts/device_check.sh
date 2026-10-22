#!/usr/bin/env bash
set -euo pipefail

for program in hackrf_info hackrf_transfer; do
  if ! command -v "$program" >/dev/null 2>&1; then
    echo "Missing $program. On Ubuntu/Debian: sudo apt install hackrf" >&2
    missing=1
  fi
done

if [[ ${missing:-0} -ne 0 ]]; then
  exit 1
fi

echo "== HackRF device information =="
hackrf_info
echo
echo "Receiver tools are ready. See README.md for receive-only demos."
