# Correção delimitada de contrato — C4

Autor: gerente C4 original, Sol medium. Escopo do quadro de continuidade: encoding do JSON de erro de autenticação e status do login com senha incorreta curta. Fonte Puck recuperada, mesmo commit c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a. Esta é correção pós-avaliação do contrato backend; não é nova implementação comparativa. Memória indisponível. Sem alteração de modelo, governança, stack ou dependências.

## Causa e delta

`Security.java`: o entrypoint escrevia mensagem com acento por `getWriter()` sem escolher charset. A resposta Tomcat usava encoding que produzia bytes inválidos em UTF-8. Agora define `StandardCharsets.UTF_8.name()` antes de obter o writer. Status401, mensagem e proteção das rotas foram preservados.

`AuthActor.java`: o DTO de login aplicava o mínimo12 do cadastro antes de verificar credenciais. Por isso uma senha incorreta curta recebia400. Foi removido somente `min=12` de `Login`; a senha continua obrigatória e limitada a128 caracteres. O cadastro mantém12–128, e-mail continua validado e o actor continua verificando a senha com o algoritmo existente.

Adicionado `AuthContractTest.java`, sem Mockito, banco ou listener de rede. Ele sobe a configuração real MVC/Security e usa um actor substituto local para isolar a fronteira HTTP. Verifica senha curta/incorreta/vazia →401, positivo de login →200, senha ausente/e-mail malformado/senha excessiva →400 e cadastro com senha curta →400. Rotas privadas, inclusive exports, são verificadas sem token e com token não autenticado, com JSON decodificado de forma estrita.

O MockHttpServletResponse assume UTF-8 para JSON e, sozinho, mascara o defeito de runtime. Por isso há uma regressão adicional que extrai o entrypoint da cadeia real e o executa sobre Response/Coyote Tomcat reais, com saída capturada em memória. O decoder UTF-8 usa REPORT; também confere401 e o texto acentuado após interpretar o JSON.

## RED e GREEN executados

| Etapa | Comando na raiz do cenário | Resultado |
|---|---|---|
| RED, produção intacta | `mvn -o -B -f backend/pom.xml -Dtest=AuthContractTest test` | exit1;5 testes,2 falhas,0 erros,0 skips: senha curta recebeu400 em vez de401; resposta Tomcat lançou MalformedInputException ao decodificar UTF-8 |
| GREEN, após delta mínimo | `mvn -o -B -f backend/pom.xml -Dtest=AuthContractTest,FinancialRulesTest test` | exit0;8 testes,0 falhas,0 erros,0 skips (5 contrato +3 financeiros) |

Antes do RED completo houve tentativas de infraestrutura, preservadas separadamente: Mockito falhou com `Could not initialize inline Byte Buddy mock maker`; o teste foi refeito sem instrumentação. A primeira preparação do objeto Tomcat não tinha Request/Connector e falhou com NullPointerException; esse setup foi completado antes de usar o resultado como RED de comportamento. O RED do teste MVC já reproduzia o400; não foi apresentado como prova do encoding.

Registros novos em `contract-repair.json`: comandos, contagens, UTC e SHA-256 dos dois arquivos de produção antes/depois e do teste final. Logs locais novos: `contract-repair-infrastructure.log`, `contract-repair-mvc-red.log`, `contract-repair-tomcat-setup.log`, `contract-repair-red.log` e `contract-repair-green.log`. Evidências históricas e hashes anteriores não foram substituídos.

## Alcance e pendências

A compilação e os testes usaram Java25 com release21, Maven offline e dependências já disponíveis. O actor substituto não prova persistência, hash, expiração ou sucesso de autenticação contra PostgreSQL; esses caminhos não foram alterados. A prova Tomcat usa classes reais, mas não equivale a subir o Compose ou receber bytes por TCP.

A revalidação Compose/Testcontainers está bloqueada neste ambiente. `docker version --format '{{.Server.Version}}'` retornou exit1: `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock`. Nenhuma permissão ou hook foi contornado. O Oráculo deve reconstruir o candidato e reexecutar o aceite comum em Java21. CI e revisão independente desta correção: não executadas. Sem delegação, Git, commit, push, merge, compras ou API key.
