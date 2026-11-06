# Puck Benchmark

Experimento exploratório de quatro implementações independentes de um controle financeiro pessoal. [Especificação congelada](experiment/specification.md), [protocolo](experiment/protocol.md) e [configurações](experiment/configs.yaml).

| Cenário | Orquestração | Modelo principal | Estado |
| --- | --- | --- | --- |
| C1 | Especialistas | GPT-6 Luna | Implementação e validação |
| C2 | Especialistas | GPT-6.1 Sol | Preparado; aguardando execução |
| C3 | Gerenciador | GPT-6 Luna | Não iniciado |
| C4 | Gerenciador | GPT-6.1 Sol | Não iniciado |

Nenhuma superioridade foi demonstrada. Métricas ausentes serão representadas por `null`, nunca por zero. A execução usa o acesso Codex existente; não autoriza compras, serviços pagos, merge ou release.

O [detalhamento de tokens](reports/token-usage.md) separa código, documentação, testes, planejamento, revisão e busca por fases declaradas, mantendo a atividade observada e as lacunas à parte. Dados em [CSV](reports/token-breakdown.csv) e [JSON](reports/token-breakdown.json); são snapshots intermediários, sem conclusão sobre superioridade. A stack efetiva inclui as [emendas de segurança](experiment/amendments).
