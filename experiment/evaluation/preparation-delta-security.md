# Parecer de segurança do delta da preparação — PR #1

Inspeção: 2026-11-06T01:48:23Z. Candidato: `b7ab08f4be710fac8ee960b6682ac73fc4ac8d4c`, branch `feat/experiment-protocol`, 26 arquivos em relação a `main`. Revisor: Neo. Escopo: infraestrutura, telemetria, configuração de agentes e CI; nível crítico pela superfície de execução e pelos controles do experimento.

**CONCLUSÃO — REPROVADO para encerrar a preparação com a telemetria atual.** Dois defeitos confirmados afetam a integridade da medição. Não foi confirmada vulnerabilidade crítica/alta nem exposição de credencial. O modelo fixo usado na infraestrutura é overhead e não representa execução de cenário. A autorização de merge/tag informada pelo Oráculo permanece condicionada aos gates; este parecer não declara CI remota aprovada.

## Evidência e método

Leitura dos arquivos do candidato por Git, do quadro temporário e dos trechos pertinentes do coletor Puck fixado em `c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a`. O SHA-256 de `benchmark/scripts/telemetry.py` no candidato é `31d888ef4743cbf8fdacb4324c0265d784a6d6d29c73aad7179ec95ea20adde7`.

As verificações mecânicas anteriores — três unittests, sintaxe, compilação e diff — foram informadas pelo Oráculo e não repetidas. As duas reproduções abaixo executaram somente as funções `aggregate` e `discover`, extraídas por AST do arquivo revisado, com registros inteiramente sintéticos em diretório temporário. Não foi executado `collect`, importado o coletor externo nem aberto qualquer log real. Cenários, resultados de cenários, conversas e credenciais ficaram fora da leitura. Arquivos não rastreados identificados pelo status não integram este parecer.

## Defeitos confirmados: corrigir antes da aprovação da preparação

### D-01 — Média: valor desconhecido antes do primeiro valor observado interrompe a coleta

**FATO.** `benchmark/scripts/telemetry.py:58-64` grava `None` quando a primeira resposta não informa uma contagem; ao chegar uma resposta com valor, soma `g.get(field, 0) + value`, cujo primeiro operando continua sendo `None`.

Reprodução sintética: `aggregate([{'input_tokens': None}, {'input_tokens': 10}])` retorna `TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'`. O resultado esperado é soma observada 10 com uma observação, preservando `null` apenas onde nenhuma resposta informa o campo. O teste de `benchmark/tests/test_telemetry.py:8-13` cobre valor conhecido seguido de ausente, mas não a ordem inversa.

Impacto: metadados incompletos válidos fazem `collect` terminar antes de atualizar os relatórios; arquivos antigos podem permanecer como a última saída disponível. É defeito de disponibilidade/integridade da evidência, sem exploração externa demonstrada. Dono: Oráculo/implementador da infraestrutura. Regressão: cobrir ambas as ordens, todos ausentes e campos parcialmente observados no mesmo grupo.

### D-02 — Média: descoberta perde sessões com metadado herdado de fork

**FATO.** `benchmark/scripts/telemetry.py:70-82` considera somente a primeira linha de cada arquivo e usa seu `payload.id` como chave. O coletor Puck fixado, em `agents/scripts/monitor-tokens.py:452-478`, documenta metadado herdado e aceita como próprio apenas o `session_meta` correspondente à UUID do nome do arquivo.

Reprodução sintética: dois arquivos, um do pai com seu metadado e outro do filho com metadado do pai na primeira linha e metadado próprio na segunda. A descoberta esperada contém duas sessões; a função retornou uma e `child_present=False`. A atribuição por chave também pode substituir o caminho associado ao pai, conforme a ordem da enumeração.

Impacto: sessões filhas ficam ausentes da seleção ou do mapa usado em `collect:116-118`, mesmo que o parser nativo reconhecesse seus tokens. A medição pode subcontar delegação e produzir comparação incorreta. O teste prova o formato sintético suportado pelo parser fixado; não afirma que uma execução real de cenário já sofreu a perda. Dono: Oráculo/implementador da infraestrutura. Regressão: identificar metadado próprio pelo arquivo, preservar pai e filho independentemente da ordem e validar a cadeia de descendência, inclusive netos. A correção não exige revelar conversas.

