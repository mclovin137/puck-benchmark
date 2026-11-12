Ficha: tarefa=benchmark-recovery agente=jarvis modelo=gpt-6.1-sol (adaptador declarado; runtime não inspecionado) esforço=medium skill=contexto-tarefa,performance-audit,verificar-antes-de-concluir,humanizer.

# Auditoria operacional de conclusão

Chamada conferida: tarefa, aceite e escopo presentes; operação efêmera e recuperação dentro do papel. Revisão documental A0 em 12/11/2026 sobre `c2703749ec119e77f439d87cbfed38d6ffc1cadf`. Somente este relatório foi criado por Jarvis. Não executei containers, rede, SQL, carga, aplicação, avaliador privado ou pentest. Não li código dos cenários. A memória externa estava indisponível conforme o quadro; usei Git e arquivos locais.

**Resultado: evidência operacional suficiente para startup, avaliação comum e limpeza dos quatro projetos sintéticos, com restore histórico aprovado nos quatro. Nenhum bloqueio operacional concreto adicional foi substanciado nesse alcance.** A conclusão reutiliza resultados do Oráculo; não é uma reexecução independente nem autorização de produção ou aprovação global de versão.

## Identidade, execução e limpeza

Os JSONs `system-c*.json` registram `source_clean=true`, `cleanup_success=true`, binds em loopback e projetos separados. Os resultados atuais `c1`–`c4-acceptance.json` e `c1`–`c4-boundaries.json` declaram 16 e quatro métodos aprovados por cenário, sem falhas ou erros.

| Cenário | Projeto Compose | Janela UTC | Commit executado |
|---|---|---|---|
| C1 | `benchmark-eval-c1-e9b1c956` | 11/11 19:02:35–19:04:04 | `1f552f1d5cbf014d3ed1da644cdc11d4e6262e3d` |
| C2 | `benchmark-eval-c2-81b05fa9` | 11/11 19:04:25–19:05:49 | `1f552f1d5cbf014d3ed1da644cdc11d4e6262e3d` |
| C3 | `benchmark-eval-c3-8738cb0d` | 11/11 19:05:49–19:12:40 | `1f552f1d5cbf014d3ed1da644cdc11d4e6262e3d` |
| C4 | `benchmark-eval-c4-d8591eda` | 12/11 11:37:09–11:38:35 | `13f775b94ab5731a4d6ae7b93aebc55513e1c2a8` |

Comparei objetos Git de `backend`, `frontend` e `compose.yaml`, sem abrir seus conteúdos: C1–C3 são idênticos entre os dois commits e o HEAD auditado. Em C4, frontend e Compose são idênticos; o backend mudou. A lista de caminhos alterados contém dois fontes de autenticação e um teste, sem mudança de migrações ou manifests nesse intervalo. Entre `13f775b` e o HEAD, `git diff --quiet -- scenarios` retornou zero. Isso sustenta a reutilização de C1–C3, sem atribuir sua execução ao commit novo nem declarar que dependências externas continuam imutáveis.

A execução C4 inicial de 11/11, projeto `benchmark-eval-c4-ca46f306`, terminou com HTTP reprovado e limpeza aprovada. `system-c4-initial.json` preserva esse fato. A nova execução completa substitui o estado corrente de HTTP; não apaga a tentativa anterior.

Conferi também o pequeno marcador privado autorizado da UI C1: projeto `benchmark-c1-ui-3397336c`, commit `13f775b`, início `2026-11-12T11:42:10.723390Z`, término `2026-11-12T11:46:56.692285Z`, `cleanup_success=true`. A identidade coincide com `c1-ui-completion.md`. Não li os demais arquivos privados nem inspecionei recursos Docker após a limpeza. As flags comprovam o alcance do registro do executor, sem inventário independente do daemon.

## Restore sintético e tentativa posterior

