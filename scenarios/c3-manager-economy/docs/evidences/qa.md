# QA independente — C3

Data: 2026-11-06. Candidato local sem commit de aplicação identificado; API em `127.0.0.1:18083` e interface em `127.0.0.1:18213`. Dados fictícios isolados por usuário; movimentações criadas foram excluídas. As contas de teste permanecem no banco, pois não há endpoint de exclusão de usuário no contrato.

Parecer: **aprovado no escopo de QA executado**, sem defeitos reproduzidos. Este parecer não atesta segurança, CI remota, inicialização reproduzível, nem aprovação integral da versão.

- `python3 tests/qa/independente.py`: passou. Cobriu cadastro, e-mail duplicado, login e revogação, acesso sem token, GET/PUT/DELETE de recurso alheio, lista isolada, filtros combinados com limites inclusivos, resumo, paginação e ordenação por valor e data, validação de datas/intervalos/paginação, conteúdo filtrado do XLSX, tipo e assinatura do PDF, exclusão e logout. Os filtros foram verificados com três movimentos de valores e datas distintos; XLSX vazio de outro usuário não contém a descrição do primeiro.
- Navegador `agent-browser` em Chromium: cadastro, login, criação de despesa de 12,34, edição para 15,00 com saldo -15,00, cancelamento de confirmação de exclusão, exclusão confirmada, estado vazio e logout. Em viewport 375×812, `scrollWidth=clientWidth=375`; não houve transbordamento horizontal nessa tela. No painel, `agent-browser a11y --tags wcag2a,wcag2aa`: axe-core 4.12.1, zero violações, zero verificações incompletas, 21 regras aprovadas. Essa ferramenta não substitui inspeção completa de acessibilidade.
- A suíte existente `tests/integration.py` cobre PDF extraído, XLSX, CRUD, filtro literal, isolamento básico e logout; sua execução prévia está documentada em `docs/verificacao.md`. Não a repeti: depende de pypdf ausente no Python padrão e o relatório prévio já registra execução. O teste independente acima não extrai conteúdo do PDF nem comprova o isolamento do conteúdo PDF; tampouco testa concorrência, todos os limites monetários, todos os filtros ou múltiplas resoluções.

## Revisão do delta — data local

Em 2026-11-06, após rebuild informado pelo implementador, navegador Chromium iniciado com `TZ=Pacific/Kiritimati` acessou `http://127.0.0.1:18213/`, autenticou usuário fictício e exibiu o formulário. No mesmo instante, `new Date().toISOString()` retornou `2026-11-06T13:07:14.411Z`, o relógio local mostrou 2026-11-07 03:07 GMT+14 e o campo de data exibiu `2026-11-07`. Resultado: **aprovado para o ajuste de conversão inicial**; a data padrão observada segue o calendário local mesmo quando UTC está no dia anterior.

Limite: `blank` é inicializado uma vez ao carregar o módulo e reutilizado ao salvar ou cancelar. Se a página permanecer aberta durante a virada do dia, a data padrão não é recalculada; não foi simulada essa permanência em navegador, e o contrato não especifica atualização automática nessa situação. Não foram repetidos os demais testes da rodada anterior.
