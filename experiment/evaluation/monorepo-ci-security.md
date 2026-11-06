# Segurança da CI de componentes e do runtime — PR #3

Primeira rodada, encerrada em 2026-11-06T02:54:14Z. Candidato `b1a03f874db364a1ca2fc289f5485a5e82052a52`, base `7b8a691`, 24 arquivos. Revisor: Neo, independente da implementação. Nível crítico pela execução de componentes e configuração de CI. Modelo e consumo desta revisão são overhead.

**CONCLUSÃO — REPROVADO no candidato inspecionado.** Dois achados médios confirmados precisam de correção: a validação de runtime aceita acesso a recursos fora do projeto e uma falha de coleta do commit pode terminar como sucesso. Nenhum comprometimento, acesso a segredo real ou execução ofensiva foi demonstrado. Os gates das aplicações continuam não observados; este parecer não os aprova.

## Escopo e método

Leitura estática do delta: workflows, roteamento de componentes, launcher, instalador, testes, métricas, Dependabot e A-002/probe neutro. As 17 aprovações de testes públicos e uma integração nativa local foram informadas pelo Oráculo e não repetidas. CI remota estava em curso, sem aprovação declarada nesta revisão.

As reproduções próprias usaram funções extraídas por AST do launcher e fixtures sintéticas. Na reprodução do fluxo completo, ROOT apontou para diretório temporário, o ambiente foi vazio e todos os subprocessos e esperas HTTP foram simulados. Nenhum Compose, scanner, build, binário baixado ou aplicação foi executado. Não foram lidos arquivos de cenários, resultados de aplicações, `.private/`, logs reais, conversas ou credenciais. A fonte privada Puck e o bootstrap não foram alterados.

## Achados confirmados

### M-01 — Média: validação do Compose não limita montagens de serviços nem interfaces publicadas

**FATO.** `benchmark/scripts/run_system_evaluation.py:37-40` examina somente `config.volumes`. A configuração de cada serviço não passa por controle de suas montagens antes de `compose up` em `:74-80`.

