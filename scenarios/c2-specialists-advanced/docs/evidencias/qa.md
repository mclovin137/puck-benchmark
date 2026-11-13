# QA independente C2

Data: 2026-11-06. Responsável: Patrick Jane. Primeira rodada de produção concluída, incluindo a leitura inicial e a retomada após integração; não houve nova rodada completa.

**Parecer: aprovado no escopo funcional e de suficiência dos testes locais examinados, sem defeito funcional bloqueante confirmado. A entrega integral permanece pendente de CI remota e pentest exigidos. Este parecer não aprova promoção, merge ou release, nem afirma ausência geral de vulnerabilidades.**

## Escopo e origem das provas

Confrontados especificação comum, contrato REST, emendas A-001/A-002, HLD/ADRs, frontend, regras/DTO/DAO/actor/exportador financeiros e suítes `DomainTest`/`ApiIntegrationTest`. Reutilizadas as evidências do implementador e coordenador em `backend.json`, `runtime.json`, `browser.json`, `downloads.json`, `recuperacao.json` e `interface.md`. Revisões independentes de arquitetura e segurança lidas em `arquitetura.md` e `seguranca.md`. Nenhum outro cenário ou teste do avaliador foi consultado; sem Git ou declaração de commit da aplicação.

Não reexecutei suítes válidas somente para trocar o executor. A inspeção QA conferiu os XML Surefire atuais, os quatro relatórios axe, o conteúdo XML do download XLSX e as capturas reais `dashboard-mobile.png` e `delete-dialog.png`. Não escrevi produção ou testes; a autoria limita-se a este parecer.

## Resultado por risco

| Área | Evidência pertinente e conclusão |
| --- | --- |
| Execução integrada | `runtime.json` registra nove grupos aprovados na API real com PostgreSQL; `browser.json` registra cadastro/login e operações pela origem Compose canônica. A falha de JSON 401 Latin-1 foi corrigida com regressão RED/GREEN; CORS da origem canônica foi corrigido e o fluxo de cadastro/login repetido com sucesso. |
| Sessão e isolamento | Integração testa email normalizado/repetido, credencial inválida, expiração, revogação e outra sessão ainda válida. CRUD alheio retorna 404, payload com owner é rejeitado e DTO não expõe proprietário. Seleção exige owner; resumo e exportações passam pelo mesmo caminho. Exportação é aberta nos testes e não contém marcador de outro usuário. Runtime verifica token revogado também na exportação. |
| Precisão/validação | Testes protegem limite monetário, excesso de precisão, zero/negativo, tipo JSON numérico e soma exata de 0.10 + 0.20. Regras e constraints usam decimal; frontend mantém strings/BigInt para dinheiro. Testes cobrem datas/filtros inválidos, intervalos invertidos, size inválido e ordenação não permitida; runtime/UI exercitam data futura e edição. |
| Filtros, totais e páginas | Teste combinado inclui tipo, categoria, descrição literal com `%`, `_` e escape, datas/valores inclusivos e página de tamanho 1. Outros testes verificam resumo sem paginação, seleção vazia e desempate de datas sem repetição entre páginas. DAO reutiliza o predicado autorizado e acrescenta id à ordem. Browser comprova filtro Casa, saldo −15.50, vazio/limpeza, amount ascendente e navegação 10/1 registros. Não foi inferida execução exaustiva de todas as combinações possíveis. |
| Arquivos | Testes abrem PDF/XLSX, conferem totais, texto pt-BR e ausência de dados alheios; size=1 não limita a seleção exportada. Há teste de PDF multipágina com cabeçalho repetido e total. Os downloads reais da UI contêm 100.10, 15.50 e 84.60, segundo a prova do coordenador. QA abriu o ZIP/XML do XLSX, confirmou os dois marcadores de descrição e valores esperados e ausência de elementos de fórmula. O Python desta inspeção não dispõe de pypdf; PDF não foi reaberto por QA, preservando a origem da prova. |
| Interface e acessibilidade | Browser real cobre criação, edição, detalhes, exclusão cancelada/confirmada, resumo, filtros, exportações e logout. Captura mobile de 390 px mostra composição utilizável, com tabela em área horizontal própria; métricas registradas não apontam overflow global. Desktop e diálogo foram capturados. Axe registra zero violações nas quatro telas; o único incomplete de contraste no diálogo recebeu inspeção manual registrada de 17.62:1. Enter abre exclusão, Escape fecha e restaura o foco ao mesmo botão. Isso não comprova toda WCAG nem todos os dispositivos. |
| Recuperação | `recuperacao.json` registra pg_dump/pg_restore em banco descartável, quatro tabelas e contagens preservadas. É prova local de restauração, sem promessa de recuperação de produção. |

## Contagem e atualidade dos testes

`backend.json`, do implementador, registra suíte base PostgreSQL 17.11 Testcontainers com 2 testes de domínio e 10 de integração, todos sem falhas, erros ou skips. Após o ajuste UTF-8, foram executados 4 testes pertinentes: 3 já existentes e 1 regressão nova. Portanto são **13 casos backend distintos cobertos pelas duas execuções**, não 16 executados em uma suíte final única.

Os XML atuais, conferidos por QA, mostram 4 integrações e 2 testes de domínio verdes; o XML parcial não prova sozinho a execução base de 12. A evidência base permanece atribuída ao implementador. O delta de encoding é estreito, com regressões pertinentes e API/browser após a correção; não foi identificada razão concreta para repetir toda a suíte. Frontend possui 2 testes monetários e build informados verdes; estes não substituem as provas de browser/API descritas acima.

## Achados e limites de encerramento

O único achado da leitura inicial era opcional: exclusão com 401 mantinha sessão local, diferentemente dos demais fluxos. O coordenador corrigiu `remove()` para fechar o diálogo e chamar `fail`; QA conferiu o delta. Não foi alegado bypass, e não há prova específica de browser para expiração durante esse diálogo; a revogação backend e o ramo de tratamento foram verificados por evidências separadas.

Não há defeito funcional bloqueante confirmado neste escopo. O roteiro de browser real é evidência de execução, não uma suíte automatizada de regressão de UI. Os testes não demonstram cobertura percentual, carga elevada ou toda a acessibilidade. PDF com glifos ausentes usa representação explícita; volumes grandes e exposição além do host local preservam os riscos de capacidade apontados nas revisões.

Neo aprovou o escopo estático, aplicabilidade Spring e barreiras do harness na rodada 2. Os componentes Spring **continuam afetados**, mantendo OSV CRITICAL e fornecedor LOW/MEDIUM visíveis; ausência das pré-condições nos caminhos examinados não significa componente corrigido. Pentest ofensivo e CI remota **não foram executados**; a política inicial vazia bloqueia a execução até integração/configuração dos gates reais. Esses controles continuam pendentes e impedem transformar este parecer funcional em aprovação integral da entrega.
