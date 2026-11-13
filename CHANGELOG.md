# Changelog

## v0.3.0 — 2026-11-13

Entrega das quatro implementações independentes do controle financeiro e da avaliação comum de cadastro/sessão, movimentações, filtros/resumo e exportações PDF/XLSX. Os mesmos 16 casos HTTP originais e quatro complementares foram observados em cada cenário; os gates do candidato final continuam exigidos para a promoção.

Inclui evidências de CI, arquitetura, QA, operação, segurança e consumo por cenário/modelo/agente/fase. Referência API é estimativa datada, separada de cobrança; cache/raciocínio não são somados novamente. Modelos mistos, uma execução por cenário, intervenções, perdas históricas de telemetria e medidas ausentes impedem declarar superioridade causal. Vídeos ausentes/parciais e provas alternativas permanecem explicitados.

O conteúdo desta entrada é preparado para a promoção #28; não declara que A1, merge, tag, release ou deploy já ocorreram. A admissão das aplicações requer CI completa, pentest protegido e triagem no candidato pertinente. Componentes afetados admitidos por decisões restritas ao snapshot e lacunas de desempenho/cobertura não se tornam ausência global de risco. As versões preparatórias v0.1.0, v0.1.1 e v0.1.2 mantêm seu histórico abaixo.

Migrações e reprodução estão nos READMEs dos cenários; restores sintéticos têm alcance próprio e não medem RPO/RTO. Nenhuma migração ou operação em produção foi executada por esta preparação de release. A confirmação de entrega e sua data efetiva vêm do merge, CI e tag, não da data de preparação desta entrada.

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
