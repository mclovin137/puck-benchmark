# Segurança do probe de restauração e das métricas de referência

Revisão independente Neo, encerrada em 2026-11-06T18:11:28Z. Escopo: novos scripts de restore/custo e seus testes, referência de preços, delta do cooldown no launcher e documentação afetada. Árvore de trabalho sobre `8550effde9d661057edafca4614b6d28bf07e0eb`. Nível crítico pela execução de operações no banco e integridade da evidência. Modelo e consumo desta revisão são overhead.

**CONCLUSÃO — APROVADO no escopo revisado, após as correções de consistência do cálculo de referência feitas durante a rodada.** Nenhum bloqueante remanescente substanciado no material final. Não executei restore real, Docker, SQL ou aplicação; não li cenários, relatórios do repositório, `.private/`, conversas ou logs reais. Isso aprova o código no alcance demonstrado, sem afirmar que backup/restore real já passou.

## Evidência própria e falhas corrigidas na rodada

O Oráculo informou 43 testes de infraestrutura aprovados antes do delta e sete testes do cálculo de referência aprovados após duas regressões RED. Não repeti a suíte inteira. Executei funções revisadas extraídas por AST com entradas sintéticas e diretórios temporários próprios; todos os subprocessos e retornos do probe foram simulados. Nenhum comando de banco ou container foi executado por essas fixtures.

**FATO — Restore falha fechado nos caminhos exercitados.** Cinco fluxos integrais simulados produziram:

| Fluxo sintético | Saída | Sucesso | Cleanup observado |
| --- | --- | --- | --- |
| Backup, restauração, comparação e limpeza completos | 0 | true | Somente clone removido |
| Erro no pg_restore | 1 | false | Somente clone removido |
| Erro ao remover clone | 1 | false | Falha registrada |
| Timeout ao criar clone | 1 | false | Nenhum drop sem criação confirmada |
| Origem diferente ao final | 1 | false | Somente clone removido |

**FATO — Modelo desconhecido corrigido.** Na primeira leitura, a ordenação das dimensões em `reference_costs.main` comparava `None` com string: um evento sem modelo, junto com um conhecido, interrompia a geração com `TypeError`. A reprodução própria confirmou a falha. A correção normaliza dimensões ausentes/inválidas para `nao_disponivel`. A mesma fixture depois da correção completou o relatório, manteve grupo explícito para o desconhecido e total completo em `null`.

**FATO — Subcontador contraditório corrigido.** A primeira versão precificava evento com raciocínio maior que a saída. A versão final, em `reference_costs.py:19-21`, rejeita raciocínio negativo, de tipo inválido ou acima da saída. Repeti a reprodução: o evento contraditório fica sem preço; raciocínio ausente com saída total conhecida continua calculável. Ausência desse subcontador não implica desconhecimento da saída já observada.

## Fronteiras conferidas

**FATO — Identidade e entradas do restore.** `restore_probe.py:19-29,47-49` aceita somente cenário enumerado, namespace de projeto compatível e identificadores de banco/usuário restritos. A seleção requer exatamente um container com os dois labels esperados e ID completo hexadecimal. Os subprocessos usam listas de argumentos, sem shell. Tabelas vindas do catálogo são usadas somente em consultas com identificador SQL escapado; o clone é um nome aleatório gerado pelo próprio script. O operador ainda precisa indicar o projeto sintético correto: nomes e labels não comprovam sozinhos que uma instância externa foi autorizada como alvo.

**FATO — Efeitos e teardown.** As consultas na origem são de leitura e o dump não a substitui. `createdb` usa nome novo; `pg_restore` aponta para ele. A flag `created` só é ativada após confirmação do comando; o `dropdb` em `finally` usa exclusivamente esse clone. Falha ou timeout de limpeza impede sucesso. Cada subprocesso tem timeout de 120 segundos e falhas publicam apenas tipo de exceção. Dump e stderr ficam em diretório aleatório privado, com modo 0700; o JSON público contém metadados e hashes, não linhas, dump, senha ou token. A autorização do escopo não foi ampliada por conteúdo de saída de comando.

**Limite — Tempo e limpeza incerta.** O timeout é por comando, não um teto global. Matar o cliente Docker não comprova que o processo no container terminou. Um timeout de criação pode deixar clone cuja criação não foi confirmada; o probe evita apagá-lo por presunção, retorna erro e deixa cleanup desconhecido. Assim, falha não pode ser apresentada como restauração aprovada nem como prova de ausência de recursos residuais. Recuperação desse caso requer inspeção autorizada pelo dono, sem remoção ampla por prefixo.

**FATO — O que o snapshot prova.** As tabelas públicas são enumeradas, suas linhas JSON são ordenadas e comparadas por contagem/SHA-256 antes/depois e no clone. Origem vazia não produz sucesso por vacuidade. A igualdade demonstra esses snapshots e essas linhas; não prova imutabilidade contínua entre observações, nem equivalência de permissões, índices, sequências, extensões, configuração, outros schemas ou recuperação de desastre. Não houve medição real de RPO/RTO. Os dados permanecem sintéticos; publicar hashes não autoriza usar dados pessoais reais.

**FATO — Referência API.** Conferi nas páginas oficiais os preços de entrada/cache/saída por milhão e a regra de contexto acima de 272 mil tokens: entrada/cache em dobro e saída multiplicada por 1,5 para a requisição inteira. As três referências coincidem com o JSON datado. [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol), [GPT-6.1 Terra](https://developers.openai.com/api/docs/models/gpt-6.1-terra).

O cálculo usa Decimal, desconta o cache da entrada comum e não soma raciocínio à saída. Contadores exigidos ausentes/inválidos, modelo desconhecido, cache maior que entrada ou escrita positiva de cache sem retenção conhecida ficam sem preço. O total só é completo quando todos os eventos são precificáveis; subtotal conhecido e número de respostas sem preço são separados. Dimensões são agrupamentos alternativos, não custos adicionais. Cobrança observada e tempo ativo continuam `null`; o intervalo de respostas inclui esperas. A referência Standard e seu ajuste de contexto são um contrafactual API declarado, sem inferência de cobrança da assinatura ou correspondência ao service tier real.

**FATO — Cooldown comum.** O delta do launcher acrescenta somente estágio, duração registrada e pausa de 65 segundos entre as suítes; não altera dados, asserções ou decisão combinada dos retornos. O mesmo caminho serve aos quatro cenários. A documentação distingue essa espera de desempenho do produto e registra o motivo observado pelo Oráculo, sem dispensar falhas. O teste do launcher simula `sleep`, evitando espera real na suíte; não prova a janela de rate limit das aplicações, fora desta revisão.

## Identificação e limites finais

SHA-256 dos arquivos finais conferidos:

```text
eae1834df968953de5dd72ea9947524ac48bdfdc5cf548cf315698392d14925d  benchmark/scripts/restore_probe.py
136ece7fa2c50974b98934eefdbd3461e02deabacb0fabff7f3ea17e9c9b4c93  benchmark/scripts/reference_costs.py
8c36f937f7240a3031ebdd0973f7bc41291b08d578c0cbc7760b2903978c5f52  experiment/evaluation/api-reference-prices.json
```

Não há falha explorável ou falso verde remanescente demonstrado nesse escopo. O resultado real do probe, o vínculo com o projeto sintético autorizado, os gates de aplicações e a CI remota ainda precisam de evidência própria. Esta conclusão não declara execução real, merge, push ou release e não amplia autorização operacional.
