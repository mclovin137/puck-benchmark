# Execução C2

Fonte: Puck c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a. Especificação e protocolo comuns na pasta experiment da raiz. Uma execução exploratória, sem inferência estatística. Os arquivos de outros cenários e o avaliador não foram consultados.

Modelos fixos: coordenador e especialistas gpt-6.1-sol, medium; Neo high. Papéis usados: Yoda, Severino, Zima Blue, Patrick Jane, Neo e Mr. Robot. Snapshot imutável do modelo não exposto. Tokens/custos são coletados pelo Oráculo; não são estimados manualmente aqui. Memória externa não exposta. A chamada de QA final encontrou limite de uso; foi retomada no mesmo agente/modelo após a janela indicada, sem compra de créditos. Uma interrupção operacional posterior também preservou a mesma revisão.

A preparação documental precedeu a janela de implementação. A retomada recebeu as emendas comuns A-001/A-002 antes do código de aplicação. Boot 3.5.16, Vite 7.3.7 e PostgreSQL 17.11 substituem a baseline original; overrides de A-002 constam no POM. Os dois componentes Spring afetados continuam visíveis. Neo conferiu ausência das pré-condições dos avisos por fonte, contexto Spring testado e JAR servido; não declarou os componentes corrigidos.

Git, PR, CI remota, promoção e tag são responsabilidade do Oráculo. Testes locais não representam execução de CI. O candidato deste diretório não foi commitado pelo coordenador C2. O limite de 30 arquivos por PR deve ser aplicado pelo Oráculo ao separar os blocos; os arquivos de governança herdados não provam execução de workflow.

## Implementação e retrabalho observado

- Yoda produziu HLD e duas ADRs; a revisão de produção não identificou bloqueio arquitetural.
- Zima implementou o frontend; build e dois testes monetários passaram. O coordenador uniformizou o tratamento de 401 na exclusão após a leitura inicial do QA; build/testes afetados passaram.
- Severino implementou o backend. Correções próprias: importação ambígua Row, fixture de descrição acima de 255 caracteres e mapeamento de data inválida para 400. RED de domínio e regressão de data foram intencionais, separados dessas correções. Suíte base: 12 testes em PostgreSQL real, sem falhas/erros/skips.
- A prova integrada encontrou JSON 401 em Latin-1. Severino confirmou RED, definiu UTF-8 antes do writer e passou quatro testes pertinentes; três sobrepõem a suíte base e um é novo. Não somar 12 + 4 como 16 testes únicos. A API real passou depois em nove grupos.
- O cadastro no browser revelou divergência entre a origem canonical 127.0.0.1 e o default localhost. O coordenador configurou CORS_ORIGIN explicitamente no Compose. Cadastro/login e todo o fluxo financeiro passaram após a correção, sem wildcard.
- Mr. Robot preparou o harness; Neo encontrou SEC-01/02, corrigidos e conferidos na mesma rodada 2. Cinco testes offline passaram. A política inicial vazia bloqueia A1 até configurar gates revisados. Nenhum pentest ofensivo foi executado no host.

## Evidências e alcance

`backend.json` registra suíte base e delta, sem XML bruto de ambiente. `runtime.json`, `browser.json`, capturas, downloads analisados e vídeo são provas reais. O vídeo `demo.webm` tem 7 min 13 s e foi decodificado integralmente sem erro. A ferramenta inicial ausente e uma gravação com FFmpeg incompatível falharam; a versão entregue usa o binário local identificado em `ferramenta-video.json`, sem instalação global ou recurso pago. Erros de refs, selector e preenchimento nativo de data na automação não foram tratados como defeitos da aplicação.

`recuperacao.json` registra dump/restore em banco C2 descartável, quatro tabelas e 27 linhas, incluindo movimentações, com contagens iguais e limpeza. Isso não comprova recuperação de produção. Scanners, revisão de segurança, arquitetura e QA têm alcance próprio nos respectivos relatórios. Hashes relativos ficam em `hashes.json`; commit e CI são registrados pelo Oráculo.

CI remota e pentest UI/ZAP em runner GitHub efêmero permanecem pendentes. O template aninhado e os testes offline não liberam promoção. O proprietário precisa integrar workflow na raiz, configurar aprovação em pentest-owner e os gates reais do mesmo SHA na base revisada. Não há aprovação de merge, release ou tag neste relatório.

## Pareceres finais locais

Yoda não identificou bloqueio arquitetural. Neo aprovou o escopo estático, a aplicabilidade dos avisos Spring e as barreiras do harness na rodada 2. Patrick Jane aprovou o escopo funcional e a suficiência das provas locais, sem bloqueante confirmado. O QA manteve explícitos o reuso do parser PDF, a contagem de testes em execuções separadas e a ausência de prova específica de expiração no diálogo de exclusão. Isso não aprova CI, pentest remoto ou promoção.

## Retrabalho posterior: status de login

Após o candidato inicial, foi informado erro de contrato no login com senha incorreta curta. A reprodução HTTP própria confirmou400 em vez de401, com os outros oito controles de autenticação/cadastro verdes. O mínimo12 duplicado no DTO de login impedia chegar à comparação da credencial. Severino criou regressão RED e removeu somente esse mínimo; cadastro12–128 e máximo128 no login foram preservados. Quatro testes pertinentes passaram em PostgreSQL real, em uma tentativa corretiva. Após rebuild, nove controles HTTP próprios passaram, incluindo login incorreto401 e cadastro11/128/129→400/201/400. Neo aprovou apenas o delta de dois arquivos, sem terceira revisão ampla. As execuções separadas agora cobrem14casos backend distintos; não houve suíte única final14. Evidências em login-status.json e seguranca-login-status.md. CI e reavaliação externa continuam com o Oráculo; nenhum commit foi feito pelo C2.
