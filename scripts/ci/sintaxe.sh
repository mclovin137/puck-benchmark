#!/usr/bin/env bash
# Checagem rápida de sintaxe para PRs de implementação (ci-rapida.yml). Adapte à stack: parse de
# configs, compile/lint rápido. Deve rodar em segundos; testes ficam para a CI completa da versão.
set -euo pipefail
for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null; done
for f in $(git ls-files '*.sh'); do bash -n "$f"; done
