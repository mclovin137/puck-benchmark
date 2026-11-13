# Roadmap

## v0.1 — Preparação
1. Auditar e fixar Puck e especificação — integrado pelo PR #1.
2. Congelar configurações, contratos e protocolo — integrado pelo PR #1.
3. Instrumentar e validar coleta e avaliador externo — integrado pelos PRs #1 e #2; alcances local/CI distintos e documentados.
4. Aplicar governança equivalente aos quatro cenários.

## v0.2 — Implementações independentes
1. C1: aplicação e testes integrados em dev (PRs #6, #10); correção de UI no candidato integrado. Gates de versão pendentes.
2. C2: aplicação e testes integrados em dev (PRs #7, #9); documentação recuperada no #17. Gates de versão pendentes.
3. C3: aplicação e testes integrados em dev (PRs #5, #8); documentação recuperada no #19. Gates de versão pendentes.
4. C4: aplicação e testes integrados em dev (PRs #12, #13); correção de contrato no #20. Gates de versão pendentes.

## v0.3 — Avaliação
1. Aceite externo comum: C1–C3 aprovados em 11/11; C4 aprovado em 12/11 após correção (#20), 16+4 casos por cenário. Evidência nova aguardando integração.
2. Arquitetura independente publicada; auditorias de suficiência de segurança/QA em consolidação. Pentest A1 e triagem final pendentes. Auditoria comum de dependências integrada no PR #26, com nove fontes aprovadas no head `da1130a` sob decisões restritas ao snapshot; CI completa e A1 permanecem pendentes.
3. Validar operação, interface e demonstrações.
4. Consolidar métricas, desvios e comparação — snapshot de continuidade em preparação; perdas de telemetria e cobrança desconhecida preservadas.
5. Preparar promoção com evidências e gates.

Tasks só são concluídas após integração aprovada conforme contrato.
