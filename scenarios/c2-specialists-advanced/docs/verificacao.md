# Verificação C2

Comandos executados na raiz do cenário. Java 21 alvo, Maven, Node 24 e Docker são pré-requisitos. Use PostgreSQL real; não há fallback H2.

| Comando | Alcance | Limite |
|---|---|---|
| `python3 scripts/local-env.py` | Gera segredo local ignorado sem sobrescrever | Não configura produção |
| `docker compose config --quiet` | Estrutura Compose e interpolação | Não inicia serviços |
| `docker compose up --build -d` | App e PostgreSQL 17.11 com bind loopback | Build/start não comprova requisitos |
| `bash scripts/check.sh` | Backend testes/build, frontend build, contraste | Revisão independente separada |
| `python3 scripts/runtime-check.py` | Auth, CRUD, isolamento, filtros, resumo e arquivos via API real | Assinaturas PDF/XLSX não provam conteúdo |
| `python3 scripts/restore-check.py` | Dump/restore em DB descartável C2, contagens iguais e limpeza | Sem SLA ou recuperação de produção |
| `python3 design/contraste.py` | 330 pares dos tokens de design | Não equivale a auditoria da tela |

Resultados atuais, limitações e hashes ficam em `docs/evidencias/`; a CI remota e os PRs são coordenados pela raiz do monorepo. Não afirmar execução de CI por existir workflow aninhado. Relatórios de scanner devem ser sanitizados; ausência de ferramenta não significa ausência de vulnerabilidade.

## Recuperação de dados

A migração inicial é aditiva e deve ser aplicada pelo Flyway numa base nova. Não editar migração depois de aplicada. Defeito de schema exige nova migração corretiva; perda de dados exige backup restaurável. Nunca executar `down -v` num banco com dados a preservar. O ensaio de backup/restore, quando executado, usa bancos descartáveis exclusivamente C2 e é registrado nas evidências. Não há promessa de rollback testado antes dessa prova.
