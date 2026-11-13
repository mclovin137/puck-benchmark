# Padrão visual

Padrão para interfaces de projetos novos que adotam o Puck. Objetivo: telas **fáceis**, com **poucos cliques**, **descritivas**, **sem burocracia** e **vivas** (movimento com propósito). Vanilla CSS/JS, sem build nem dependências.

## Princípios

1. **Poucos cliques.** A ação principal fica sempre visível (um único botão primário por tela). Qualquer ação alcançável em 1–2 passos pela command palette (`Ctrl/⌘+K`).
2. **Descritivo.** Rótulos dizem o que acontece ("Criar projeto", não "OK"). Erros dizem como corrigir. Estados vazios explicam o próximo passo.
3. **Defaults sensatos.** Pré-selecione a opção mais comum; marque "(recomendado)".
4. **Sem burocracia.** Peça só o necessário; use `autocomplete`, lembre a última escolha; **desfazer em vez de confirmar** (toast com "Desfazer"). Modal só para ação irreversível.
5. **Feedback imediato.** Todo clique responde em < 100 ms (hover, press, carregando). Validação inline ao sair do campo.
6. **Vivo, mas sem exagero.** Movimento explica mudança de estado; nunca bloqueia nem entretém.

## Temas e paleta

Cinco temas via `<html data-tema="1..5">`, cada um com modo claro e escuro (`data-modo="claro|escuro"`; sem atributo, segue `prefers-color-scheme`). Cores usam `light-dark()` em `tokens.css`.

| Tema | Base (fundo, destaque, acento) | Claro: fundo / primária / acento | Escuro: fundo / primária / acento |
| --- | --- | --- | --- |
| 1 Musgo | #090907, #6c5636, #899d73 | derivado / #6c5636 / #899d73 | #090907 / #9a7d52 (derivada) / #899d73 |
| 2 Oceano | #021861, #255DCE, #DE1110 | derivado / #255DCE / #DE1110 | #021861 / #6d9bff (derivada) / #DE1110 |
| 3 Areia | #5B4632, #F4D9A0, #C8792C | derivado / #5B4632 / #C8792C | #2e2418 (derivado; #5B4632 em superfície elevada) / #F4D9A0 / #C8792C |
| 4 Grafite | #171717, #06110C, #A31C1B | derivado / #06110C / #A31C1B | #171717 (#06110C em superfície rebaixada) / #6fd0a0 (derivada) / #c8332f (derivada) |
| 5 Argila | #A5A79B, #E8D2B5, #590907 | #f3e9da (tinta de #E8D2B5) / #590907 / #A5A79B | #1b1211 (derivado de #590907) / #E8D2B5 / #A5A79B |

Papéis (tokens `--cor-*`): `fundo`, `superficie`, `superficie-2`, `borda`, `borda-forte` (campos, ≥ 3:1), `texto`, `texto-suave`, `primaria` + `sobre-primaria`, `primaria-texto` (links, foco, ícones), `acento` + `sobre-acento`, `acento-texto`, e estados `sucesso`, `erro`, `aviso` (texto/ícone/borda; fundos suaves via `color-mix`). Estado nunca depende só de cor: sempre há texto ou ícone.

Pares base que não passam sozinhos (tratados com tons derivados): #6c5636 sobre #090907 = 2,87:1; #255DCE sobre #021861 = 2,71:1; #DE1110 como texto sobre claro < 4,5:1; #06110C sobre #171717 = 1,07:1; #A31C1B sobre #171717 = 2,34:1; #A5A79B como texto sobre fundo claro. Regra: base como preenchimento com `sobre-*` de contraste ≥ 4,5:1; base como texto só quando passa, senão usar o derivado `*-texto`. Rode `python3 contraste.py` após qualquer mudança de cor.

## Movimento

