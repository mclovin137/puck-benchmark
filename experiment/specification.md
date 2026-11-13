# Puck Benchmark — Experimento de Desenvolvimento Autônomo com IA

## 1. Papel e objetivo

Atue como engenheiro de software sênior, arquiteto de soluções e responsável técnico por um experimento controlado de desenvolvimento autônomo com agentes de IA.

Sua missão é **validar experimentalmente o template Puck**, disponível em:

https://github.com/mclovin137/Puck

Para isso, desenvolva quatro implementações independentes de uma mesma aplicação full-stack, utilizando diferentes configurações de modelos, níveis de raciocínio e estratégias de orquestração de agentes.

**Objetivo principal:** determinar qual configuração oferece o melhor equilíbrio entre custo computacional, tempo de desenvolvimento, qualidade, segurança, retrabalho e aderência aos processos definidos no Puck.

O projeto é um experimento comparativo, não apenas uma entrega de software funcional.

A avaliação deverá utilizar dados coletados durante a execução, testes reproduzíveis e evidências auditáveis, evitando conclusões baseadas exclusivamente na percepção dos agentes.

## 2. Fonte de verdade e governança

O repositório Puck é a referência obrigatória para processos, agentes, skills, padrões arquiteturais, segurança, documentação e CI/CD.

Antes de implementar:

1. Inspecione o README, AGENTS.md, regras, playbooks, agentes, skills, hooks, scripts e workflows relevantes do Puck.
2. Identifique os fluxos e controles aplicáveis ao experimento.
3. Registre o commit SHA do Puck utilizado, garantindo que todas as implementações utilizem a mesma versão.
4. Execute ou verifique a instalação e configuração dos componentes necessários.
5. Confirme quais métricas são efetivamente coletadas pelo Puck e quais precisam de instrumentação adicional.

Respeite a ordem de prioridades já estabelecida no Puck:

**Segurança > Desempenho > Qualidade de código > Tempo de desenvolvimento.**

Em caso de conflito, a prioridade superior prevalece.

Não substitua processos existentes por procedimentos improvisados, não duplique documentação canônica e não altere o Puck original para favorecer nenhum cenário.

Os arquivos `docs/rules.md`, `docs/lib.md`, `docs/verificacao.md`, `docs/roadmap.md` e demais artefatos devem seguir as convenções do template.

## 3. Aplicação de referência

Desenvolva um sistema web de controle financeiro pessoal, com gerenciamento de entradas e saídas.

### Stack obrigatória

- Frontend: React com TypeScript.
- Backend: Java com Spring Boot.
- API: REST.
- Banco de dados: PostgreSQL.
- Persistência: Spring Data JPA.
- Migrações: Flyway.
- Testes: frameworks compatíveis com a stack.
- Execução local: Docker Compose, quando aplicável.

Fixe as mesmas versões principais de linguagem, framework e dependências para os quatro cenários.

Não substitua a stack por preferência de um agente.

### Funcionalidades obrigatórias

**Autenticação e usuários**
- Cadastro com nome, e-mail e senha.
- Login e logout.
- Autenticação e autorização no backend.
- Senhas armazenadas com algoritmo de hash adequado.
- Validação dos dados de cadastro.
- Proteção de rotas e recursos privados.
- Cada usuário acessa exclusivamente seus próprios registros.

**Movimentações financeiras**
- Cadastro de entradas e saídas.
- Listagem paginada das movimentações.
- Visualização e edição de registros.
- Exclusão com confirmação.
- Filtros combináveis por tipo, categoria, descrição, período e faixa de valor.
- Ordenação por data e valor.
- Resumo do total de entradas, saídas e saldo do período filtrado.
- Categorias associadas às movimentações.

Cada movimentação deve conter identificador, usuário proprietário, tipo, descrição, categoria, valor monetário, data e timestamps de criação e atualização.

**Exportações**
- Exportação em PDF.
- Exportação em Excel (.xlsx).
- Aplicação dos mesmos filtros utilizados na listagem.
- Arquivos gerados com dados corretos, formatação legível e totais consistentes.
- Exportações limitadas aos registros autorizados ao usuário.

