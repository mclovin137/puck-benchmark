# C1 — Especialistas com modelos econômicos

[Especificação comum](../../experiment/specification.md) · [Protocolo](../../experiment/protocol.md) · [Arquitetura](docs/architecture.md) · [ADR-001](docs/adr/ADR-001-implementacao.md).

Candidato de implementação para controle financeiro pessoal, feito com React/TypeScript, Spring Boot/Java 21, Spring Data JPA, PostgreSQL e Flyway. O cenário usa tokens opacos revogáveis, senha BCrypt e exportações PDF/XLSX. Cada usuário opera somente seus próprios registros.

## Executar localmente

Pré-requisitos: Node 24/npm, Java 21+ com Maven 3.9+ e Docker Compose v2. Crie `.env` na raiz deste cenário com `POSTGRES_PASSWORD` para desenvolvimento; não versione esse arquivo. Compile os artefatos no host:

```sh
cd frontend && npm ci && npm run build
cd ../backend && mvn -B -ntp package -DskipTests
cd .. && docker compose up --build
```

Abra `http://localhost:5173`. API local: `http://localhost:8080/api`. Os ports do Compose ficam vinculados a `127.0.0.1`; defina `POSTGRES_PASSWORD` em `.env` local antes de subir. O frontend mantém o bearer token apenas em memória; atualizar a página encerra a sessão local. As imagens finais copiam os builds host, permitindo executar em Docker sem acesso aos registries Maven/npm durante `docker build`.

## Verificações

Consulte [docs/verificacao.md](docs/verificacao.md) para comandos, pré-requisitos e limites. Registros de execução ficam em `evidences/`; estados de gates só são declarados após execução.
