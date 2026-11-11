Ficha: tarefa=benchmark-recovery/C4-qa-recovery agente=patrick-jane modelo=gpt-6.1-sol esforço=medium skill=verificar-antes-de-concluir,e2e-testing,humanizer

# QA C4 — recuperação do gate interrompido

Data: 2026-11-11T18:48:16Z. Escopo: somente C4, especificação, protocolo, configurações e emendas comuns. Continuação do gate interrompido, sem reiniciar implementação nem abrir terceira rodada. Nenhuma fonte de aplicação ou evidência anterior foi alterada. Memória indisponível conforme quadro da retomada. Avaliador privado, outros cenários e comparativos não foram lidos.

**Parecer: parcialmente aprovado quanto às evidências funcionais disponíveis; entrega completa ainda pendente.** Não foi substanciado defeito funcional novo nesta leitura. Há provas autorais relevantes e reproduções locais positivas, porém falta executar a avaliação comum e fechar CI/pentest. Pendência executável não caracteriza dependência indisponível nem autoriza declarar o cenário bloqueado.

## Identidade e reaproveitamento das provas

HEAD observado da raiz: `8550effde9d661057edafca4614b6d28bf07e0eb`. C4 aparece como `?? scenarios/c4-manager-advanced/`; esse HEAD não identifica sua implementação. A identidade válida é o conteúdo:

- Os 36 arquivos de produção/configuração, calculados pelo algoritmo de `security-review.md`, produzem SHA-256 `960690818506b1b0fdca9802d2ae0d4aa46d8e2ae5c106c7825fab575ea10f9c`, igual ao snapshot Neo R2.
- `source-manifest.json`, de 2026-11-06T18:11:35.452448+00:00, contém 61 arquivos: nenhum ausente; 60 hashes coincidem. A única divergência é `scripts/pentest/api-cases.py`. O delta de fixture é mencionado em `pentest-preparation.md` e `security-review.md`; o manifesto anterior deve permanecer preservado. A integração precisa registrar o hash atual desse script no novo snapshot.
- Os XML Surefire locais confirmam os números de `backend-tests.json`: 2 integrações e 3 unitários, zero falhas/erros/skips. Leitura de resultado anterior, sem nova execução Maven.
- `ui-tests.json` registra 2 jornadas esperadas, zero falhas/skips/flaky, início 2026-11-06T14:24:46.465Z e duração 14.779 segundos. Quatro resumos axe têm zero violações e zero verificações incompletas. Fonte do teste e hashes foram confrontados; são provas autorais reaproveitadas, sem nova sessão navegador.

## Alcance contra os requisitos

| Área | Evidência disponível | Limite relevante |
|---|---|---|
| Cadastro, login, logout | Integração com PostgreSQL/Testcontainers, duplicidade normalizada, credencial inválida, revogação; UI autoral | Expiração de sessão não exercitada. Limites de cadastro não têm matriz de bordas completa. |
| CRUD e isolamento | Backend valida IDOR GET/PUT/DELETE; UI cria, consulta, edita e exclui com cancelamento/confirmação | Sem execução independente da aplicação recuperada nesta revisão. Mass assignment está coberto pela análise Neo e pelo caso A1 preparado, ainda não executado. |
| Precisão e validação | Unitários rejeitam valores inválidos; integração aceita máximo e data futura; Vitest preserva moeda/data local | Não há prova de rejeição de toda data inválida nem de ausência de persistência parcial em todos os caminhos. |
| Filtros, resumo, paginação e ordem | Integração combina filtros literais, testa limites inclusivos, total/páginas, amount asc e intervalos invertidos | Não cobre as quatro ordens com empate por id, páginas sucessivas, todas as bordas page/size e consistência de cada combinação entre lista/resumo/ambos exports. |
| PDF e XLSX | Integração interpreta PDF e workbook; smoke autoral interpreta ambos com seleção e saldo | Cobertura parcial de combinações, grandes seleções e renderização legível; o A1 preparado verifica apenas assinatura/tipo de PDF. |
| Interface | Jornadas desktop 1280 e mobile 360: CRUD, detalhes, filtros, downloads, ausência de overflow e axe; dois temas/modos auditados | Downloads da jornada conferem nome, não conteúdo. Não há cobertura navegador de todos os estados de erro/carregamento nem todos os temas. |
| Execução e recuperação | Smoke Compose e restore sintético autorais; dependências e stacks conformes às emendas lidas | `docker ps` não encontrou stack puck-c4 ativa nesta retomada; prontidão atual não foi comprovada. Restore confere contagens, não equivalência integral dos dados. |
| Segurança | Neo R1 e R2, scanners autorais e tratamento A-002 explícito | Componente continua afetado; nenhum scanner ou pentest foi executado por este QA. A0 é somente preparação. |