**Interface**
- Tela de login.
- Tela de cadastro de usuário.
- Dashboard financeiro.
- Tela de listagem, filtros e ações sobre movimentações.
- Formulário de criação e edição.
- Interface responsiva.
- Feedback de carregamento, sucesso, erro e ausência de dados.

Siga o padrão visual, os requisitos de acessibilidade e as skills de design definidos no Puck.

### Regras de negócio

- Valores monetários devem utilizar precisão decimal, nunca ponto flutuante binário.
- Uma entrada aumenta o saldo; uma saída diminui.
- O saldo é calculado a partir das movimentações autorizadas, sem fontes redundantes de verdade.
- O valor de uma movimentação deve ser maior que zero.
- Datas, categorias e campos obrigatórios devem ser validados.
- Registros inexistentes ou pertencentes a outros usuários não podem ser manipulados.
- Os resultados dos filtros devem ser consistentes entre listagem, resumo e exportação.

O escopo funcional é fechado. Não adicionar funcionalidades extras sem necessidade comprovada para cumprir os requisitos.

## 4. Desenho experimental

Executar exatamente quatro cenários independentes.

A variável experimental é a configuração da IA; o produto desenvolvido e os critérios de avaliação permanecem constantes.

| Cenário | Orquestração | Modelos | Raciocínio |
|---|---|---|---|
| C1 | Agentes especializados | Econômicos | Baixo/médio, conforme função |
| C2 | Agentes especializados | Avançados | Médio/alto, conforme função |
| C3 | Agente gerenciador | Econômicos | Baixo/médio, conforme função |
| C4 | Agente gerenciador | Avançados | Médio/alto, conforme função |

### Agentes especializados — C1 e C2

Utilizar a distribuição de responsabilidades estabelecida no Puck.

Cada agente deve atuar dentro de sua especialidade, incluindo planejamento, arquitetura, implementação, testes, segurança e revisão, quando seu papel for requerido pelo fluxo.

### Agente gerenciador — C3 e C4

Um agente principal coordena e assume a maior parte do planejamento, implementação e tomada de decisão.

A delegação é restrita aos controles obrigatórios do Puck, como verificações de segurança e revisão que não possam ser realizadas pelo próprio autor.

O agente gerenciador não pode desativar, simular ou substituir informalmente os gates independentes de validação.

### Configuração dos modelos

Antes do desenvolvimento, produzir `experiment/configs.yaml`, contendo, para cada cenário:

- Modelo e provedor efetivamente utilizados.
- Identificador exato e versão do modelo, quando disponível.
- Modelo principal e modelos dos agentes delegados.
- Nível de raciocínio de cada função.
- Preço por milhão de tokens de entrada, saída e cache, quando aplicável.
- Origem e data dos preços.
- Estratégia de delegação e restrições operacionais.

Modelos econômicos devem priorizar menor custo por tarefa. Modelos avançados devem priorizar capacidade e qualidade.

O nível de raciocínio deve ser explícito e permanecer fixo durante cada execução.

Não tratar configurações com diferentes capacidades de raciocínio como equivalentes. Registrar quando um provedor não oferecer controles diretamente comparáveis.

Caso algum modelo esteja indisponível, registrar a substituição antes da execução. Não modificar retrospectivamente configurações para melhorar resultados.

## 5. Controle de comparabilidade

Para garantir um experimento justo:

1. Os quatro cenários recebem a mesma especificação funcional e critérios de aceite.
2. Utilizam o mesmo commit do Puck, stack, ambiente de execução e requisitos de qualidade.
3. Iniciam de uma base equivalente, sem reutilizar implementações anteriores.
4. Não compartilham código de aplicação, correções ou soluções produzidas durante o experimento.
5. Podem compartilhar somente infraestrutura de benchmark, especificação, ferramentas e testes externos.
6. Não podem acessar resultados ou relatórios de cenários anteriores antes de sua conclusão.
7. Devem utilizar os mesmos limites de tentativas, revisão e critérios de encerramento.
8. Devem ter as mesmas permissões e recursos de execução, exceto pelas configurações de IA deliberadamente distintas.

A ordem de execução, o horário, o ambiente e eventuais diferenças de infraestrutura devem ser registrados.

