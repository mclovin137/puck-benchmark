# Parecer de segurança do avaliador — PR #2

**Veredito vigente ao encerrar a segunda rodada: APROVADO no candidato `39ece86`, no escopo deste parecer.** E-01 foi resolvido pela retirada integral do classificador de wrappers e do caminho que alterava as atividades nativas. Nenhum bloqueante remanescente de integridade ou privacidade foi identificado no delta final. A aprovação continua condicionada aos demais gates e preserva as limitações documentadas; as análises dos candidatos anteriores abaixo são históricas.

Primeira rodada deste bloco. Inspeção em 2026-11-06T02:02:56Z, candidato `b948afbcd7bc1657ce0d18ae1a6286857fd8d07c`, delta contra `dev`, 25 arquivos. Revisor: Neo, independente da implementação. Nível crítico pela configuração de CI e integridade do avaliador. Modelo e consumo do revisor pertencem ao overhead.

**CONCLUSÃO — REPROVADO para publicar as novas categorias de atividade como detecção válida.** Há um defeito médio de integridade confirmado no reconhecimento de comandos do wrapper. Não foi confirmado vazamento de credencial, execução do conteúdo analisado ou vulnerabilidade crítica/alta no delta. A autorização existente para merge permanece condicionada aos gates e à resolução do achado.

## Escopo e evidência

Foram revisados o delta do coletor, o avaliador HTTP, renderer, testes, emenda A-001, freeze do aceite e alterações dos workflows. Os relatórios foram consultados somente por esquema e busca de sinais de vazamento, sem emitir valores nem avaliar conclusões comparativas. Não foram lidos aplicações, arquivos de cenários, resultados de aceite de cenários, `.private/`, conversas, tokens privados ou logs reais.

As 13 aprovações locais foram informadas pelo Oráculo e não repetidas. Uma reprodução própria usou somente `wrapper_writes`, extraída por AST do código revisado, e entradas sintéticas; nenhum comando extraído foi executado. Também foram conferidos os hashes: `acceptance.py` corresponde ao freeze, SHA-256 `2b291d277ecfbda0a02d2a499abc5be14eaf661ab6eab31ad0892351166db484`; `telemetry.py` tem SHA-256 `30e8a1e472b72072de6d6a51f71fc8408076b72c27d5d66cee275ddb2ddeb4fe`.

## Achado confirmado — E-01, Média: texto sem chamada e expressões dinâmicas viram escrita detectada

**FATO.** `benchmark/scripts/telemetry.py:93-100` procura `cmd:` por regex em qualquer posição do wrapper, sem separar comentário, string ou chamada. O retorno do decoder JSON inclui o fim do literal, mas esse índice é descartado; assim, também aceita o primeiro literal de uma expressão concatenada.

Reprodução mínima sintética, dentro de um registro `response_item/custom_tool_call` com nome `functions.exec`:

```javascript
// cmd: "cat > code.py"
```

O wrapper contém somente comentário e não escreve arquivo, mas `wrapper_writes` detectou um comando. O controle legítimo `tools.exec_command({cmd: "cat > code.py"})` também detectou um. Já `tools.exec_command({cmd: "cat > code.py" + suffix})` foi aceito como o mesmo comando literal, embora seu valor completo dependa da expressão. A reprodução usou um adaptador de `shell_writes` que devolve o literal recebido; a inspeção do parser Puck confirma que redirecionamento `> code.py` é uma escrita reconhecida por ele.

**Impacto.** `enrich_activities`, em `telemetry.py:123-130`, entrega esses resultados a `apply_activity`, substituindo as dimensões de escrita e a categoria da resposta. Tokens e IDs permanecem nativos, mas podem ser classificados como código/documentação/teste sem a chamada correspondente. Isso pode afetar o detalhamento de consumo solicitado. A declaração de ausência de atribuição causal não cobre esse falso positivo de identificação da chamada.

Não há execução de JavaScript ou shell no extrator: o defeito confirmado é classificação incorreta, não injeção de código. Dono: Oráculo/implementador da infraestrutura. Correção esperada: reconhecimento estático conservador de chamada admitida, ignorando comentários e strings e aceitando apenas o valor literal inteiro de `cmd`; casos ambíguos permanecem sem enriquecimento. Regressões: comentários, strings contendo exemplos, concatenações e expressões dinâmicas devem produzir zero detecções; uma chamada literal válida deve continuar reconhecida. A classificação deve indicar chamada detectada, sem afirmar escrita efetivada no disco. Recalcular os relatórios derivados após a correção.

## Fronteiras revisadas sem achado bloqueante adicional

**FATO — Execução e isolamento da telemetria.** O carregador preserva a verificação de SHA e diferenças rastreadas antes da importação. O novo código usa regex/decoder JSON e funções estáticas do parser, sem `eval`, shell ou subprocesso sobre conteúdo dos logs. O enriquecimento só processa registros após metadado próprio e aplica categoria ao evento com `thread_id` correspondente. Não observei nova alteração dos contadores de tokens ou de suas identidades. Dados locais e parser importado continuam dentro das limitações de confiança do host já declaradas.

