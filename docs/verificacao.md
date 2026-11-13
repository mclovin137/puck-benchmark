# Verificação A0

- `python3 scripts/ci/bootstrap.py verify --base <SHA-base> --head <SHA-head>` confere árvores de Git, contexto do evento, imports da fonte fixa e escopo; não aprova A1.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s benchmark/bootstrap -v` verifica os negativos do gate em fixtures locais.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s benchmark/pentest/tests -v` executa fixtures inertes das guardas, sem containers, navegador ou request real.
- AST dos Python, parse dos JSON e `node --check benchmark/pentest/ui-security.cjs` conferem sintaxe, sem executar a aplicação.
- `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci --ignore-scripts --no-audit --no-fund` em cópia temporária do manifest/lock verifica resolução, sem navegador ou hooks de instalação.
- O instalador fixado seguido de `python3 scripts/ci/bootstrap.py audit --scanner <binário-fixado> --report <arquivo-fora-da-árvore>` verifica duas fontes com OSV neutro. Não cobre apt/imagens e não aplica triagem de apps. Artefatos públicos contêm somente metadados sanitizados.

Os comandos acima são o contrato de verificação, não um relato antecipado de sucesso. Resultados locais, CI e limites observados constarão no PR/parecer. actionlint não executado por indisponibilidade local; sem alegação de validação por essa ferramenta. Não houve A1, alteração de controles do GitHub ou deploy nesta preparação.

Preparação local em 13/11/2026, Python 3.14.4 e Node 24.16.0: Oráculo executou as 35 fixtures A0 existentes, conferência byte a byte dos 16 imports, AST, sintaxe Node e resolução npm isolada sem hooks/navegador. Severino informou 14 testes do novo verificador aprovados; scanner nesses testes foi simulado. A execução real de OSV e a CI ainda não foram observadas neste ponto. Não houve A1.

Após as correções locais, Severino informou 17 testes focados aprovados e executou OSV real com o binário fixado: npm 3/3 pacotes, PyPI 1 principal e 1 suplemento, sem advisories reportados. O Oráculo conferiu o relatório sanitizado. O parser agora exige caminho exato, cobertura principal e avalia também os suplementos; essa última alteração ainda não recebeu revisão independente adicional. O parecer R2 preserva esse bloqueio de admissão; CI ainda pendente. Isso não é aprovação global de segurança nem A1.

Revisão extra focada autorizada pelo dono: Neo encerrou B-03, conferiu 18 casos independentes e a CI `43359114747` no head `78b2585`. Logs da CI confirmam 17 + 35 testes A0 (52 no total); o artefato npm/PyPI foi conferido por hash. A revisão R3 em `docs/bootstrap-security.md` sustenta admissão no escopo preparatório; publicar o parecer exige CI no novo SHA. Nenhuma aplicação, A1, proteção remota ou imagem/apt foi aprovada por essa conclusão.
