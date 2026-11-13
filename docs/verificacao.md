# Verificação A0

- `python3 scripts/ci/bootstrap.py verify --base <SHA-base> --head <SHA-head>` confere árvores de Git, contexto do evento, imports da fonte fixa e escopo; não aprova A1.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s benchmark/bootstrap -v` verifica os negativos do gate em fixtures locais.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s benchmark/pentest/tests -v` executa fixtures inertes das guardas, sem containers, navegador ou request real.
- AST dos Python, parse dos JSON e `node --check benchmark/pentest/ui-security.cjs` conferem sintaxe, sem executar a aplicação.
- `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci --ignore-scripts --no-audit --no-fund` em cópia temporária do manifest/lock verifica resolução, sem navegador ou hooks de instalação.
- O instalador fixado seguido de `python3 scripts/ci/bootstrap.py audit --scanner <binário-fixado> --report <arquivo-fora-da-árvore>` verifica duas fontes com OSV neutro. Não cobre apt/imagens e não aplica triagem de apps. Artefatos públicos contêm somente metadados sanitizados.

Os comandos acima são o contrato de verificação, não um relato antecipado de sucesso. Resultados locais, CI e limites observados constarão no PR/parecer. actionlint não executado por indisponibilidade local; sem alegação de validação por essa ferramenta. Não houve A1, alteração de controles do GitHub ou deploy nesta preparação.

Preparação local em 13/11/2026, Python 3.14.4 e Node 24.16.0: Oráculo executou as 35 fixtures A0 existentes, conferência byte a byte dos 16 imports, AST, sintaxe Node e resolução npm isolada sem hooks/navegador. Severino informou 14 testes do novo verificador aprovados; scanner nesses testes foi simulado. A execução real de OSV e a CI ainda não foram observadas neste ponto. Não houve A1.
