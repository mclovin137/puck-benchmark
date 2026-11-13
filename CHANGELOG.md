# Changelog

## v0.3.0 — 2026-11-13

Entrega das quatro implementações independentes do controle financeiro e da avaliação comum de cadastro/sessão, movimentações, filtros/resumo e exportações PDF/XLSX. Os mesmos 16 casos HTTP originais e quatro complementares foram observados em cada cenário; os gates do candidato final continuam exigidos para a promoção.

Inclui evidências de CI, arquitetura, QA, operação, segurança e consumo por cenário/modelo/agente/fase. Referência API é estimativa datada, separada de cobrança; cache/raciocínio não são somados novamente. Modelos mistos, uma execução por cenário, intervenções, perdas históricas de telemetria e medidas ausentes impedem declarar superioridade causal. Vídeos ausentes/parciais e provas alternativas permanecem explicitados.

O conteúdo desta entrada é preparado para a promoção #28; não declara que A1, merge, tag, release ou deploy já ocorreram. A admissão das aplicações requer CI completa, pentest protegido e triagem no candidato pertinente. Componentes afetados admitidos por decisões restritas ao snapshot e lacunas de desempenho/cobertura não se tornam ausência global de risco. As versões preparatórias v0.1.0 e v0.1.1 mantêm seu histórico abaixo.

Migrações e reprodução estão nos READMEs dos cenários; restores sintéticos têm alcance próprio e não medem RPO/RTO. Nenhuma migração ou operação em produção foi executada por esta preparação de release. A confirmação de entrega e sua data efetiva vêm do merge, CI e tag, não da data de preparação desta entrada.

## v0.1.1 — 2026-11-13

Corrige o bloqueio da fase 3 quando outros cenários da matriz aguardam aprovação. A guarda passa a conferir o job ativo do próprio cenário, run, tentativa e runner antes de aceitar o estado global waiting; a aprovação protegida continua obrigatória.

Patch exclusivo da infraestrutura confiável, sem aplicações ou execução A1. Mantém escopo, política e controles do dono. Sem migração de dados, release ou deploy; defeitos exigem novo patch revisado.

## v0.1.0 — 2026-11-13

Preparação da base confiável de pentest, com política, guardas, suíte e triagem comuns preservadas da fonte revisada. Inclui gate A0 próprio, verificação de integridade/escopo, fixtures inertes e auditoria das dependências npm/PyPI do runner.

Não contém aplicações e não aprova A1. Imagens e pacotes apt não estão cobertos pela auditoria de lockfiles. Os controles e a execução protegida continuam sob responsabilidade do dono. Não há migração de dados ou deploy; uma correção após admissão exige versão própria revisada, sem alterar os controles do dono.
