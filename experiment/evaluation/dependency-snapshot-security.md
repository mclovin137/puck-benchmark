Ficha: tarefa=benchmark-recovery agente=neo modelo=gpt-6.1-sol (adaptador declarado; runtime não inspecionado) esforço=high skill=security-audit,verificar-antes-de-concluir,humanizer.

# Consumidor inativo do snapshot — revisão R1

Chamada conferida: tarefa, aceite e escopo presentes; revisão independente de CI e fronteiras de confiança dentro do papel. Em 12/11/2026, HEAD `031c1f46eda14e115e5e03a315ea128eb18f319d`, base de comparação `076116b`. Novo bloco: dependency_snapshot.py, delta dependency-audit.py, dois módulos de testes e payload proposto de policy/provas. Só este relatório foi escrito no escopo versionável. Não houve leitura de código de aplicação ou avaliador funcional privado, alteração de records, workflow, aplicação, controles GitHub, A1, commit ou push. Fixtures Git e canários inertes existiram somente em diretórios temporários próprios.

**CONCLUSÃO R1:** corrigir os vínculos descritos abaixo antes de recomendar ativação. A policy real continua proposed/pending_neo; triagem padrão vazia e oito findings bloqueantes permanecem. O controle positivo demonstra o caminho combinado com dados sintéticos, sem aprovar uma execução real com a policy ativa. DEP-01/DEP-02 do bloco anterior não foram reabertos; esta revisão cobre a nova extensão de contrato.

## SNAP-01 — Média: primários de advisory não são vinculados ao consumidor

**FATO:** `_advisory_records` valida os dois JSONs primários e seu manifest, mas não é chamada por prepare_snapshot, assert_authorization_current ou outro caminho. `_validate_policy` verifica somente o formato de record.advisory_sha256; a ligação entre esse valor e o manifest primário não é exigida.

**Reprodução própria:** checkout source/trusted sintéticos separados e limpos, quatro cenários, árvores canônicas, scanner medido de fixture, oito records ativos apenas na fixture e evidência com hash do manifest OSV. O manifest OSV contém records=[] e os JSONs primários estão ausentes. prepare_snapshot autoriza oito records; a checagem final aceita; um finding exato recebe decisão. Chamar o validador `_advisory_records` sobre esse mesmo manifest o rejeita. Maven e scanner foram simulados; nenhum pacote, rede ou fonte de produto foi executado.

**Impacto e pré-condição:** ao consumir uma base autorizada que contenha vínculo incompleto/inconsistente, o mecanismo pode aplicar decisão sem a evidência primária prometida pelo contrato. Não prova que o payload atual tenha metadata incorreta ou que um candidato possa escolher a base. É falha do vínculo, não exploração da aplicação. **Dono:** Oráculo/implementador. **Correção esperada:** validar os primários/manifest no preparo e na verificação final e exigir, para cada record, igualdade do digest primário correspondente. **Regressões:** positivo completo; ausência/alteração de primário, manifest incompleto, identidade/digest/modified divergentes e metadata alterada entre preparo/final devem bloquear.

## SNAP-02 — Média: bytecode ignorado pode substituir o helper verificado

**FATO:** o carregador mede dependency_snapshot.py contra o blob Git, depois chama SourceFileLoader.exec_module. Python pode executar um `.pyc` válido de `__pycache__` nesse ponto. `sys.dont_write_bytecode=True` impede escrita, não leitura. O cache pode ser ignorado pelo Git e escapar do status usado como guarda.

**Reprodução própria:** trusted/source em Git temporário, avaliador/helper com bytes correspondentes ao SHA fixado e regra de ignore para __pycache__. Execução por python3 -I, sem cache: canário não existe. Inserir cache com timestamp/tamanho correspondentes ao fonte, mas contendo somente escrita de marcador inerte e RuntimeError, mantém Git clean no escopo. Nova execução cria o canário antes de terminar com helper inválido/código 2. O código executado, portanto, não é o blob medido. Não houve Maven, scanner ou rede nesse controle.

**Impacto e pré-condição:** requer controle de cache preexistente no trusted worktree; essa condição não foi observada no ambiente real e não há exploit de PR demonstrado. Uma limpeza efetiva do checkout pode impedir a pré-condição, mas o consumidor atual não a comprova nem recusa esse cache. O resultado falha, porém a execução já ocorreu. **Dono:** Oráculo/implementador. **Correção esperada:** carregar por compile/exec os próprios bytes previamente verificados, sem seleção de bytecode de cache; manter isolamento Python e separação de roots. **Regressões:** helper legítimo continua funcionando; cache forjado não executa o canário e fonte/helper alterados continuam recusados.

## SNAP-03 — Média: configuração do candidato pode ocultar findings do OSV

