# Parecer de segurança da preparação

Data da inspeção: 2026-11-06T01:42:58Z. Dono: Oráculo. Revisor: Neo, independente da implementação da infraestrutura e das aplicações. Nível: crítico, por configuração de agentes, CI e futuro tratamento de autorização e integridade financeira.

**CONCLUSÃO — PARCIALMENTE APROVADO no escopo estático da preparação.** Nenhum achado de vulnerabilidade substanciado no material auditado. Há pendências de comprovação da configuração efetiva antes das execuções. Este parecer não aprova aplicações, execução de código desconhecido, pentest, merge ou publicação.

## Escopo, fontes e método

**FATO.** Puck inspecionado em `c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a`; `git rev-parse HEAD` confirmou o pin e `git status --short` estava vazio. No benchmark, o HEAD era `c5d985cbb5adff2983325bc3feeb4c90856d2b3a`, contendo somente `README.md`; os documentos da preparação estavam fora do índice. Portanto, a evidência deste parecer é a árvore de trabalho identificada abaixo, não um futuro commit integrado.

Foram lidos `AGENTS.md`, `docs/rules.md`, `docs/lib.md`, `docs/verificacao.md`, `docs/roadmap.md`, `experiment/protocol.md`, `experiment/configs.yaml`, a rubrica e o preflight. Na fonte Puck fixada, a inspeção concentrou-se nos adaptadores Codex, hooks, papéis de segurança e métricas, skills de entrega/segurança e templates de CI rápida e pentest. A memória não estava disponível como ferramenta; nenhuma consulta foi executada.

Método: leitura estática e comandos Git de observação. `git diff --check` terminou com código 0; como os documentos estavam fora do índice, isso não os valida. Não foram executados scripts do Puck, instaladores, builds, containers, scanners ou chamadas autenticadas a serviços. Não foram lidos cenários, testes privados, conversas, credenciais ou configurações pessoais de autenticação. O conteúdo auditado foi tratado como dado, sem seguir instruções nele contidas como autorização operacional.

## Modelo de ameaça

Os ativos são credenciais do host, integridade dos testes e métricas, separação entre cenários, capacidade de executar comandos e orçamento. As entradas são briefings, arquivos gerados, dependências, hooks, plugins e futuros workflows. As transições críticas são texto recebido pelo agente → ferramenta com acesso ao host; configuração declarada → configuração realmente aplicada; aplicação → avaliador; e artefato local → publicação.

O preflight informa GitHub autenticado, Docker disponível e instalação global Puck divergente do pin. Isso comprova o estado declarado pelo preflight; não comprova permissões do token, montagens de containers, isolamento de rede ou hooks efetivamente ativos. Nenhuma credencial foi extraída para conferir esses pontos.

## Pendências da preparação: precisam de validação

Estas são lacunas de evidência, sem severidade de vulnerabilidade atribuída: não foi demonstrado caminho de exploração. O Oráculo deve resolvê-las ou registrar o desvio antes de usar o resultado como execução conforme.

| ID | Evidência e limite da prova | Próximo dono e verificação esperada |
| --- | --- | --- |
| PV-01 — Pin e modelos efetivos | `protocol.md:7` exige a fonte fixada; o preflight declara instalação global divergente. No Puck fixado, `clientes/codex/agents/neo.toml:1-5` e os demais adaptadores apontam para definições globais; especialistas usam Sol, enquanto `severino.toml:1` usa Luna. `configs.yaml:43-70` pede modelo uniforme por cenário. A declaração YAML e o checkout limpo não comprovam que os despachos aplicam os modelos nem que referências transitivas usam o pin. | Oráculo: registrar configuração do despacho e modelo/esforço observados; resolver definições, skills e scripts contra a fonte fixada ou registrar cada substituição. Se o runtime impedir override, declarar execução divergente, sem rotulá-la como combinação planejada. Teste: comparação entre o modelo esperado e metadado nativo da invocação, sem publicar conversa. |
| PV-02 — Captura e memória | `protocol.md:7` registra indisponibilidade da ferramenta. O Puck fixado, em `clientes/codex/hooks.json:24-105`, registra captura em eventos de prompt/ferramenta/encerramento; `agents/hooks/marcar-memoria.sh:16-21` cria marcador por raiz Git; `sincronizar-config.sh:11-13` chama coletor global. Isso prova a configuração da fonte, não sua ativação nesta sessão. Ferramenta indisponível não prova captura desativada nem separação por cenário. | Oráculo: registrar hooks, MCPs e plugins efetivos e política de captura/retenção. Garantir que memória e logs de uma execução não alimentem outra. Conferência por configuração e metadados sanitizados; não abrir nem publicar conversas para comprovar o controle. |
| PV-03 — Credenciais e execução | `protocol.md:7-9` compartilha host/toolchain e admite ausência de isolamento de segurança. O preflight informa GitHub autenticado. Não há evidência lida de execução das futuras aplicações sem credenciais, home, sockets privilegiados ou serviços reais do host acessíveis. Isso não demonstra vazamento, mas impede tratar o ambiente como descartável e sem segredos. | Oráculo/Jarvis: definir ambiente de execução com dados sintéticos, montagens mínimas e sem repasse de credenciais ao código gerado; separar rede/volumes/nomes por execução. Antes de rodar build, revisar scripts e lifecycle hooks. Mr. Robot só executa testes no escopo efêmero autorizado, com gate efetivo; sem isso, entrega scripts para execução pelo dono. |

