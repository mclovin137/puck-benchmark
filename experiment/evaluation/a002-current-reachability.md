Ficha: tarefa=benchmark-recovery agente=neo modelo=gpt-6.1-sol (adaptador declarado; runtime não inspecionado) esforço=high skill=security-audit,verificar-antes-de-concluir,humanizer.

# A-002 — alcance no candidato atual

Chamada conferida: tarefa, aceite e escopo presentes; investigação independente das pré-condições A-002 dentro do papel. Nível crítico por autorização e integridade do gate. Revisão A0 em 12/11/2026 sobre `076116b24bb98cd28b5137a0818c3d6b45acbc56`. Somente este relatório, o JSON de contexto e o probe externo privado C3 foram escritos por Neo. Nenhuma aplicação, schema versionado, avaliador, política ou triagem foi alterada. Sem request HTTP, payload ofensivo, scanner novo, A1, configuração GitHub, commit ou push. Provisionamento e descarte do ambiente sintético pertencem ao Oráculo.

**CONCLUSÃO:** a lacuna de observação do contexto C3 foi encerrada no snapshot e condições abaixo. A inspeção de fonte e os metadados do contexto real não substanciam caminho até as duas cadeias A-002. Os tratamentos independentes anteriores de C1/C2/C4 permanecem reutilizáveis em seu alcance. Spring WebMVC 6.2.19 continua afetado; os oito findings do scanner não foram removidos ou declarados corrigidos. Este parecer não habilita exceção de CI nem aprova A1, segurança global ou promoção.

## Prova faltante e método

A lacuna de C3 era a configuração efetiva: `neo.md` documentava ausência estática das cadeias, sem observar handlers e view resolvers do contexto real. A condição a conferir é SSE com fragmentos de view e dados entre usuários para GHSA-j9f9-w8pj-32f8; para GHSA-pc63-qcmh-9cmg, XsltView com catch-all de renderização e view implícita. Encontrar as classes do framework no JAR é esperado e não prova caminho alcançável.

O probe externo ContextProbe inicia `SpringApplication.run(com.puck.finance.App.class, ...)` com as classes, recursos e bibliotecas do JAR C3 construído. Não registra beans, mocks, controllers, profiles ou endpoints. Só altera bind para loopback e porta zero; datasource usa a configuração original e credencial sintética fornecida pelo Oráculo. Enumera mappings, métodos, produces, tipos de retorno, beans XsltView/XsltViewResolver e resolvers/delegates/viewClass; não invoca handlers nem lê dados de usuário, tokens, senhas ou bodies. Fecha o contexto no finally antes de imprimir uma única linha JSON marcada. Falha de startup/inspeção não produz aprovação por ausência de resultado.

Compilação própria com `javac --release 21 -proc:none`, código zero, class major 65. A extração privada valida caminhos do ZIP e conserva os bytes dos 17 arquivos de BOOT-INF/classes e das 79 bibliotecas. O launcher do probe usa classpath explícito desses bytes, em vez de JarLauncher; essa diferença de bootstrap é declarada. Nenhuma propriedade de MVC, negociação, view resolver ou segurança foi sobrescrita.

Identidades SHA-256:

| Artefato | Hash |
| --- | --- |
| JAR C3 copiado para o probe | `3eb1fce94a3cc0e804c9519cb4404f36e7f0464b14d89a6eab04bb6f8cd1c83c` |
| ContextProbe.java externo | `f61b5003fa9ce86cb02338d194e052d6f717a5ae3d1fbc1e4294fe6d176748b0` |
| ContextProbe.class externo | `21ce4e9b6d7a1fe1dd4b2a32282c75005711be95e2453a2bdf010a62c8b2cfa4` |
| C3 backend/src/main + POM + Compose, 11 arquivos | `3b913bbd9c019d9f4fe91e4d630514e44ff88cd6d73569e835113ba529baf1d6` |

