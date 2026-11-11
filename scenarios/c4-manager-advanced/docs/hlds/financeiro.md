# Estrutura do financeiro
Pergunta: como preservar autorização e precisão entre telas e exports? Fonte: especificação, contrato comum e baseline A001/A002. Dono: autor C4; revisão independente pendente.

React/TypeScript chama REST por proxy /api. Spring Security autentica bearer opaco: 256 bits aleatórios, somente SHA-256 do token em PostgreSQL, prazo8h e exclusão no logout. UI mantém token em memória; recarga exige login. REST recebe DTOs allowlist; Actor orquestra caso de uso; regras financeiras puras e ExportService; DAO/JPA persiste. Nenhuma entidade é devolvida diretamente.

Usuários, sessões e movimentações são tabelas Flyway; DECIMAL(16,2), checks de valor positivo e tipo. Toda consulta por movimentação inclui ownerId. O mesmo Specification combina proprietário e filtros em listagem/resumo/export, com desempate por id. Resumo deriva dos registros; não há saldo persistido. Exports usam PDFBox e POI sem fórmulas. Limite de página100; export todas as linhas selecionadas, custo proporcional ao volume (carga grande não foi especificada).

V1 é migração aditiva em banco vazio. Rollout: iniciar PostgreSQL17.11, Flyway aplica V1 transacional e Hibernate valida schema. Em falha de V1, transação reverte; após dados reais preservar volume e criar migração corretiva aditiva. Recuperação de versão: parar apenas esta aplicação e restaurar pg_dump em banco novo; alternar DATABASE_URL após conferir contagens. Nenhuma restauração em produção foi executada. Sem alteração destrutiva.

Topologia local: navegador→Vite18204→Spring18084→Postgres15434, todos publicados em127.0.0.1. Compose roda containers em rede própria. Não usa SSE, view fragments, XsltView ou templates servidor; componente Spring afetado continua visível conforme A002 e exige parecer Neo.
