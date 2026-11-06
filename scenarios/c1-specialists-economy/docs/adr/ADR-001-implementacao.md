# ADR-001 — Sessões revogáveis e exportações

- Status: decisão de implementação do cenário C1, pendente de revisão independente.
- Data: 2026-11-06 (UTC).

## Contexto

O contrato comum exige bearer token com expiração e revogação efetiva no logout; aceita mecanismo opaco ou assinado. Exportações precisam aplicar filtros e autorização do usuário. `experiment/configs.yaml` e emendas comuns A-001/A-002 fixam Spring Boot 3.5.16, PDFBox 3.0.6, Apache POI 5.4.1, Vite 7.3.7, PostgreSQL 17.11 e pins transitivos Java. A atualização de dependências não altera os pins de Boot/Spring.

## Decisão

Usar token opaco aleatório com 256 bits, persistir somente SHA-256, expirar após 12 horas e revogar atualizando o registro no logout. Guardar bearer apenas em memória no frontend. Usar BCrypt custo 12 para senhas. Gerar PDF com PDFBox e XLSX com Apache POI, reutilizando a seleção filtrada do serviço.

## Consequências

A revogação tem efeito imediato em chamadas seguintes e exige consulta ao banco por requisição autenticada. Tokens expirados permanecem armazenados até limpeza futura; não há política de retenção definida no contrato. Exportações consultam páginas de 500 registros sem limite funcional/truncamento. XLSX usa SXSSFWorkbook com janela de 100 linhas e saída HTTP em fluxo; PDFBox usa cache de escrita em arquivo temporário e páginas geradas em blocos. Um semáforo global permite no máximo duas exportações simultâneas por processo e retorna 429 às demais. Cada geração soma totais durante a leitura. PDF usa fonte base e remove caracteres fora do conjunto ASCII. Login (20/minuto por IP) e cadastro (8/minuto por IP) usam janela com TTL de 60 s e mapa limitado a 4096 chaves; entradas expiradas são removidas nas requisições subsequentes.

## Alternativas consideradas

JWT assinado reduziria consulta de autenticação, mas revogação imediata exigiria estado adicional ou denylist. Sessão no servidor atenderia ao contrato, porém bearer opaco mantém REST simples. CSV não satisfaz PDF/XLSX.