**FATO:** `_run` não fornece configuração neutra ao scanner. A [documentação oficial OSV](https://google.github.io/osv-scanner/configuration/) permite ocultar pacotes/findings em osv-scanner.toml e define --config como substituição das configurações dos diretórios. --all-vulns não neutraliza esses overrides.

**Prova real do Oráculo, conferida por Neo nos metadados:** dois manifests neutros iguais com pypdf 6.0.0 e typing_extensions 4.15.0, sem instalação ou execução dos pacotes. Scanner 2.7.0, mesma opção --all-vulns. Sem TOML: exit 1, três entradas de pacote e 113 entradas de finding. Só adicionar PackageOverrides para ignorar pypdf/PyPI: exit 0, duas entradas e zero findings. Raw JSONs privados têm SHA-256 `c978735924a2f76a87ed945ac221c6237b2b82771cce518f61e33ebe639a0de9` e `8c887f7bc284ee00718ac6b404e59b0d2259863ef3c501ae8cd9e99eab3c53cb`. Neo não repetiu os scans. Controle próprio de `_run` com esses JSONs/retornos simulados aceita a saída filtrada como dois pacotes e nenhum finding.

**Impacto e pré-condição:** o candidato controla configuração ao lado de um manifest escaneado. benchmark/requirements.txt e a configuração OSV nesse diretório ficam fora do digest dos cenários; portanto o binding dos oito A-002 não impede ocultar um finding adicional nessa fonte. A contagem continua não nula e o retorno é coerente, escapando das guardas de parse. Não se afirma exploit de PR no GitHub ou supressão já publicada neste projeto. **Dono:** Oráculo/implementador. **Correção esperada:** o avaliador cria TOML vazio privado fora do candidato e o fornece explicitamente como configuração global em todas as nove fontes. Não criar allowlist. **Regressões:** conferir argumento/origem/conteúdo neutro e demonstrar, com o mesmo controle real, que configuração candidata deixa de ocultar os findings; preservar scanner/parse/UNKNOWN bloqueantes.

### Compatibilidade adicional — campos opcionais do OSV

**FATO:** o baseline real acima tem 47 entradas sem database_specific. A extensão do parser o rejeita por ausência de campos obrigatórios antes de produzir inventário. As funções de hash exigem presença de todos os campos, enquanto a canonicalização declarada do manifest usa missing → null. O campo [database_specific no formato OSV](https://ossf.github.io/osv-schema/#database_specific-field) é informação adicional da base. Isso é incompatibilidade/falha de evidência, não falsa aprovação: o erro atual falha fechado. Recomendação de qualidade: alinhar a representação de campos opcionais ausentes entre hash do finding e do primário, mantendo identidade/estrutura obrigatórias e severidade UNKNOWN bloqueante; ausência de metadado não pode virar LOW ou dispensa. O caso foi identificado com dados recebidos, sem exigir testar pacotes na aplicação.

## Controles positivos e fronteiras conferidas

- Neo executou os 27 testes focados; todos passaram. A rodada final conferiu os quatro hashes antes/depois sem alteração. A fixture de relógio foi congelada pelo Oráculo durante o bloco; sua correção foi tratada como delta de teste, sem atribuir um RED histórico não observado ao implementador original.
- Controle próprio combinado com primários OSV válidos, Git source/trusted separados, quatro árvores, nove fontes e policy ativa **somente em fixture**: prepare_snapshot → audit → checagem final. No modo padrão, código 1, failed e oito pendentes; com opt-in, código 0 e oito CRITICAL preservados como aplicada. Apenas resolução Maven e scan foram simulados. O controle mantém o positivo legítimo enquanto os negativos acima isolam os vínculos ausentes.
- O opt-in exige roots separados, SHA externo exato, avaliador/helper em layout confiável e bytes de blob limpos. Policy candidata é ignorada; não há auto-SHA na policy nem fallback para código candidato. O carregamento ainda precisa da correção SNAP-02. A inexistência de policy/avaliador admitidos bloqueia o CLI real, em vez de substituir silenciosamente pela cópia candidata.
- A medição cobre o cenário inteiro e o conjunto comum fixado, usando caminhos canônicos, blobs regulares, comparação dos bytes com object IDs e hashes. Symlinks, entradas não resolvidas, árvore modificada e novo arquivo relevante são recusados nos controles observados. Nenhum digest declarado pelo candidato substitui o recálculo.
- Scanner binário tem hash real fixado e pin do instalador. Árvores preservam relações e escopos, canonicalização e versão Spring. Maven copia somente o POM para projeto temporário, com settings, home e repository próprios, ambiente restrito e MAVEN_PROJECTBASEDIR temporário; não herda `.mvn` do cenário/ancestral. O teste desse isolamento foi lido e executado com subprocesso simulado. A execução real C1 de 20,328s, com digest correspondente, é informação do Oráculo; Neo não duplicou o comando em andamento nem executou resolução real.
- Validade UTC de até 30 dias, status ativo explícito, oito identidades fechadas, reviewer Neo e evidence blobs exatos são exigidos. UNKNOWN, mudança de advisory do finding, pacote/versão diferente e expiração não recebem decisão. A verificação final revalida tempo, policy, fontes e scanner, sem tornar records globais por alias.

## Payload proposto — conferência sem ativação

SHA-256 do JSON examinado: `401ddb9a87e4e46db6cc71a6b18d2043b5e774f994a649cebb9272b315ecf8b3`. Status superior e oito records estão proposed, reviewer=pending_neo. O validador o recusa como política não ativa. Foram conferidos por recálculo os oito pares C1–C4 × GHSA-j9f9-w8pj-32f8/GHSA-pc63-qcmh-9cmg, os blobs de evidência, os quatro digests de fonte, as árvores e os campos de segurança dos dois JSONs primários. Não foram lidos novos fontes de aplicação: hashes e pareceres já produzidos sustentam a identidade e o alcance A-002.

| Cenário | Source SHA-256 | Grafo canônico SHA-256 |
| --- | --- | --- |
| C1 | `329c4ecf7f262c5c9c7218a2bfddf54cb637e63409a27a6acb6e7c78046583d7` | `37741ac746080dfa8b26ef37732299da4914ecda5fe447df533400c2fd53844d` |
| C2 | `6933fead525fbffb318b4121a8eb5738f9bee04cb5a11f5d48e11b9911e8cbfe` | `632766885f2b7783f2db1ecd6b82b632c08a2e4ef8d0700d9209bc6030c0f701` |
| C3 | `cdfebf756bea0238a2bc8525710f408e6b3207c9a5409fe76f8992201cf6ea13` | `d0cb4939c44d6a9c74a166d78c9ce5c49b82aff91ff1a3db8f8314c833c3b294` |
| C4 | `0cb71dbe587e8c52242abb4933819091f118074d792fafdef34580c6cb7f339a` | `174580aed141a89a2c2a28bf2b20ca78b19e72be0fcdc075ffbecc80937c4787` |

As árvores têm respectivamente 113/131/113/131 nós e um número de arestas menor em uma unidade; todos incluem spring-webmvc 6.2.19. Os digests primários são `9ce056d8bc6297dd2d8d3500e8750b152958f22f8e9622f274bc9416a6455f53` e `83d7a84aa6ec2996584950dc6163ec6a42f7cb002d92bafb95587f6880df57d6`. Emissão `2026-11-12T17:53:31Z` e término `2026-12-12T17:53:31Z` são 30 dias, sem renovação automática.

**Avaliação de mérito:** as oito decisões propostas têm fundamento nos pareceres A-002 e vínculos conferidos, incluindo o complemento runtime C3, mantendo componente afetado e risco residual. Isso não recomenda ativação enquanto houver falhas no consumidor. Qualquer alteração de payload, provas ou fontes exige conferir o delta; o owner só poderá admitir/ativar após parecer explícito da versão corrigida e gates da admissão. Não há dispensa implícita neste R1.

## Identidade e limites

Snapshot R1: helper `0f07281887de188cb96a38e988eb0c2c40b8da7da02368586f76568ac89db58d`; avaliador `8ac3ca480e1904759201832658b0402691f672bade9f04d8df94e9d4075f135a`; testes snapshot `c2f849eab74fc93f8f63724b2d1ecbe377f1a3432c2373d95690ece8f65fbe3e`; testes audit `bd2e1592d76fedcb6d99f1a6590f2019871decf5901efcbfeb3b61d6766f8882`. Revisão da correção será R2 somente no delta. A execução de CI desse consumidor, política ativa real, isolamento do futuro workflow e admissão em dev não foram observados nesta revisão. A1 e a decisão owner de bootstrap continuam independentes.

## R2 — correções dos vínculos e transição exata da policy

**Parecer vigente: aprovado no escopo técnico para admissão em dev do consumidor e das oito decisões vinculadas abaixo, sujeito aos gates já exigidos.** SNAP-01, SNAP-02 e SNAP-03 estão corrigidos no conteúdo conferido; nenhum achado substanciado remanescente no delta. Isso não autoriza ignorar check reprovado, nem declara consumidor ativo, execução real de opt-in, CI verde, merge, A1 ou promoção. Somente este relatório foi alterado por Neo nesta R2; a policy e as provas referenciadas permaneceram intactas.

**FATO — SNAP-01:** prepare_snapshot e assert_authorization_current agora leem os primários/manifest e vinculam cada record ao digest do advisory correspondente. Neo repetiu o controle combinado em fixtures Git com Maven/OSV simulados: default failed com oito pendentes; opt-in passed conservando oito CRITICAL como aplicada e checagem final válida. O controle original com primários ausentes/manifest vazio agora é rejeitado. Um segundo controle próprio alterou o primário depois do preparo e ocultou a alteração do Git status com assume-unchanged: a checagem final recusou os bytes divergentes do blob. Não depende apenas de detectar dirty worktree.

**FATO — SNAP-02:** o helper é compilado/executado a partir dos mesmos bytes que passaram pela conferência de blob; não há SourceFileLoader escolhendo cache. Neo repetiu a reprodução anterior por CLI python3 -I em Git temporário, com cache forjado válido por timestamp/tamanho: o canário não foi executado e o helper genuíno foi carregado. A fixture terminou bloqueada por scanner ausente, como esperado, sem disfarçar isso como gate aprovado. O teste autoral de fonte legítima também passou.

**FATO — SNAP-03 e compatibilidade:** `_run` cria TOML vazio em diretório temporário próprio e fornece --config para cada modo/fonte. O Oráculo executou novamente o controle real, mantendo o TOML candidato de ignore presente: três entradas de pacote, 113 findings e zero UNKNOWN, conforme fixed-neutral-result.json privado. Neo não repetiu a varredura real; conferiu o resultado e reprocessou por mock o JSON real original, verificando durante a chamada o arquivo externo absoluto, regular e vazio: mesmos 3/113/0. Campos opcionais severity/database_specific ausentes agora são canonicalizados como null, sem dispensar id/modified/affected obrigatórios ou converter UNKNOWN em aprovação. Os achados legítimos antes rejeitados por falta de database_specific permanecem no inventário.

Neo executou os 35 testes focados e conferiu hashes iguais antes/depois; código zero, sem falhas. O Oráculo informou a regressão RED de quatro falhas/dois erros, GREEN 35 e suíte ampla 88 aprovada; Neo não presenciou o RED nem repetiu os 88 testes. As verificações próprias acima são controles adicionais delimitados, sem Maven real, instalação de pacotes, aplicação, HTTP ou A1.

| Arquivo R2 | SHA-256 |
| --- | --- |
| dependency-audit.py | `b98530807b83c5c1661eba3b3bd1124d2a470cb6ed0f0874d3bce47dbb78b58c` |
| dependency_snapshot.py | `e77109f4b0f0621be19841909662a94ea70f4547e60ceee2c063eb5ad1d6d0e8` |
| test_dependency_audit.py | `ce45e275f66ee2e5f0427b77b902b37dc828a4e447ece6cc401ddd7c8153dc61` |
| test_dependency_snapshot.py | `7a00902edc534067f24f45eea75823247bc8d3d14121110a524a934635fb1adf` |

### Payload delimitado aprovado para a transição

O JSON real continua com SHA-256 `401ddb9a87e4e46db6cc71a6b18d2043b5e774f994a649cebb9272b315ecf8b3`, status proposed e reviewer pending_neo. O mérito das oito decisões e todos os seus vínculos da R1 permanecem válidos. **Aprovo tecnicamente o Oráculo aplicar somente:** status superior → active; status de cada um dos oito records → active; reviewer de cada record → neo. São 17 valores alterados, calculados em memória; nenhuma modificação foi gravada por Neo.

Preservar datas, identidades, digests, risco residual, evidências, ordem dos campos e serialização JSON UTF-8 com ensure_ascii=false, indent=2 e LF final. O **SHA-256 esperado da versão após essa transição exata é `8530c564ed3c0823575515173ee1525c09bb026af4f42338e609a9965d3d4ea5`**. Qualquer outra mudança fica fora deste aceite e exige conferência do delta. O prazo permanece o mesmo, sem renovar os 30 dias na ativação.

O consumo dessas decisões pela CI depende de avaliador, policy e provas admitidos no mesmo SHA confiável de dev e de workflow que fixe esse SHA e mantenha source/trusted separados com isolamento Python, conforme desenho já revisado. Nenhum opt-in foi adicionado ao workflow nesta R2. O modo padrão e a triagem vazia seguem sem dispensa dos oito findings. Aprovação técnica para admissão não comprova que a admissão ou o consumo tenham ocorrido. Componente afetado/CRITICAL permanecem visíveis quando a decisão for aplicada; ausência de pré-condições no snapshot não é patch da biblioteca nem aprovação global de segurança. Controles GitHub e bootstrap/A1 continuam exclusivamente com o owner e não foram aprovados aqui.
