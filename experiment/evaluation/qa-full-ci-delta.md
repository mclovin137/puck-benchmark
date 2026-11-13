Ficha: tarefa=benchmark-recovery agente=patrick-jane modelo=gpt-6.1-sol esforço=medium skill=verificar-antes-de-concluir,receber-revisao,humanizer

# QA do delta de CI e comparação

Parecer de 13/11/2026 UTC: sem achados novos no delta de `reports/comparison.md`, `docs/roadmap.md`, `docs/verificacao.md` e `experiment/evaluation/full-ci-b100f94/`. Este parecer complementa `qa-completion-audit.md`; não aprova globalmente a versão.

## Proveniência e alcance

Consulta independente, somente leitura, por `gh run view 43350462043 --json headSha,status,conclusion,event,jobs` confirmou run concluído com sucesso, evento `pull_request`, head `b100f94ebddaf7e3ae0f1d70ec1bb6c45e67328e` e nove jobs aprovados. As quatro aplicações têm os passos de build/testes e aceite HTTP aprovados. A API de artefatos do mesmo run confirmou os IDs/nomes registrados no manifest e o head associado.

`git rev-parse <sha>^{tree}` confirmou que head e merge de teste `881270edf11c31490b4d712288c65bad2e6e5285` têm a mesma árvore `388eb296af053481297cceb23574d827ce901730`. São commits distintos; a equivalência declarada é de árvore.

Verificação Python de leitura confirmou os 12 SHA256 do manifest e igualdade byte a byte com os arquivos em `/tmp/benchmark-full-ci-artifacts/<acceptance-Cn>/`. Cada seleção pertence ao cenário do próprio artefato; arquivos históricos de outros cenários foram excluídos da prova. C1–C4 apresentam `stage=complete`, `success=true`, `source_clean=true`, `cleanup_success=true` e commit igual ao merge de teste. Cada cenário tem 16 casos originais e quatro complementares, todos aprovados, sem falhas/erros: 80 casos observados no conjunto.

## Números e interpretação

Reagregação de `reports/token-breakdown.json` exclusivamente por cenário e fase (`planejamento` + `revisao`) conferiu todas as cinco linhas novas, incluindo respostas desconhecidas e frações arredondadas com denominador de toda a saída do cenário. Os totais foram confrontados com `reports/metrics.json`. As saídas associadas são overhead 79.011 (9,95%), C1 85.054 (27,93%), C2 39.158 (17,37%), C3 16.579 (20,99%) e C4 20.329 (18,68%). Atividade e agente não foram somados como parcelas adicionais.

Os totais entrada + saída fecham: C4 22.126.366; C3 22.217.173; C2 43.676.032; C1 95.804.512. Cache/raciocínio não foram contados novamente. `cost-estimates.json` confirma C3 USD 1,99518580 e C1 USD 2,03292154 como os dois menores subtotais de referência API por cenário, sem overhead; cobrança real permanece `null`. A redação preserva a distinção entre estimativa, cobrança, contexto associado, tempo e causalidade. Não declara vencedor nem superioridade global a partir de 20 casos HTTP ou de um controle arquitetural.

## Delta dos critérios e limites

- **Critério 7:** a pendência de CI completa não observada no parecer anterior está resolvida para a candidatura `b100f94` e sua árvore de teste. Testes/builds/CI desta candidatura estão aprovados no alcance acima. Alteração posterior requer conferir a validade dos gates no candidato final.
- **Critério 8:** continua parcial. A CI verde não substitui A1, seu teardown e sua triagem, nem elimina componentes afetados admitidos apenas por decisão restrita ao snapshot. Bootstrap/configuração protegida do owner e pentest não foram executados por este QA.
- **Critério 10:** continua parcial. Há nova evidência de CI e comparação mais explícita; métricas finais de continuidade, perdas desconhecidas de telemetria, cobrança indisponível e limites históricos de vídeos permanecem. Os números novos descrevem o snapshot de 12/11 às 11:38:56 UTC, sem incluir o fechamento posterior.

Nenhuma aplicação, suíte, scanner, navegador, restore ou loop de LLM foi executado nesta revisão. Nenhum conteúdo de conversa foi lido. A memória indisponível registrada no quadro não foi tomada como evidência de aprovação. Permanecem válidos os demais limites do QA anterior; este delta não autoriza promoção ou merge.


## R2 — Continuidade da telemetria em 13/11/2026

Ficha: tarefa=benchmark-recovery agente=patrick-jane modelo=gpt-6.1-sol esforço=medium skill=verificar-antes-de-concluir,receber-revisao,humanizer

Sem achados novos no delta de telemetria. Esta seção atualiza somente os números e limites do snapshot; o R1 acima conserva o contexto histórico de 12/11 e a conferência anterior da CI.

A comparação independente de `git show b100f94:reports/token-events.jsonl` com o arquivo atual confirmou 3.143 linhas anteriores byte a byte e igualdade integral dos registros por correlação. Há 3.917 registros únicos, zero anteriores ausentes/alterados e 774 novos, exclusivamente overhead. Os sete pares de SHA256 anteriores/atuais em `telemetry-continuity-20261113.json` conferem com Git e os arquivos atuais.

O snapshot registra corte em 13/11 às 02:19:47,330840 UTC, 46 sessões e os mesmos dois erros de parse. O registro privado de escopo contém uma raiz principal e três continuações explícitas, coerentes com quatro raízes declaradas; nenhum identificador foi publicado por esta revisão. O checkout do Puck está no pin `c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a`; `telemetry.py`, `render_metrics.py` e `reference_costs.py` não diferem de `b100f94`. Não foi reexecutada coleta nem inspecionado conteúdo de sessões/conversas; a cobertura das 46 sessões é metadado declarado, não censo independente da origem nativa. A preservação dos registros anteriores foi verificada diretamente, sem reconstrução ou backfill nesta revisão.

Reagregação dos eventos conferiu todos os grupos de `token-breakdown.json`, contadores de observação, totais de `metrics.json` e ambos os CSVs campo a campo. C1–C4 preservam todos os campos de métricas, exceto o timestamp de geração. Overhead fecha em 2.070 respostas, 305.343.162 tokens de entrada e 1.352.966 de saída. Planejamento + revisão conservam 99 respostas, 19.236.328 de entrada e 79.011 de saída; a fração cai para 5,84% pelo aumento do denominador, e a fase desconhecida reúne 956 respostas. Isso não mede queda de esforço nem aderência a uma meta de tempo.

Recálculo com `Decimal`, preços datados e multiplicadores por resposta confirmou o subtotal conhecido geral de referência API USD 77,86627436 e os subtotais por cenário. Uma resposta continua sem preço; total completo e cobrança real permanecem `null`. A atualização de `comparison.md` explicita o corte, as perdas desconhecidas, o overhead sem rateio e a ausência de conclusão causal. Os números deste snapshot substituem os números correntes de overhead citados em R1, sem invalidar sua conferência histórica.

Nenhum novo teste de aplicação, scan, CI, navegador, restore, pentest ou loop de LLM foi executado. O delta não resolve A1 nem altera o estado parcial dos critérios 8 e 10. Os gates do candidato final continuam sujeitos à conferência própria; este snapshot não representa consumo final completo ou aprovação global.
