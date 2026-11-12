# Comparação — consolidação em andamento

Snapshot de 12/11/2026, código integrado em `13f775b94ab5731a4d6ae7b93aebc55513e1c2a8`. Uma execução por cenário, com intervenções corretivas registradas. As quatro aplicações existem e passaram nos mesmos 16 casos HTTP originais e quatro casos complementares. A aprovação integral continua pendente de segurança, QA e CI completa; nenhum vencedor foi demonstrado.

## Configuração efetiva

| Cenário | Orquestração | Modelos | Ressalva |
| --- | --- | --- | --- |
| C1 | Especialistas | Luna na implementação original; Terra nas correções/gates restantes | Mistura autorizada pela A-003, sem reatribuir autoria |
| C2 | Especialistas | Sol | Configuração avançada original |
| C3 | Gerenciador | Terra | Substituição prévia à implementação, A-003 |
| C4 | Gerenciador | Sol | Correção de contrato após avaliação inicial |

As configurações originais e o freeze permanecem preservados. A-001/A-002 atualizaram a baseline comum de segurança; A-003 trata indisponibilidade de modelo. Não se trata de comparação fatorial 2×2 inalterada. Os manifests e as emendas documentam a stack efetiva; o coletor registra os modelos observados por resposta.

## Aceite funcional e operação

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

Snapshot nativo de 12/11/2026 11:38:56 UTC: 3.143 respostas observadas, 39 sessões e dois erros de parse. Os históricos com NUL foram preservados privadamente; não se conhece o consumo perdido. Os totais abaixo são observados, com essa incompletude. Entrada inclui cache; saída inclui raciocínio.

| Cenário | Respostas | Entrada | Saída | Referência API Standard (USD) | Intervalo entre respostas (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| C1 | 954 | 95.499.973 | 304.539 | 2,03292154 | 519.107,874 |
| C2 | 432 | 43.450.614 | 225.418 | 8,47794240 | 44.311,959 |
| C3 | 275 | 22.138.201 | 78.972 | 1,99518580 | 21.574,958 |
| C4 | 186 | 22.017.531 | 108.835 | 4,15418320 | 473.312,834 |
| Overhead | 1.296 | 187.569.287 | 793.988 | Total desconhecido | 554.394,892 |

Fonte: `token-breakdown.json`, `token-events.jsonl`, `metrics.json` e `cost-estimates.json`. A referência usa preços datados de `experiment/evaluation/api-reference-prices.json`, por resposta, com cache descontado e multiplicadores de contexto longo. Não é cobrança da assinatura nem preço atual. Uma resposta do overhead não pôde ser precificada; o subtotal conhecido geral é USD 53,96746070, com total completo `null`. Overhead não é rateado entre cenários. Intervalos incluem pausas, interrupções e retomadas; tempo ativo e duração completa por tarefa são `null`.

O snapshot tem menos tokens de entrada no C4 e menos saída no C3. A menor referência API entre os cenários é C3. São observações desta execução incompleta, sem demonstrar menor custo faturado ou melhor custo-benefício. Não calcular custo por requisito aprovado enquanto os gates integrais estiverem pendentes.

## Agentes, skills, planejamento e revisão

`token-breakdown.{csv,json}` permite agrupar por cenário, modelo, agente, fase e atividade; `cost-estimates.json` oferece agrupamentos alternativos, que não devem ser somados entre si. `token-usage.md` detalha código, documentação, testes, planejamento, revisão e busca. Configuração, atividade mista e ausência de observação são preservadas. Wrappers e scripts dinâmicos podem escapar à detecção de escrita; fase declarada não é atribuição causal do contexto.

Sem rastreamento explícito suficiente, custo por skill, efeito causal de especialistas, tempo ativo e eficiência de revisão ficam não disponíveis. Não usar contagem de mensagens, linhas ou commits como substituto dessas medidas. C4 teve dois defeitos pós-avaliação corrigidos; os demais retrabalhos estão nos pareceres e no ledger, sem contagem consolidada confiável por requisito.

## Qualidade, segurança e conformidade

A revisão independente `experiment/evaluation/architecture-final.md` aprova os controles observados de proprietário, seleção comum e precisão decimal nos quatro cenários. O controle integral REST→Actor→Service/DAO é aprovado no C2 e reprovado no C1/C3 e parcialmente atendido no C4. Não há medição comparável de complexidade, duplicação, cobertura ou carga; esses campos continuam desconhecidos. As estratégias de consulta e exportação têm custos estruturais diferentes documentados no parecer, sem ranking de latência.

Pareceres de segurança e QA próprios de cada cenário são evidências delimitadas, não aprovação global. CI rápida foi exigida nos PRs de implementação; CI completa de promoção, scanner comum atualizado e pentest comum ainda precisam de evidência. O pentest está preparado em A0: a API do GitHub retornou nenhum environment em 12/11, logo falta `pentest-owner` com aprovação exclusiva do dono, além das imagens fixadas e gates exigidos. Não houve A1 nesta retomada.

A [jornada adicional independente do C1](../experiment/evaluation/c1-ui-completion.md), em 12/11, comprovou CRUD, filtros/resumo, downloads e logout pela tela. Desktop 1280 e mobile 360 foram aprovados no escopo observado; filtros a 320 têm excesso visual de cerca de 11 px, sem ação inacessível confirmada. A [auditoria operacional](../experiment/evaluation/operations-completion-audit.md) não encontrou bloqueio operacional adicional no ambiente sintético. O [resumo individual C1](c1-resumo-metricas.md) preserva os números e limites do snapshot.

Vídeos e capturas não provam por si só toda a jornada. `experiment/results/media-validation.json` registra remux e limites históricos; disponibilidade no checkout e cobertura visual são auditadas separadamente. A ausência de vídeo integral deve continuar explícita, com alternativas verificáveis.

## Limitações e próximos resultados necessários

Host e filesystem são compartilhados, sem garantia técnica de cegamento; caches e recursos não foram equalizados. Há uma execução por cenário, versões auxiliares não totalmente congeladas, modelos mistos e intervenções por disponibilidade/segurança. Preparação sobreposta, interrupções, histórico corrompido e overhead elevado impedem inferência estatística ou atribuição causal. Custos reais, tempo ativo, efeito por skill e perdas de telemetria são desconhecidos.

Para fechar: concluir auditorias de QA/segurança, integrar e executar o gate comum de dependências, resolver a configuração externa do pentest, obter sua execução/triagem e a CI completa, e consolidar estados finais conforme a rubrica. A promoção não pode tratar gates ausentes como aprovados.

Recomendações sustentadas pelas lacunas observadas: validar disponibilidade de modelos antes do freeze; tornar testes públicos do contrato executáveis pelos autores sem expor o avaliador privado; manter backup verificável dos eventos; separar orçamento de implementação e overhead; registrar início/fim por tarefa e IDs de rastreamento de skills; planejar bootstrap dos gates protegidos antes de implementar. O efeito dessas mudanças deve ser medido numa nova rodada, com repetições e controle de cache/capacidade, antes de recomendar uma configuração de agentes ou modelo.
