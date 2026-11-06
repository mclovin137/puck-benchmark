# Roadmap C1

## v0.1.0 — Controle financeiro · implementação candidata, revisão pendente

- **Objetivo/aceite:** autenticação com revogação, CRUD financeiro isolado por usuário, filtros/paginação/resumo, exportações PDF/XLSX, UI acessível/responsiva e Compose local, conforme contrato central; Vitest atualizado após advisory.
- **Superfícies:** autenticação, autorização, integridade monetária, exportação e execução local.
- **Decisões:** ADR-001; token opaco revogável, BCrypt, JPA/Flyway, exportações PDFBox/POI.

| # | Task | Dependência | Critério e teste | Status |
|---|---|---|---|---|
| 1 | API e schema | — | build e testes de regra locais executados; pareceres delta independentes ainda pendentes | candidata |
| 2 | UI e exportações | API | build TS/testes locais executados; QA delta e medição responsiva pós-correção pendentes | candidata |
| 3 | Execução e gates | 1–2 | Compose/smoke final e gates documentados; revisão independente delta pendente | em validação |
