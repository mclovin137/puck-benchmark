# C1 — resumo de métricas

Atualizado em 12/11/2026. **Implementação e aceite funcional verificados; fechamento integral pendente.** Este resumo será atualizado quando os gates finais forem concluídos.

## Resultado da aplicação

| Verificação | Resultado |
| --- | --- |
| Aceite HTTP comum | **20/20 casos aprovados (100%)**: 16 originais + 4 complementares |
| Backend | Maven verify: **12 testes aprovados**, reexecutados em 12/11 |
| Frontend | **4 testes aprovados** e build aprovado, reexecutados em 12/11 |
| Interface | Cadastro/login, criação, edição, exclusão, filtros/resumo, PDF/XLSX e logout pela tela aprovados no escopo observado |
| Responsividade | Desktop 1280 e mobile 360 verificados; ressalva visual de cerca de 11 px nos filtros a 320, sem ação inacessível confirmada |
| Operação | Startup Compose, migração e limpeza aprovados; restore sintético histórico aprovado |
| Ainda pendente | Scanner comum atual/triagem, pentest A1 protegido e CI completa de promoção |

20/20 mede os casos HTTP executados, não a aprovação de todos os requisitos. Não somar testes de componentes, métodos HTTP e ações de navegador como uma única contagem de funcionalidades. Cobertura de código e desempenho sob carga não foram medidos.

## Consumo observado

Snapshot nativo: **2026-11-12T11:38:56.502412+00:00**. Dados atribuídos explicitamente ao C1; coordenação e avaliação comuns ficam no overhead do experimento.

| Métrica | Valor |
| --- | ---: |
| Respostas observadas | 954 |
| Tokens de entrada, incluindo cache | 95.499.973 |
| Tokens de saída, incluindo raciocínio | 304.539 |
| Entrada atendida por cache | 93.940.864 (98,37%) |
| Escrita de cache observada | 0 |
| Raciocínio, subconjunto da saída | 118.295 |
| Referência contrafactual API Standard | **USD 2,03292154** |
| Cobrança real da assinatura | Não disponível |
| Tempo ativo | Não disponível |

Cache já está incluído na entrada; raciocínio já está incluído na saída. Não somar esses subconjuntos novamente. A entrada acumula o contexto enviado em cada resposta; não representa texto novo produzido. A referência API usa preços datados de 06/11/2026, cache e regra de contexto longo, e não equivale à cobrança da assinatura ou a um orçamento atual.

## Modelos efetivamente usados

Especialistas com Luna na implementação original; Terra nas correções e gates restantes, conforme A-003. O C1 é um cenário de modelos mistos. A troca ocorreu por indisponibilidade do provedor; os registros originais foram preservados.

| Modelo | Respostas | Entrada | Saída | Referência API (USD) |
| --- | ---: | ---: | ---: | ---: |
| gpt-6-luna | 830 | 88.190.087 | 275.808 | 1,12206854 |
| gpt-6.1-terra | 124 | 7.309.886 | 28.731 | 0,91085300 |

## Consumo por fase declarada

| Fase | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 89 | 5.513.560 | 43.514 | 14,29% |
| Documentação | 278 | 36.829.342 | 81.362 | 26,72% |
| Testes | 221 | 25.568.267 | 69.241 | 22,74% |
| Planejamento | 12 | 389.784 | 4.309 | 1,41% |
| Revisão | 203 | 16.297.921 | 80.745 | 26,51% |
| Busca | 122 | 9.853.651 | 15.682 | 5,15% |
| Sem fase observada | 29 | 1.047.448 | 9.686 | 3,18% |

Planejamento + revisão correspondem a **27,93% da saída observada**. Essas são associações por fase marcada, não tempo gasto nem atribuição causal do contexto. A classificação por atividade de escrita é outra dimensão: 42,6% da saída não tem atividade nativa identificada. Por isso, a fase “Código” não deve ser confundida com volume de código entregue.

## Consumo por agente

| Agente | Respostas | Entrada | Saída | Referência API (USD) |
| --- | ---: | ---: | ---: | ---: |
| c1 | 326 | 33.298.476 | 50.984 | 0,37803016 |
| c1/neo_osv_delta | 18 | 1.011.604 | 12.201 | 0,02364874 |
| c1/neo_security | 19 | 1.186.494 | 10.164 | 0,02766612 |
| c1/patrick_qa | 74 | 6.121.089 | 34.942 | 0,08929190 |
| c1/patrick_qa_r2 | 24 | 1.307.712 | 6.947 | 0,02210902 |
| c1/severino | 361 | 45.038.729 | 157.211 | 0,57605280 |
| c1/yoda | 8 | 225.983 | 3.359 | 0,00526980 |
| c1_finish_terra | 64 | 3.937.791 | 14.546 | 0,43730500 |
| c1_neo_terra | 27 | 1.718.831 | 8.527 | 0,25532840 |
| c1_qa_terra | 33 | 1.653.264 | 5.658 | 0,21821960 |

As tabelas de agentes, fases e modelos repartem os mesmos eventos de formas diferentes; não somar custos entre essas tabelas. Consumo causal por skill e contagem consolidada de retrabalho por requisito continuam não disponíveis.

## Duração, qualidade e limites

Primeira resposta C1 observada: `2026-11-06T01:46:18.207000+00:00`. Última no snapshot: `2026-11-12T01:58:06.081000+00:00`. Intervalo: **519107,874 segundos**, incluindo interrupções e retomadas. Não é tempo ativo nem duração completa do projeto; a jornada adicional de navegador de 12/11 ocorreu depois desse intervalo e foi contabilizada como avaliação comum, fora do subtotal C1.

A revisão de arquitetura aprova os controles observados de proprietário, seleção comum e precisão decimal. A separação integral REST→Actor→Service/DAO foi reprovada na rubrica do C1. Segurança possui pareceres independentes delimitados; eles não substituem o scanner atual nem o pentest. Não há vídeo novo capturado nesta rodada; as capturas e os resultados de downloads são evidências alternativas.

O coletor geral encontrou dois erros de parse e históricos com bytes NUL; a perda de eventos/tokens é desconhecida. Os totais deste resumo são o que foi observado e atribuído ao C1, sem garantir completude dos históricos nem incluir overhead comum. Uma execução, modelos mistos, caches e host compartilhados impedem concluir superioridade ou custo-benefício frente aos demais cenários.

## Fontes para conferir

- [Eventos e grupos nativos](token-breakdown.json), [eventos sanitizados](token-events.jsonl), [métricas](metrics.json) e [referência API](cost-estimates.json).
- [Aceite HTTP](../experiment/results/c1-acceptance.json), [quatro complementares](../experiment/results/c1-boundaries.json), [startup](../experiment/results/system-c1.json) e [restore histórico](../experiment/results/restore-c1.json).
- [Jornada independente de interface de 12/11](../experiment/evaluation/c1-ui-completion.md), [matriz QA](../experiment/evaluation/qa-completion-audit.md), [arquitetura](../experiment/evaluation/architecture-final.md) e [suficiência de segurança](../experiment/evaluation/security-completion-audit.md).
- [Configuração congelada](../experiment/configs.yaml), [emendas](../experiment/amendments) e [verificação reproduzível](../docs/verificacao.md).

Fonte funcional: código C1 sem alterações entre `1f552f1d5cbf014d3ed1da644cdc11d4e6262e3d` (HTTP de 11/11) e `13f775b94ab5731a4d6ae7b93aebc55513e1c2a8` (build/testes e UI de 12/11). As novas evidências complementam os resultados originais; não reatribuem a autoria ou o modelo.
