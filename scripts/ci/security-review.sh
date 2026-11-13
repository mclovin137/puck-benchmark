#!/usr/bin/env bash
set -euo pipefail
if command -v gitleaks >/dev/null; then
  gitleaks git --redact --no-banner --config .gitleaks.toml .
else
  docker run --rm --network none -v "$PWD:/repo:ro" ghcr.io/gitleaks/gitleaks:v8.30.1 detect --source=/repo --config=/repo/.gitleaks.toml --redact
fi