As lacunas acima delimitam o que ainda precisa ser provado; não são afirmações de que o comportamento está defeituoso. Não é necessário duplicar cada teste se a avaliação comum fornecer evidência suficiente.

## Comandos executados na retomada

Além das leituras delimitadas, inspeção de Git e hashes com Python stdlib:

| Comando | Resultado observado |
|---|---|
| `npm test --prefix frontend` | exit 0; 2 testes Vitest passaram. |
| `./node_modules/.bin/tsc --noEmit --incremental false` no frontend | exit 0; nenhuma saída. |
| `./node_modules/.bin/vite build --outDir /tmp/c4-qa-recovery-build-20261111` no frontend | exit 0; 33 módulos, build em 774 ms; aviso de diretório externo não esvaziado. |
| `python3 design/contraste.py` | exit 0; 330 pares, zero falhas/erros; cobre tokens. |
| `python3 -B scripts/pentest/runner.py prepare` | exit 0; `preparacao-A0-validada`, `rede_utilizada:false`, `pentest_executado:false`. |
| `git diff --check -- scenarios/c4-manager-advanced` na raiz | exit 0; arquivos C4 não rastreados, portanto alcance limitado. |
| `docker ps --filter name=puck-c4 --format '{{.Names}} {{.Status}} {{.Ports}}'` | exit 0; sem linhas. |
| `ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height -of json scenarios/c4-manager-advanced/evidence/jornada-final.webm` na raiz | exit 127: ffprobe ausente; nenhuma validação audiovisual nova. Arquivo existe. |
| `python3 benchmark/scripts/telemetry.py phase --agent /root/c4_qa_recovery --phase testes --scenario C4 --task qa-recovery` | exit 0; fase registrada durante a retomada, sem atribuição retroativa. |

Uma primeira extração dos resumos axe falhou com TypeError ao tratar o contador `incomplete` como lista; extração corrigida confirmou os contadores descritos acima. Essa falha foi do comando de inspeção, não da aplicação.

## Achados e próximos gates

1. **Escalar — gate de CI pendente.** `scripts/ci/{code,test,security,architecture}-review.sh` continuam com `exit 1`; templates aninhados não provam execução. Integrar controles reais na raiz, rodar CI rápida e CI completa pertinente, preservando conclusões dos revisores independentes. Dono: Oráculo; mudanças de segurança/CI exigem revisão adequada.
2. **Escalar — pentest A1 pendente.** Preparação A0 passou, mas não substitui execução isolada, fixture de expiração, DAST autenticado, segurança de UI e triagem independente descritos na preparação. Respeitar autorização e ambiente protegidos; nenhum teste ofensivo foi realizado neste host. Donos: Oráculo/Mr. Robot/Neo.
3. **Corrigir registro na integração — vinculação ao candidato.** Registrar SHA do commit que efetivamente contenha C4 e novo manifesto para o delta `api-cases.py`, sem reescrever o manifesto histórico. As provas anteriores devem manter autoria e timestamp originais.
4. **Escalar para avaliação comum — cobertura funcional incompleta.** Iniciar stack recuperada e executar avaliador comum independente, incluindo expiração, ordenações/desempate, bordas de paginação e seleção consistente nos exports. Este QA não leu nem executou o avaliador privado. Verificar resultado no candidato integrado antes da conclusão.
5. **Limitação documental — demonstração audiovisual parcial.** `video.json` descreve login, dashboard, detalhes, modo escuro e logout; não demonstra sozinho cadastro/edição/exclusão/filtros/exportações exigidos na especificação. A jornada automatizada fornece alternativas verificáveis para esses fluxos. Registrar explicitamente o vídeo como parcial ou completar a demonstração, sem declarar sua abrangência integral.

Este parecer recupera o estado de QA; não concede aprovação de segurança geral, CI, pentest, merge ou promoção. Novas alterações de aplicação exigem avaliação do delta dentro dos limites de rodadas já definidos.
