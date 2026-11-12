Ficha: tarefa=benchmark-recovery agente=patrick-jane modelo=gpt-6.1-sol (adaptador; runtime não inspecionado) esforço=medium skill=agent-browser,e2e-testing,verificar-antes-de-concluir,humanizer.

# C1 — complemento funcional pela interface

Chamada conferida: tarefa, aceite e escopo presentes; QA de interface dentro do papel. Execução em 12/11/2026, encerrada às 11:46:20Z, com Chromium via `agent-browser`, sessão própria `c1-qa-completion-20261112`. Aplicação em `http://localhost:5173`, ambiente sintético exclusivo iniciado pelo Oráculo, projeto `benchmark-c1-ui-3397336c`, commit informado pelo marcador de prontidão `13f775b94ab5731a4d6ae7b93aebc55513e1c2a8`.

**Resultado: aprovado no escopo funcional observado em desktop 1280 e mobile 360, com ressalva visual em 320.** O critério 9 da auditoria geral passa de parcial para aprovado no escopo observado. Não há nova aprovação de CI, segurança, A1 ou versão. Não foram lidos testes privados nem alterados fontes, dados de outros usuários ou ambiente. A conta é sintética; nome e e-mail com domínio reservado exibidos nas capturas são fictícios. Senha, sessão e downloads ficaram privados. Todos os registros financeiros criados foram excluídos pela UI; a conta permanece até o descarte do banco, pois o contrato não oferece exclusão de usuário.

## Jornada executada

Todas as mutações funcionais abaixo usaram formulários e botões reais. Não houve chamada API para cadastro, autenticação, seed ou CRUD, nem execução JavaScript para disparar handlers ou modificar estado da aplicação. JavaScript foi usado somente para leitura de DOM/dimensões e tentativa de rolagem da janela.

| Passo | Resultado observado |
|---|---|
| Cadastro e login, 1280×900 | Formulário de cadastro mostrou “Conta criada. Entre com seu e-mail e senha.”; botão Entrar abriu o dashboard da pessoa sintética. |
| Criar entrada e saída | “Entrada QA”, Trabalho, 100.10 e “Mercado QA”, Casa, 20.03 apareceram na tabela. A data inicial do formulário foi usada, sem alterar o controle nativo. |
| Editar saída | Alteração para 15.50 pelo botão Editar e Salvar; resumo exibiu entradas 100,10, saídas 15,50 e saldo 84,60. |
| Filtro e resumo, desktop | Abrir “Filtrar movimentações” e preencher categoria Casa selecionou só Mercado QA; resumo exibiu entrada 0,00, saída 15,50, saldo −15,50 e uma movimentação. Limpar restaurou os dois registros e 84,60. |
| PDF e Excel, desktop | Os dois botões iniciaram downloads reais. PDF tem assinatura `%PDF`; XLSX foi aberto como ZIP/XML e contém Mercado QA/15.50, sem Entrada QA/100.10. |
| Edição e filtros, 360×812 | Editar entrada para “Entrada QA editada” funcionou; descrição sem correspondência produziu lista vazia, contagem zero e resumo zerado; Limpar recuperou entrada e saldo 100,10 após exclusão da saída. |
| PDF e Excel, 360×812 | Downloads reais pelos mesmos botões; XLSX contém a entrada/100.10 e não contém a saída/15.50 já excluída. PDF conferido somente por assinatura/tamanho. |
| Exclusão, 320×812 | Cancelar preservou a saída e o saldo 84,60; confirmar a removeu e deixou 100,10. A entrada editada também foi excluída; tela vazia apareceu. A tabela exigiu rolagem horizontal própria para alcançar ações; um aviso sobreposto foi fechado pelo botão normal antes do clique final. |
| Logout, 320×812 | Botão Sair voltou ao login e mostrou “Sessão encerrada com segurança.”; senha estava vazia na captura. |

A edição desktop e exclusão mobile não representam repetição completa da suíte de QA. Não foram testados todos os filtros/ordenações/temas, paginação com volume, expiração, teclado completo ou WCAG. A prova HTTP comum permanece responsável por semântica mais ampla das exportações e contratos.

## Responsividade e consequências observadas

