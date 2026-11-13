#!/usr/bin/env bash
set -euo pipefail
python3 -m unittest discover -s benchmark/tests -v
python3 -m unittest discover -s benchmark/pentest/tests -v
if [ -n "${BASE:-}" ] && [ -n "${HEAD:-}" ]; then
  python3 benchmark/scripts/check_applications.py --changed --base "$BASE" --head "$HEAD"
fi