**FATO — JSON público do aceite.** `benchmark/scripts/acceptance.py:184-198` publica IDs de testes, estados, contagens e o nome do tipo da exceção; não serializa corpo HTTP, token, headers ou mensagem da exceção. Os parâmetros dos subtestes usados nesta versão são dados sintéticos ou nomes/valores fixados pelo avaliador, não mensagens retornadas pela aplicação. `TextTestRunner` ainda escreve tracebacks no console: esses logs devem permanecer privados, conforme `docs/verificacao.md`; o JSON sanitizado não torna a saída completa do processo publicável. O aceite não é acionado pelos testes da infraestrutura e requer base explícita.

**FATO — Alcance do aceite.** O cliente trata `HTTPError` como resposta, preservando status para asserção; `JSONResult` mantém erros e falhas como insucesso. O relatório declara escopo HTTP e não aprova UI, arquitetura, scanner ou CI. Contas e valores são sintéticos. O exame foi estático; não executou os 16 casos contra aplicações nem conclui suficiência total da cobertura funcional ou de segurança.

**FATO — Renderer e privacidade dos artefatos.** `render_metrics.py:23-31` mantém separação entre fase e categoria, registra limitações causais e deixa custo faturado, tempo ativo, taxa funcional e atribuição por skill em `null`. O scan focado dos arquivos alterados em `reports/` não encontrou padrões de caminho pessoal, UUID nativo, credencial nos formatos conferidos ou chaves de contexto bruto. O esquema JSONL contém somente campos de metadados esperados. Essa busca de padrões não prova ausência universal de segredo; não foi um scanner de histórico nem leitura de evidência de aplicações.

**FATO — CI.** Os novos checkouts Puck usam SHA fixado, Action por SHA e `persist-credentials: false`; `PUCK_SOURCE` passa pelo ambiente, sem interpolação de entrada do PR em shell. Assim, o job passa a fornecer a fonte necessária ao teste de integração nativo, reduzindo a dispensa por indisponibilidade. Não há novo segredo, publicação ou ampliação de permissão nesse delta. CI remota estava em curso segundo o Oráculo; não foi declarada aprovada por este revisor.

**FATO — Emenda comum.** A-001 preserva configurações/freeze originais e registra substituições, aplicação aos quatro cenários e intervenção ocorrida após o início de implementação. Isso torna o desvio explícito; não comprova manifests efetivos nem resolução de todas as dependências transitivas, fora deste escopo. Os registros OSV fornecidos são evidência documental da consulta, não uma nova varredura executada nesta revisão. Nenhuma eficácia de correção de aplicação foi inferida.

## Limites e próximo passo

Não há outro bloqueante substanciado no delta lido. Falsos negativos de classificadores estáticos, distinção entre chamada e efeito real, causalidade dos tokens de contexto e host compartilhado são limitações que precisam continuar visíveis. E-01 é diferente: foi demonstrada uma identificação positiva sem chamada, com caminho direto até a categoria publicada. Após a correção, cabe uma segunda rodada somente no delta e nos relatórios regenerados, limitada à integridade e sanitização; sem acesso às aplicações.

## Segunda e última rodada — candidato intermediário `59215ca`

Data: 2026-11-06T02:09:35Z. Candidato: `59215caf3e1055da8433a48ac19db2e80da2365d`. Revisados somente o lexer, regressões, separação da integração, workflows, documentação de alcance e sanitização dos relatórios alterados. Não foram lidos logs reais, `.private/`, cenários, aplicações ou conclusões comparativas.

**FATO — Casos originais corrigidos.** O novo lexer e a inspeção das propriedades rejeitam comentário simples e concatenação do literal. Em reprodução sintética independente, esses dois casos passaram a produzir zero comandos; o controle legítimo `tools.exec_command({cmd: "cat > code.py"})` continuou produzindo um. As regressões adicionadas cobrem comentários, strings simples, regex, concatenação, propriedade duplicada, spread e `cmd` aninhado. Nenhum conteúdo extraído foi executado.

**FATO — E-01 parcialmente resolvido, com bloqueante remanescente.** O ramo de strings de `benchmark/scripts/telemetry.py:118-128`, dentro de `js_tokens`, trata o primeiro backtick seguinte como término da string, sem reconhecer template aninhado dentro de interpolação. A entrada JavaScript válida abaixo só constrói uma string; não chama `tools.exec_command`:

```javascript
const s = `x${ `tools.exec_command({cmd:"cat > code.py"})` }`;
```

Uma execução exclusivamente sintética de `js_tokens` e `wrapper_writes`, extraídos por AST do código revisado, retornou um comando para essa entrada. O backtick de abertura da string interna foi tratado como fechamento da externa, expondo seu conteúdo como código. O caminho até `enrich_activities` e a classificação publicada continua o mesmo de E-01. A severidade média de integridade e o bloqueio da publicação dessas categorias permanecem. Não há execução de código, acesso a dados reais ou vazamento demonstrado nessa reprodução.

