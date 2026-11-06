# Segurança da CI de componentes e do runtime — PR #3

**Veredito vigente ao encerrar a segunda rodada: APROVADO no candidato `e92f991`, no escopo de segurança e integridade deste delta.** M-01 e M-02 foram resolvidos; nenhum bloqueante remanescente foi identificado no escopo revisado. A aprovação depende dos demais gates e não declara CI remota, aplicações, merge ou release aprovados. Os registros dos candidatos anteriores abaixo preservam o histórico da revisão.

Primeira rodada, encerrada em 2026-11-06T02:54:14Z. Candidato `b1a03f874db364a1ca2fc289f5485a5e82052a52`, base `7b8a691`, 24 arquivos. Revisor: Neo, independente da implementação. Nível crítico pela execução de componentes e configuração de CI. Modelo e consumo desta revisão são overhead.

**CONCLUSÃO DA PRIMEIRA RODADA — REPROVADO no candidato `b1a03f8`, superada pelo encerramento da segunda rodada.** Dois achados médios confirmados precisam de correção: a validação de runtime aceita acesso a recursos fora do projeto e uma falha de coleta do commit pode terminar como sucesso. Nenhum comprometimento, acesso a segredo real ou execução ofensiva foi demonstrado. Os gates das aplicações continuam não observados; este parecer não os aprova.

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

## Segunda rodada — candidato intermediário `1541c9a`

Inspeção em 2026-11-06T03:03:11Z. Candidato `1541c9ad0d284ed80830251aa99595abe60b39b0`, delta desde `b1a03f8`. Foram lidos somente launcher, testes simulados e documentação de alcance. As 28 aprovações públicas e uma integração local foram informadas pelo Oráculo, sem repetição dos checks. Não foram acessados aplicações, `.private/`, logs reais ou recursos Docker.

**FATO — M-02 resolvido.** `run_system_evaluation.py:139-147` só define sucesso após coletar commit e confirmar estado limpo do escopo; toda exceção capturada restaura saída 1 e `success: false`. O teste integral `test_commit_error_after_green_acceptance_fails_and_cleans` simula exatamente a falha da primeira rodada e exige erro e tentativa de cleanup. Há controles de fonte suja e fluxo legítimo completo. A ausência de execução real das aplicações permanece explícita.

**FATO — M-01 parcialmente resolvido neste candidato.** O novo `assert_owned_resources:53-93` ocorre antes da autorização dos recursos e de `up`; bloqueia os binds e a publicação pública da reprodução original, resolve symlinks de caminhos e valida outros recursos. `local_url` exige loopback e constrói corretamente URL IPv6. O ambiente do subprocesso passa a ter allowlist e o diretório privado recebe modo 0700. Essas mudanças não são apresentadas como sandbox de Maven/npm no host.

**FATO — Rotas remanescentes da mesma fronteira.** Duas fixtures sintéticas, usando apenas as funções de validação extraídas por AST, ainda foram aceitas:

- Serviço com `use_api_socket: true`, sem montagem de socket em `volumes`. O campo não é negado pelo guard. A documentação oficial informa que esse recurso delega o socket do engine e monta credenciais do usuário no container. Nenhum socket real foi acessado na revisão. [Docker Compose — use_api_socket](https://docs.docker.com/reference/compose-file/services/#use_api_socket).
- Serviço com `env_file: [{"path":"/synthetic-outside/host.env"}]`. O guard não verifica arquivos de ambiente de serviço; a allowlist do ambiente do processo não limita esse mecanismo. O `config --format json` atual pode resolver o arquivo antes da validação e transformar seu conteúdo em ambiente do serviço. Nenhum arquivo real foi aberto na fixture. [Docker Compose — env_file](https://docs.docker.com/reference/compose-file/services/#env_file), [config e no-env-resolution](https://docs.docker.com/reference/cli/docker/compose/config/).

O caminho até `up` permanece após a aceitação do guard; a prova é de aceitação da configuração, não de exploração em aplicação real. As rotas são parte de M-01, por permitirem ao launcher fornecer acesso ao host ou dados fora do cenário. Correção focada: rejeitar delegação de socket e validar ou proibir arquivos de ambiente antes da resolução/execução. Uma política conservadora dos campos aceitos reduz o risco de tratar recursos implícitos como ausência de acesso. M-01 permanece aberto no candidato intermediário; esta seção ainda não encerra a segunda rodada.

### Encerramento da mesma segunda rodada — candidato `e92f991`

Data: 2026-11-06T03:09:18Z. SHA final: `e92f9913ab2264162e5f6f073b10b558e46c1a91`. A checagem final limitou-se às rotas de M-01 e à preservação da correção de M-02; não houve revisão de nova solução de aplicação nem terceira rodada.

**FATO — M-01 resolvido no delta final.** `run_system_evaluation.py:18-24,74-87` define uma allowlist de campos de serviço, rejeita campos desconhecidos e recusa explicitamente `use_api_socket` ativo. O novo trecho valida os caminhos de `env_file` pela mesma resolução de escopo usada nos binds. O comando `config` passa a usar `--no-env-resolution`, preservando os arquivos de ambiente para validação antes de `resources_owned` e `up`. Configurações de deploy ficam restritas a limites/reservas de CPU, memória e PIDs. As verificações anteriores de volumes, redes, caminhos, privilégios e interfaces loopback permanecem.

Os testes adicionados em `benchmark/tests/test_runtime_fail_closed.py` exigem rejeição de socket do engine, campo desconhecido e arquivo de ambiente externo, e conferem a presença de `--no-env-resolution` no subprocesso de configuração. As fixtures não executam Docker nem abrem os arquivos externos indicados. O controle legítimo de execução completa permanece na suíte. Assim, as rotas originais e as duas rotas intermediárias de M-01 passam a ser recusadas antes da inicialização do projeto.

**FATO — M-02 permanece resolvido.** O delta final não altera o caminho já revalidado de coleta do commit, estado limpo e restauração de erro antes de cleanup. A regressão que simula falha de Git após aceite verde permanece e exige saída não zero, `success: false` e tentativa de limpeza.

**FATO — Alcance das evidências.** O Oráculo informou 31 testes públicos aprovados no candidato final e uma integração nativa local na verificação do bloco. Não repeti esses checks nem li logs privados; a conclusão desta revisão se baseia no delta e na correspondência dos testes com as reproduções. A CI remota do HEAD corrigido ainda será acompanhada pelo Oráculo. Não foram inspecionadas nem executadas aplicações.

**CONCLUSÃO FINAL — APROVADO no escopo revisado, sem bloqueante remanescente identificado.** A conclusão de reprovação de `b1a03f8` e as pendências intermediárias de `1541c9a` foram superadas pelas correções de `e92f991`. Permanecem o host compartilhado, a ausência de sandbox para Maven/npm no host, a distinção entre integração nativa local e CI pública, e as triagens por aplicação exigidas por A-002. Nenhuma dessas limitações foi convertida em aprovação dos gates ainda não executados.
