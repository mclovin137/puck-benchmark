# Clareza — C4 gerenciador avançado

Controle financeiro pessoal independente em React/TypeScript e Spring Boot/JPA/Flyway/PostgreSQL. Especificação integral em [specification.md](../../experiment/specification.md), contrato REST em [protocol.md](../../experiment/protocol.md), baseline efetiva nas emendas A001/A002. Gerente Sol medium, gates independentes previstos; Puck c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a.

## Executar
Crie `.env` local com `DATABASE_PASSWORD` aleatória (não versionar). Execute `docker compose up --build -d`. Frontend http://127.0.0.1:18204, API http://127.0.0.1:18084/api, banco127.0.0.1:15434. Portas somente loopback; rede própria10.217.44.0/24 e volume puck-c4_c4-data. Não use esta senha em outro ambiente.

Para desenvolvimento: `docker compose up -d db`, exporte DATABASE_PASSWORD do seu `.env`, `mvn -f backend/pom.xml spring-boot:run`; em outro terminal `npm ci --prefix frontend && npm run dev --prefix frontend`. UI mantém sessão apenas em memória: recarregar pede login novamente. Logout revoga o token no banco.

Valores monetários são strings decimais com ponto nos centavos, nunca Number; filtros inclusivos combinam tipo/categoria/descrição/período/faixa. Resumo e exports usam seleção autorizada integral, independentemente da página. XLSX armazena moeda como texto decimal para preservar os14inteiros e centavos. PDF embute DejaVuSans; glifos ausentes são representados por código Unicode legível `[U+…]` em vez de perda silenciosa. Dados não são convertidos de timezone.

[Arquitetura e recuperação](docs/hlds/financeiro.md), [decisão de sessão](docs/adrs/001-sessoes.md), [bibliotecas](docs/lib.md), [comandos de verificação](docs/verificacao.md) e [evidências de autoria](evidence/autoria.md). CI e integração Git são conduzidas pelo Oráculo; sem commit/push/merge nesta autoria. Gates ausentes não são aprovação.
