# Contrato do benchmark

Segurança > desempenho > qualidade de código > tempo de desenvolvimento. Política de referência: [Puck fixado](https://github.com/mclovin137/Puck/blob/c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a/agents/rules.md).

Nível crítico: autorização e integridade financeira; infraestrutura do experimento também toca configuração de agentes e CI. Neo faz revisão independente antes de merge. Branches de tarefa → dev, até 30 arquivos por PR, CI rápida; promoção dev → main com fechamento de versão, CI completa e revisão/QA independentes. Bootstrap do repositório vazio contém somente este README. O usuário autorizou expressamente nesta sessão merges em dev, promoção main e tag final neste repositório, sempre após os gates obrigatórios passarem. Não há autorização para compras ou serviços pagos.

A especificação comum é imutável durante as execuções. Código de aplicação nunca é copiado entre cenários. Desvios e controles não executados precisam constar nos resultados. Dados e evidências públicas não podem conter credenciais, conversas ou caminhos pessoais.

## Base preparatória admitida

A versão v0.1.0 foi integrada em main pelo PR #31 no commit `98894e1e09585f9b12f07921eb4650fd3ce4f1a8`, com CI A0 `43416741349` aprovada e tag remota conferida. A exceção da linha `integration/pentest-bootstrap` valeu somente para essa versão sem aplicações; o fluxo normal tasks → dev → versões em main é preservado.

Esta integração incorpora a ancestralidade real da base confiável, preserva os 16 arquivos comuns byte a byte e retira da dev apenas workflow, verificador, manifesto e testes exclusivos de bootstrap. As fixtures das guardas comuns permanecem e passam a executar na CI rápida/completa. Não se amplia a allowlist nem se usa o gate A0 como substituto da CI funcional ou do A1. O parecer da preparação é histórico, não aprovação automática deste candidato.

O acionamento e a configuração protegida do pentest continuam reservados ao dono. A1/triagem e os gates do novo SHA continuam necessários antes da promoção das aplicações; resultados anteriores permanecem evidência histórica de seu escopo. Sem alteração de defaultbranch, proteções, variáveis ou environment por esta integração.