Parse e comparação automatizada dos quatro `restore-c*.json` confirmaram projeto igual ao runtime correspondente e início/fim dentro de sua janela; para C4 o vínculo é com `system-c4-initial.json`. Todos registram `success=true`, `source_unchanged=true`, `restored_matches=true` e `cleanup_success=true`. Cada snapshot contém quatro tabelas não vazias, com contagens e hashes, incluindo 29 registros financeiros. Os resultados não publicam linhas ou dumps.

| Restore de 11/11 | Janela UTC | Projeto vinculado |
|---|---|---|
| C1 | 19:03:37–19:03:39 | `benchmark-eval-c1-e9b1c956` |
| C2 | 19:04:41–19:04:43 | `benchmark-eval-c2-81b05fa9` |
| C3 | 19:11:32–19:11:34 | `benchmark-eval-c3-8738cb0d` |
| C4 | 19:12:56–19:12:58 | `benchmark-eval-c4-ca46f306` |

`restore-c4-resume-unavailable.json` preserva uma tentativa distinta: início `2026-11-12T11:38:36.560730Z`, depois do término/cleanup do runtime C4 às `11:38:35.106780Z`; projeto `benchmark-eval-c4-d8591eda`, `stage=identity`, `success=false`, `ValueError`, `cleanup_success=null`. É coerente com alvo já desmontado, conforme informado pelo executor; os metadados sozinhos não demonstram toda a causa interna. Não comprova novo restore, perda de dados ou clone residual. Também não deve ser convertido em sucesso ou substituir o restore histórico aprovado.

Não há restore aprovado executado no novo runtime C4. O histórico conserva sua validade para o banco sintético anterior; a ausência de mudança de migrações/manifests sustenta sua reutilização limitada, sem provar o comportamento do backend novo após restauração. Se for exigida uma prova vinculada à execução de 12/11, o dono deverá executar o probe enquanto esse projeto sintético estiver ativo e preservar as duas tentativas existentes. Isso é condição para ampliar a afirmação, não defeito demonstrado da aplicação.

## Limites e pendências reais

A revisão anterior [operations-metrics-security.md](operations-metrics-security.md) aprova o código do probe com fixtures e explicita timeout por subprocesso, ausência de teto global e possível limpeza desconhecida após timeout de criação. Não a trato como execução real. Os restores publicados fornecem a execução sintética que faltava naquela revisão; não provam permissões, índices, sequências, extensões ou outros schemas restaurados, nem continuidade integral da origem entre snapshots.

RPO, RTO, recuperação de desastre, retenção externa de backups, rollback de produção, vazão, p95/p99, capacidade, concorrência sob carga e custo operacional não foram medidos. Não há orçamento operacional de produção estabelecido neste escopo. Durações de startup incluem build e cooldown comum de 65 segundos; não são latências de requisição nem RTO. A espera `npm ci` C3 de 320,2 segundos terminou naturalmente conforme diagnóstico no quadro; a causa não foi determinada e não sustenta achado de regressão.

As subnets registradas são evidência histórica, não reserva permanente. Nova execução exige conferir sobreposição no momento e limpar somente recursos comprovadamente próprios, como descrito em [runtime-recovery.md](runtime-recovery.md) e `docs/verificacao.md`. Não houve inspeção atual de ocupação ou recursos residuais nesta auditoria.

O estado C4 reprovado em `runtime-recovery.md` e `runtime-evidence-security.md` descreve o snapshot anterior; o estado corrente está nos JSONs de 12/11 e neste complemento. Esses relatórios históricos não aprovam nem reprovam retroativamente o novo runtime. A-001/A-002 continuam sendo baseline comum, A-003 mantém a alteração de disponibilidade/modelos e as limitações de comparação. O trabalho desta auditoria é overhead de retomada, sem reatribuição aos autores e sem compra.

Pendências de CI, segurança, pentest A1, mídia e promoção devem ser decididas pelos respectivos donos. Startup, HTTP e restore sintético não as dispensam. Nenhum novo gate de carga ou operação de produção foi criado por esta auditoria.
