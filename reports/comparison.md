# Comparação — consolidação em andamento

Consolidação de 13/11/2026, fontes da candidatura `b100f94ebddaf7e3ae0f1d70ec1bb6c45e67328e`. Uma execução por cenário, com intervenções corretivas registradas. As quatro aplicações existem e passaram nos mesmos 16 casos HTTP originais e quatro casos complementares. A aprovação integral continua pendente do pentest protegido, sua triagem e da conferência dos gates no candidato final; nenhum vencedor foi demonstrado. A CI completa descrita abaixo passou na primeira candidatura de promoção.

## Configuração efetiva

| Cenário | Orquestração | Modelos | Ressalva |
| --- | --- | --- | --- |
| C1 | Especialistas | Luna na implementação original; Terra nas correções/gates restantes | Mistura autorizada pela A-003, sem reatribuir autoria |
| C2 | Especialistas | Sol | Configuração avançada original |
| C3 | Gerenciador | Terra | Substituição prévia à implementação, A-003 |
| C4 | Gerenciador | Sol | Correção de contrato após avaliação inicial |

As configurações originais e o freeze permanecem preservados. A-001/A-002 atualizaram a baseline comum de segurança; A-003 trata indisponibilidade de modelo. Não se trata de comparação fatorial 2×2 inalterada. Os manifests e as emendas documentam a stack efetiva; o coletor registra os modelos observados por resposta.

## Aceite funcional e operação

