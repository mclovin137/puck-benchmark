# Template de design

Padrão visual para projetos novos: tokens, base, componentes e animações em CSS/JS puro, sem build nem dependências. Leia [PADRAO-VISUAL.md](PADRAO-VISUAL.md) (princípios, movimento, checklist, adoção).

| Arquivo | Função |
| --- | --- |
| `tokens.css` | Cores dos 5 temas (`[data-tema]`, claro/escuro via `light-dark()`), tipografia fluida, espaço, raios, sombras, durações e easings |
| `base.css` | Reset leve, foco visível, utilitários e `prefers-reduced-motion` |
| `animacoes.css` | Keyframes e utilitários (entrada, revelar ao rolar, view-transition) |
| `componentes.css` / `componentes.js` | 17 componentes e comportamento mínimo (tema, toast, validação, modal, abas, palette Ctrl/⌘+K, stepper) |
| `exemplo/index.html` | Demonstração navegável; trocar tema/modo; capturas em `exemplo/capturas/` |
| `contraste.py` | Valida WCAG AA de todos os pares, temas e modos; falha com código 1 |

Uso: `python3 contraste.py` (após editar cores) e abrir `exemplo/index.html`. Teste: `agents/scripts/tests/test_design_tokens.py`.

Temas: 1 Musgo, 2 Oceano, 3 Areia, 4 Grafite, 5 Argila. A identidade da marca do projeto troca só as cores dos tokens; o resto é reutilizado.
