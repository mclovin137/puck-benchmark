Ficha: tarefa=benchmark-recovery agente=neo modelo=gpt-6.1-sol (adaptador declarado; runtime não inspecionado) esforço=high skill=security-audit,verificar-antes-de-concluir,humanizer

# Revisão independente da continuidade da telemetria

Data: 11/11/2026. Base: `8550effde9d661057edafca4614b6d28bf07e0eb` mais o delta não commitado delimitado abaixo. Nível crítico do bloco informado pelo Oráculo; este parecer cobre somente a continuidade.

**Conclusão atual, após R2:** CONT-01 corrigido e verificado com reprodução independente. Nenhum achado substanciado remanescente no delta auditado. As provas e hashes R1 abaixo descrevem o candidato anterior; os hashes finais estão na seção R2. Não há aprovação global.

Verificação de chamada: tarefa, aceite e escopo presentes no briefing e em `.contexto/benchmark-recovery.md`; revisão de integridade/privacidade dentro do papel do Neo. Ownership exclusivo deste relatório e anotações no quadro; nenhuma alteração de produção, commit, push ou merge.

## Escopo e ameaça

- Delta `git diff HEAD` de `benchmark/scripts/telemetry.py` e `benchmark/tests/test_telemetry.py`.
- Somente documentação de continuidade/recuperação em `docs/verificacao.md`, evento `recovery_after_interruption` de `experiment/results/deviations.jsonl` e integridade sanitizada de `phases.jsonl`.
- Ativos: integridade de atribuição de fases e métricas; isolamento das sessões selecionadas; privacidade das saídas públicas.
- Entrada: IDs explicitamente escolhidos pelo operador, metadados JSONL locais e ledger. Fronteira: descoberta → seleção de árvores → filtro de sessões → atribuição de fase → projeção pública. Ausência/corrupção de metadados é uma condição relevante de recuperação, mesmo sem adversário remoto.
- Não foram lidos cenários, relatórios comparativos, conversas, credenciais nem `.private`. Não houve coleta real, acesso de rede, scanner externo ou instalação.

## Achado confirmado

### CONT-01 — Média: continuidade sem data de início herda fase antiga

**FATO:** em `telemetry.py:110`, timestamp ausente ou vazio torna-se `''`; a verificação em `:114` exige somente a presença do ID. `:118` propaga o valor vazio e `phase_at` em `:129–132` aceita toda fase anterior à resposta, inclusive a fase da raiz antiga.

**Pré-condição:** o arquivo da continuidade selecionada contém `session_meta` com ID correspondente ao nome, mas não contém um timestamp utilizável. Não requer acesso remoto; pressupõe metadados locais incompletos ou alterados. Não foi verificado se essa condição existe nos logs reais.

**Reprodução independente:** em diretório temporário, criar duas sessões sintéticas com IDs distintos: raiz antiga com timestamp `2026-11-06T00:00:00Z` e continuidade sem timestamp. Executar `discover(tmp, antiga, [nova])`; então `phase_at([{'agent':'/root','timestamp':'2026-11-06T10:00:00Z','phase':'codigo'}], '/root', '2026-11-11T11:00:00Z', metadata[nova]['root_started_at'])`. Resultado observado e assertado: `{'phase':'codigo', ...}`, com início vazio. O controle com continuidade inexistente lançou `ValueError`.

**INFERÊNCIA/impacto:** uma retomada incompleta pode publicar autoria temporal incorreta por fase/cenário/tarefa. A soma de tokens não é alterada por esse caso; o impacto demonstrado é a classificação. Severidade média pela integridade dos resultados, limitada à entrada local selecionada. Não demonstra exfiltração, execução de código ou manipulação atual das métricas reais.

**Contraprova:** a validação de presença da continuidade e o limite temporal para timestamps completos funcionam; nenhum deles impede o caso sem timestamp. O resultado foi rederivado a partir do fluxo completo, sem assumir falha por busca textual.

**Correção esperada / dono:** Severino/Oráculo deve impedir atribuição histórica quando faltar uma data válida: rejeitar a continuidade explicitamente ou manter sua fase desconhecida com diagnóstico claro. Validar e normalizar o timestamp antes de usá-lo como fronteira temporal. Regressão deve cobrir continuidade sem timestamp/vazio e controle legítimo com timestamp válido; não aceitar fase antiga como fallback.

## Provas executadas

