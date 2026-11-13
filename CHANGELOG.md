# Changelog

## v0.1.2 — 2026-11-13

Separa o ciclo global da execução e a atividade do job protegido. A guarda reconhece os estados globais não terminais documentados e continua exigindo prova do job ativo do próprio cenário, run/tentativa/runner exatos e aprovação do dono. Estados terminais ou desconhecidos continuam bloqueados, sem retry ou fallback.

Falhas dos predicados de runtime passam a ter códigos discriminantes e valores normalizados, sem publicar o corpo da API. A observação externa de queued com C1 ativo motivou o contrato; não recupera a resposta histórica recebida pela guarda nem comprova causa de cache.

Patch exclusivo da infraestrutura confiável, sem alteração de aplicações ou critérios funcionais. Não aprova A1; o dono precisa de novo candidato após integração e gates. Não há migração, release ou deploy. Se a próxima variante falhar, o diagnóstico deve ser escalado, sem ampliar estados por tentativa.

## v0.1.1 — 2026-11-13

Corrige o bloqueio da fase 3 quando outros cenários da matriz aguardam aprovação. A guarda passa a conferir o job ativo do próprio cenário, run, tentativa e runner antes de aceitar o estado global waiting; a aprovação protegida continua obrigatória.

Patch exclusivo da infraestrutura confiável, sem aplicações ou execução A1. Mantém escopo, política e controles do dono. Sem migração de dados, release ou deploy; defeitos exigem novo patch revisado.

## v0.1.0 — 2026-11-13

Preparação da base confiável de pentest, com política, guardas, suíte e triagem comuns preservadas da fonte revisada. Inclui gate A0 próprio, verificação de integridade/escopo, fixtures inertes e auditoria das dependências npm/PyPI do runner.

Não contém aplicações e não aprova A1. Imagens e pacotes apt não estão cobertos pela auditoria de lockfiles. Os controles e a execução protegida continuam sob responsabilidade do dono. Não há migração de dados ou deploy; uma correção após admissão exige versão própria revisada, sem alterar os controles do dono.
