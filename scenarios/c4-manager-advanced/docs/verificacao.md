# Verificação
Pré-requisitos: Java21+, Maven3.9+, Node24, Docker, PostgreSQL17.11 via Compose. Raiz deste cenário. Comandos abaixo descrevem alcance; resultados em evidence/autoria.md.

| Comando | Prova | Limite |
|---|---|---|
| `mvn -f backend/pom.xml test` | unitários e integração JPA/Flyway/PostgreSQL Testcontainers, autorização, revogação, filtros, exports parsados | não pentest independente |
| `npm ci --prefix frontend && npm test --prefix frontend && npm run build --prefix frontend` | lock, precisão visual e typecheck/build | não jornada navegador |
| `npm run test:e2e --prefix frontend` | UI desktop1280/mobile360, CRUD, export, axe, temas; vídeo separado | aplicação deve estar ativa; instalar browser antes (`npx playwright install chromium` no frontend) ou definir CHROMIUM_EXECUTABLE |
| `python3 design/contraste.py` |330pares cores Puck | contraste real também depende da composição |
| `docker compose config -q && docker compose build` | configuração/build21 e24 | não equivale a teste runtime |
| `docker compose up -d` | stack própria com healthcheck DB | .env local obrigatório |
| `mvn -f backend/pom.xml org.cyclonedx:cyclonedx-maven-plugin:2.9.1:makeAggregateBom` | SBOM resolvido backend | scanner separado |
| `osv-scanner scan source -L backend/target/bom.json --format json` | advisories backend | A002 continua no componente |
| `osv-scanner scan source -L frontend/package-lock.json --format json` | advisories frontend incluindo devtools | base temporal do scanner |
| `git diff --check -- scenarios/c4-manager-advanced` (raiz monorepo) | whitespace | não revisão semântica |

CI da raiz do monorepo é responsabilidade do Oráculo. Este cenário oferece manifests e comandos para adaptação; templates de workflow aninhados herdados não provam GitHub CI. Pentest: preparação A0 e execução A1 no runner isolado, nunca host compartilhado.
