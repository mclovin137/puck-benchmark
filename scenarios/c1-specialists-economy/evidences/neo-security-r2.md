# Parecer independente Neo — C1, rodada 2 no delta

**CONCLUSÃO ATUALIZADA:** aprovada a revisão de segurança dos deltas examinados nesta rodada, com os limites abaixo. As duas hipóteses registradas foram tratadas e os testes isolados foram relatados sem falhas. Isto não aprova CI, pentest, implantação ou a entrega integral; os dois advisories Spring continuam visíveis e afetados.

**Escopo:** C1, HEAD `8e792ccb7b7e22b934647e8fb08b1c2acec692e8` mais alterações não commitadas em `Application.java`, `Transactions.java` e testes; hashes abaixo identificam o conteúdo examinado. Ativos: senhas, sessões e dados financeiros; atores: anônimo e usuário autenticado; entradas: HTTP, JSON, filtros; saídas: JSON, PDF e XLSX. Revisão estática e teste de bibliotecas em memória, sem requisições ao serviço, scanner ou pentest. Evidências anteriores e `implementation-checks.json` foram lidos, sem tratar seu resultado como execução independente desta revisão.

## Histórico da hipótese: possível bypass do limitador por URI codificada

**FATO:** `Auth.java:31-38` decide proteger login/cadastro comparando `req.getRequestURI()` literalmente com `/api/auth/login` ou `/api/auth/register`. Em ensaio local com classes Spring 6.2.19 (`RequestPath.parse` e `PathPatternParser`), a string `/api/auth/%6Cogin` não é igual a `/api/auth/login`, mas o padrão MVC `/api/auth/login` casa com o caminho codificado. Nenhuma rede foi usada. Isso prova a diferença de interpretação dos componentes, não que o Tomcat, filtro e proxy efetivos encaminhem essa variante até o controller.

**HIPÓTESE:** se a borda e o container admitirem e preservarem a URI codificada para o filtro enquanto MVC a normaliza, qualquer origem pode contornar o limite por IP e repetir bcrypt; o risco prático inclui tentativas de senha e exaustão de CPU. A severidade depende de demonstrar o caminho completo e os limites da borda. Testar em ambiente efêmero com request sintético único, incluindo variações codificadas e resposta de controle após atingir limite; normalizar/selecionar a rota de modo coerente no filtro ou vincular o controle ao handler, sem depender exclusivamente do proxy. Dono: implementação.

## Histórico da hipótese: ciclo de vida do semáforo

**FATO:** `Transactions.java:33-34` adquire um dos dois slots antes de retornar `StreamingResponseBody`; o `finally` que o libera roda dentro do callback, ou no erro inicial de identidade/critério. **HIPÓTESE:** se o processamento assíncrono for rejeitado, cancelado ou expirar antes de o callback começar, o slot pode ficar retido, até bloquear novas exportações. A revisão não demonstrou que esse estado ocorra na configuração real. Verificar ciclo de falha do executor Spring com teste controlado e garantir liberação em todos os encerramentos; callback efetivamente iniciado libera no `finally`. Dono: implementação.

## Validação do delta corretivo

**FATO:** `Auth.java:33-34` usa `RequestPath` e `PathPattern` para identificar a rota e uma chave canônica para cada endpoint. Os testes `AuthRateLimitFilterTest.java:10-20` usam requisições mockadas, alternam URIs codificadas e comuns, verificam os limites de 20/8 e o contexto `/app`. O caminho que produziu divergência na prova anterior é coberto nessa fronteira isolada. Não houve tráfego HTTP real nem verificação de toda normalização possível na borda.

**FATO:** `Transactions.java:33-34` agora só adquire slot dentro do callback e libera em `finally`; callbacks não iniciados não adquirem slot. `ExportConcurrencyTest.java:15-38` exercita callbacks abandonados, duas exportações ativas, rejeição da terceira e posterior liberação com mocks. `ExportAsyncResponseTest.java:13-18` verifica resposta 429 via MockMvc e async dispatch com serviço mockado; `Auth.java:29` fornece JSON ao tratar o erro. Não prova comportamento de container real, desconexões ou carga.

**FATO:** relatórios Surefire existentes informam 12 testes, zero falhas, erros e ignorados; incluem duas verificações de limite por rota, duas de concorrência e uma de resposta assíncrona. Inspecionei os relatórios e testes, sem reexecutá-los; a vinculação ao estado atual depende da execução relatada pelo responsável e não é provada somente pelos XMLs.

**Hashes do delta corretivo:** `Auth.java` SHA-256 `840fa6b7ccf55796c7a1979b806e6121679b4794475901b5f45cf29116846aad`; `Transactions.java` `e86cf55ec0a9eb78ed577524d131ae43cca452aff7c34e7ae2bfd85c745eb1ae`; `AuthRateLimitFilterTest.java` `b7f55f28457f164a6d28796b9aa0fabc3fe1222e2718f67c1bbfdd826d5afc21`; `ExportConcurrencyTest.java` `31e32a4e17b4d205fc8676c6cf016e32c9b3c501cb57c4ba7a949e2e3dd09812`; `ExportAsyncResponseTest.java` `6d2033af722a440548ceff412892bbaeb43afc1f3313e711f9ef93d5476bc851`. Os hashes históricos de Auth e Transactions ao fim deste documento identificam o estado anterior, não o corrigido.

