# Evidências do autor C4

Candidato independente C4, gerente Sol medium, Puck c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a. Código ainda sem commit nesta autoria; hashes de conteúdo em source-manifest.json. Esta página registra execução, não aprovação independente.

## Resultado verificável

- Maven: 3 testes unitários financeiros e2 integrações com PostgreSQL17.11 real/Testcontainers; zero falhas, erros ou skips. Testes: precisão máxima/centavos, negativos, cadastro/login, IDOR GET/PUT/DELETE, filtros inclusivos e literais, paginação/ordem, resumo e PDF/XLSX interpretados, logout revogável. TDD financeiro teve RED por classe ausente antes de GREEN. JaCoCo em backend/target/site/jacoco (artefato local, não meta de cobertura).
- Frontend:2 testes Vitest verdes, TypeScript e build Vite verdes. Playwright final:2 jornadas verdes,1280x900 e360x800,14.8s; cadastro, CRUD, detalhes, filtros, downloads, exclusão cancelada/confirmada e logout. Relatório sanitizado em ui-tests.json. Quatro auditorias axe, Musgo/claro e Oceano/escuro nas duas resoluções:0violações; resumos axe-*.json. Capturas desktop-1280.png, desktop-360.png, dark-1280.png e dark-360.png; ausência de overflow verificada pelo teste.
- Design:330pares de contraste dos tokens,0falhas e0erros. Removida transição de cores do body: evitou contraste transitório insuficiente ao trocar o modo.
- Compose: build backendJava21 e frontendNode24 concluídos; stack completa iniciou em loopback18084/18204/15434. Smoke real do candidato em runtime-smoke.json, com PDF interpretado por pypdf e XLSX por ZIP/XML: filtro selecionou uma saída0.20 e saldo-0.20, sem a entrada excluída. JSON monetário sempre em strings.
- Recuperação: pg_dump do banco sintético restaurado em finance_restore do próprio container; contagens de usuários/sessões/movimentos/Flyway coincidiram (restore.json). Não é restauração de produção.
- OSV Scanner2.7.0: frontend0advisories após Vitest4.1.12; backend2advisories A002 em spring-webmvc6.2.19. Não suprimidos: Neo analisou pré-condições e preservou divergência OSVCRITICAL/fornecedorLOW-MEDIUM em security-review.md.
- Gitleaks: scans padrão/redigidos de backend/src e frontend/src, exit0, listas vazias. Não cobre histórico, manifests nem o .env runtime privado. Não substitui guarda de push.
- Vídeo real em jornada-final.webm: login, dashboard, detalhes, tema escuro e logout do candidato Compose; pausas apenas para legibilidade da gravação. Vídeo não substitui asserções do runner.

## Iterações e limites

Três versões de implementação da UI: inicial; labels com htmlFor/id; correção do estado pós-logout e contraste durante troca de tema. Contagem bruta de invocações Playwright:5 (ui-run, ui-run-r2, ui-run-r3 interrompida, ui-run-final e ui-final-candidate). As primeiras pegaram DB ainda indisponível e/ou bundle obsoleto: Vite não recebia eventos no filesystem /mnt/c, confirmado por curl do módulo servido. Watch polling e reinício somente do Vite C4 corrigiram esse ambiente. A execução posterior identificou os dois defeitos de UI descritos, corrigidos antes da última execução verde. A contagem de comandos excede três se o limite for interpretado por invocação de runner; preservar esse desvio potencial, sem reclassificar ou ocultar falhas.

Playwright1.56.1 não instala browser em Ubuntu26.04 por autodetecção; instalação com plataforma Ubuntu24 ficou sem concluir após download e foi interrompida. A prova usou Chromium já disponível por CHROMIUM_EXECUTABLE. Gravação integrada ao runner produzia demora/falha de teardown com as páginas auxiliares do axe, e foi desligada; vídeo final foi coletado em contexto simples separado. A tentativa agent-browser de gravar falhou por ffmpeg indisponível/incompatível; navegação e capturas com agent-browser funcionaram. Sem vídeo inventado.

Pool automático de redes Docker estava esgotado. Compose usa rede própria10.217.44.0/24; nenhuma rede ou serviço alheio foi parado. Sem memória exposta. Execução paralela dos cenários e interrupção/reset por limite do provedor pertencem às limitações metodológicas do experimento; consumo real permanece no coletor. Nenhuma compra, alteração de modelo, commit, push, merge ou tag neste cenário.

## Gates

Revisão estática Neo rodada1 em security-review.md; preparação MrRobot A0 concluída após interrupção do provedor; QA independente e revisão Neo do delta de pentest ainda pendentes no instante desta redação. CI raiz e pentest A1 exigem execução real pelo Oráculo em runner isolado. Templates aninhados herdados não provam CI; scripts/ci de review ainda são placeholders fail-closed. Não declarar versão aprovada, segurança geral, CI verde ou pentest executado a partir destas provas autorais.

## Nota de integração — 11/11/2026

Os registros acima preservam a autoria e a data da execução original. O JSON bruto de Playwright permanece local; a publicação usa `ui-tests-summary.json`, que mantém SHA-256 do original, estatísticas e resultados sem configuração, traces ou saída bruta. `video.json` descreve somente a gravação parcial de 5,88 segundos; o arquivo não acompanha esta fatia e não constitui demonstração integral publicada. As capturas PNG são alternativas verificáveis do candidato original, não uma nova execução.

O `source-manifest.json` é histórico: scripts/security de preparação serão integrados separadamente; o cache `frontend/tsconfig.tsbuildinfo` foi excluído da publicação e passou a ser ignorado. A mudança de `.gitignore` é de integração, sem alteração de comportamento da aplicação. QA da retomada está em `qa-recovery.md`; o aceite comum e a CI completa têm evidências próprias.

A guarda de segredos marcou sete checksums do manifesto como `generic-api-key`. A representação foi convertida de mapa para registros `path`/`sha256`, preservando os 61 pares e o SHA-256 da serialização original. Não houve supressão de regra nem alteração dos hashes históricos; o hash antigo de `scripts/pentest/api-cases.py` continua divergindo do delta posterior já descrito pelo Neo.