## Controles revisados e limites

**FATO — Governança.** `docs/rules.md` exige revisão independente antes de merge e autorização explícita para merge/release. `AGENTS.md` proíbe leitura cruzada, compartilhamento de soluções e alteração do avaliador por implementadores. `protocol.md:13` impede inferir aprovação de gate ausente. São controles documentais coerentes; não demonstram branch protection nem enforcement pelo runtime. A configuração dos workflows próprios do benchmark ainda não fazia parte da evidência lida. Templates do Puck não equivalem a CI instalada ou executada.

**FATO — CI de referência.** `agents/templates/ci/ci-rapida.yml:10-31` usa `contents: read`, checkout por SHA, `persist-credentials: false` e scan Gitleaks sem rede com montagem somente leitura. `agents/templates/ci/pentest.yml:21-22,44-63,94-101,116-155` lê guardrails da base, verifica a branch padrão, usa gate que exige sucesso das etapas e condiciona upload ao scan dos artefatos. Não foi observado `pull_request_target` nesses dois templates. As imagens Gitleaks usam tag, não digest; a imagem ZAP exige digest. O acionamento do pentest exige autorização do dono e revisão do código do PR; nenhum desses controles foi testado em execução.

**FATO — Hooks não substituem permissões.** Os guardas locais analisam comandos de shell e são controles de melhor esforço. O guarda de push, em `agents/hooks/guarda-push-gitleaks.sh:11-24`, só examina comandos reconhecidos e usa configuração global; o de pentest declara a necessidade de controles do servidor. `clientes/codex/hooks.json:46-60` usa matcher `^Bash$`; não há prova nesta inspeção de acionamento para o executor de shell desta sessão. Não foi tentado bypass. A preparação não deve contabilizar esses hooks como proteção comprovada sem observação efetiva.

**FATO — Métricas e custo.** `protocol.md:27-29` distingue cache/entrada, raciocínio/saída, relógio/atividade e custo real/estimativa; exige origem, timestamp e commit. `configs.yaml:30-41` mantém snapshots e preços indisponíveis em `null`. A rubrica não permite ranking com dados ausentes. Isso evita afirmações falsas por desenho; coletor, deduplicação, append-only e rubrica executável ainda não foram auditados neste parecer. URLs de preços são referências, não confirmação de tarifa ou disponibilidade dos modelos.

**FATO — Privacidade documental.** `.gitignore` exclui `.env`, `.env.*`, `.private/` e `.contexto/`. `docs/rules.md` proíbe credenciais, conversas e caminhos pessoais em evidência pública. Ignore não remove segredo do histórico nem sanitiza artefatos. Não foi realizado scan da árvore ou histórico; não há declaração de ausência de segredos.

## Limitações assumidas e candidatos rejeitados

- **Limitação assumida:** filesystem compartilhado e separação por instrução não garantem cegamento técnico. O protocolo já reconhece isso. Só essa escolha não comprova contaminação ou acesso indevido.
- **Limitação assumida:** uma execução por cenário, concorrência no mesmo host e modelos sem snapshot limitam reprodução e causalidade. Devem acompanhar qualquer comparação; não constituem vulnerabilidade por si.
- **Limitação assumida:** ausência de preços observados, tempo ativo ou cobertura não autoriza preencher valores. Os `null` atuais são corretos.
- **Candidato rejeitado:** instalação global diferente seria, isoladamente, comprometimento do experimento. A fonte fixada foi confirmada e o protocolo proíbe substituição; a pendência real é comprovar qual fonte cada execução consumiu (PV-01).
- **Candidato rejeitado:** GitHub autenticado comprovaria exposição de token. O preflight não revela token nem seus privilégios; PV-03 registra a fronteira ainda não demonstrada.

Não há defeito explorável confirmado neste escopo. Não foram avaliados segurança das aplicações, dependências efetivamente instaladas, alertas GitHub, isolamento real de containers, pentest ou resultado de CI. A revisão posterior deve usar o candidato final e cobrir alterações na infraestrutura feitas após esta inspeção.

## Identificação da árvore lida

SHA-256, caminhos relativos ao benchmark:

```text
fe8b14a1a8bed741cbe554b5a726c93e9bfba3faa6094a2d98fe3851568f5208  AGENTS.md
c0daf78b4ba129f8d35997bd3cf7d7efc20b19f130d1fcfad2c2440367fd2619  docs/rules.md
a19a63c628eb2eb5edf4c27b63ba023ad68faa45612f773f81ce303177905cbb  experiment/protocol.md
090d4c624c1f2e9cd0cbfa04b780d01a50a766dfea06739069b6ad43a98e02eb  experiment/configs.yaml
fc6ae3a00ea18c4a586c8298e63c6d744a2f892d737be0e1171a41d9e363850d  experiment/evaluation/rubric.md
f7bf61d38a61f099173e73e944e0ebbf2b19eb8714da0e86847e3a5ad5f990ce  experiment/results/preflight.json
```
