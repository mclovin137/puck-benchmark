# Auditoria de segurança independente — C1

**Escopo:** `scenarios/c1-specialists-economy`, commit `7b8a691e7b924cc23aa75302792b3a72503d9387`. Revisão estática do candidato presente na árvore; o estado não é tratado como versão final ou aceita. A árvore global tinha alterações e arquivos não rastreados fora deste escopo; não os abri nem os considerei evidência.

**Modelo de ameaça:** ativos são credenciais, sessões bearer e dados financeiros por usuário; atores são visitante anônimo, usuário autenticado e atacante remoto que alcance a API. Entradas são rotas REST, parâmetros/filtros, corpos JSON e credenciais; saídas incluem JSON, PDF e XLSX. Não executei a aplicação, payloads ofensivos, builds, scanners ou testes. A revisão limita-se à configuração e código de C1.

**Telemetria:** tentativa requerida `python3 /tmp/puck-benchmark-source/telemetry.py phase --agent /root/c1/neo_security --phase revisao --scenario C1 --task security-audit` falhou: o arquivo não existe nesse snapshot (`can't open file`). A fase não foi registrada.

## Achados

### [Média] Sem limitação visível para tentativas de login e cadastro

**FATO:** `/api/auth/login` e `/api/auth/register` são rotas públicas (`backend/src/main/java/br/com/puck/finance/Auth.java:21-25`). Cada senha correta ou incorreta para usuário existente executa `BCryptPasswordEncoder(12)` (`Application.java:14`, `Auth.java:16`); o cadastro também calcula bcrypt (`Auth.java:15`). Não encontrei rate limit, atraso, bloqueio progressivo ou limite por IP/conta no código/configuração examinados. A resposta para conta inexistente e senha incorreta é comum, reduzindo enumeração direta.

**Caminho/reprodução estática:** enviar repetidamente `POST /api/auth/login` com JSON válido e e-mail existente força comparação bcrypt; `POST /api/auth/register` com novas identidades também força hash. Não realizei carga nem request à aplicação.

**Impacto e pré-condições:** atacante que alcance a API pode consumir CPU por chamadas anônimas e tentar senhas de contas conhecidas sem contenção implementada neste candidato. O alcance operacional depende de proxy/WAF e limites externos, não fornecidos; impacto demonstrado é potencial de abuso de recurso/brute force, não indisponibilidade observada. Severidade média, sujeita a rebaixamento caso haja rate limiting efetivo na borda.

**Remediação esperada:** aplicar limites de frequência e concorrência por origem e identidade, com resposta e telemetria que não revelem a existência de conta; validar esses limites na implantação. Teste de regressão deve exercitar tentativas válidas/inválidas e limites sem bloquear o fluxo legítimo.

### [Média] PDF/XLSX materializam todos os registros do usuário sem limite de exportação

**FATO:** endpoints PDF/XLSX aceitam filtros fornecidos pelo usuário (`Transactions.java:10-11`); `export` usa `selected`, que carrega a lista integral sem paginação (`Transactions.java:30,35-36`). O XLSX monta workbook em memória, percorre todas as linhas e chama `autoSizeColumn`; o PDF acumula as linhas e páginas em memória. Não encontrei teto por usuário, quantidade de linhas, bytes, timeout ou concorrência nesse caminho. A criação de registros é autenticada e não tem cota visível (`Transactions.java:7,22`).

**Caminho/reprodução estática:** usuário autenticado com muitos registros pode chamar repetidamente `/api/transactions/export.xlsx` ou `/export.pdf` sem filtros; o servidor busca e serializa tudo em memória por chamada. Não foi feita execução com massa ou medição de memória.

**Impacto e pré-condições:** usuário autenticado controla a chamada e pode aumentar seu conjunto de dados; concorrência pode ampliar o consumo da API e afetar disponibilidade compartilhada. O limite prático e a severidade dependem de heap, quotas e infraestrutura não presentes no escopo. O `size<=100` da listagem não se aplica aos exports. Remediação: estabelecer limites explícitos de registros/bytes e concorrência, exportação em fluxo ou processamento paginado, com teste de teto e controle legítimo.