- `python3 -m unittest discover -s benchmark/tests -p test_telemetry.py -v`: **8/8 passaram**, saída e código zero conferidos. Inclui união das árvores, exclusão da sessão alheia, raiz repetida e corte de fase entre raízes com timestamps válidos.
- Reprodução sintética CONT-01: falha de isolamento temporal confirmada; continuidade inexistente rejeitada como controle.
- `git diff --check` dos cinco arquivos delimitados: código zero, sem saída.
- Revisão estática: delta sem rede, subprocesso shell, dependência, execução dinâmica ou novo campo de conversa em saída pública; scripts/testes são arquivos regulares, sem controles bidi detectados.
- Validação do ledger em memória, sem imprimir eventos: **168 registros JSON**, zero NUL; campos limitados a timestamp/agente/fase/cenário/run/task/correlation; agentes, tarefas, correlações, cenários e fases conformes aos formatos restritos. O prefixo de 12 registros já no HEAD permaneceu idêntico.
- O SHA256 dos **165 primeiros registros** corresponde ao `recovered_sha256` registrado. Acrescentar exatamente os **200 NUL declarados** a esse prefixo reproduz o `original_sha256` registrado. `lost_event_count` permanece `null`.

**O que a prova do ledger demonstra:** consistência matemática entre o prefixo atual, o sufixo NUL declarado e os hashes públicos do evento. **O que não demonstra:** autenticidade ou existência do backup privado, causa da corrupção, ausência de perda anterior, quantidade de eventos perdidos ou recuperação de conteúdo não registrado. Nenhum evento foi reconstruído nesta revisão.

## Cobertura sem outro achado substanciado

- `roots` é união da raiz original com continuidades explicitamente fornecidas; o fechamento por pai inclui descendentes, e a consulta filtra pelo ID presente em `metadata`. Raiz repetida não duplica a árvore. Não há seleção por proximidade temporal que inclua raízes alheias.
- Metadados próprios são vinculados ao ID do nome de arquivo, desconsiderando metadados herdados de outra sessão; o teste de pai/filho/neto confirma essa fronteira.
- Com datas válidas, a propagação do início da raiz aos descendentes e o corte inferior de `phase_at` impedem a herança da fase anterior testada.
- A projeção pública continua omitindo IDs nativos e conteúdo de conversa; correlação é derivada de hash do identificador de evento. O ledger/evento de recuperação examinados não possuem campos de conversas ou credenciais.

## Limites e estado final

Deduplicação e ingestão nativas não mudaram no delta; foram rastreadas estaticamente até a mesma base SQLite e o mesmo coletor fixado, mas **não foram reexecutadas** por este revisor. A integração nativa informada pelo Oráculo não é prova própria deste parecer. Também não foram executados os 47 testes integrais, pois a suíte focada cobre o delta e não houve alteração de produção nesta revisão.

Autenticação web, APIs, aplicações, CI, custos comparativos, dependências e recuperação operacional estão fora do escopo. CONT-01 demandou tratamento, verificado em R2 abaixo. Este parecer não constitui aprovação global nem autorização de merge.

Hashes do candidato revisado:

- `benchmark/scripts/telemetry.py`: `6e9c20aeb7f2c18269257c922b1eab2c0e1aa822659005f674c5606e6259acff`.
- `benchmark/tests/test_telemetry.py`: `a024ec9cd8767542aecd88d5a38c36ea236428f6fb0a8823fee41997884c161f`.
- Ledger no instante da prova: `31254cef68241ce213c2aba69957479014f888a014defb23f64c1fa06b97f85b` (pode receber novos eventos legítimos depois da revisão).

## R2 — correção de CONT-01 e comparação de instantes

O Oráculo corrigiu somente a fronteira de timestamps e seus testes: `discover` chama `instant` para todas as raízes de continuidade antes de selecionar a árvore; `instant` exige string ISO com fuso e normaliza para UTC. `phase_at` compara e escolhe a fase por instantes, evitando a ordenação lexical incorreta entre offsets. A compatibilidade da raiz original sem data permanece; uma continuidade explicitamente selecionada precisa de data válida.

**FATO, prova própria:** os **10/10 testes focados passaram**, com código zero. Em reprodução independente com arquivos temporários, timestamp ausente, vazio, inválido, sem fuso e inteiro foram rejeitados com `ValueError`; uma continuidade válida com offset `+03:00` foi aceita; a fase antiga foi excluída; instantes equivalentes em UTC e `+03:00` foram iguais. O teste novo de seleção de fase entre offsets também passou. `git diff --check` dos dois arquivos retornou zero.

**CONCLUSÃO:** CONT-01 corrigido no candidato R2. Não houve outro achado substanciado no delta delimitado. Nenhuma coleta real foi executada pelo revisor; os limites sobre deduplicação nativa, backup privado e demais superfícies continuam válidos. A revisão não demonstra se o caso ocorreu nos dados reais.

Hashes finais R2:

- `benchmark/scripts/telemetry.py`: `55e5e77f4b0822e1dcff7dfe9be50efa17a1e1cf9fe2f57cdc8a4765d95af76a`.
- `benchmark/tests/test_telemetry.py`: `1deff31e1ea848230753bac559899847b842c4ae9ce902f3c20ce76c26cf89a1`.
