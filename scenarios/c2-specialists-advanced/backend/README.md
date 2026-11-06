# Backend C2

Contrato em `../../../experiment/protocol.md`; decisões em `../docs/hlds/financas.md` e `../docs/adrs/`. Java 21, Spring Boot 3.5.16, PostgreSQL 17.11; versões efetivas incluem as emendas A-001/A-002 no POM.

Execute pelo Compose da raiz do cenário. Para executar diretamente, configure `DB_PASSWORD` e, quando necessário, `DB_URL` e `DB_USER`; então use `mvn spring-boot:run`. CORS permite a origem configurada por `CORS_ORIGIN` (padrão `http://localhost:18202`); o Compose define explicitamente `http://127.0.0.1:18202`. Na execução direta, use a origem exata do seu frontend. Nenhuma credencial vem do código.

`mvn verify` executa testes de domínio e integração em PostgreSQL 17.11 descartável via Testcontainers e produz o JAR. Alternativamente, configure `TEST_DB_URL`, `TEST_DB_USER` e `TEST_DB_PASSWORD`: o teste usa um schema exclusivo, sem tocar nas tabelas da aplicação. Docker é obrigatório para o modo padrão; não há H2.

A suíte cobre autenticação, normalização de e-mail, senha longa, revogação, expiração, concorrência de cadastro, CRUD e isolamento, valores decimais, filtros, paginação, desempate, totais e leitura real de PDF/XLSX. Também inspeciona os mapeamentos da aplicação e ausência de beans XSLT; isso fornece evidência para revisão independente, sem declarar os componentes Spring afetados corrigidos.

Valores de XLSX são células de texto para preservar exatamente até 16 dígitos monetários, além de impedir fórmulas inseridas pelo usuário. PDF embute DejaVu Sans, quebra linhas e repete cabeçalho por página. Caracteres sem glifo nessa fonte recebem representação explícita `[U+HEX]`; XLSX preserva o texto original.

## Migração e recuperação

`V1__finance.sql` é aditiva e transacional: cria o schema lógico de uma aplicação sem dados anteriores; JPA apenas valida a estrutura. A execução local não implica autorização para migrar produção. O teste de integração aplica Flyway em PostgreSQL novo e exercita constraints e operações após a migração.

Falha ao aplicar V1 transacionalmente exige corrigir a causa antes de uma nova execução; não há backfill nem versão anterior coexistente. Depois de aplicada, V1 permanece imutável: defeitos de estrutura são corrigidos por nova migração versionada, preservando dados. Se houver perda/corrupção de dados, restaurar backup verificado pelo responsável operacional. Backup e restauração de produção não foram testados neste escopo. No modo descartável, o Testcontainers encerra o banco de teste ao terminar.