O agregado ordena caminhos relativos ao cenário e concatena caminho + NUL + SHA-256 hexadecimal + LF. Api.java mantém `a162d872650d5acb7d68935b0b1a1cc67b3adf07a32d4b9db580f8641dc5016d`, igual ao parecer independente anterior. App.java é `12d5c0a00cfff03a14c772a48b1defae9493f6a8181f1ea547a3dce700924a16`; application.properties, `87d370a17d20575fba9622fe07cc64704fe6b26cc75a05e3f52c806df1f5b857`. O build Maven concluído e quatro testes são execução do Oráculo; Neo conferiu o término registrado, sem repetir build/testes.

## Estado da execução

**FATO:** o Oráculo executou o probe preparado por Neo no projeto próprio `benchmark-c3-context-69411d7a`, entre `2026-11-12T12:14:25.499803Z` e `12:14:36.889259Z`; processo exit 0, cleanup_success=true. O marcador do probe registra contexto entre `12:14:29.581349168Z` e `12:14:35.955790355Z`, context_closed=true, Java 21.0.13, Spring 6.2.19, Boot 3.5.16 e profiles vazios. O metadado operacional registra PostgreSQL 17.11 (Debian 17.11-1.pgdg13+2), o mesmo hash de JAR/commit e descarte concluído. Neo leu somente a linha marcada e o pequeno JSON operacional autorizado; não inspecionou Docker independentemente ou abriu o restante do log de runtime.

O Oráculo registra rede interna exclusiva sem portas publicadas, credencial DB sintética efêmera, Java UID10001/read-only/cap-drop/no-new-privileges, montagem RO só da pasta do probe, tmpfs e limites de recursos, sem socket Docker, diretório pessoal ou tokens reais. As imagens foram `eclipse-temurin@sha256:0b99b3376fbb50dbf9c0af8535fdd5b8eb0d3fdfc8b1e4967f383b6919f6901a` e `postgres@sha256:748a18a54d3842d43bc156f0840d78029b8d349e0feca98c12b9c4ce3404a6b3`. Essas condições e remoção de rede/DB no finally são atribuídas ao executor, sem inferir prova de confinamento para pentest.

**Evidência pública:** [a002-c3-context.json](a002-c3-context.json), SHA-256 `8330604edc1335ae72ad8f81a08668e8919fd43ac642ec61ee30841ad53f4948`. O arquivo contém somente o objeto da linha A002_PROBE_RESULT, com formatação JSON; a igualdade estrutural com o marcador foi conferida. Não inclui log bruto, credenciais, dados financeiros, endereço de host ou ambiente. O marcador original tem SHA-256 `cced113269b65b617a9f251ace9d0e00791e7c79a9e3845431aceb0f325f805f`; o metadado operacional privado, `dd73266de99969e4da790d04034e4dec04cb2d9ff5824b9fec3773b13c921862`.

## Resultado C3 por pré-condição

**FATO — handlers efetivos:** seis beans HandlerMapping foram observados. O RequestMappingHandlerMapping tem 14 métodos: 12 em `com.puck.finance.Api`, todos RestController com rotas explícitas `/api/...`, e dois em BasicErrorController para `/error`. Nenhum dos 12 declara SSE, emissor, fragmentos ou view. Produces vazio não é prova de ausência de SSE, assim como retorno Object não basta para excluí-lo: a leitura do mesmo Api.java identifica Map em register/login/me/list, records em CRUD/resumo, void em exclusão/logout e ResponseEntity<byte[]> em PDF/XLSX. Os dados são serializados como corpo; não há caminho de view/SSE introduzido por esses métodos.

**FATO — resolvers reais:** nenhum bean XsltView ou XsltViewResolver. Há quatro ViewResolvers: BeanNameViewResolver, InternalResourceViewResolver configurado com InternalResourceView, ViewResolverComposite sem delegates e ContentNegotiatingViewResolver que delega aos anteriores. Os resolvers com classe de view configurável e seus delegates registram configured_view_is_xslt=false. Nenhuma configuração de XSLT foi adicionada pelo probe.