## Fronteiras revisadas e pendências sem exploração confirmada

**FATO — Proveniência do código executado.** `load_native`, em `telemetry.py:25-30`, importa e executa o arquivo indicado por `--puck`; `collect:130` publica o pin constante sem verificar o checkout importado. No caminho inspecionado, a fonte Puck já havia sido confirmada no pin. Isso não configura injeção remota: o argumento é fornecido pelo operador. Entretanto, o relatório sozinho não comprova sua proveniência. Registrar verificação do SHA e da integridade da árvore imediatamente antes da importação, ou fazer o carregador falhar diante de divergência, fecha essa pendência. Não considerar o campo constante uma verificação executada.

**FATO — Deduplicação.** O parser fixado usa chave primária `(client,event_id)` (`monitor-tokens.py:245-250`) e faz upsert em `put:406-419`; o wrapper exporta uma linha por registro de `usage`, sem somar cache à entrada ou raciocínio à saída. Há fundamento estático para deduplicação nativa, mas não foi testado aqui o ciclo completo de duas coletas. `new_records` vem da contagem de ingestão do parser: não tratá-lo automaticamente como quantidade de eventos inéditos em reprocessamento.

**FATO — Publicação e sanitização.** `telemetry.py:122-127` exporta uma seleção explícita de campos; IDs nativos são substituídos por hash, e caminhos de log/IDs de sessão não são copiados ao relatório. O parser fixado restringe modelo e esforço com `safe_name`. Porém, `agent`, `scenario` e `task` vêm de metadados/marcações sem allowlist, em `telemetry.py:38-39,80-82,119-127`, e aparecem nos arquivos públicos. É risco condicionado à entrada fornecida, não vazamento observado. Usar identificadores controlados e revisar a saída antes de publicar; a extensão `.json` ou o hash da correlação não sanitizam os outros valores.

**FATO — Fases e histórico.** A fase é escolhida pelo agente e último timestamp anterior à resposta (`telemetry.py:120-125`); não há atribuição causal inferida a partir de texto. O ledger de fases é aberto em append (`:40`); os relatórios de tokens são snapshots reescritos (`:137-144`). Não apresentar esses snapshots como ledger imutável. Atribuição por fase deve ser conferida com identificadores estáveis e metadados sintéticos antes de afirmar cobertura de tarefa/sessão; não houve leitura dos registros reais.

**FATO — CI e segredos.** Os dois workflows versionados usam runner hospedado, `contents: read`, checkout por SHA e `persist-credentials: false`; não há `pull_request_target`, publicação ou repasse explícito de segredo aos scripts lidos. Gitleaks usa montagem somente leitura, rede desabilitada e `--redact`. O gate de `.github/workflows/ci.yml:82-99` exige sucesso de todos os jobs e falha nos estados ausentes/cancelados. A imagem Gitleaks permanece fixada por tag, não digest: endurecimento de cadeia de suprimentos, sem comprometimento demonstrado. Os scripts revisados usam caminhos fixos, sem executar o módulo importado pelo seu `main` na CI. Os três testes atuais não cobrem D-01/D-02.

**FATO — Configuração e autorização.** `AGENTS.md` mantém a proibição de leitura cruzada e alteração do avaliador; `docs/rules.md:5` registra a autorização de merge/promoção/tag com gates. O quadro temporário ainda diz que não há autorização específica: está desatualizado e não revoga a instrução atual do usuário. A configuração local Codex só define esforço; o deny de leitura Claude não impede acesso via shell e não constitui isolamento do host. Continuam válidos os limites do primeiro parecer sobre memória, credenciais, isolamento e modelos efetivos dos futuros cenários.

## Alcance da conclusão

D-01 e D-02 foram rederivados contra os controles contrários: o teste atual não cobre a ordem que falha; o parser nativo suporta forks, mas só recebe arquivos e atribuições depois da seleção defeituosa. Portanto, os dois candidatos permanecem confirmados. Suas severidades refletem a integridade da evidência e a ausência de exploração externa demonstrada.

Nenhuma leitura adicional de aplicações, scan de segredos, pentest ou execução de CI remota foi feita nesta rodada. As alterações após o SHA indicado precisam de revisão do delta; aprovação anterior não se estende automaticamente a elas.
