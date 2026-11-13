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

## Patch v0.1.1

A correção de runtime foi admitida na dev pelo PR #33, fonte `b5d680d8f158d4edd60495cda9333acca1919b71`. A CI rápida `43428886931` e a auditoria `43428886919` passaram no candidato revisado. O artefato conferido contém nove fontes, 1.020 pacotes, oito CRITICAL com decisões restritas aplicadas e zero não triados; não demonstra ausência global de vulnerabilidades. O PR #34 admitiu previamente os novos vínculos de fonte, sem renovar a expiração ou alterar as decisões.

Nesta árvore preparatória, somente três dos 16 imports diferem da v0.1.0. Severino executou 20 testes do verificador após RED/GREEN, incluindo patch sobre base não vazia e negativos de origem/base/manifesto; AST e diff check passaram. O algoritmo de validação e a allowlist continuam preservados, com origem/base/ref fixadas para este patch. A conferência Git do candidato, revisão independente e CI hospedada permanecem exigidas antes da admissão. Os 38 testes de guardas são fixtures inertes; não são execução A1. Nenhum controle remoto ou aplicação foi acionado por esta preparação.

CI do patch: `43437264247` aprovada no head `2688528`, com 20 testes do bootstrap e 38 de guardas confirmados nos logs. A auditoria hospedada cobriu npm (3/3 pacotes) e PyPI (1 principal e 1 suplemento), sem advisories reportados; artefato SHA-256 `5bc68056e02bd518b39ed740786ba9cd7188f487248060c1a322893163f07cb9`. O parecer R1 v0.1.1 foi confirmado e congelado pelo Neo. A preparação da promoção muda apenas documentação; exige nova CI no SHA pertinente e CI verde em main antes da tag. Nenhum A1 foi executado por esse gate.

## Patch v0.1.2

A fonte `450d1b250e707eed682c2e0bf4f9bd8699b7a3b9` foi admitida pelo PR #39 após CI rápida `43447835065` e auditoria real `43447835078`. O artefato conferido contém nove fontes, 1.020 pacotes, oito CRITICAL com decisões exatas aplicadas e zero não triados; SHA-256 `abda09fa57b8b899a600ccfa7a78d4e304d52cef238ece3c666f965ca00f9e12`. A política foi admitida antes pelo PR #38, sem mudar decisões ou validade.

Neo R1 combinada executou 41 testes de guardas e 77 controles independentes; R2 conferiu os dois pins e a continuidade dos hashes. Isso é evidência A0, com APIs simuladas nos controles, e não A1 ou comprovação de cache. A árvore preparatória ainda exige sua revisão de transporte/proveniência, fixtures e CI hospedada antes da promoção; dois imports mudam e os outros 14 são preservados. Nenhuma aplicação ou controle remoto foi acionado por esta preparação.

Severino executou RED/GREEN dos pins e da ref antiga; 20 testes do verificador passaram na versão v0.1.2. A fixture de patch tem baseline não vazia de 30 caminhos, 10 alterações e preservação dos 14 imports, além dos negativos de origem/base/manifesto/histórico/ref/merge. AST e diff check passaram. O parser e as regras de auditoria não mudaram; a CI hospedada e a revisão de proveniência ainda são exigidas antes da admissão.

CI do patch `43449647441` aprovada no head `7a835ca`: logs confirmam 20 testes bootstrap e 41 fixtures de guardas. A auditoria npm/PyPI reportou duas fontes aprovadas sem advisories no escopo, artefato SHA-256 `5bc68056e02bd518b39ed740786ba9cd7188f487248060c1a322893163f07cb9`. Neo R1 de transporte foi concluída e congelada. A preparação posterior altera somente registro de evidências e roadmap; CI do novo SHA e da main continuam exigidas antes da tag. Não houve A1 por esses testes.

## Patch v0.1.3 — contexto C1

Fonte admitida `908047555ea8808d7c263f42adb62692a043a225`, PR #44. CI rápida43507218043 (88+41 testes e segredos) e auditoria43507218020 aprovadas no head revisado K5. Artefato SHA-256 ec6a5e93624cd1532232c4b392b25be79a27f8eb094a8c8eda533291d30edbf1: nove fontes/1.020 pacotes, oito CRITICAL com decisões exatas aplicadas e zero não triados. A política confiável e84832fc4b388fa7b0278fe3d9f764a161c61bf8 foi admitida antes dos pins, sem renovar validade.

O transporte altera somente a policy de contexto entre os imports; helper/manifesto/fixtures fixam fonte, baseline v0.1.2 e ref exata da task. Algoritmos e allowlist permanecem iguais. Testes bootstrap e guardas são fixtures inertes, sem A1. Somente CI A0 e revisão próprias deste transporte podem aprovar a preparação; não atribuir resultados de aplicação a esta árvore.
