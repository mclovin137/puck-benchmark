# Migrações C1 e recuperação

Flyway controla schema; `spring.jpa.hibernate.ddl-auto=validate` valida o mapeamento sem alterar a base.

## V2 — `token_hash` para VARCHAR(64)

**Motivo:** execução com PostgreSQL 17.11 revelou `CHAR(64)` aplicado pela V1, enquanto o modelo JPA `String` espera `VARCHAR(64)`. A API não iniciou. V1 é imutável e permanece intacta.

**Mudança:** `ALTER COLUMN ... TYPE VARCHAR(64) USING token_hash::VARCHAR(64)`. Transforma tipo preservando o texto e tamanho; nenhum campo ou registro é removido. Pré-condição: V1 aplicada e dados no formato SHA-256 hexadecimal de exatamente 64 caracteres. Invariante: comprimento 64, unicidade e associação do usuário preservadas.

**Lock/volume:** PostgreSQL pode obter lock exclusivo de tabela durante `ALTER TABLE`; duração e tamanho de produção não foram medidos. O cenário não tem ambiente de produção nem volume representativo. Planejar janela conforme volume real antes de implantação. A migration é transacional no Flyway/PostgreSQL.

**Recuperação:** C1 não está em produção. Em ambiente local descartável, destruir somente o volume de teste e recriar pelo Flyway restaura V1; isso não é recuperação aceitável de dados úteis. Em ambiente com dados, preservar backup validado antes da mudança. Se `ddl validate` continuar falhando ou valores/hash mudarem, interromper rollout e restaurar backup; não editar migration já aplicada. Não foi executado restore. `VARCHAR(64)` pode ser convertido de volta para `CHAR(64)` por migration corretiva nova somente após avaliar dados e lock; estratégia preferida é forward-fix.

**Validação:** aplicar V2 no PostgreSQL Compose descartável, observar Flyway `migrate` e Hibernate `validate`, e exercitar login/logout. Não se declara rollback/restore testado.