Reprodução sintética: configuração com `volumes` do topo vazio e `services.backend.volumes = [{"type":"bind","source":"/synthetic-host-data","target":"/data"}]` foi aceita por `assert_owned_volumes`. Nenhum caminho real foi montado. O prefixo do projeto não limita bind mounts: a semântica de volumes de serviço permite mapear diretórios do host para o container. [Referência oficial do Compose](https://docs.docker.com/reference/compose-file/services/#volumes).

**Impacto e precondições.** O autor de um Compose entregue ao launcher pode fazer o processo automatizado iniciar containers com dados do host montados fora do projeto efêmero. Não é necessário contornar a verificação atual: esses campos simplesmente não são inspecionados. A capacidade de escrever ou ler esses dados depende do mount e das permissões do processo. A prova demonstra aceitação e caminho até a execução, não que alguma aplicação do experimento já use esse recurso. O host compartilhado já era uma limitação conhecida; esta nova automação não deve tratar o namespace `-p` como confinamento das montagens.

Na mesma fronteira, `published_urls:22-34` ignora `host_ip`: uma porta em `0.0.0.0` é aceita e um bind em IP específico também vira URL `127.0.0.1`. O primeiro pode expor o ambiente fora do host; o segundo pode fazer a espera HTTP consultar endereço diferente do efetivamente publicado. São consequências da ausência de validação de interface, sem acesso externo reproduzido. [Semântica oficial de portas e host IP](https://docs.docker.com/reference/compose-file/services/#ports).

Dono: Oráculo/implementador da infraestrutura. Correção esperada: validar a configuração resolvida antes de marcar recursos como autorizados e iniciar o Compose; rejeitar montagens fora do escopo permitido e recursos que ampliem acesso ao host; restringir interfaces publicadas ao alcance local previsto e construir destinos coerentes com elas. Regressões sintéticas devem rejeitar mount externo e publicação fora do escopo, preservar o caso legítimo e comprovar que a rejeição ocorre antes de `up`. O tratamento deve permanecer focado nesse launcher, sem presumir isolamento completo do host.

### M-02 — Média: erro após o aceite mantém resultado e exit code de sucesso

**FATO.** Em `run_system_evaluation.py:84`, o retorno zero do aceite é imediatamente copiado para `code` e `result.success`. Se a obtenção do commit em `:85` falhar, o `except` em `:87-88` registra apenas `error_type`; não restaura estado de falha. Com cleanup bem-sucedido, o processo retorna o zero anterior em `:95`.

Reprodução integral sintética: resposta de configuração válida, `up` e aceite retornando zero, falha `CalledProcessError(128)` no `git rev-parse HEAD`, cleanup zero. Resultado observado: saída zero, `success: true`, `stage: acceptance`, `error_type: CalledProcessError` e ausência do campo `commit`.

**Impacto.** Um erro de infraestrutura/proveniência pode ser contado como execução aprovada pelo job que usa o exit code, embora o próprio JSON registre erro e não identifique o commit. Não depende de a aplicação estar vulnerável. Dono: Oráculo/implementador. Correção esperada: toda exceção do caminho avaliado deve restaurar `code != 0` e `success: false`; sucesso só é confirmado quando as etapas obrigatórias terminam. Regressão: simular a falha após aceite verde e verificar saída não zero, erro sanitizado e cleanup tentado; preservar o caso completo legítimo.

## Fronteiras revisadas sem bloqueante adicional

**FATO — Matriz e roteamento.** A promoção inclui quatro cenários fixos, `fail-fast: false` e um resultado de matriz exigido pelo gate final. Os scripts usam argumento de cenário com escolhas fixas, caminhos derivados do mapa interno e subprocessos em lista, sem shell. A seleção por diff exige SHAs completos e falha se o Git falhar. Backend exige POM e executa Maven verify; frontend exige lockfile e scripts test/build. PRs só de infraestrutura continuam com alcance de infraestrutura, sem inferir teste das aplicações. A presença de comandos não comprova execução: não li manifests nem resultados de cenários.

**FATO — Credenciais e limpeza.** O launcher cria nomes de projeto aleatórios, gera valores efêmeros para chaves convencionais de banco/token e os mascara no Actions. Configuração resolvida e logs brutos não entram no JSON de resultado, que contém campos fixos e tipo da exceção. `down --volumes --remove-orphans` recebe o mesmo projeto e é tentado em `finally` depois da autorização atual dos recursos. Isso favorece rastreabilidade e limpeza própria, mas não corrige M-01 nem comprova que todos os Compose usarão as variáveis geradas; essa aplicação efetiva depende da configuração de cada cenário. Limpeza em cancelamento abrupto e isolamento completo do host não foram testados.

**FATO — Artefatos e permissões.** Os workflows mantêm checkout por SHA, credenciais não persistidas e permissões de leitura. A matriz publica somente caminhos JSON de aceite/runtime e não inclui os logs privados. O glob com `always()` pode incluir arquivos anteriores já existentes: os consumidores devem conferir commit, timestamps, estágio e status, sem tomar a mera existência de artefato como aprovação. Não foi observado payload sensível; validação adicional do esquema antes do upload é endurecimento, sem exploração confirmada neste escopo.

**FATO — Instalador OSV.** O instalador admite somente Linux amd64, fixa URL/versão/hash, confere o digest antes de substituir o arquivo e não executa o binário baixado. A consulta própria à API pública da release oficial confirmou o asset `osv-scanner_linux_amd64` e digest `sha256:160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b`, igual ao código. [Release oficial v2.7.0](https://github.com/google/osv-scanner/releases/tag/v2.7.0). Não baixei nem executei o scanner. Fixação por digest não dispensa revisão da ferramenta, mas não houve divergência de origem identificada.

**FATO — Dependabot e métricas.** Dependabot abre atualizações para `dev`, com limites por ecossistema; não adiciona automerge ou credenciais. O workflow de métricas tem permissões de leitura e passa janela/repositório por argumentos, sem avaliação de shell. A saída agrega contagens e números de PR, sem publicar títulos, corpos ou nomes de arquivos coletados. A contagem de CI por branch e limites de paginação são proxies de acompanhamento, não evidência de causalidade nem gates de aprovação.

**FATO — A-002 e probe neutro.** O POM compartilhado contém somente dependências e propriedades da stack, sem implementação de aplicação. A-002 preserva as configurações/freeze originais, versões substituídas, alertas remanescentes e divergência de severidades. Não cria dispensa global dos dois componentes Spring: exige revisão por aplicação e mantém o gate pendente sem prova. Nas fontes oficiais consultadas, o primeiro advisory envolve SSE com fragmentos de view e dados controlados por atacante; o segundo envolve `XsltView` e mapeamento abrangente com nome de view implícito. As fontes preservam severidades LOW/MEDIUM, distintas do registro CRITICAL do scanner. [CVE-2026-47890](https://spring.io/security/cve-2026-47890/), [CVE-2026-47884](https://spring.io/security/cve-2026-47884/).

Isso fundamenta o escopo da futura triagem, sem provar ausência das pré-condições nas aplicações. O probe e seu relatório não substituem auditoria dos manifests efetivos ou execução independente dos gates de cada cenário. Nenhum componente afetado foi chamado de corrigido por mera ausência presumida de uso.

## Limites da conclusão

M-01 e M-02 sobreviveram à verificação contrária: o primeiro controle só alcança volumes no topo e não é complementado antes de `up`; no segundo, cleanup verde não altera o zero já atribuído ao resultado. Não há outro bloqueante substanciado no delta inspecionado. Correções cabem em um bloco, com segunda rodada somente sobre o delta; os checks remotos e os gates futuros das aplicações continuam independentes deste parecer.
