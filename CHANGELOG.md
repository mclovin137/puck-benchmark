# Changelog

## v0.1.1 — 2026-11-13

Corrige o bloqueio da fase 3 quando outros cenários da matriz aguardam aprovação. A guarda passa a conferir o job ativo do próprio cenário, run, tentativa e runner antes de aceitar o estado global waiting; a aprovação protegida continua obrigatória.

Patch exclusivo da infraestrutura confiável, sem aplicações ou execução A1. Mantém escopo, política e controles do dono. Sem migração de dados, release ou deploy; defeitos exigem novo patch revisado.

## v0.1.0 — 2026-11-13

Preparação da base confiável de pentest, com política, guardas, suíte e triagem comuns preservadas da fonte revisada. Inclui gate A0 próprio, verificação de integridade/escopo, fixtures inertes e auditoria das dependências npm/PyPI do runner.

Não contém aplicações e não aprova A1. Imagens e pacotes apt não estão cobertos pela auditoria de lockfiles. Os controles e a execução protegida continuam sob responsabilidade do dono. Não há migração de dados ou deploy; uma correção após admissão exige versão própria revisada, sem alterar os controles do dono.
