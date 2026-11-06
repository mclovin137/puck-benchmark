# QA independente — C1, rodada 2 (delta)

Data: 2026-11-06 UTC. Continuação da rodada interrompida por quota, com gpt-6.1-terra medium conforme A-003; autoria anterior Luna preservada. Escopo: revalidar o defeito de filtros de data, overflow mobile e regressões relacionadas. Não é aceite integral do produto.

## Resultado

O erro HTTP 500 anterior não foi reproduzido nos oito cruzamentos de `startDate` e `endDate` isolados com listagem, resumo, PDF e XLSX: todos retornaram 200 com corpo não vazio. A smoke também conferiu contagem correta para ambos os limites na listagem e resumo, PDF com assinatura válida para `startDate` e conteúdo filtrado do XLSX para `endDate`. A smoke não comprova conteúdo e totais de todos os cruzamentos de exportação por data.

A anomalia de largura do documento **persiste**, apesar da redução: no dashboard com tabela populada, viewport 360 px apresentou documento 383 px, corpo 360 px e tabela com 308 px de área visível e 410 px de conteúdo; em 320 px, documento 382 px, corpo 320 px e tabela 268/408 px. A tabela usa `overflow-x: auto`. O elemento `.sr` absolutamente posicionado tinha retângulo 381–382 px no viewport de 320 px. `window.scrollTo(100,0)` manteve `scrollX=0` em ambas larguras; portanto permanece uma discrepância DOM mensurável, sem rolagem horizontal visível de página demonstrada. Não se afirma bloqueio funcional de responsividade exclusivamente por essa medição.

## Execução e evidência

- Build do README: `cd frontend && npm ci && npm run build` passou; `cd backend && mvn -B -ntp package -DskipTests` passou, sem executar testes Maven nessa etapa.
- `docker compose -p c1-qa-delta-r2 up -d --build` construiu imagens, mas não criou rede: pool automático do Docker esgotado. Repetição com override temporário somente de IPAM (`10.254.243.0/24`, sem sobreposição observada nas redes e rotas consultadas) iniciou banco saudável, API e web. Portas publicadas do Compose original: loopback 8080 e 5173. Não houve alteração de daemon nem remoção de recursos de terceiros.
- `python3 scripts/smoke-api.py`: passou, 54 casos HTTP relatados; inclui auth, CRUD, ownership negativo, listagem, resumo, filtros, exportações, logout e limites de requisição, conforme script. Dados sintéticos isolados.
- Requisições HTTP adicionais autenticadas verificaram individualmente os oito cruzamentos de parâmetro/rota acima. Essa verificação adicional verificou status e corpo, não semântica completa dos arquivos.
- `agent-browser` em sessão própria: cadastro, login e criação de uma movimentação por formulário, seguida da medição DOM com tabela preenchida em 360 e 320 px. O formulário usou a data inicial apresentada. Não foi realizada auditoria de acessibilidade completa.
- Artefatos de runtime SHA-256: JAR `6834f53cbd28de18cc6c08932ab12fd2778d081cd456e67a4d00b8d282b175e5`; CSS `a5f2f2e960379c59f4cc92632260937e5660b24c85e23723c39df30095cc6058`; JS `d5832126a507443dff7e44bdfef2402abcc487e0f5d8cf5468269cd7443b591b`; Compose `ad55bfc3492e590e53ba6700981299a385d933b4de307ae214d694d48dbe9532`.
- Sessão de navegador, containers, volume, rede e credencial temporária desta rodada foram removidos após os testes.

## Limites

Não executei CI remota, pentest, scanners de segurança, carga ou revisão de arquitetura; seus resultados não são inferidos aqui. Os testes anteriores de QA permanecem no relatório original, com seus próprios artefatos e limites. Este parecer cobre apenas o delta observado e não aprova o cenário integral.
