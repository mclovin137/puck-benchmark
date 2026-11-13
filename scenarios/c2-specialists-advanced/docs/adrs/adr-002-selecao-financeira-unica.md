---
date: 2026-11-06
status: aceita
---
# ADR 002: seleção autorizada única para consultas financeiras

## Para o futuro agente

Lista, resumo e arquivos dependem do mesmo predicado de seleção financeira. Paginação pertence apenas à lista; proprietário é obrigatório e vem da autenticação.

## Contexto e critérios

O [protocolo](../../../../experiment/protocol.md) exige filtros combináveis consistentes e isolamento. Não existe consulta anterior a preservar. Valores exatos, subconjuntos autorizados e manutenção simples prevalecem sobre micro-otimização.

## Opções consideradas

- **Filtro normalizado e predicado JPA compartilhado — escolhida:** todos os consumidores têm os mesmos critérios; exige manter normalização separada da paginação.
- **Queries independentes por endpoint — descartada:** permitem otimização específica, mas duplicam decisões de autorização/filtro e favorecem divergência.
- **Carregar todos os registros do usuário e filtrar na aplicação — descartada:** facilita reutilização, porém desperdiça memória e transfere trabalho apropriado ao PostgreSQL.

## Decisão

REST valida DTO de filtro e Actor obtém ownerId. DAO combina ownerId obrigatório com filtro normalizado único, reutilizando predicado parametrizado. Escapar metacaracteres de substring LIKE. Ordenação permite apenas campos/direções do protocolo e acrescenta id. API usa strings decimais; domínio `BigDecimal`; banco `NUMERIC(16,2)` com amount>0. Totais de entradas/saídas e saldo derivam da seleção sem página, com zero decimal explícito para conjunto vazio. Não armazenar saldo redundante.

Exportação recebe a seleção completa e constrói linhas/totais do mesmo conjunto, evitando nova query fora do snapshot. Lista com count separado usa transação de leitura de snapshot consistente. Seleções em chamadas HTTP diferentes refletem o estado de cada chamada. Nenhum truncamento silencioso ou substituição de XLSX por CSV.

## Consequências e revisão

Alterar um filtro passa a alterar todos os consumidores e exige testes de contrato correspondentes. Exportação materializada pode consumir memória; só substituir por streaming com snapshot consistente após medir necessidade, mantendo totais e linhas iguais. Reabrir esta decisão se volume demonstrar necessidade de exportação assíncrona ou fontes múltiplas; isso não está no escopo atual.

## Relações, aceite e histórico

Afeta transaction DAO/Actor, geradores e [HLD](../hlds/financas.md). Decisão técnica rotineira autorizada pela seção 12 da especificação e briefing do Oráculo em 2026-11-06; aceita sob esse mandato, com verificação e revisão independente ainda pendentes. Criada em 2026-11-06; não substitui ADR anterior.
