#!/usr/bin/env bash
set -euo pipefail
python3 -m compileall -q benchmark
scripts/ci/sintaxe.sh
git diff --check
