# QA independente — C1

**Data:** 2026-11-06 UTC  
**Agente:** Patrick Jane  
**Escopo:** artefato candidato C1 após build local; API, filtros, ownership, precisão, exportações, frontend HTTP, responsividade e axe-core. Dados usados foram sintéticos, em Compose isolado `c1-patrick-qa`.

## Parecer

**Reprovado para aceite funcional:** os filtros por data retornam HTTP 500 nas rotas de listagem, resumo e exportação. Isso impede filtrar períodos e impede concluir que resumo e arquivos exportados respeitam períodos selecionados. Os demais cenários abaixo passaram dentro do alcance indicado.

## Evidências executadas

- `mvn -B -ntp verify`: passou; 2 testes, 0 falhas/erros.
- `npm test -- --run`: passou; 4 testes em 2 arquivos.
- `npm run build`: passou; TypeScript e Vite geraram a distribuição.
- Compose C1 subiu PostgreSQL 17.11, API Java 21 e frontend; healthcheck do banco ficou saudável. Recriei API e web depois dos builds e repeti o smoke contra esses artefatos.
- `python3 scripts/smoke-api.py`: passou, 23 casos. Inclui HTTP do frontend, auth, registro duplicado, dois usuários, CRUD, ownership (leitura/edição/exclusão cruzadas 404), paginação, busca literal com `%`, resumo, exportações PDF/XLSX com exclusão de dados de outro usuário e revogação no logout.
- QA complementar: 4 valores inválidos (zero, negativo, mais de duas casas, acima do limite inteiro) e 3 campos inválidos (data impossível, categoria vazia, descrição vazia) retornaram 400. Intervalo invertido, faixa monetária invertida, ordenação inválida, página negativa e tamanho acima de 100 retornaram 400.
- Filtros combinados sem datas (tipo, categoria exata, substring literal com `_` e `%`, mínimo e máximo inclusivos) produziram o mesmo registro na listagem, resumo, PDF e XLSX. O PDF retornou `application/pdf` e assinatura `%PDF`; o XLSX foi aberto como ZIP real e continha a linha selecionada e saldo `-20.10`, sem a linha não selecionada. Comparação monetária feita como decimal exato.

## Achado bloqueante

**Alta — filtros de período retornam 500.** Em requests autenticados com data válida, `startDate` sozinho e `endDate` sozinho falharam. A falha foi reproduzida após reconstruir e iniciar o candidato atual em:

- `GET /transactions?startDate=2026-11-04` e `...?endDate=2026-11-04`;
- `GET /transactions/summary` com cada parâmetro separadamente;
- `GET /transactions/export.pdf` com `startDate` e `/transactions/export.xlsx` com `endDate`.

Todos retornaram JSON com `status: 500`, `error: "Internal Server Error"` e caminho da rota. Antes da reconstrução, também reproduzi as duas datas em todas as quatro rotas (listagem, resumo e PDF/XLSX). O frontend usa esses parâmetros para selecionar período; a falha bloqueia esse requisito. Não investiguei causa no código nem alterei a aplicação.

## Interface, responsividade e acessibilidade

- HTTP `http://localhost:5173/` foi servido com 200; navegador carregou o login. Cadastro e login via interface funcionaram. Um registro sintético criado pela API apareceu no dashboard com `R$ 42,17` de saída e saldo `-R$ 42,17`.
- Axe-core 4.12.1: 0 violações na tela de login e no dashboard populado. Houve verificações incompletas de contraste em conteúdo sobreposto (arte decorativa no login; célula e ações da tabela no dashboard), sem violação reportada. Não é auditoria completa com leitor de tela.
- Com tabela populada, a 360 px: `documentElement.scrollWidth=421`, `body.scrollWidth=360`; `.table-wrap` tinha 308 px de área visível, `scrollWidth=410` e `overflow-x:auto`. A largura maior do documento coincide com o `span.sr` recortado do cabeçalho de ações, cujo retângulo DOM vai de x=383 a x=421. `window.scrollTo(100,0)` manteve `scrollX=0`; portanto medi overflow no documento, mas não confirmei rolagem horizontal visível da página. A tabela tem rolagem horizontal interna.
- Diagnóstico adicional a 320 px: documento 420 px, corpo 320 px e tabela interna 408 px. A 600 px e 1280 px, documento e corpo ficaram na largura do viewport; a 1280 px não houve overflow horizontal.
- Limite do navegador automatizado: a ferramenta não conseguiu preencher o controle nativo `input[type=date]`; por isso não considero validado o envio de um formulário financeiro completo pela UI. O endpoint de período foi testado diretamente e falhou conforme acima.

## Artefatos verificados (SHA-256)

- `backend/target/finance-api-0.1.0.jar` — `c693a2e8d2ea376ed95d1f91ebca4811b6d3a8630009ffb0ffd7f055986aff6f`
- `frontend/dist/index.html` — `402ad466d0bb129c7ec6651bfd99f2fc0e11274d08799473af4fc7b3680d1247`
- `frontend/dist/assets/index-C2F_Rl_q.css` — `06c4c813d99dcaa790612b378e7aafd8d02e007cb6da61deeb4b9b67f7fd8847`
- `frontend/dist/assets/index-Dp81b4dF.js` — `d5832126a507443dff7e44bdfef2402abcc487e0f5d8cf5468269cd7443b591b`
- `frontend/package-lock.json` — `a2da5f9a4458a8840619e97ea0116f136ea243d165d936eafd51f6339e1c9fa2`
- `compose.yaml` — `f418cf44cb780669f21718f1484eeb3b61b41a6994de566acb90241134978243`

O `implementation-checks.json` referencia outro hash para o JAR (`4d8a2a…`). Esta rodada reconstruiu o JAR, executou `mvn verify` e recriou o serviço API antes da reprodução final; o hash acima identifica o artefato usado no runtime desta QA.

## Limites

Não executei CI GitHub, Dependency-Check Java, pentest, carga, nem revisão de segurança. A evidência local anterior registra esses gates pendentes. Não houve alteração de aplicação.
