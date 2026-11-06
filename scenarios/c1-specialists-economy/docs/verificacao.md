# Verificação do cenário C1

Pré-requisitos locais: Java 21, Maven 3.9+, Node 24, npm 11, Python 3, Docker Compose v2. Container usa Java 21 e PostgreSQL 17.11. Compose depende de `POSTGRES_PASSWORD` em arquivo `.env` local.

| Comando (raiz do cenário) | Comprova | Limite |
| --- | --- | --- |
| `scripts/ci/code-review.sh` | versões, lockfile e inventário de bibliotecas | não avalia qualidade funcional |
| `scripts/ci/test-review.sh` | `mvn verify` (inclui TTL/rate limit e PDF paginado de 501 linhas) e `npm ci && npm test` (frontend) | o smoke Compose separado não é suíte integrada à CI |
| `scripts/ci/security-review.sh` | npm audit e Dependency-Check Java com API key do NVD | fail-closed sem `NVD_API_KEY`/`DEPCHECK_VERSION`; chave de scanner Java indisponível nesta sessão |
| `scripts/ci/architecture-review.sh` | stack, Flyway, JPA e execução declaradas presentes | não substitui revisão arquitetural independente |
| `python3 design/contraste.py` | tokens de cor do design do Puck | não mede contraste da interface renderizada |
| `python3 scripts/smoke-api.py` | exercita web/API, ownership, filtros por data nas quatro saídas, nulidade de auth, rate limit por abuso, paginação, revogação e artefatos PDF/XLSX no Compose | dados sintéticos locais, não é pentest/QA independente |
| `mvn -B -ntp dependency:tree -Dincludes=...` | versões transitivas Java efetivas após A-002 | OSV continua sendo uma ferramenta separada; não substitui revisão Neo |

A CI do repositório é configurada na raiz; workflows deste diretório são templates e não provam execução no GitHub. Nenhum resultado de CI é inferido a partir de execução local. O scanner Java sem chave do NVD permanece não executado e bloqueia o gate de segurança completo.