**FATO — alternativas aparentes:** `/**` e `/webjars/**` são mappings para ResourceHttpRequestHandler, de recursos estáticos. Não são catch-all de controller com renderização implícita. O BasicErrorController tem errorHtml com ModelAndView e produces text/html em `/error`; isso não é ausência universal de HTML, mas também não constitui a cadeia XsltView/catch-all: não há resolver/view XSLT observado. A existência desses handlers foi preservada na evidência, sem filtrar para obter ausência artificial de views.

**CONCLUSÃO C3:** os caminhos REST da aplicação não implementam a cadeia SSE com view fragments; o contexto efetivo não apresenta XsltView nem resolver/delegate XSLT, e o catch-all observado é estático. A combinação de fonte identificada, JAR e contexto Java21/PG sintético fecha a validação runtime pedida pelo parecer anterior, nesse snapshot. Não é reprodução de exploit, demonstração por carga ou prova de todas as configurações possíveis.

## Reutilização dos outros pareceres

Os pareceres e hashes já conferidos em `security-completion-audit.md` são reutilizáveis para C1, C2 e C4 no alcance declarado. Não foram lidos novos fontes desses cenários. Git não mostra alteração em scenarios entre `13f775b` e o HEAD acima. C2 tem prova histórica adicional de contexto/JAR; C1/C4 preservam seus limites estáticos e deltas independentes. O relatório de dependências real mantém os dois advisories CRITICAL em spring-webmvc 6.2.19 por cenário; nenhuma revisão representa correção do componente.

| Cenário | Tratamento independente reaproveitado ou completado | Estado do componente/gate |
| --- | --- | --- |
| C1 | `evidences/neo-security-r2.md`: cadeias ausentes nos caminhos fonte examinados; hashes corretivos conferidos, sem nova revisão completa. | Afetado; dois findings permanecem no inventário. Sem nova prova runtime nesta tarefa. |
| C2 | `docs/evidencias/seguranca.md` R2 e `seguranca-login-status.md`: fonte, contexto e JAR históricos mais delta identificado; pré-condições ausentes no alcance registrado. | Afetado; dois findings permanecem. Sem atribuir JAR histórico a imagem nova. |
| C3 | `docs/evidences/neo.md` mais o contexto real deste relatório: lacuna runtime complementada sem alterar a aplicação ou forçar configuração. | Afetado; dois findings permanecem. Alcance dos caminhos atuais tratado nesta observação. |
| C4 | `evidence/security-review.md` R2 e `contract-repair-security.md`: cadeias ausentes nos caminhos fonte, delta Login/UTF-8 identificado e demais arquivos conservados. | Afetado; dois findings permanecem. Sem nova prova runtime nesta tarefa. |

Caminhos da tabela são relativos ao respectivo cenário. As decisões tratam pré-condições com os limites explícitos de cada prova; não descartam a condição de versão vulnerável nem aplicam uma dispensa global por advisory. A divergência OSV CRITICAL/fornecedor LOW e MEDIUM registrada em A-002 permanece visível.

**Atualização factual de CI:** a API GitHub consultada por Neo confirma o [run 43215110268](https://github.com/mclovin137/puck-benchmark/actions/runs/43215110268) concluído com failure, evento pull_request e head `076116b24bb98cd28b5137a0818c3d6b45acbc56`. O parser nesse objeto Git tem SHA-256 `6510ee194a79b794c29e500a7a3382f21a861aff60ba401c4f8917adf293b961`, o R2 revisado. O artefato fornecido pelo Oráculo desse run foi conferido: SHA-256 `78b9d9864d018884d75e6400561753d60a06c82d35745ee8e4f920a9b87c9779`, nove fontes, 1.020 entradas, oito CRITICAL e status failed. O conteúdo é idêntico ao inventário local anterior. Essa nova execução supera o limite histórico de não haver execução real do parser R2; não altera o bloqueio dos oito findings nem reabre a revisão do gate ou cria dispensa A-002.

Binding CI, política vazia e a autorização/infraestrutura A1 são blocos separados. Este documento não escreve exceção nem transforma análise de alcance em scanner verde, pentest executado ou autorização de promoção. Habilitar SSE, fragmentos, XSLT, resolvers ou rotas de view exige reabrir a análise; mudanças no grafo, código e configuração também exigem conferir o delta.
