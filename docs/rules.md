# Contrato do benchmark

Segurança > desempenho > qualidade de código > tempo de desenvolvimento. Política de referência: [Puck fixado](https://github.com/mclovin137/Puck/blob/c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a/agents/rules.md).

Nível crítico: autorização e integridade financeira; infraestrutura do experimento também toca configuração de agentes e CI. Neo faz revisão independente antes de merge. Branches de tarefa → dev, até 30 arquivos por PR, CI rápida; promoção dev → main com fechamento de versão, CI completa e revisão/QA independentes. Bootstrap do repositório vazio contém somente este README. O usuário autorizou expressamente nesta sessão merges em dev, promoção main e tag final neste repositório, sempre após os gates obrigatórios passarem. Não há autorização para compras ou serviços pagos.

A especificação comum é imutável durante as execuções. Código de aplicação nunca é copiado entre cenários. Desvios e controles não executados precisam constar nos resultados. Dados e evidências públicas não podem conter credenciais, conversas ou caminhos pessoais.

## Base preparatória admitida

A versão v0.1.0 foi integrada em main pelo PR #31 no commit `98894e1e09585f9b12f07921eb4650fd3ce4f1a8`, com CI A0 `43416741349` aprovada e tag remota conferida. A exceção da linha `integration/pentest-bootstrap` valeu somente para essa versão sem aplicações; o fluxo normal tasks → dev → versões em main é preservado.

Esta integração incorpora a ancestralidade real da base confiável, preserva os 16 arquivos comuns byte a byte e retira da dev apenas workflow, verificador, manifesto e testes exclusivos de bootstrap. As fixtures das guardas comuns permanecem e passam a executar na CI rápida/completa. Não se amplia a allowlist nem se usa o gate A0 como substituto da CI funcional ou do A1. O parecer da preparação é histórico, não aprovação automática deste candidato.

O acionamento e a configuração protegida do pentest continuam reservados ao dono. A1/triagem e os gates do novo SHA continuam necessários antes da promoção das aplicações; resultados anteriores permanecem evidência histórica de seu escopo. Sem alteração de defaultbranch, proteções, variáveis ou environment por esta integração.

## Base confiável v0.1.1

O patch de autorização foi admitido na main pelo PR #36, sem aplicações, após revisão combinada Neo e gates A0. A guarda exige o job ativo do próprio cenário quando o estado global da matriz é waiting, mantendo run/tentativa/runner, aprovação protegida e os demais gates. A fonte revisada do runtime é `b5d680d8f158d4edd60495cda9333acca1919b71`; nenhuma exigência funcional mudou.

Esta integração preserva os quatro arquivos exclusivos de bootstrap retirados na admissão anterior: workflow, helper, manifesto e testes do bootstrap continuam ausentes na dev das aplicações. Os 16 imports comuns permanecem idênticos à main v0.1.1. A promoção das aplicações exige CI completa e novo A1/triagem no candidato pertinente; execução falha e aprovação anteriores não são reutilizadas. Environment, imagens e acionamento/aprovação continuam sob controle do dono.