## Advisories de dependências

**Evidência automatizada recebida, não reproduzida:** informado que OSV Scanner 2.7.0 reportou 23 achados para `backend/pom.xml` (7 críticos, 7 altos, 9 moderados). Não recebi a saída por advisory, CVE, caminho transitivo ou versão resolvida. Não instalei/executuei ferramenta nem alterei baseline; logo não atribuo nem descarto os outros 21 itens individualmente.

### GHSA-j9f9-w8pj-32f8 — Spring WebMVC 6.2.19

**FATO:** o advisory inclui `spring-webmvc` 6.2.19; o `pom.xml` fixa Spring Boot 3.5.16 e deixa Spring Framework sob gerenciamento do Boot (`backend/pom.xml:1`). A correção OSS publicada pelo Spring é 7.0.9; o advisory oficial aponta para Spring MVC/WebFlux usando SSE com view fragments e controle do atacante sobre dados transmitidos a outros usuários. [Advisory Spring](https://spring.io/security/cve-2026-47890/), [registro GHSA](https://github.com/advisories/GHSA-j9f9-w8pj-32f8).

**FATO sobre o caminho de C1:** os controllers examinados retornam objetos JSON ou bytes de arquivos, não há endpoint `SseEmitter`/SSE nem emissão de view fragments; não encontrei renderização MVC por fragmento nos pontos de entrada revisados. Assim, a pré-condição do advisory não está presente no código analisado, embora o artefato afetado esteja no grafo reportado.

**CONCLUSÃO:** risco de exploração desse advisory não substanciado para os caminhos atuais de C1; registrar como não aplicável ao caminho, preservando o alerta de componente vulnerável e reavaliando se SSE/views forem adicionados. A severidade publicada diverge: GitHub mostra Critical, Spring classifica Low e descreve corrupção de stream condicionada. A severidade operacional aqui não é Critical sem a pré-condição. A ausência de uso foi verificada por leitura dos controllers e configuração, não por busca exaustiva em classes transitivas/binários.

### GHSA-pc63-qcmh-9cmg — Spring WebMVC 6.2.19

**FATO:** o advisory inclui Spring WebMVC 6.2.19. O caminho vulnerável requer `XsltView` e mapeamento `/**` que resulte em renderização sem view explicitamente especificada; correção OSS publicada: 7.0.9. O Spring lista condição e versões afetadas em [CVE-2026-47884](https://spring.io/security/cve-2026-47884/); [GHSA](https://github.com/advisories/GHSA-pc63-qcmh-9cmg).

**FATO sobre o caminho de C1:** controllers são mapeados em `/api/auth` e `/api/transactions` e respondem com DTOs/JSON/arquivos. Não encontrei mapeamento catch-all `/**`, `XsltView` ou resolução de nome de view na aplicação revisada.

**CONCLUSÃO:** risco de SSRF/RCE do advisory não está substanciado no caminho atual, ainda que a biblioteca afetada exista. GitHub classifica Critical, enquanto o advisory Spring classifica Medium e condiciona a exploração à configuração acima. Tratar como alerta de dependência pendente de correção compatível com Spring Boot, não como exploit alcançável provado neste candidato. A ausência foi verificada no código-fonte revisado, não em todos os artefatos transitivos.

### Outros advisories transitivos informados

**DESCONHECIDO:** Tomcat 10.1.55 (7 critical/high), Jackson 2.21.4, commons-lang3 3.17, log4j-api 2.24.3 e PG JDBC 42.7.11 foram mencionados sem identificadores de advisory, faixas afetadas, descrições ou árvores de dependência. Sem esses dados não é possível avaliar pré-condições e exposição específicas. O POM declara PostgreSQL JDBC em runtime; não há evidência apresentada de onde entram os demais artefatos ou dos sinks vulneráveis. Não rebaixei os alertas por serem transitivos nem confirmei impacto no aplicativo. Necessário fornecer o JSON/SARIF de OSV com IDs, pacote/ecossistema, faixa e caminho transitivo para triagem por finding. A incompatibilidade reportada entre corrigir para Spring 7.0.9 e permanecer em Boot 3.5 reforça que a escolha da atualização deve respeitar a matriz de compatibilidade; este parecer não propõe override de versão.

## Fronteiras revisadas sem achado substanciado

- **Sessão/auth:** `Auth.java:9,14-18` valida hash SHA-256 de token aleatório de 32 bytes, expiração e revogação em logout; `BearerFilter` limpa o `ThreadLocal` em `finally`. Não há cookie de sessão no frontend (`frontend/src/main.tsx:4`), token permanece em estado React. Senhas armazenadas via BCrypt custo 12. Não vi segredo hardcoded nas fontes lidas. Login sem rate limit está reportado acima.
- **Ownership/IDOR:** operações por ID usam `owner(id)` → consulta `owned(uid,id)` e retornam 404 para não encontrado; `uid()` rejeita ausência de identidade (`Transactions.java:20-25`; `Repositories.java:17`). Listagens, sumários e exports recebem `uid()` na consulta filtrada por `userId` (`Transactions.java:29-35`; `Repositories.java:13-16`). Não executei casos multiusuário; a conclusão é estática.
- **Filtros/SQL:** consultas são JPQL parametrizadas; caracteres `%`, `_` e escape `!` são normalizados para busca literal (`Transactions.java:28`; `Repositories.java:13-16`). Ordenação é allowlist `date|amount` e `asc|desc`; paginação limita listagem a size 100 (`Transactions.java:28,32`). Não achei SQL dinâmico.
- **Validação financeira:** DTO aplica Bean Validation e `validate` restringe tipo, positividade e precisão/escala (`Transactions.java:7,16,26`). Cadastro valida tamanho/formato da entrada (`Auth.java:15`), ressalvado potencial erro 500 para senha nula não classificado como falha de segurança neste escopo.
- **Exportações:** ambas filtram pelo proprietário. XLSX cria células string para campos de texto, sem fórmula explícita; PDF normaliza para ASCII antes de `showText` (`Transactions.java:35-36`). A vulnerabilidade identificada é volume/memória sem limite, não acesso cruzado ou fórmula comprovados.
- **CSRF/CORS:** token é enviado no header `Authorization` pelo cliente e não há credencial cookie/`allowCredentials`; CORS limita origem por configuração a um valor (`Application.java:15`). Isso não prova política segura da borda em produção; origem padrão localhost pode não corresponder à implantação.
- **Bind/segredos/configuração:** Spring escuta porta 8080 e compose publica `8080:8080`, enquanto PostgreSQL não publica porta (`application.yml:12-15`; `compose.yaml:1-27`). Bind externo efetivo depende do host e do proxy. `application.yml` tem credenciais fallback `finance` para conexão local; compose exige `POSTGRES_PASSWORD`. Uso do fallback em produção não foi demonstrado e deve ser proibido por configuração de implantação.
- **Logs e erros:** não encontrei log de senha/token ou dados financeiros no código revisado; advice retorna mensagem controlada e configuração desativa `include-message` (`Auth.java:29`; `application.yml:14-15`). Logs da infraestrutura não foram inspecionados.

## Precisa validação / limites

- Obter saída detalhada do OSV para rederivar os outros advisories por CVE e caminho transitivo. Não aceitar ou descartar os 21 não reavaliados com base apenas em versões agregadas.
- Confirmar proxy/WAF, rate limit, limites de corpo/conexões, quotas por usuário, heap e timeout na implantação; não disponíveis neste escopo.
- Executar QA de isolamento entre duas contas, expiração/revogação de token e exports em dados grandes em ambiente efêmero autorizado, por executor de testes; esta auditoria não fez requests ou carga.
- Verificar segredo real de produção e logs operacionais fora do repositório exige evidência específica do operador; não acessada.

**Conclusão:** dois riscos de disponibilidade/abuso estão substanciados estaticamente no código C1. Os dois advisories de Spring foram rederivados: versões afetadas confirmadas, porém suas condições de exploração não apareceram nos caminhos da aplicação revisados; isso não altera o baseline de dependências. Não declarar o candidato seguro ou pronto para produção.
