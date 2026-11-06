# Segurança — delta login-status

**APROVADO no escopo do ajuste e das regressões examinadas**, em 2026-11-06. Nenhum bypass ou alteração indevida de política de cadastro foi substanciado. Revisão independente Neo limitada a `AuthDtos.java` e à regressão pertinente em `ApiIntegrationTest.java`, com leitura do caminho de autenticação para conferir o efeito. O parecer amplo em `seguranca.md` permanece histórico; não houve terceira revisão ampla, teste ofensivo ou uso de Git.

**FATO — causa e correção:** o Login usava mínimo de 12 caracteres no DTO e devolvia 400 antes de verificar a credencial. O delta remove somente esse mínimo do Login, preservando `@NotNull` e máximo de 128. Register mantém `@NotNull` e 12–128. `AuthREST.login` continua validando o DTO; `AuthActor.login` compara a senha com o hash armazenado ou dummy e lança Unauthorized se usuário inexistente ou senha incorreta. Só depois dessas condições cria a sessão e retorna token. Portanto, permitir que senha curta alcance a comparação não satisfaz a condição de autenticação nem permite cadastrar senha curta.

**FATO — evidência:** `login-status.json` registra a reprodução HTTP anterior: senha curta incorreta retornou 400 em vez de 401, enquanto os oito demais controles passaram. A nova regressão exige 401 para essa credencial, 400 no cadastro com senha curta, cadastro e login legítimos com 128 caracteres e rejeição de 129 no cadastro e login. O XML Surefire atual foi conferido: quatro testes, zero falhas, erros ou skips, correspondendo a encoding 401, status/bordas da senha, credenciais/revogação e expiração. Execução do implementador em PostgreSQL 17.11 Testcontainers; Neo conferiu fonte e resultado, sem repetir a suíte. A evidência registra RED e uma tentativa de correção.

Identidade das fontes na revisão:

| Arquivo | SHA-256 |
| --- | --- |
| `auth/dto/AuthDtos.java` | `be66d0d39f55d02cf9a7fd180ed5c00258b856929dc5f0bc680f60bb76dcb7a1` |
| `ApiIntegrationTest.java` | `7f1939eb5d014c1c8b6908fdba40b0d58f7b2f47c02f637a5a3a841e684f1c36` |

**Limites:** o HTTP após rebuild ainda não integra esta evidência; a aprovação acima cobre código e regressões de integração, não a identidade do novo artefato servido. Senhas curtas agora também executam a derivação de senha; esse é o custo esperado de verificar a credencial antes de responder 401, dentro do limite de 128 caracteres. O risco de capacidade das rotas públicas já registrado no parecer amplo não foi medido ou resolvido aqui. Hashing, tokens, owner, renderização Spring e harness não foram reavaliados nem declarados alterados. Não se infere CI, pentest, merge ou release aprovado.
