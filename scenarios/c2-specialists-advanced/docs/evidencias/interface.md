# Interface C2

O coordenador exercitou o frontend real no Chrome por agent-browser 0.41.1, primeiro no Vite local e depois no Compose em `http://127.0.0.1:18202`. Contas e dados foram sintéticos; respostas não foram simuladas. O roteiro e seus limites estão em `browser.json`.

Cadastro/login, entrada, saída, edição, detalhes, filtros combinados, ausência de resultados, limpeza, ordenação por valor, paginação, downloads, exclusão com cancelar/confirmar e logout passaram. Onze registros foram criados pela API real da mesma conta para testar duas páginas com 10 e 1 linha; a sessão de seed foi revogada. PDF e XLSX baixados pelos botões foram abertos e conferidos em `downloads.json`.

As capturas `dashboard-desktop.png` e `dashboard-mobile.png` mostram a interface em 1440 px e 390 px. No mobile, viewport, documento e body mediram 390 px de largura; a tabela tem rolagem própria. O vídeo `demo.webm` grava os fluxos reais, dura 7 min 13 s e tem hash em `browser.json`.

Axe-core 4.12.1, tags WCAG2A/WCAG2AA: login e cadastro tiveram 12 verificações aprovadas cada; dashboard teve 23. Nenhuma violação ou verificação incompleta nessas telas. O diálogo de exclusão teve 11 aprovações, nenhuma violação e uma verificação de contraste inconclusiva por sobreposição. O par foi conferido em estilos computados e captura: texto RGB(26,25,18) sobre branco, 16 px, opacidade 1, contraste 17,62:1. A abertura por Enter e fechamento por Escape restauraram o foco ao mesmo botão de exclusão.

Essas verificações não equivalem a auditoria completa WCAG. Nome só com espaços, e-mail inválido e senha curta foram rejeitados também pela validação nativa do cadastro; a validação do backend tem provas próprias. Armazenamentos local/session estavam vazios e não havia cookie de autenticação durante a sessão privada.
