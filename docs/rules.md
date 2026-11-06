# Contrato do benchmark

Segurança > desempenho > qualidade de código > tempo de desenvolvimento. Política de referência: [Puck fixado](https://github.com/mclovin137/Puck/blob/c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a/agents/rules.md).

Nível crítico: autorização e integridade financeira; infraestrutura do experimento também toca configuração de agentes e CI. Neo faz revisão independente antes de merge. Branches de tarefa → dev, até 30 arquivos por PR, CI rápida; promoção dev → main com fechamento de versão, CI completa e revisão/QA independentes. Bootstrap do repositório vazio contém somente este README. O usuário autorizou expressamente nesta sessão merges em dev, promoção main e tag final neste repositório, sempre após os gates obrigatórios passarem. Não há autorização para compras ou serviços pagos.

A especificação comum é imutável durante as execuções. Código de aplicação nunca é copiado entre cenários. Desvios e controles não executados precisam constar nos resultados. Dados e evidências públicas não podem conter credenciais, conversas ou caminhos pessoais.