## Controles examinados e limites

- **FATO:** novos hashes usam SHA-256 da senha UTF-8 codificado em Base64 seguido de BCrypt custo 12 e prefixo discriminador; hashes BCrypt sem prefixo seguem verificação legada (`Application.java:14-18`). Testes de fonte cobrem 128 caracteres ASCII, sufixo distinto, 128 caracteres UTF-8 e hash legado (`AuthPasswordBoundaryTest.java:8-27`). Não executei esses testes. A compatibilidade mantém as limitações intrínsecas de hashes legados, até eventual atualização de credencial; não há migração automática observada.
- **FATO:** token aleatório de 32 bytes é armazenado por SHA-256; consulta exige expiração futura e revogação nula (`Auth.java:9,16-17`, `Repositories.java:11`). Identidade é limpa no `finally`. Isso não demonstra efeito de requisições simultâneas já autenticadas durante logout. Evidência anterior relata smoke de logout, sem reexecução por esta revisão.
- **FATO:** acesso por ID consulta `userId` e ID; listagem, resumo e cada lote dos exports usam proprietário como parâmetro obrigatório (`Transactions.java:20-25,29,34-35`, `Repositories.java:13-15`). A consulta é parametrizada e escapa metacaracteres de LIKE; ordenação e paginação da lista têm allowlist e limite. Não executei teste multiusuário independente.
- **FATO:** exportações fazem lotes de 500, XLSX usa janela SXSSF e arquivo temporário com limpeza; PDF usa cache temporário e páginas (`Transactions.java:35-38`). Concorrência pretendida é limitada a duas. Isso reduz a materialização anterior, mas não comprova limite de disco, tempo, memória do PDF ou consistência transacional durante alterações concorrentes. O teste de fonte cobre 501 registros e dois lotes do PDF por mocks (`TransactionExportTest.java:19-29`), não prova integralidade de XLSX, carga ou condições concorrentes. Caracteres fora da fonte WinAnsi viram `?`; NFC preserva acentos suportados, sem prova de preservação Unicode geral.
- **FATO:** contador por origem tem TTL de 60 segundos, capacidade 4096, bloqueio ao esgotar capacidade e controles de 20 logins/8 cadastros (`Auth.java:31-38`). É local à instância e depende de `getRemoteAddr`, logo proxy compartilhado pode agrupar clientes e múltiplas réplicas não compartilham limite. Testes unitários existentes cobrem janela e capacidade, não a rota codificada. Não demonstrei disponibilidade sob carga.
- **FATO:** A-002 mantém Spring WebMVC 6.2.19 afetado pelos advisories GHSA-j9f9-w8pj-32f8 e GHSA-pc63-qcmh-9cmg. Código e configuração de backend pesquisados não apresentam SSE/view fragments, `XsltView`, `ViewResolver` nem mapeamento catch-all; os controllers examinados retornam JSON ou arquivos. O novo `StreamingResponseBody` é usado com PDF/XLSX, não demonstra SSE. **CONCLUSÃO:** pré-condições específicas não evidenciadas neste recorte; componente continua afetado, alertas não foram suprimidos nem declarados corrigidos. Reabrir análise ao adicionar essas funcionalidades/configuração. OSV classifica ambos como Critical e Spring como Low/Medium, respectivamente, conforme A-002. Dependências transitivas e configuração externa não foram exaustivamente auditadas nesta rodada.
- `implementation-checks.json` relata cinco testes backend anteriores e 54 casos smoke; essa evidência antecede o delta atual, e não substitui testes no conteúdo atual. Dependency-Check foi relatado bloqueado. Sem conclusão sobre CI, pentest, proxy, implantação ou ausência global de vulnerabilidades.

## Identidade de conteúdo SHA-256 — estado anterior à correção dos dois achados

- `backend/src/main/java/br/com/puck/finance/Application.java`: `fbf492a9430a299a6e845d87d47a219a10102cd79e4a58da4d57581e676e7f41`
- `backend/src/main/java/br/com/puck/finance/Auth.java`: `90eaac266a25a02c0107cfa6fb68d2c3e98091bb2986639e25b5fa3ebb83d15a`
- `backend/src/main/java/br/com/puck/finance/Transactions.java`: `2c61cda843ecfa3561a3102708c01199fb0a3a40b9b983b0b993010e520264df`
- `backend/src/main/java/br/com/puck/finance/Repositories.java`: `2281e9a2e3ec220b49d0dc6927cb767b38f1d4301875cc8762ccd299ee78d764`
- `backend/pom.xml`: `f45801907a8ef501fbe4f79a567a9727550d4b044aac48b3c90c8f431db5ea81`
- `backend/src/test/java/br/com/puck/finance/AuthPasswordBoundaryTest.java`: `3277923d48257b554b4a764426dd13d34b335f0d9b9857955861ebaad2b33551`
- `backend/src/test/java/br/com/puck/finance/TransactionExportTest.java`: `9047472a1b0d59eaa567d122b644f06734a673458a926406b8a6ddda9c80b70d`
- `evidences/implementation-checks.json`: `630e0c703375cccb54e91dfbbd85b0cb2a290f414a0702a28e0d27865404d624`

`git diff --check -- scenarios/c1-specialists-economy` sem saída; não valida execução. Qualquer alteração posterior exige conferir hashes e validar apenas o delta afetado, sem alegar revisão de outro conteúdo.
