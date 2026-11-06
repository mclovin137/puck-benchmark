# Parecer de segurança do avaliador — PR #2

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
