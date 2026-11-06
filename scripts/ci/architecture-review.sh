#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
for file in ['experiment/specification.md','experiment/protocol.md','experiment/configs.yaml','docs/rules.md','docs/lib.md','docs/verificacao.md']:
    if not Path(file).is_file():raise SystemExit('Contrato ausente: '+file)
print('Contratos da infraestrutura presentes; arquitetura das aplicações requer avaliação específica.')
PY
