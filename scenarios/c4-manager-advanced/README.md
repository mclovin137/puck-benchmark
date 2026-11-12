# Clareza — C4 gerenciador avançado

Controle financeiro pessoal independente em React/TypeScript e Spring Boot/JPA/Flyway/PostgreSQL. Especificação integral em [specification.md](../../experiment/specification.md), contrato REST em [protocol.md](../../experiment/protocol.md), baseline efetiva nas emendas A001/A002. Gerente Sol medium, gates independentes previstos; Puck c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a.

## Executar
Crie `.env` local com `DATABASE_PASSWORD` aleatória (não versionar). Execute `docker compose up --build -d`. Frontend http://127.0.0.1:18204, API http://127.0.0.1:18084/api, banco127.0.0.1:15434. Portas somente loopback; rede própria10.217.44.0/24 e volume puck-c4_c4-data. Não use esta senha em outro ambiente.

Para desenvolvimento: `docker compose up -d db`, exporte DATABASE_PASSWORD do seu `.env`, `mvn -f backend/pom.xml spring-boot:run`; em outro terminal `npm ci --prefix frontend && npm run dev --prefix frontend`. UI mantém sessão apenas em memória: recarregar pede login novamente. Logout revoga o token no banco.

Valores monetários são strings decimais com ponto nos centavos, nunca Number; filtros inclusivos combinam tipo/categoria/descrição/período/faixa. Resumo e exports usam seleção autorizada integral, independentemente da página. XLSX armazena moeda como texto decimal para preservar os14inteiros e centavos. PDF embute DejaVuSans; glifos ausentes são representados por código Unicode legível `[U+…]` em vez de perda silenciosa. Dados não são convertidos de timezone.

[Arquitetura e recuperação](docs/hlds/financeiro.md), [decisão de sessão](docs/adrs/001-sessoes.md), [bibliotecas](docs/lib.md), [comandos de verificação](docs/verificacao.md) e [evidências de autoria](evidence/autoria.md). CI e integração Git são conduzidas pelo Oráculo; sem commit/push/merge nesta autoria. Gates ausentes não são aprovação.

## Avaliação comum — 12/11/2026

O C4 passou nos **16 casos HTTP originais e quatro complementares (20/20)**. A execução comum observou inicialização limpa de backend, frontend e banco, migração e remoção do ambiente. A fonte executada corresponde a `13f775b94ab5731a4d6ae7b93aebc55513e1c2a8`; os registros preservam seus horários e alcance. Provas: [aceite HTTP](../../experiment/results/c4-acceptance.json), [complementares](../../experiment/results/c4-boundaries.json) e [runtime](../../experiment/results/system-c4.json).

O [restore sintético histórico](../../experiment/results/restore-c4.json) foi aprovado no alcance de comparação de snapshots em banco novo; não mede recuperação de desastre. O aceite HTTP não aprova por si só interface, segurança ou versão. CI completa, tratamento do gate comum de dependências e pentest A1 protegido continuam pendentes. Os dois avisos Spring WebMVC 6.2.19 da A-002 permanecem visíveis e não estão declarados corrigidos.

O aceite atual já inclui a correção de UTF-8 dos erros e status de login integrada no PR #20. Uma tentativa posterior de restore começou após o teardown e falhou na identidade do container; está [preservada separadamente](../../experiment/results/restore-c4-resume-unavailable.json) e não é restore novo aprovado.

Esta seção registra a avaliação comum conduzida pelo Oráculo. As evidências autorais anteriores mantêm seu alcance original.
