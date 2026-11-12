# C1 — Especialistas com modelos econômicos

[Especificação comum](../../experiment/specification.md) · [Protocolo](../../experiment/protocol.md) · [Arquitetura](docs/architecture.md) · [ADR-001](docs/adr/ADR-001-implementacao.md).

Candidato de implementação para controle financeiro pessoal, feito com React/TypeScript, Spring Boot/Java 21, Spring Data JPA, PostgreSQL e Flyway. O cenário usa tokens opacos revogáveis, senha BCrypt com pré-hash SHA-256 em novos cadastros e exportações PDF/XLSX. Cada usuário opera somente seus próprios registros.

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

## Avaliação comum — 12/11/2026

O C1 passou nos **16 casos HTTP originais e quatro complementares (20/20)**. A execução comum observou inicialização limpa de backend, frontend e banco, migração e remoção do ambiente. A fonte executada corresponde a `1f552f1d5cbf014d3ed1da644cdc11d4e6262e3d`; os registros preservam seus horários e alcance. Provas: [aceite HTTP](../../experiment/results/c1-acceptance.json), [complementares](../../experiment/results/c1-boundaries.json) e [runtime](../../experiment/results/system-c1.json).

O [restore sintético histórico](../../experiment/results/restore-c1.json) foi aprovado no alcance de comparação de snapshots em banco novo; não mede recuperação de desastre. O aceite HTTP não aprova por si só interface, segurança ou versão. CI completa, tratamento do gate comum de dependências e pentest A1 protegido continuam pendentes. Os dois avisos Spring WebMVC 6.2.19 da A-002 permanecem visíveis e não estão declarados corrigidos.

A [jornada independente de interface](../../experiment/evaluation/c1-ui-completion.md) verificou cadastro/login, criação, edição, exclusão, filtros/resumo, downloads e logout em desktop e mobile. Há ressalva visual nos filtros a 320 px, sem ação inacessível confirmada. O [resumo individual de métricas](../../reports/c1-resumo-metricas.md) separa tokens, agentes, fases, referência API e pendências. O modelo original Luna teve correções/gates com Terra conforme A-003.

Esta seção registra a avaliação comum conduzida pelo Oráculo. As evidências autorais anteriores mantêm seu alcance original.
