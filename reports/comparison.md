# Comparação em andamento

Este relatório ainda não contém resultados finais. O experimento tem uma execução por cenário e preserva a configuração inicial com emendas datadas em experiment/amendments. A configuração efetivamente executada precisa ser conferida com a telemetria e manifests finais.

O detalhamento observado está em metrics.json, metrics.csv e token-usage.md. Entrada/cache e saída/raciocínio são mantidos separadamente, sem dupla contagem. Código, documentação, testes, planejamento, revisão e busca são apresentados com configuração, mista e não disponível. O quadro primário separa as seis fases declaradas; a atividade de escrita detectada pelo Puck é um quadro separado. Wrappers aninhados e scripts dinâmicos podem ficar sem atividade observada. O complemento estático JS foi retirado após falso positivo na revisão, com reprocessamento comum de todos registros. Fases declaradas não são atribuição causal exata do contexto. O custo faturado e o tempo ativo estão indisponíveis.

Nenhuma aplicação recebeu aceite externo neste estágio. Não há taxa funcional, cobertura, qualidade, segurança, conformidade ou relação custo-benefício final demonstrada. Não há fundamento para escolher vencedor.

Limitações já observadas: filesystem e credenciais do host compartilhados; ausência de garantia técnica de cegamento; instalação global divergente do pin; preparação C2 sobreposta por agendamento e retomada sequencial planejada; atualização comum de versões de segurança durante implementação C1; versões de ferramentas auxiliares não totalmente congeladas. Estes fatos devem acompanhar qualquer conclusão final, com impacto e controles não executados.
