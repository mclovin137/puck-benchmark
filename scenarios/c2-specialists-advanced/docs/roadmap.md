# Roadmap C2

## v0.1.0 — finanças pessoais · em andamento

Objetivo: entregar os critérios comuns da [especificação](../../../experiment/specification.md) e [protocolo](../../../experiment/protocol.md). Nível crítico por autorização e valores monetários. Uma versão, até 10 tasks; PRs até 30 arquivos, organizados pelo Oráculo.

| # | Task | Dependência | Aceite e prova | Estado |
|---|---|---|---|---|
| 1 | Arquitetura e persistência | — | HLD e migração PostgreSQL | implementada; aguarda CI/merge |
| 2 | Autenticação revogável | 1 | Cadastro/login/logout e negativos | implementada; aguarda CI/merge |
| 3 | Movimentações e consultas | 1,2 | CRUD isolado, filtros/paginação/totais | implementada; aguarda CI/merge |
| 4 | PDF e XLSX | 3 | Arquivos reais com mesma seleção | implementada; aguarda CI/merge |
| 5 | Interface responsiva | 2,3,4 | Fluxos completos desktop/mobile | implementada; aguarda CI/merge |
| 6 | Integração e execução | 2–5 | Build, testes PostgreSQL e compose | implementada; aguarda CI/merge |
| 7 | Validação independente | 6 | QA, arquitetura, segurança e pentest | QA/Yoda/Neo concluídos; pentest aguarda CI |
| 8 | Entrega e evidências | 7 | Documentação e promoção sob Oráculo | candidato e evidências prontos; promoção pendente |

Conclusão de task depende de integração em dev e CI; execução local não equivale a CI. Revisão limitada a duas rodadas, segunda no delta. Tags/releases somente pelo Oráculo após gates.
