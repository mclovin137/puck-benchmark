# Puck Benchmark

Experimento exploratório de quatro implementações independentes de controle financeiro pessoal. [Especificação congelada](experiment/specification.md), [protocolo](experiment/protocol.md), [configurações](experiment/configs.yaml) e [emendas](experiment/amendments).

| Cenário | Orquestração | Modelo efetivo | Estado verificado |
| --- | --- | --- | --- |
| [C1](scenarios/c1-specialists-economy/README.md) | Especialistas | Luna; correções/gates com Terra (A-003) | 20/20 casos HTTP; gates finais pendentes |
| [C2](scenarios/c2-specialists-advanced/README.md) | Especialistas | Sol | 20/20 casos HTTP; gates finais pendentes |
| [C3](scenarios/c3-manager-economy/README.md) | Gerenciador | Terra (A-003) | 20/20 casos HTTP; gates finais pendentes |
| [C4](scenarios/c4-manager-advanced/README.md) | Gerenciador | Sol | 20/20 casos HTTP após correção; gates finais pendentes |

Resultados individuais em [runs.json](experiment/results/runs.json), [comparação e limites](reports/comparison.md) e [revisão de arquitetura](experiment/evaluation/architecture-final.md). O aceite HTTP não aprova a interface, a segurança ou a promoção de versão. A comparação permanece aberta até concluir os gates ou documentar os impedimentos externos.

O [resumo de métricas do C1](reports/c1-resumo-metricas.md) reúne consumo, modelos, agentes, fases, testes e pendências do cenário em um único arquivo.

O [detalhamento de tokens](reports/token-usage.md) separa fases declaradas e atividade observada, com [CSV](reports/token-breakdown.csv), [JSON](reports/token-breakdown.json) e [referência de custo API](reports/cost-estimates.json). Cobrança real e tempo ativo são desconhecidos. A execução usa a assinatura existente, sem compras autorizadas.