Em 13/11/2026 UTC, a [CI completa da promoção](https://github.com/mclovin137/puck-benchmark/actions/runs/43350462043) passou nos nove jobs: código, segurança, testes da infraestrutura, arquitetura, quatro aplicações e gate. Cada aplicação executou build/testes e novamente os 16+4 casos comuns, com fonte limpa e teardown aprovados. A [prova preservada](../experiment/evaluation/full-ci-b100f94/manifest.json) distingue o head `b100f94` do merge de teste `881270e`; as duas árvores Git são idênticas. Os 12 arquivos selecionados vieram exclusivamente do cenário correspondente a cada artefato, com hashes e IDs registrados. Isso não comprova A1, nova jornada UI ou novo restore. A tabela seguinte conserva as execuções históricas locais e suas provas de restore.

| Cenário | Originais | Complementares | Fonte executada | Restore sintético |
| --- | ---: | ---: | --- | --- |
| C1 | 16/16 | 4/4 | `1f552f1`, execução de 11/11 | Aprovado, prova histórica |
| C2 | 16/16 | 4/4 | `1f552f1`, execução de 11/11 | Aprovado, prova histórica |
| C3 | 16/16 | 4/4 | `1f552f1`, execução de 11/11 | Aprovado, prova histórica |
| C4 | 16/16 | 4/4 | `13f775b`, execução de 12/11 | Aprovado em 11/11; não reexecutado nesta rodada |

Provas: `experiment/results/{c1,c2,c3,c4}-acceptance.json`, `*-boundaries.json`, `system-*.json` e `restore-*.json`. Cada JSON preserva seu timestamp e alcance; os resultados C1–C3 podem ser reutilizados porque o código executável desses cenários não mudou. Startup limpo, migração, frontend respondendo e teardown foram observados pelo launcher. Restore compara snapshots das tabelas públicas em banco novo, sem medir recuperação de desastre, RPO ou RTO.

Taxa dos casos HTTP comuns: 20/20 (100%) por cenário. Esse denominador é a suíte executada, não todos os requisitos da especificação. Testes de interface, dez critérios de aceite, cobertura, segurança e conformidade permanecem dimensões separadas.

C4 falhou inicialmente em respostas JSON de erro não UTF-8 e no status de login com senha incorreta curta. A correção independente foi integrada no PR #20, com CI rápida aprovada e revisão de segurança do delta. As falhas originais permanecem em `*-c4-initial.json` e `c4-*-initial.json`. Em 12/11, uma tentativa de restore começou depois do teardown e falhou na identidade do container, antes de acessar o banco; está preservada em `restore-c4-resume-unavailable.json` e não substitui a prova histórica.

## Tokens, referência API e duração

Snapshot nativo de 13/11/2026 02:19:47 UTC: 3.917 respostas observadas, 46 sessões e dois erros de parse. A atualização preserva byte a byte os contadores dos 3.143 eventos anteriores e acrescenta 774 eventos, todos no overhead; nenhum contador de cenário foi alterado. A [prova de continuidade](../experiment/evaluation/telemetry-continuity-20261113.json) registra cobertura e hashes sem IDs nativos. Os históricos com NUL foram preservados privadamente; não se conhece o consumo perdido. Os totais abaixo são observados, com essa incompletude. Entrada inclui cache; saída inclui raciocínio.

| Cenário | Respostas | Entrada | Saída | Referência API Standard (USD) | Intervalo entre respostas (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| C1 | 954 | 95.499.973 | 304.539 | 2,03292154 | 519.107,874 |
| C2 | 432 | 43.450.614 | 225.418 | 8,47794240 | 44.311,959 |
| C3 | 275 | 22.138.201 | 78.972 | 1,99518580 | 21.574,958 |
| C4 | 186 | 22.017.531 | 108.835 | 4,15418320 | 473.312,834 |
| Overhead | 2.070 | 305.343.162 | 1.352.966 | Total desconhecido | 607.244,918 |

Fonte: `token-breakdown.json`, `token-events.jsonl`, `metrics.json` e `cost-estimates.json`. A referência usa preços datados de `experiment/evaluation/api-reference-prices.json`, por resposta, com cache descontado e multiplicadores de contexto longo. Não é cobrança da assinatura nem preço atual. Uma resposta do overhead não pôde ser precificada; o subtotal conhecido geral é USD 77,86627436, com total completo `null`. Overhead não é rateado entre cenários. Intervalos incluem pausas, interrupções e retomadas; tempo ativo e duração completa por tarefa são `null`.

O snapshot tem menos tokens de entrada no C4 e menos saída no C3. A menor referência API entre os cenários é C3. São observações desta execução incompleta, sem demonstrar menor custo faturado ou melhor custo-benefício. Não calcular custo por requisito aprovado enquanto os gates integrais estiverem pendentes.

## Agentes, skills, planejamento e revisão

`token-breakdown.{csv,json}` permite agrupar por cenário, modelo, agente, fase e atividade; `cost-estimates.json` oferece agrupamentos alternativos, que não devem ser somados entre si. `token-usage.md` detalha código, documentação, testes, planejamento, revisão e busca. Configuração, atividade mista e ausência de observação são preservadas. Wrappers e scripts dinâmicos podem escapar à detecção de escrita; fase declarada não é atribuição causal do contexto.

Sem rastreamento explícito suficiente, custo por skill, efeito causal de especialistas, tempo ativo e eficiência de revisão ficam não disponíveis. Não usar contagem de mensagens, linhas ou commits como substituto dessas medidas. C4 teve dois defeitos pós-avaliação corrigidos; os demais retrabalhos estão nos pareceres e no ledger, sem contagem consolidada confiável por requisito.

## Qualidade, segurança e conformidade

A revisão independente `experiment/evaluation/architecture-final.md` aprova os controles observados de proprietário, seleção comum e precisão decimal nos quatro cenários. O controle integral REST→Actor→Service/DAO é aprovado no C2 e reprovado no C1/C3 e parcialmente atendido no C4. Não há medição comparável de complexidade, duplicação, cobertura ou carga; esses campos continuam desconhecidos. As estratégias de consulta e exportação têm custos estruturais diferentes documentados no parecer, sem ranking de latência.

Pareceres de segurança e QA próprios de cada cenário são evidências delimitadas, não aprovação global. CI rápida foi exigida nos PRs de implementação. A auditoria comum de dependências passou no head `da1130a` do PR #26, integrado em `a5e3706`: nove fontes e 1.020 entradas, com oito achados CRITICAL preservados e decisões de não alcançabilidade aplicadas somente ao snapshot revisado. Nenhum alto/crítico ficou sem triagem nesse relatório; o componente continua afetado. Prova: [dependency-ci-da1130a.json](../experiment/evaluation/dependency-ci-da1130a.json), run `43349371614`, policy confiável `8530c564…`, válida até 12/12/2026 e invalidada por mudança de fonte, grafo ou advisory. A CI completa da candidatura `b100f94` passou conforme a prova acima; o pentest comum continua pendente. Alteração posterior exige conferir os gates do novo candidato. O pentest está preparado em A0: a API do GitHub retornou nenhum environment em 12/11, logo falta `pentest-owner` com aprovação exclusiva do dono, além das imagens fixadas e gates exigidos. Não houve A1 nesta retomada.

A [jornada adicional independente do C1](../experiment/evaluation/c1-ui-completion.md), em 12/11, comprovou CRUD, filtros/resumo, downloads e logout pela tela. Desktop 1280 e mobile 360 foram aprovados no escopo observado; filtros a 320 têm excesso visual de cerca de 11 px, sem ação inacessível confirmada. A [auditoria operacional](../experiment/evaluation/operations-completion-audit.md) não encontrou bloqueio operacional adicional no ambiente sintético. O [resumo individual C1](c1-resumo-metricas.md) preserva os números e limites do snapshot.

Vídeos e capturas não provam por si só toda a jornada. `experiment/results/media-validation.json` registra remux e limites históricos; disponibilidade no checkout e cobertura visual são auditadas separadamente. A ausência de vídeo integral deve continuar explícita, com alternativas verificáveis.

## Respostas sustentadas pelo snapshot

As respostas abaixo usam o snapshot nativo de 13/11 às 02:19:47 UTC. Os totais C1–C4 são idênticos aos do snapshot anterior de 12/11; a atualização acrescenta somente overhead de continuidade até o corte informado, sem representar todo o fechamento futuro. São descrições dos contadores observados; perdas de telemetria desconhecidas e intervenções impedem tratá-las como consumo completo ou efeito causal da configuração.

| Pergunta | Resposta e limite |
| --- | --- |
| Qual consumiu menos tokens? | C4 tem o menor total observado de entrada + saída: 22.126.366; C3 tem 22.217.173, C2 43.676.032 e C1 95.804.512. Cache e raciocínio já estão contidos nesses totais. C3 tem a menor saída isolada; C4, a menor entrada. |
| Qual teve menor custo total? | Cobrança real desconhecida em todos. Na referência API datada e sem rateio de overhead, C3 tem o menor subtotal estimado (USD 1,99518580), seguido por C1 (USD 2,03292154). Isso não mede o custo total do experimento nem demonstra economia causal. |
| Qual entregou mais funcionalidades por custo? | Os quatro passaram nos mesmos 20 casos HTTP. C3 combina esse resultado com a menor referência API entre cenários, mas casos de teste não equivalem a funcionalidades independentes e os gates finais não estão todos aprovados. Não há vencedor demonstrado em custo-benefício. |
| Qual produziu código de melhor qualidade? | A fronteira REST→Actor→Service/DAO foi atendida no C2, com limites descritos em architecture-final.md. Esse controle isolado não determina qualidade global; faltam medidas comparáveis de cobertura, complexidade e duplicação. |
| Qual teve menor retrabalho? | Não determinado: correções reais de contrato/UI estão registradas, mas não há série completa e comparável de tentativas, aceites e retrabalho por tarefa. Não usar commits, respostas ou duração de calendário como substitutos. |
| Quanto planejamento e revisão consumiram? | A tabela abaixo soma somente fases declaradas e mutuamente exclusivas. Não soma atividade detectada nem agentes à mesma contagem. Contexto associado não é custo causal, saída não mede tempo, e fases desconhecidas permanecem visíveis. |
| Quais agentes e skills tiveram maior impacto? | token-breakdown.json separa consumo associado a agente/modelo/fase. Não houve contrafactual para medir impacto causal de agentes; falta rastreamento explícito para atribuição por skill, que permanece desconhecida. |
| A especialização compensou? Modelos avançados justificaram investimento? | Não determinado: uma execução por cenário, modelos mistos, disponibilidade, intervenções e overhead sem rateio impedem isolar esses efeitos. A menor tarifa unitária também não garante menor custo por entrega. |
| Quais controles funcionaram e quais geraram overhead? | O aceite externo revelou falhas de contrato preservadas nas evidências iniciais; a auditoria de dependências rejeitou execução inválida e depois aplicou decisões apenas ao snapshot comprovado. Coordenação, instrumentação e avaliação aparecem como overhead separado. Não se mediu quanto desse overhead seria dispensável, nem quais defeitos ocorreriam sem esses controles. |
| Que mudanças mensuráveis testar no Puck? | Pré-validar disponibilidade e bootstrap dos gates; medir tarefas com início/fim, aceite e retrabalho; tornar a cobertura do detector de escrita explícita; manter backup dos eventos e repetir os cenários com controle de recursos. Comparar tokens por entrega aceita e defeitos/retrabalho na nova rodada; não remover gates por uma razão de respostas sem escrita por arquivo. |

| Cenário | Respostas em planejamento + revisão | Entrada associada | Saída associada | Fração da saída do cenário | Respostas com fase desconhecida |
| --- | ---: | ---: | ---: | ---: | ---: |
| overhead | 99 | 19.236.328 | 79.011 | 5,84% | 956 |
| C1 | 215 | 16.687.705 | 85.054 | 27,93% | 29 |
| C2 | 82 | 6.463.104 | 39.158 | 17,37% | 14 |
| C3 | 69 | 4.730.721 | 16.579 | 20,99% | 4 |
| C4 | 28 | 2.108.173 | 20.329 | 18,68% | 5 |

Os denominadores da fração são todas as saídas observadas do respectivo cenário, inclusive fases desconhecidas. Overhead tem denominador próprio. A ausência de marcação impede afirmar que toda análise/revisão foi identificada; a fração não comprova aderência a uma meta de tempo de planejamento/revisão.

## Limitações e próximos resultados necessários

Host e filesystem são compartilhados, sem garantia técnica de cegamento; caches e recursos não foram equalizados. Há uma execução por cenário, versões auxiliares não totalmente congeladas, modelos mistos e intervenções por disponibilidade/segurança. Preparação sobreposta, interrupções, histórico corrompido e overhead elevado impedem inferência estatística ou atribuição causal. Custos reais, tempo ativo, efeito por skill e perdas de telemetria são desconhecidos.

Para fechar: concluir auditorias de QA/segurança, manter o gate de dependências válido no candidato final, resolver a configuração externa do pentest, obter sua execução/triagem, manter a CI completa válida no candidato final e consolidar estados finais conforme a rubrica. A promoção não pode tratar gates ausentes como aprovados.

Recomendações sustentadas pelas lacunas observadas: validar disponibilidade de modelos antes do freeze; tornar testes públicos do contrato executáveis pelos autores sem expor o avaliador privado; manter backup verificável dos eventos; separar orçamento de implementação e overhead; registrar início/fim por tarefa e IDs de rastreamento de skills; planejar bootstrap dos gates protegidos antes de implementar. O efeito dessas mudanças deve ser medido numa nova rodada, com repetições e controle de cache/capacidade, antes de recomendar uma configuração de agentes ou modelo.