Correção esperada, sob responsabilidade do Oráculo/implementador: tratar esse formato corretamente ou rejeitar conservadoramente wrappers ambíguos com template literal, preservando o caso legítimo. A descrição em `render_metrics.py` de que strings são ignoradas ainda excede o comportamento demonstrado. O limite estático e a ausência de prova de escrita em disco não explicam uma detecção positiva dentro de string; por isso o caso não foi convertido em limitação aceita. Esta é a segunda rodada prevista; a pendência deve ser levada ao usuário conforme a política, sem presumir uma terceira rodada de rotina ou aprovação do risco.

**FATO — Separação da fonte privada adequada no delta.** Os workflows removem o checkout cruzado e o ambiente `PUCK_SOURCE`, preservando permissões restritas e sem acrescentar credencial. O teste nativo foi movido para `benchmark/integration/test_native_collector.py`; a ausência da fonte agora falha, em vez de dispensar o teste. `docs/verificacao.md` e `experiment/evaluation/instrumentation-verification.json` distinguem os 16 testes públicos da integração local com a fonte fixada. Assim, não se alega integração nativa executada no GitHub Actions. A indisponibilidade de acesso ao Puck privado foi informada pelo Oráculo; não fiz chamada autenticada nem ampliei acesso para reproduzi-la.

**FATO — Evidência informada e privacidade.** O registro de instrumentação informa 16 testes públicos e uma integração nativa local aprovados, sem skips, e identifica o SHA-256 do arquivo nativo `88489bb8d40bb3e3b074699b4722f2e568d589e006b1672239733ebb5e1449af`. Esses checks não foram repetidos nesta revisão; seu alcance está explícito e não inclui o caso de template acima. A busca focada nos relatórios alterados do próprio commit não encontrou os padrões conferidos de caminho pessoal, UUID nativo, credencial ou chave de contexto bruto. Isso não substitui scan de histórico nem prova ausência universal de segredo. Nenhum valor comparativo foi emitido ou avaliado.

**CONCLUSÃO — E-01 permanece aberto; nenhum bloqueante adicional substanciado no delta.** A separação CI pública/integração privada resolve a limitação operacional de acesso sem publicar fonte privada ou ampliar tokens. O parecer não declara CI remota, merge ou release concluídos e não aprova as categorias enquanto o falso positivo remanescente for tratado como detecção válida.

### Encerramento da mesma segunda rodada — retirada no candidato `39ece86`

Data: 2026-11-06T02:12:37Z. SHA final: `39ece86e99cb1b0543b91a6e368a478e578fb816`. Após a reprodução intermediária, o Oráculo retirou o complemento, sem acrescentar outro parser JavaScript. A checagem final limitou-se à retirada e ao alcance dos artefatos derivados; não houve terceira rodada de revisão de solução alternativa.

**FATO — E-01 resolvido por remoção da superfície.** O diff `59215ca..39ece86` remove integralmente `js_tokens`, `wrapper_writes`, `enrich_activities`, sua invocação e o contador associado. A busca por esses símbolos no código versionado de `benchmark/`, workflows e documentação de comandos não encontrou ocorrências no candidato final. O caminho que entregava falsos positivos a `apply_activity` deixou de existir. As regressões específicas do componente também foram retiradas, junto com o componente.

**FATO — Retorno à fonte nativa e limite explícito.** O wrapper volta a receber a atividade somente de `native.ingest`. A opção `--reprocess` passa a flag nativa de reprocessamento e é rejeitada em combinação com `--watch`; não interpreta JavaScript nem cria algoritmo de classificação. `render_metrics.py` mostra primeiro as fases declaradas e mantém a atividade nativa em dimensão separada. Código, documentação, testes, planejamento, revisão e busca sem marcação não passam a ser inventados. A ausência de cobertura dos wrappers fica declarada, assim como a distinção entre atividade detectada, chamada e efeito real em disco.

**FATO — Regeneração e privacidade.** A retirada consta em `docs/verificacao.md`, no registro de desvios e no inventário de instrumentação. O Oráculo informou reprocessamento nativo de 405 eventos sem erros, nove testes públicos e uma integração nativa local aprovados, sem skips; esses checks não foram repetidos e nenhum log real foi aberto. A inspeção de padrões nos sete relatórios alterados do candidato final não encontrou os sinais conferidos de caminho pessoal, UUID nativo, credencial ou chave de contexto bruto. Não foram emitidos valores ou conclusões comparativas. A conclusão permanece limitada a esses padrões e esquemas, sem equivaler a uma garantia universal de ausência de segredo.

**CONCLUSÃO FINAL — APROVADO no escopo de segurança e integridade deste bloco, sem bloqueante remanescente identificado no candidato final.** As conclusões de reprovação dos candidatos `b948afb` e `59215ca` foram superadas pela retirada integral do caminho E-01. Permanecem os alcances separados de CI pública e integração local com Puck privado, a limitação de reprodução sem acesso autorizado ao upstream, a cobertura incompleta de atividade nativa e o host compartilhado. Não foi declarado gate remoto aprovado, merge, tag ou aceite de aplicações.