- **1280:** composição em colunas e resumo legível; formulário, filtro e downloads utilizados.
- **360:** corpo 360 px, documento 383 px, tabela 308 px de área visível e 410 px de conteúdo. `window.scrollTo(100,0)` manteve `scrollX=0`. Os fluxos de edição, filtro, limpar e downloads foram executáveis. Nome da pessoa e opções dos seletores do cabeçalho aparecem abreviados pelo espaço disponível; não foi demonstrada ação bloqueada.
- **320 com filtros abertos:** corpo 331 px, documento 391 px; `scrollTo(100,0)` resultou em `scrollX=5` em uma observação. Em outra posição, a janela estava em `scrollX=11`; a variação acompanha rolagem/foco. Categoria, De, Valor mínimo e Limpar filtros tinham limite direito 330,59 px com janela em x=0, excedendo o viewport em aproximadamente 10,59 px. As capturas mostram bordas dos campos fora do cartão. Preencher Categoria e clicar Limpar funcionaram mesmo nesse estado; nenhum botão ou valor foi comprovadamente inacessível pelo excesso. Não se afirma ausência de overflow em 320.
- **Tabela mobile:** largura interna maior que a área visível é observável. Rolagem horizontal da própria tabela permite alcançar ações; não é ausência de conteúdo. Cliques podem ser cobertos por aviso de sucesso enquanto ele está aberto; fechar o aviso restituiu a ação. Não houve necessidade de alterar CSS ou forçar clique.

O excesso de largura em 320 é uma limitação de apresentação a registrar, sem falha funcional bloqueante confirmada nesta jornada. A aprovação do critério 9 se limita às resoluções e ações observadas, preservando a ressalva em vez de afirmar responsividade perfeita.

## Artefatos e falhas da automação

Capturas reais sanitizadas em [ui-c1/](ui-c1/): `desktop-filtered.png`, `mobile-360-filtered.png`, `mobile-320.png`, `mobile-320-actions.png`, `mobile-320-final.png` e `logout-320.png`. Foram abertas para inspeção as versões desktop, 360, 320-final e logout. Screenshots de página inteira capturam conteúdo além da altura inicial e podem refletir a largura do documento; não são prova de que todo esse conteúdo esteja simultaneamente visível na janela.

Downloads privados, sem publicação de bytes ou dados de sessão:

| Arquivo | Bytes | SHA-256 |
|---|---:|---|
| PDF filtrado desktop | 923 | `dfb5f397ab06336972ebb53fe2184f12768e7e027a1995c2e4132475d6a686b7` |
| XLSX filtrado desktop | 3604 | `c79f320b3aa229a5d1897d0870c95f835eb0d00ade4c842801e65ad2f389a972` |
| PDF mobile | 925 | `82c0323b6f09b515beea5bf47a765cd5b5d21cbc8fa4e3f2415027a95876c263` |
| XLSX mobile | 3606 | `541b4ee4f5e3d9671ef594e69fc6d802c9ae95ddba212534cf452728cc0dec36` |

A tentativa `agent-browser record start` falhou ao resolver `ffmpeg` no ambiente do CLI. O Oráculo informou depois um binário existente do Playwright; ele não foi usado e nenhuma configuração foi ajustada nesta rodada. Portanto a captura de vídeo não foi executada nesta rodada; não se alega indisponibilidade geral do recurso. Capturas, resultados dos downloads e este relato são as alternativas verificáveis.

A automação teve duas esperas de 25 s sem sucesso: a primeira procurou “Nova movimentação”, enquanto a tela usa “Adicionar movimentação”; a segunda procurou Entrar após um clique com ref desatualizada. Snapshots corrigiram ambos, e o login/logout final foi observado. Seletores por placeholder/tipo que não existiam e refs não atualizadas falharam; foram substituídos por snapshot novo ou seletor `aria-label`. Alguns cliques ocorreram durante atualização assíncrona da lista; esperar o marcador do registro resolveu. Um clique de exclusão inicial abriu edição, sem mutação; a nova seleção explícita de `aria-label` abriu o diálogo correto. Esses erros não são apresentados como defeitos da aplicação nem omitidos como sucesso de todas as tentativas.

A sessão de navegador foi fechada; o Oráculo executou a limpeza. O marcador privado terminal foi lido por este QA: projeto `benchmark-c1-ui-3397336c`, commit `13f775b94ab5731a4d6ae7b93aebc55513e1c2a8`, `cleanup_success=true`, término `2026-11-12T11:46:56.692285Z`; o Oráculo também informou exit0 do processo. Isso comprova a limpeza no alcance do registro operacional, sem inspeção independente de todos os recursos Docker. Não há aprovação de pentest ou versão implícita na conclusão funcional.