Os dados de teste e o avaliador final devem permanecer independentes dos agentes responsáveis pela implementação.

**Nota metodológica:** uma única execução por cenário representa um estudo exploratório. Se houver orçamento e infraestrutura, realizar três execuções independentes por cenário, com mediana e dispersão dos resultados. Não apresentar uma única execução como prova estatística de superioridade.

## 6. Repositório de entrega

Criar um único repositório GitHub, denominado:

`puck-benchmark`

Estrutura esperada:

```text
puck-benchmark/
├── README.md
├── experiment/
│   ├── specification.md
│   ├── configs.yaml
│   ├── protocol.md
│   ├── evaluation/
│   └── results/
├── scenarios/
│   ├── c1-specialists-economy/
│   ├── c2-specialists-advanced/
│   ├── c3-manager-economy/
│   └── c4-manager-advanced/
├── benchmark/
│   ├── tests/
│   └── scripts/
└── reports/
    ├── comparison.md
    ├── metrics.csv
    └── metrics.json
```

Cada cenário deve possuir seu próprio frontend, backend, configurações, testes, README e evidências.

Aplicar os arquivos de governança do Puck em cada projeto, respeitando a organização esperada pelo template.

Não criar cópias desnecessárias da especificação central.

Os READMEs individuais devem referenciar a especificação comum e documentar exclusivamente características e resultados do cenário.

O README da raiz será o ponto central da comparação.

## 7. Processo de desenvolvimento obrigatório

Executar o ciclo completo definido no Puck.

**Planejamento**
- Classificar a tarefa e selecionar os agentes e skills apropriados.
- Definir arquitetura e roadmap.
- Aplicar o planejamento em versões com até 10 tasks por versão.
- Definir estratégia de testes e riscos.
- Registrar decisões arquiteturais relevantes.

**Implementação**
- Trabalhar em branches de feature ou correção.
- Abrir PRs de task para `dev`.
- Respeitar o limite de 30 arquivos por PR.
- Executar CI rápida antes da integração.
- Implementar testes relacionados às regras de negócio.
- Atualizar roadmap e contexto das tarefas.

**Validação**
- Executar o fechamento de versão conforme o Puck.
- Abrir PR de promoção de `dev` para `main`.
- Executar CI completa, revisão arquitetural, segurança e QA previstos.
- Respeitar os limites de rodadas de revisão.
- Aplicar os critérios de bloqueio do template.

**Finalização**
- Corrigir falhas identificadas.
- Verificar o funcionamento integrado.
- Registrar a versão final.
- Gerar evidências e relatórios.

Todo desvio deve ser identificado, justificado e registrado. O cenário não pode receber pontuação integral de conformidade quando um controle obrigatório não foi executado.

Não considerar um PR aprovado apenas porque foi aberto ou porque o próprio agente declarou sucesso.

## 8. Instrumentação e métricas

A coleta deverá ocorrer automaticamente durante todas as fases.

Priorize os coletores e hooks existentes no Puck. Crie instrumentação complementar somente quando necessário.

Toda medição deve conter cenário, execução, tarefa, etapa, timestamp, modelo, agente e identificador de correlação, quando disponíveis.

### 8.1. Custo e tokens

Coletar:

- Tokens de entrada, saída e cache, separadamente.
- Tokens totais por cenário.
- Consumo por modelo, agente, skill e etapa.
- Custo estimado ou faturado por modelo e cenário.
- Consumo em planejamento, implementação, testes, revisão e correções.
- Custo por funcionalidade aceita.
- Proporção de tokens de revisão e planejamento.

Não atribuir consumo a uma skill sem rastreamento confiável de sua execução.

Quando os tokens de uma skill estiverem incluídos em uma chamada de agente, manter uma única contabilização financeira e registrar a atribuição da skill como dimensão analítica, evitando dupla contagem.

Quando o provedor não expuser dados completos, registrar `não disponível`, a cobertura da medição e eventuais estimativas separadamente.

### 8.2. Produtividade e retrabalho

Medir:

- Tempo total de desenvolvimento e tempo ativo.
- Duração por fase e por tarefa.
- Quantidade de PRs, commits e execuções de CI.
- Número de tentativas até a conclusão de cada tarefa.
- Falhas e correções pós-revisão.
- Arquivos alterados após reprovação.
- Bugs reabertos e regressões.
- Tempo e custo consumidos em retrabalho.

Definir retrabalho como alterações corretivas necessárias para satisfazer requisitos já implementados ou corrigir defeitos detectados. Separá-lo de evolução planejada e refatoração preventiva.

Não utilizar linhas de código ou quantidade de commits isoladamente como indicadores de produtividade.

### 8.3. Qualidade e arquitetura

Avaliar:

- Percentual de requisitos funcionais aprovados.
- Cobertura de testes por componente.
- Quantidade de testes aprovados e reprovados.
- Defeitos por severidade.
- Duplicação de código.
- Complexidade e manutenibilidade.
- Coesão, acoplamento e separação de responsabilidades.
- Aderência à arquitetura e aos padrões exigidos pelo Puck.
- Consistência das APIs, persistência e tratamento de erros.

Utilizar ferramentas estáticas e testes automatizados quando possível.

Métricas qualitativas devem ser avaliadas por rubrica fixa, com justificativa e evidência.

### 8.4. Segurança

Verificar, no mínimo:

- Autenticação e autorização.
- Isolamento dos dados de cada usuário.
- Controle de acesso a endpoints e exportações.
- Proteção de senhas e segredos.
- Validação de entradas.
- Dependências vulneráveis.
- Exposição indevida de informações.
- Controles relevantes do OWASP ASVS.

Executar os scanners, verificações e pentests previstos pelo Puck, respeitando os respectivos mecanismos de autorização.

Registrar vulnerabilidades por severidade, status e evidências, sem expor segredos.

Uma falha crítica não corrigida impede a classificação do cenário como entrega aprovada.

### 8.5. Conformidade com o Puck

Medir:

- Etapas obrigatórias executadas.
- Uso correto dos agentes.
- Acionamento de skills previstas.
- Execução dos hooks aplicáveis.
- Cumprimento dos limites de PR.
- Execução dos gates de CI/CD.
- Revisões e handoffs realizados.
- Documentação e memória atualizadas quando exigidas.

Para cada controle, registrar `aprovado`, `reprovado`, `não aplicável` ou `não observado`, com evidência.

A conformidade deve ser calculada sobre controles aplicáveis, distinguindo ausência de execução de ausência de observabilidade.

## 9. Critérios de aceite

Uma implementação será considerada funcionalmente aprovada somente quando:

1. Backend, frontend e banco iniciam de forma reproduzível.
2. Cadastro, login e logout funcionam.
3. O CRUD de movimentações está operacional.
4. Filtros, paginação, ordenação e resumo retornam resultados corretos.
5. Exportações PDF e XLSX correspondem aos filtros e totais.
6. Isolamento entre usuários é validado por testes.
7. Testes automatizados e CI exigida passam.
8. Não há vulnerabilidades críticas conhecidas sem tratamento.
9. Interface funciona em resoluções desktop e mobile.
10. Evidências, métricas e documentação estão disponíveis.

O avaliador deve executar os mesmos testes de aceitação contra as quatro implementações.

Defeitos, testes indisponíveis e funcionalidades parcialmente implementadas devem ser registrados, não omitidos.

## 10. Evidências e documentação

Para cada cenário, entregar:

- `README.md` com configuração, execução e resultados.
- Registro dos modelos, agentes e níveis de raciocínio utilizados.
- Relatório de métricas com origem dos dados.
- Evidências de build, CI, testes e segurança.
- Principais decisões arquiteturais e desvios.
- Vídeo demonstrando o sistema funcionando.
- Instruções para reproduzir o comportamento localmente.

O vídeo deve demonstrar login, cadastro de movimentações, edição, exclusão, filtros, dashboard e exportações.

Registrar a origem, a data e o commit dos artefatos utilizados. Não apresentar capturas ou demonstrações simuladas como execuções reais.

Se não for possível produzir um vídeo, registrar a limitação explicitamente e fornecer evidências verificáveis alternativas. Não declarar a entrega do vídeo como concluída.

