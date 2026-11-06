# Protocolo prévio

Estudo exploratório: uma execução por cenário. Sem inferência estatística ou pontuação geral. O commit Puck e as versões de stack estão em configs.yaml. Especificação integral em specification.md, sem alterações.

## Ambiente e isolamento

Mesmo host WSL/Linux, Docker e toolchain. Java 21 nos containers, release 21 no Maven; host Java 25 pode executar Maven. Node 24. Dependências adicionais da aplicação devem ser fixadas no manifest e registradas. Puck é consultado no checkout imutável /tmp/puck-benchmark-source; instalação global divergente não substitui a fonte fixada. A memória não foi exposta como ferramenta nesta sessão; nenhuma consulta é declarada.

Ordem de despacho C1 → C2 → C3 → C4; execução sequencial por cenário para reservar capacidade de delegação especializada; no máximo três subagentes simultâneos, horários registrados no ledger. Cada cenário parte somente da governança fixada, sem código de aplicação. Atribuições isoladas e contexto vazio; proibição de leitura cruzada. O filesystem compartilhado não constitui isolamento de segurança: esta limitação impede alegar cegamento tecnicamente garantido. Avaliador independente mantido pelo Oráculo, fora da autoria das aplicações. Testes não são revelados aos implementadores durante a implementação.

## Execução e encerramento

Até três tentativas de implementação por tarefa; até duas rodadas de revisão, segunda no delta. Correções por requisito já entregue são retrabalho; evolução planejada e refatoração preventiva são separadas. Gates ausentes são não observados ou reprovados, nunca aprovados por inferência. Estados finais possíveis: aprovado, parcialmente aprovado ou bloqueado, com motivos verificáveis. Um estado bloqueado exige dependência realmente indisponível, não apenas trabalho pendente.

## Contrato comum REST

Base /api. Bearer token opaco ou assinado, com expiração e revogação efetiva no logout. Frontend não persiste token em localStorage. POST /auth/register {name,email,password} → 201; POST /auth/login {email,password} → 200 {token}; POST /auth/logout → 204 e token revogado. /auth/me → usuário autenticado. Erros de validação 400, credencial inválida 401, ausente/de outro usuário 404, e-mail repetido 409. E-mail normalizado, senha 12–128 caracteres; nome 1–120; descrição 1–255; categoria 1–80, strings aparadas. Usuários nunca informam proprietário por payload.

/api/transactions: POST → 201 com registro; GET lista; /{id}: GET e PUT → registro, DELETE → 204. Campos: id, type (INCOME/EXPENSE), description, category, amount (decimal em string, >0, até 14 inteiros e 2 decimais), date (ISO yyyy-MM-dd), createdAt, updatedAt; propriedade implícita. Datas válidas, datas futuras permitidas. Categorias são nomes livres não vazios validados; CRUD de categorias não é exigido.

GET lista retorna {content:[],totalElements,page,size,totalPages}. page >=0, size 1–100 (padrão 20). Filtros combináveis: type, category (exato), description (substring literal case-insensitive), startDate, endDate (inclusivos), minAmount, maxAmount (inclusivos); intervalos invertidos → 400. sort=date,desc|date,asc|amount,asc|amount,desc, desempate determinístico por id.

GET /transactions/summary → {income,expense,balance,count}, decimais em string, mesma seleção autorizada sem paginação. GET /transactions/export.pdf e /transactions/export.xlsx: mesmos filtros, todas as linhas selecionadas e totais, nomes e content-types adequados; sem acesso cruzado. Datas e valores são domínio local, não convertidos por timezone. CSV não substitui XLSX.

## Evidência e métricas

Eventos append-only com cenário, execução, tarefa, fase, timestamp UTC, modelo, agente e correlação quando disponíveis. Tokens de cache são subconjunto da entrada; raciocínio é subconjunto da saída. Deduplicar eventos pelo identificador nativo. Custos reais indisponíveis são null; estimativas API separadas de cobrança. Skills só recebem dimensão analítica com rastreamento explícito e nunca custo financeiro duplicado. Duração de relógio não equivale a tempo ativo. Governança comum é overhead do experimento, não atribuída arbitrariamente a cenários.

Funcionalidade, testes, cobertura, arquitetura, segurança e conformidade são dimensões separadas. Crítica aberta impede aprovação. Sem scanner/revisão independente não afirmar ausência de vulnerabilidades. Vídeos só reais; indisponibilidade registrada com alternativas verificáveis. Métricas finais precisam de origem, timestamp e commit.

## Detalhamento de tokens solicitado

Categorias: código, documentação, testes, planejamento, revisão e busca; configuração, mista e não disponível preservam o que não cabe honestamente nas seis. Categoria de escrita vem do coletor Puck; fase vem de marcações explícitas por agente e timestamp. Entrada, saída, cache e raciocínio separados, sem somar subconjuntos novamente. Uma resposta recebe somente uma categoria de atividade e uma fase; consultas sem escrita não são presumidas como busca. Relatórios reports/token-breakdown.{csv,json} e token-events.jsonl são metadados sanitizados, sem conteúdo ou IDs nativos de sessão.
