# C2 — especialistas avançados

Aplicação de finanças pessoais do [experimento](../../experiment/specification.md), com [REST comum](../../experiment/protocol.md). Modelos gpt-6.1-sol medium, Neo high. Puck fixado em `c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a`.

Baseline efetiva: Java 21, Spring Boot 3.5.16, React 19.2.0, TypeScript 5.9.3, Vite 7.3.7, PostgreSQL 17.11, JPA/Flyway, PDFBox 3.0.6 e POI 5.4.1. As emendas A-001/A-002 do experimento prevalecem sobre as versões originais; os advisories Spring remanescentes dependem de análise independente sobre as pré-condições e não são declarados corrigidos.

## Executar localmente

```bash
python3 scripts/local-env.py
docker compose up --build -d
```

Interface: `http://127.0.0.1:18202`; backend: `http://127.0.0.1:18082/api`; PostgreSQL: `127.0.0.1:15432`. O segredo local `.env` fica ignorado. Não reutilizar credenciais locais em outro ambiente. Para parar somente o projeto C2: `docker compose stop`.

O token permanece somente na memória da interface; recarregar exige login. Logout revoga a sessão no backend. Valores financeiros trafegam como strings decimais; categorias são nomes livres validados. Todos os filtros se aplicam também ao resumo e às exportações.

A implementação está pronta e foi aprovada no escopo funcional local pelo QA. Yoda não identificou bloqueio arquitetural; Neo aprovou o escopo estático, a análise dos dois avisos Spring e as barreiras do harness. CI remota e pentest ofensivo continuam pendentes; o candidato não está liberado para promoção. O Oráculo coordena Git, PR, CI e tag.

O [vídeo real](docs/evidencias/demo.webm), de 7 min 13 s, mostra cadastro/login, movimentações, edição, filtros, dashboard, exportações, exclusão e logout. Veja [QA](docs/evidencias/qa.md), [segurança](docs/evidencias/seguranca.md), [arquitetura](docs/evidencias/arquitetura.md), [provas no browser](docs/evidencias/browser.json), [comandos](docs/verificacao.md), [roadmap](docs/roadmap.md), [processo e limitações](docs/evidencias/processo.md) e [bibliotecas](docs/lib.md). Hashes relativos estão em [hashes.json](docs/evidencias/hashes.json).

## Avaliação comum — 12/11/2026

O C2 passou nos **16 casos HTTP originais e quatro complementares (20/20)**. A execução comum observou inicialização limpa de backend, frontend e banco, migração e remoção do ambiente. A fonte executada corresponde a `1f552f1d5cbf014d3ed1da644cdc11d4e6262e3d`; os registros preservam seus horários e alcance. Provas: [aceite HTTP](../../experiment/results/c2-acceptance.json), [complementares](../../experiment/results/c2-boundaries.json) e [runtime](../../experiment/results/system-c2.json).

O [restore sintético histórico](../../experiment/results/restore-c2.json) foi aprovado no alcance de comparação de snapshots em banco novo; não mede recuperação de desastre. O aceite HTTP não aprova por si só interface, segurança ou versão. CI completa, tratamento do gate comum de dependências e pentest A1 protegido continuam pendentes. Os dois avisos Spring WebMVC 6.2.19 da A-002 permanecem visíveis e não estão declarados corrigidos.

Esta seção registra a avaliação comum conduzida pelo Oráculo. As evidências autorais anteriores mantêm seu alcance original.
