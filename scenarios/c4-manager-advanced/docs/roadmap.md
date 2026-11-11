# Roadmap

## v0.1.0 — Finanças pessoais · em andamento
Nível crítico: autorização e integridade financeira. Aceite: contrato integral em ../../experiment/protocol.md e especificação comum. Dono: gerente C4. Sem merge nesta autoria; tasks aguardam CI rápida e integração pelo Oráculo.

| Task | Dependência | Prova | Estado |
|---|---|---|---|
| 1. Persistência e autenticação | — | Flyway, registro/login/logout, expiração e isolamento | implementada; aguarda CI/merge |
| 2. Movimentações e filtros | 1 | CRUD, validações, precisão, seleção consistente | implementada; aguarda gates/CI/merge |
| 3. PDF e XLSX | 2 | parse de conteúdo e totais filtrados | implementada; aguarda gates/CI/merge |
| 4. Interface responsiva | 1–3 | jornadas desktop/mobile, teclado, axe | implementada; aguarda gates/CI/merge |
| 5. Entrega verificável | 1–4 | build, testes, scanner e gates independentes | implementada; aguarda gates/CI/merge |

Até 10 tasks e PRs até30 arquivos, organização dos PRs pelo Oráculo. Gates: Neo autorização/dependências, Patrick QA e Mr Robot preparação A0 para CI A1. Recuperação: preservar volume; restore de backup antes de atualizar versão se necessário (ver HLD).
