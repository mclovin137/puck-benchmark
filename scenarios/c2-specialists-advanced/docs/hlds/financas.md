# HLD: finanças pessoais C2

Versão: 1 | Data: 2026-11-06 | Responsável: Yoda

## Objetivo e estado

Desenho para implementar a [especificação](../../../../experiment/specification.md) e o [REST comum](../../../../experiment/protocol.md), sem duplicá-los. Este documento descreve decisões de implementação autorizadas pela autonomia técnica do experimento; não comprova código, execução nem aprovação independente. Memória indisponível nesta sessão.

## Topologia e componentes

Browser React/TypeScript → HTTP REST `/api` → Spring Boot → PostgreSQL. Docker Compose local, projeto `puck-c2`; frontend 18202, backend 18082 e banco 15432 vinculados a `127.0.0.1`. Sem serviço pago, fila ou cache. Exposição pública e metas de carga/disponibilidade não foram solicitadas.

Baseline: Java 21, Boot 3.5.16, React 19.2.0, TS 5.9.3, Vite 7.3.7, PostgreSQL 17.11, JPA/Flyway, PDFBox 3.0.6 e POI 5.4.1. Aplicar A-002: Jackson BOM 2.21.7, commons-lang3 3.18.0, Log4j2 BOM 2.25.5, Tomcat 10.1.61, JDBC 42.7.14. A baseline não equivale a ausência de vulnerabilidades.

| Componente | Responsabilidade | Dependências |
|---|---|---|
| Frontend | Formulários, sessão em memória, filtros e download autenticado | API por DTO; valores monetários em string |
| REST | Validar allowlist de DTO/query, mapear HTTP e erros | Actor; sem acesso a repositório |
| Actor | Orquestrar um caso de uso e sua transação | Service e DAO |
| Service | Regras puras de valores/filtros e geração de arquivos | Domínio, PDFBox/POI; sem consulta direta ao banco |
| DAO | Consultas JPA com proprietário obrigatório, persistência | PostgreSQL |
| Segurança | Resolver token em principal autenticado; respostas 401 | DAO de sessão; domínio separado das movimentações |

Pastas por entidade/função: `auth/{rest,actor,service,dao,dto,dominio}`, `transaction/{rest,actor,service,dao,dto,dominio}`; segurança e erros compartilhados em `comum/`. Helpers e builders somente se houver necessidade real. Sem interface/fábrica genérica por antecipação.

## Fluxos e invariantes

Cadastro normaliza e-mail, valida nome/senha, calcula hash parametrizado e persiste usuário com unicidade no banco; colisão concorrente vira 409. Login valida hash e cria token opaco; logout revoga a sessão persistida. Toda consulta privada deriva proprietário do principal, nunca do payload. Busca/alteração/exclusão por `(id,ownerId)` evita revelar existência alheia; ausência retorna 404. DTO não expõe entidade, hash ou proprietário.

Movimentação usa `BigDecimal`, `LocalDate` e timestamps UTC; `NUMERIC(16,2)` e DTO decimal em string, até 14 inteiros e 2 decimais, positivo. Rejeitar precisão excedente antes da persistência, sem arredondamento silencioso. Datas financeiras nunca sofrem conversão de fuso. Saldo não é coluna nem fonte paralela de verdade.

Um filtro normalizado reúne type, category exata, description substring literal sem distinguir maiúsculas, limites inclusivos de data/valor e sort permitido. DAO produz uma única seleção lógica com `owner_id` obrigatório, reutilizada em lista, resumo e exports. Escapar `%`, `_` e caractere de escape em LIKE; parametrizar entradas. Resumo usa toda a seleção, não a página. Exportação usa toda a seleção e ordenação determinística com id como desempate, sem teto silencioso de registros. Totais são calculados com decimal exato. Semântica e limites completos permanecem no protocolo.

Em uma resposta de exportação, linhas e totais devem vir do mesmo conjunto materializado ou snapshot transacional. Chamadas HTTP separadas podem observar alterações concorrentes entre si; igualdade é exigida para mesmo estado/filtros, sem promessa de snapshot entre chamadas. Lista e contagem devem compartilhar snapshot quando duas queries forem usadas. PDF pagina linhas com cabeçalho repetido e totais; XLSX escreve descrição/categoria como células de texto, sem fórmulas controladas pelo usuário. Geradores fecham recursos e não deixam arquivos temporários sensíveis.

## Dados e persistência

`app_user`: id, name, email normalizado único, password_hash, created_at. `auth_session`: id, user_id FK, token_hash único, expires_at, revoked_at. `financial_transaction`: id, owner_id FK, type, description, category, amount NUMERIC(16,2), date DATE, created_at/updated_at. Constraints espelham enum, limites essenciais e amount>0; índice inicial `(owner_id,date,id)` e índice único de e-mail/hash. Índices adicionais somente com evidência de consulta.

Flyway versiona schema PostgreSQL; JPA valida schema, sem `ddl-auto=update`. Testes de persistência e integração usam PostgreSQL 17.11, jamais H2. Retenção/backup de produção são lacunas fora do ambiente local; não inventar SLA. Migrações aplicadas são imutáveis; correção por nova versão, recuperação de dados depende de backup verificado pelo dono operacional.

## Segurança, operação e riscos

Sessão e seleção financeira estão nas [ADRs 001](../adrs/adr-001-sessoes-opacas-revogaveis.md) e [002](../adrs/adr-002-selecao-financeira-unica.md). API exclusivamente JSON/arquivos, sem SSE/view fragments, XsltView ou resolução de views por catch-all. Isso é restrição de desenho: os advisories Spring GHSA-j9f9-w8pj-32f8 e GHSA-pc63-qcmh-9cmg continuam pendentes de prova Neo sobre código e dependências. Severidade OSV CRITICAL e fornecedor LOW/MEDIUM permanecem visíveis; ausência de pré-condição não corrige componente.

Logs registram status/erro e duração, sem token, senha, payload financeiro ou dados pessoais. Erros externos não expõem stacktrace/SQL. Segredos vêm do ambiente e nunca do repositório. CORS restringe origem local configurada; Bearer em Authorization, sem cookie de sessão. A configuração efetiva ainda exige revisão independente.

| Risco | Probabilidade / impacto | Mitigação e contingência |
|---|---|---|
| Falta de owner em consulta | Plausível / vazamento crítico | DAO exige owner e testes negativos de CRUD, resumo/export; bloqueia entrega se falhar |
| Filtro divergente ou arredondamento | Plausível / integridade financeira | Seleção compartilhada, decimal exato e testes de borda; corrigir antes do aceite |
| Exportação grande esgota memória | Desconhecida / indisponibilidade local | Sem carga conhecida; fechar recursos, testar múltiplas páginas e medir antes de otimizar; não truncar dados |
| Advisory Spring residual | Dependente de pré-condição / potencial crítico | Neo independente comprova restrições; se houver uso afetado, reabrir baseline/gate |

## Verificação pendente

Implementador deve provar cadastro/login/logout/expiração, isolamento em todas as rotas, intervalos inválidos, LIKE literal, limites monetários, paginação/desempate, totais e arquivos reais em PostgreSQL. QA/Neo avaliam evidência independentemente; este HLD não aprova a própria solução. Comandos e alcance ficam em `docs/verificacao.md`, sem logs duplicados aqui.
