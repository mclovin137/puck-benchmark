Ficha: tarefa=benchmark-recovery agente=neo modelo=gpt-6.1-sol (adaptador declarado; runtime não inspecionado) esforço=high skill=security-audit,verificar-antes-de-concluir,humanizer.

# Revisão independente do gate de dependências

Chamada conferida: tarefa, aceite e escopo presentes; segurança de CI e integridade do gate dentro do papel. Revisão A0 em 12/11/2026 sobre HEAD `c2703749ec119e77f439d87cbfed38d6ffc1cadf`, com cinco arquivos locais: `.github/workflows/auditoria-dependencias.yml`, `scripts/ci/dependency-audit.py`, `benchmark/tests/test_dependency_audit.py`, `experiment/dependency-triage.json` e delta de `docs/verificacao.md`. Só este relatório foi escrito. Sem aplicação, avaliador privado, pentest, A1, alteração de controles externos, commit ou push. A execução live existente foi apenas observada; não houve reinício, sinal ou nova varredura.

**Parecer vigente após R2:** DEP-01/DEP-02 corrigidos, sem achado substanciado remanescente no delta de infraestrutura conferido. A integração dessa infraestrutura é sustentada pelos controles demonstrados. O gate de dependências continua reprovado pelos oito findings CRITICAL; A1, binding de triagem e promoção permanecem pendentes. As seções R1 abaixo preservam o estado anterior à correção.

## R1 — achados de integridade a corrigir

**CONCLUSÃO R1:** duas falhas de validação permitem tratar respostas inválidas do scanner como aprovação. Corrigir antes de declarar o gate pronto. Os nove testes existentes passaram em execução própria; não cobrem as duas condições abaixo. Nenhuma evidência mostra que o scanner real tenha emitido essas respostas ou que um aplicativo tenha sido explorado.

### DEP-01 — Média: código 1 sem achados pode produzir gate aprovado

**FATO:** `_run` aceita returncode 0/1 sem confrontar a presença de findings extraídos. Controle próprio com subprocesso simulado: returncode=1, JSON com results não vazio e um pacote sintético sem vulnerabilidades. Os nove alvos existem em diretório temporário próprio, triagem vazia. `audit` retorna status=passed e código 0. Não foi executado scanner, rede ou container nesse controle.

