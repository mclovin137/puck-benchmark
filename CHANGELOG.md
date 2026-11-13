# Changelog

## v0.1.3 — 2026-11-13

Alinha o contexto de build frontend C1 à raiz do próprio cenário, incluindo os tokens de design originais. É o único import comum alterado; guardas, autorização, suíte, limites e workflow de pentest permanecem iguais. As correções de Dockerfiles/compose ficam na dev e não são importadas nesta árvore de 30 arquivos.

Mantém origem/base/ref e hashes fixados, com revisão e CI A0 antes da promoção. Não é execução A1 nem promoção de aplicações. Falhas Docker do run43503520863 não preservaram subetapa nem prova pública de cleanup. Novo candidato e novo A1 pelo dono continuam necessários após integração e gates. Sem migração, release ou deploy.

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
