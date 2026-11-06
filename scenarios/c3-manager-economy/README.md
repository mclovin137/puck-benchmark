# C3 — gerenciador econômico

Implementação independente da [especificação](../../experiment/specification.md), contrato REST em [protocolo](../../experiment/protocol.md). Puck fixado em `c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a`. Conforme A-003, modelo principal e gates: gpt-6.1-terra medium; Neo high. O modelo econômico originalmente planejado estava indisponível. Um cenário, sem réplica; não inferir superioridade estatística.

## Executar

Requer Docker Compose com acesso às imagens e dependências. No diretório deste cenário:

```sh
python3 -c 'import secrets; open(".env","w").write("DATABASE_PASSWORD="+secrets.token_urlsafe(32)+"\n")'
docker compose up -d --build
```

Interface: http://127.0.0.1:18213; API: http://127.0.0.1:18083/api; PostgreSQL local: 15433. O arquivo `.env` é ignorado e deve ser mantido privado. O banco persiste no volume `puck-c3_c3-data`; `docker compose stop` encerra os serviços sem apagar dados. A porta inicialmente sugerida 18203 estava ocupada e foi substituída por 18213.

## Estado e evidências

Candidato implementado; QA independente aprovou o escopo testado e Neo registrou parecer estático. CI remota e pentest ainda pendentes; não é uma entrega aprovada. As provas e limitações estão em [verificação](docs/verificacao.md) e [evidências](docs/evidences/registro.md). Senhas são transformadas em SHA-256 e depois BCrypt; tokens aleatórios têm apenas seu hash SHA-256 armazenado, expiram em 12 horas e são removidos no logout. O token fica apenas em memória no navegador. O banco é a única fonte das movimentações; valores são `BigDecimal` e saem como texto.

A consulta atual carrega em memória as movimentações do usuário antes de filtrar e paginar; o custo cresce com o volume e deve ser endereçado antes de uso com grandes bases. Exportações também são montadas em memória. A solução não inclui limitação de tentativas de login nem recuperação de senha. A revisão independente deve avaliar os riscos pertinentes.