- **Duração 120–300 ms**: `--dur-rapida` 120 (hover, press), `--dur-media` 200 (abrir/fechar, trocar estado), `--dur-lenta` 300 (entrada de seção, revelar ao rolar).
- **Easing**: `--ease-saida` para entradas (rápido e suave no fim), `--ease-entrada` para saídas, `--ease-padrao` para mudanças de cor/estado, `--ease-mola` só em microinterações pequenas (seletor de tema, pulso).
- **Animar**: `transform`, `opacity`, cor, sombra. **Não animar**: `width/height/top/left` (exceto barra de progresso), conteúdo ao ler, textos longos, nada em loop infinito exceto carregamento (spinner, skeleton) e o pulso discreto de estado vazio.
- **Escalonar** entradas em até ~4 itens (60 ms de atraso), nunca listas longas.
- Revelar ao rolar com `IntersectionObserver` (classe `.revelar`); troca de tema com View Transitions API quando disponível.
- `prefers-reduced-motion: reduce` desliga animações e transições (já em `base.css`); o conteúdo continua visível.
- Interação padrão: hover levanta 1–2 px, press afunda (`scale(.97)`), foco com anel de 3 px.

## Grade e espaçamento

Base de 4 px (`--espaco-1…8`: 4, 8, 12, 16, 24, 32, 48, 64). Conteúdo até `--largura-conteudo` (72 rem), gutter mínimo 16 px, `grid auto-fit minmax(16rem, 1fr)` para cartões. Alvos de toque ≥ 44 px (`--altura-controle`). Raios: 6, 10, 16 px e pill para botões/seletores. Navegação lateral a partir de 52 rem; abaixo disso, menu recolhível. Sombras só para elevação real (cartão em hover, modal, toast).

## Tipografia

Fonte do sistema (sem download, carrega instantâneo). Escala fluida com `clamp()`: `--texto-xs…3xl` (corpo 15–16 px). Altura de linha 1,55 no corpo e 1,2 nos títulos, `text-wrap: balance` em títulos, medida de leitura ≤ 65 caracteres. Peso 600–700 para rótulos e botões, 400 no corpo. Números em tabelas e métricas com `tabular-nums`.

## Acessibilidade (WCAG AA)

Contraste: texto normal ≥ 4,5:1; UI e foco ≥ 3:1 (validado por `contraste.py` em todos os temas e modos). Tudo operável por teclado; foco sempre visível; `<label>` em todo campo; erros ligados por `aria-describedby` e `aria-invalid`; `role="status"` nos toasts; `<dialog>` para modais (foco preso e Esc nativos); abas com setas; link "Pular para o conteúdo". Funciona sem JS para leitura e navegação. Respeita `prefers-reduced-motion` e `prefers-color-scheme`.

## Componentes

Botão (primário, secundário, fantasma, acento, perigo, carregando), campo com validação inline, seletor de tema/modo, cartão, tabela, modal, toast com desfazer, abas, acordeão, navegação topo/lateral, estado vazio, skeleton, progresso, tooltip, command palette, stepper. Veja `exemplo/index.html`. Extensão: novos componentes usam só tokens (`--cor-*`, `--espaco-*`, `--dur-*`) e nomes `.componente--variante`.

## Checklist de tela nova (≤ 10 itens)

1. Há uma única ação principal, visível sem rolar?
2. Os rótulos e mensagens dizem o que acontece e como corrigir erros?
3. Só pede o necessário (autopreenchimento, defaults)?
4. Ações destrutivas têm "Desfazer" em vez de confirmação (modal só se irreversível)?
5. Estados cobertos: carregando (skeleton/botão), vazio, erro, sucesso, desabilitado?
6. Tudo alcançável por teclado, com foco visível e ordem lógica?
7. Só tokens (sem cor/medida solta); `python3 contraste.py` passa se mexeu em cor?
8. Movimento 120–300 ms, só transform/opacity, e `prefers-reduced-motion` respeitado?
9. Funciona em 360 px e em 1280 px sem rolagem horizontal?
10. Testado em pelo menos dois temas, claro e escuro?

## Como adotar

Copie a pasta (menos `exemplo/` se quiser) para o projeto, por exemplo `web/design/`, e inclua no `<head>`:

```html
<link rel="stylesheet" href="design/tokens.css">
<link rel="stylesheet" href="design/base.css">
<link rel="stylesheet" href="design/animacoes.css">
<link rel="stylesheet" href="design/componentes.css">
<script src="design/componentes.js" defer></script>
```

Defina o tema em `<html data-tema="3">`. Para evitar piscada ao carregar com tema salvo, copie o pequeno script inline do `<head>` de `exemplo/index.html`. Para a paleta de ações, marque elementos com `data-comando="Rótulo"` e `data-grupo="Grupo"`; a palette os lista e aciona por clique. Abra `exemplo/index.html` no navegador para ver tudo (`?tema=N&modo=claro|escuro`).