O [contrato oficial do OSV-Scanner 2.7.0](https://github.com/google/osv-scanner/blob/v2.7.0/docs/output.md#return-codes) diferencia retorno sem achados e retorno com achados. A combinação recebida é inconsistente; aceitá-la converte erro/incompletude de resultado em sucesso. Pré-condição: resposta inconsistente do scanner; nenhum controle adversarial dessa resposta foi demonstrado no ambiente real. Impacto: falsa evidência verde. Dono: Severino. Correção esperada: recusar inconsistência entre código e conteúdo, preservando aprovação de relatório limpo coerente e política de severidade para findings válidos. Regressão: o controle acima precisa reprovar, junto de controles legítimos 0/limpo, 1/baixa e 1/alta.

### DEP-02 — Média: NaN na severidade é rebaixado para LOW

**FATO:** `_severity({}, {"max_severity":"NaN"})` devolve LOW. `float` aceita NaN e todas as comparações de limiar retornam falso; a rotina chega ao retorno LOW. `audit` só bloqueia HIGH/CRITICAL/UNKNOWN, logo essa entrada não numérica válida para float evita o bloqueio destinado à severidade desconhecida. Prova própria local, sem scanner ou rede. Pré-condição: metadado malformado e severidade explícita ausente; não foi observado em advisory real. Impacto: classificação desconhecida pode virar evidência não bloqueante. Dono: Severino. Correção esperada: validar valor finito e intervalo CVSS antes de classificar, ou rejeitar o relatório. Regressões: NaN, infinitos e valores fora de faixa; manter limiares válidos e UNKNOWN bloqueante.

## Fronteiras conferidas sem outro achado substanciado

- Workflow só PR/push para dev, runner hospedado, contents:read, sem secrets, checkout sem persistência de credenciais e Actions por SHA. Timeout de job 30 minutos e de scanner 300 segundos por fonte; falha de scanner/parse/triagem resulta em processo não zero. Não há pull_request_target, shell interpolado a partir de evento ou autorização A1 nesse fluxo.
- O instalador existente fixa URL oficial e SHA-256 antes da execução. O binário local confere `160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b`. Apenas o help desse binário foi executado por Neo; confirmou resolução transitiva habilitada por padrão, `--all-packages` e `--all-vulns`. Isso não valida a execução live ou a completude do grafo resolvido.
- Os nove alvos são constantes: quatro diretórios Maven, quatro diretórios npm e requirements PyPI do avaliador. Uso de argv estruturado, sem shell; stdout/stderr brutos não são publicados. O relatório projeta campos técnicos de pacote/advisory. Contagem não nula prova reconhecimento de pacotes, sem provar sozinha identidade de todos os manifests ou lock integral das transitivas.
- Triagem diferente de [] é rejeitada antes de qualquer scan. Não existe exceção ativa para A-002, glob, advisory global ou decisão sem binding. Severity UNKNOWN bloqueia, ressalvado DEP-02. Código baixo/moderado pode permanecer observado por política; não é supressão silenciosa de alta/crítica.
- Upload ocorre mesmo em falha e exige relatório presente. Erro antes da escrita pode deixar ausência de artefato, mas os passos/job falham; ausência não deve ser relatada como execução sem vulnerabilidades. O relatório local não contém SHA/timestamp próprios; a associação ao candidato depende da evidência externa do run, não apenas do nome do arquivo.

## Execução real e pendências

O Oráculo informou que a primeira execução reconheceu 1.020 pacotes e oito altas/críticas, mas o relatório se perdeu. Esses números não são prova auditável dos achados individuais. A segunda execução, PID 44648, estava ativa e sem relatório final na última observação R1; não é aprovada por este parecer. Resultados reais, origem/SHA, término e sanitização serão conferidos quando entregues. Os dois avisos A-002 por cenário ainda não receberam nova triagem a partir desse resultado.

**FATO — bootstrap A1:** `git ls-tree origin/main scripts/pentest .github/workflows/auditoria-dependencias.yml` retornou vazio nesta revisão. O pipeline A0 exige guardas da branch padrão, além do environment/variáveis do dono e gates reais. Portanto integrar o workflow em dev não resolve, por si, a prontidão do A1. O contrato main-só-versões e a exigência de A1 antes da promoção podem formar dependência circular. Escalar ao owner/Oráculo uma decisão explícita de bootstrap confiável, versionada, revisada e testada, que preserve gates; não fabricar aprovação, apontar guardas ao candidato ou afrouxar fail-closed para destravar a execução. Nenhuma mudança de branch padrão, guardas ou ambiente foi feita aqui.

**Avaliação solicitada das alternativas, sem autorização operacional:** o owner pode considerar dev como branch padrão confiável após confirmar revisões e proteções. O workflow já resolve `github.event.repository.default_branch` e fixa a base por SHA; essa opção preserva o mecanismo sem alteração de guardas, mas muda a raiz de confiança. A branch padrão também é a base usual de PRs/commits e sua presença afeta o disparo manual de workflows, conforme [GitHub — branch padrão](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/changing-the-default-branch) e [workflow manual](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow). Risco a controlar: mudanças unilaterais na policy/triagem/guardas da nova base. Exigir revisão/proteção efetivas, gates do SHA exato e approval exclusivo do owner, environment, digests, isolamento e teardown intactos. Outra opção é uma versão preparatória de bootstrap como exceção explicitamente autorizada pelo owner, com escopo e gates aplicáveis documentados; isso não permite declarar A1 ausente como aprovado ou promover aplicações ignorando o gate. Dev como padrão tende a exigir menos alteração técnica, mas sua aceitabilidade depende das proteções comprovadas. Nenhuma opção está aprovada ou executada por este parecer.

## Desenho mínimo de binding, ainda não implementado

Se o owner optar por permitir triagem de pré-condições ausentes, a decisão precisa corresponder exatamente a cenário, ecossistema, pacote, versão resolvida e advisory canônico, sem glob. Vincular também a hash do grafo de dependências observado e snapshot dos fontes/configurações capazes de habilitar o caminho vulnerável. Usar decisão explícita de alcance não demonstrado, preservando componente afetado, severidades do scanner/fornecedor e evidência independente; não representar isso como pacote corrigido.

A política e os registros autorizados precisam vir de uma base confiável revisada, com revisão Neo identificada, evidência por caminho/blob imutável, validade limitada e condição de reabertura. Mudança de código/configuração/grafo, pacote/versão/advisory, expiração, evidência ausente ou correspondência ambígua deve bloquear. Testar positivos exatos e negativos para cada campo, entrada antiga, wildcard, base do próprio candidato e falha de leitura; nenhuma exceção entra no gate antes da implementação e revisão do delta. As provas antigas têm alcances distintos, sobretudo configuração runtime de C3 não observada; não autorizam dispensar automaticamente os oito resultados.

Snapshot R1 dos cinco arquivos, SHA-256 individuais: workflow `4d8a904ad1d04a626ce3d047021873039dd17e25e78a393936ba19e155a599a6`; script `565de0badbd77154e1318f6aa13c74bcdbb31675bef37ee7c8fe8198d242f38c`; testes `f0591211ebe1f43ca79e2357f5979ba0f6fe792a8d6464e8e125013e454ec9e1`; triagem `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`; verificação `4229c00c11c17b6fb3fa6162aba4438595017ddb2a18682f83804c34324cd17b`. Alterações corretivas exigem R2 somente no delta; este snapshot não as aprova antecipadamente.

## Inventário real entregue após R1

O relatório terminal privado autorizado foi lido sem executar novo scanner: SHA-256 `78b9d9864d018884d75e6400561753d60a06c82d35745ee8e4f920a9b87c9779`. JSON válido, nove fontes e soma de 1.020 entradas de pacotes, oito findings CRITICAL pendentes, status=failed. Não há respostas brutas, credenciais, caminhos pessoais ou instruções no relatório; apenas campos técnicos projetados. O local privado não é link de artefato publicado nem prova de execução GitHub. O Oráculo identifica como parser da execução o hash R1 `565de0bad...`; as correções posteriores não foram retroativamente aplicadas à execução. O término do PID e a existência do JSON foram observados, mas seu código de saída não foi coletado por Neo. É inventário informativo; não é gate verde do parser novo.

| Fonte | Entradas de pacotes | Findings |
| --- | ---: | --- |
| C1 Maven / npm | 119 / 145 | Dois CRITICAL em Maven; nenhum em npm |
| C2 Maven / npm | 140 / 71 | Dois CRITICAL em Maven; nenhum em npm |
| C3 Maven / npm | 121 / 176 | Dois CRITICAL em Maven; nenhum em npm |
| C4 Maven / npm | 140 / 106 | Dois CRITICAL em Maven; nenhum em npm |
| Avaliador PyPI | 2 | Nenhum |

Os oito registros são `org.springframework:spring-webmvc` 6.2.19, GHSA-j9f9-w8pj-32f8 e GHSA-pc63-qcmh-9cmg em cada C1–C4. Esses números contam entradas reconhecidas, não necessariamente pacotes únicos entre fontes. Zero findings de npm/PyPI se limita à consulta entregue; não prova ausência global ou eterna de vulnerabilidades.

### Confronto informativo por cenário, sem exceção ativa

Git não mostra mudanças em scenarios entre `13f775b` e HEAD desta revisão. A identidade dos pareceres foi conferida em `security-completion-audit.md`; não houve nova revisão completa das aplicações.

| Cenário, ambos os avisos | Evidência independente anterior e limite | Decisão nesta revisão |
| --- | --- | --- |
| C1 | Neo R2 rastreou rotas REST/exports, sem cadeia SSE/view fragments ou XsltView/catch-all; deltas de auth/semáforo não habilitam esses caminhos. Revisão de fonte, sem confirmação de todos os beans/artefatos externos. | Componente afetado confirmado pelo inventário; exploração não substanciada no recorte anterior. Manter dois findings pendentes no gate. |
| C2 | Neo R2 acrescentou contexto Spring testado e inspeção do JAR histórico aos caminhos REST; delta posterior Login tem identidade própria. O artefato histórico não identifica uma imagem nova. | Componente afetado confirmado; condições ausentes no alcance documentado. Manter dois findings pendentes até binding revisado e evidência correspondente ao candidato. |
| C3 | Neo registrou ausência estática das cadeias, sem comprovar configuração efetiva de runtime. Os hashes relevantes de backend permanecem identificados. | Componente afetado confirmado; runtime continua não observado. Não dispensar os dois findings por inferência de arquitetura ou busca textual. |
| C4 | Neo R1/R2 rastreou REST/exports sem SSE/fragments/XSLT/catch-all; correção delimitada Login/UTF-8 preserva os demais arquivos de produção. | Componente afetado confirmado; exploração não substanciada no recorte anterior. Manter dois findings pendentes no gate. |

Severidade CRITICAL do scanner permanece; a divergência LOW/MEDIUM do fornecedor registrada em A-002 não é usada para reduzi-la neste relatório. Nenhum registro foi escrito na triagem vazia. O relatório projetado atual não contém a lista integral/hashes do grafo e dos fontes: sozinho não fornece o binding mínimo proposto. A avaliação de alcance acima é informativa e não muda status, retorno do scanner ou autorização A1.

## R2 — somente delta corretivo estável

O Oráculo informou entrega estável de Severino; os hashes foram conferidos antes e depois da execução própria dos 13 testes focados, sem divergência: script `6510ee194a79b794c29e500a7a3382f21a861aff60ba401c4f8917adf293b961`, testes `440ccda243943fb562ce6a7f2d66ef2ed0e83e7e518051d96f6e8fd1b8524098`. Workflow, triagem vazia e documentação conservam os hashes R1. O Oráculo informou 66/66 testes amplos e validação de sintaxe/YAML; esses checks amplos não foram repetidos por Neo.

**FATO — DEP-01 corrigido:** o parser conta findings e rejeita retorno 1 sem achados, assim como retorno 0 com achados. As regressões próprias retornaram erro para ambas as combinações contraditórias. Controles próprios com JSON sintético e subprocesso simulado preservaram relatório limpo coerente e finding LOW válido; CRITICAL permaneceu CRITICAL. Nenhum desses controles executou scanner ou rede.

**FATO — DEP-02 corrigido:** float não finito ou fora de 0–10 vira UNKNOWN. Os testes cobrem NaN, infinito, números fora de faixa e texto inválido. O controle próprio NaN passou a produzir UNKNOWN, cuja barreira de audit permanece bloqueante. O delta adicional de severidade conserva o nível mais alto entre label válido e escore válido; label desconhecido ou escore inválido não rebaixa o finding. A regressão de conflito foi lida e executada entre os 13 casos aprovados.

**CONCLUSÃO R2:** nenhum achado substanciado remanescente nos controles corretivos examinados. DEP-01 e DEP-02 estão fechados nesse conteúdo. Não foi reexecutado scan real com o parser novo: o inventário anterior continua identificado pelo hash próprio e status failed, sem oito dispensas ou aprovações retroativas. A próxima proposta de binding/fluxo confiável é trabalho separado e exige implementação/testes/revisão antes de habilitar qualquer decisão. Nada nesta R2 autoriza alterar guardas, branch padrão, environment, variáveis ou aprovação do owner.