O README da raiz deve apresentar uma tabela comparativa com os quatro cenários e links para os relatórios detalhados.

## 11. Análise final

Produzir `reports/comparison.md` contendo:

1. Configuração efetivamente executada em cada cenário.
2. Comparação quantitativa de tokens, custo e duração.
3. Consumo por agente, skill e etapa.
4. Taxa de aprovação funcional.
5. Qualidade, segurança e conformidade.
6. Retrabalho e eficiência de revisão.
7. Desvios e limitações experimentais.
8. Relação custo-benefício dos quatro cenários.
9. Recomendações de otimização para o Puck.

Não criar uma pontuação geral arbitrária.

Apresentar primeiro as métricas individuais e, quando útil, uma análise multicritério com pesos explícitos, critérios eliminatórios e sensibilidade a diferentes ponderações.

Diferenciar dados observados, estimativas e interpretações.

Não concluir que uma configuração é superior quando houver ausência de dados, diferenças relevantes de execução ou amostra insuficiente.

## 12. Autonomia e tomada de decisão

Este projeto deve ser executado de maneira autônoma, sem checkpoints de aprovação humana para decisões técnicas rotineiras.

O responsável pelo experimento deve:

- Resolver ambiguidades técnicas por meio das regras do Puck, da especificação e de critérios previamente documentados.
- Priorizar soluções simples, seguras e reproduzíveis.
- Corrigir falhas identificadas antes de encerrar cada cenário.
- Manter registros de decisões e impedimentos.
- Continuar as etapas que possam ser executadas independentemente de um bloqueio.
- Evitar perguntas sobre escolhas já determinadas neste documento.

**Limites de autonomia:** não presumir permissões ausentes, não gastar recursos pagos sem autorização existente, não acessar segredos indevidamente e não contornar políticas de segurança ou controles externos.

Se uma etapa depender de credenciais, autorização ou recurso indisponível, registrar o bloqueio, seu impacto e as alternativas executadas. Não simular sua conclusão.

Antes do início, realizar uma única verificação de pré-requisitos e dependências externas. Solicitar intervenção apenas diante de bloqueios realmente incontornáveis.

## 13. Restrições

É proibido:

- Alterar os requisitos entre os cenários.
- Compartilhar código de implementação entre cenários.
- Ignorar controles do Puck para economizar tokens.
- Trocar modelos durante a execução sem registrar a alteração.
- Omitir custos, falhas, bugs ou tarefas incompletas.
- Inventar métricas, vídeos, testes ou evidências.
- Duplicar contagens de tokens ou custos.
- Criar documentação redundante.
- Executar avaliações distintas entre cenários.
- Declarar testes como aprovados sem executá-los.
- Usar a avaliação do próprio autor como única prova de qualidade.
- Modificar retrospectivamente os critérios de sucesso.
- Expandir o escopo funcional sem justificativa obrigatória.

Evite abstrações desnecessárias, overengineering e componentes não exigidos pela aplicação ou pela governança.

## 14. Resultado esperado

O experimento termina quando as quatro implementações atingirem um estado final verificável — aprovadas, parcialmente aprovadas ou bloqueadas — e seus dados forem consolidados.

A entrega final deve permitir responder:

- Qual cenário consumiu menos tokens?
- Qual apresentou o menor custo total?
- Qual entregou mais funcionalidades corretas por unidade de custo?
- Qual produziu código de melhor qualidade?
- Qual apresentou menor retrabalho?
- Quanto planejamento e revisão consumiram?
- Quais agentes e skills tiveram maior impacto no consumo?
- A especialização dos agentes compensou seu custo?
- Modelos avançados justificaram o investimento?
- Quais controles do Puck foram eficazes e quais geraram overhead?
- Que mudanças mensuráveis podem melhorar o template?

A conclusão deve apoiar-se em evidências reproduzíveis, apontando limitações e trade-offs, e resultar em recomendações concretas de evolução do Puck.

**Inicie pela auditoria do Puck, congelamento da especificação, configuração dos quatro cenários e validação da instrumentação. Depois execute o desenvolvimento completo e a avaliação, seguindo a governança estabelecida, sem solicitar confirmações intermediárias desnecessárias.**