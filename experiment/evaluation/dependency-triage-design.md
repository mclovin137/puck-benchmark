Ficha: tarefa=benchmark-recovery agente=yoda modelo=gpt-6.1-sol (adaptador declarado; runtime não inspecionado) esforço=medium skill=gerar-adr,contexto-tarefa,receber-revisao,verificar-antes-de-concluir,humanizer.

# Proposta de triagem do snapshot final

Status: **proposta; nenhuma decisão individual dispensada**. Categoria: contrato do gate de dependências. Dono da proposta: Yoda; revisão independente do mecanismo e das decisões individuais: Neo, pendente sobre a implementação deste desenho. Tarefa, aceite e escopo conferidos; análise de contratos dentro do papel.

## Escopo e evidências

A proposta atende somente o snapshot final deste experimento de uma execução por cenário. A avaliação do Oráculo sobre a versão anterior foi classificada como **corrigir, não bloqueante**: manutenção permanente e branch de política separada excediam essa necessidade. Foram retiradas. Qualquer alteração nos vínculos invalida a decisão e exige novo PR crítico com Neo e coordenação do Oráculo; não há renovação automática nem exceção universal.

O inventário sanitizado entregue contém nove fontes, 1.020 entradas de pacotes e oito CRITICAL: `org.springframework:spring-webmvc@6.2.19`, os dois advisories A-002 em cada C1–C4. Permanece `failed`. [A-002](../amendments/002-transitive-baseline.json) mantém o componente afetado e exige revisão Neo individual de pré-condições. Severidades do scanner e do fornecedor continuam distintas e visíveis. O [parecer Neo](dependency-gate-security.md) delimita a evidência anterior, inclusive runtime não observado em C3.

Fontes adicionais: [protocolo](../protocol.md), [configurações](../configs.yaml), [contrato](../../docs/rules.md) e [bibliotecas](../../docs/lib.md). Não houve leitura de aplicações, testes privados ou nova execução de scanner. Na conferência desta revisão, HEAD `076116b24bb98cd28b5137a0818c3d6b45acbc56`, da branch de recuperação do gate, contém workflow, script e triagem vazia; não está integrado em dev. A referência local `origin/dev` é `d7b68159391cb5374f595662be1251c1db72bc03` e não contém esses três arquivos, conforme `git ls-tree`. O script candidato recusa registros. A admissão prévia em dev ainda é possível; commit local não significa ativação ou integração. Proteções externas não foram inspecionadas nesta revisão.

## Contrato mínimo

O scanner mede as fontes candidatas. Registros, política e avaliador vêm de **um SHA exato revisado no PR crítico para dev**, conforme a emenda de execução abaixo, previamente admitido pelo fluxo existente de PR crítico, Neo e owner/Oráculo. O workflow fixa esse SHA e o informa no resultado; o candidato não escolhe a base nem fornece sua própria autorização. A confiança nas alterações do workflow continua nesses controles existentes, sem novo sistema de checks externos.

Um registro cobre exatamente um advisory em um cenário. Não aceitar wildcard, versão por faixa, duplicata ambígua ou aplicação da decisão de um cenário aos demais. Para oito achados, são necessárias oito correspondências válidas, caso as provas existam.

| Vínculo | Conteúdo mínimo |
| --- | --- |
| Identidade | Cenário/fonte, ecossistema, pacote, versão resolvida e advisory canônico exatos. Aliases somente com mapeamento explícito e verificável. |
| Fontes e configuração | Digest canônico dos caminhos/blobs do snapshot congelado que cobrem fontes, manifests/locks, recursos, build e configuração capazes de alterar pré-condições. A lista e regra de cobertura ficam na base revisada; arquivo relevante novo também invalida. |
| Dependências | Digest do grafo resolvido por fonte, com representação e algoritmo definidos. Inventário ou contagem não prova relações; se o scanner não fornecer relações, obter evidência complementar e identificar esse limite. |
| Advisory e ferramenta | Snapshot/digest dos metadados dos dois advisories, versão/digest do scanner e versão da política. Conteúdo alterado não herda a decisão. |
| Prova Neo | Conclusão independente sobre pré-condições SSE/view fragments e XsltView/catch-all no snapshot exato, com evidência por blob/artefato imutável e digest. Quando depender de runtime, vincular artefato/imagem e configuração efetiva sanitizada observados; dado não observado não serve como prova. |
| Validade | Exclusiva para esta avaliação final, identificada por snapshot e execução; emissão UTC e estado ativo/revogado. Novo snapshot, nova execução de avaliação final ou evidência/advisory alterados exigem novo PR crítico/Neo. Retries técnicos do mesmo gate não ampliam escopo. Não há prazo de renovação nem manutenção automática a definir. |

A severidade CRITICAL e o componente afetado permanecem no relatório mesmo quando uma decisão de alcance é aplicada. A divergência do fornecedor não basta para dispensar os achados: A-002 exige prova por implementação. O resultado distingue falha de execução, bloqueio por achado pendente e aprovação com decisões vinculadas; esta última não equivale a componente corrigido nem autoriza A1, promoção ou encerramento.

Ausência de prova, UNKNOWN, vínculo diferente, registro revogado, resposta inconsistente ou falha de leitura bloqueiam. Qualquer mudança nas entradas vinculadas reabre o gate, inclusive adição de arquivo relevante ou alteração do grafo/advisory. Mudança apenas em evidência documental não deve modificar o digest das aplicações; a regra de cobertura precisa explicitar essa separação sem excluir configuração operacional relevante.

## Sequência limitada ao fechamento

1. Neo examina as pré-condições do snapshot final e produz provas individuais. Materializar fontes/grafo/advisory e seus digests; o relatório resumido atual não basta para isso.
2. Admitir provas e política por tarefa documental em dev **antes de habilitar o consumo das decisões pela CI**, mantendo o scanner atual reprovado enquanto faltar suporte. Conferir gates já aplicáveis; admissão documental não é auditoria verde e não autoriza ignorar check obrigatório.
3. Admitir o avaliador com suporte ao contrato por PR crítico revisado por Neo e coordenado pelo Oráculo, sem permitir autoautorização por triagem candidata. O SHA confiável deve conter provas, política e avaliador compatíveis antes de o workflow consumidor apontar para ele. Se o avaliador ainda não existir nessa base, sua admissão precede a ativação do consumo; o PR somente documental não pode fornecer código ausente. Essa ordem pode exigir separar o PR crítico do avaliador inativo do PR que ativa o workflow; para manter apenas dois PRs totais, o primeiro teria de conter também o avaliador inativo revisado, deixando de ser estritamente documental. Não executar silenciosamente o avaliador candidato como substituição.
4. Ativar o consumo por workflow revisado, fixando o mesmo SHA admitido para avaliador/política/provas e mantendo checkout distinto das fontes candidatas. Rodar o gate do snapshot exato, registrar hashes/origem/execução e conferir correspondência antes de integrar ou usar o resultado.

Não há ciclo permanente a resolver: este desenho termina na avaliação final. Se futuramente for preciso mudar uma entrada vinculada, o resultado anterior deixa de servir; novo PR crítico/Neo ou manutenção do bloqueio, sem plataforma de admissão.

A presença do workflow na branch de recuperação não significa ativação em dev. Se a admissão documental for impedida por alguma auditoria obrigatória já reprovada, o fluxo proposto não resolve esse impedimento administrativo: manter bloqueio e devolver ao Oráculo o fato verificável. Não desativar workflow, omitir check ou declarar sucesso para viabilizar a sequência. A pergunta A1 já aberta ao dono permanece independente; nenhuma nova pergunta foi criada aqui.

## Ameaça concreta e menor controle

Se somente a triagem vier da base, um candidato pode trocar `dependency-audit.py` por um programa que retorna zero, sem validar os vínculos. O controle mínimo é executar avaliador e política do SHA revisado, com caminho separado das fontes candidatas e sem importação de módulos/configuração executável controlados por elas. O workflow e seus argumentos entram na revisão crítica Neo já prevista. Não há necessidade demonstrada de checks externos adicionais ou branch de política para fechar essa ameaça no modelo de confiança definido pelo Oráculo.

Outro caso é aceitar o digest informado pelo próprio JSON candidato: o candidato poderia declarar o digest antigo sem medir os fontes novos. O avaliador confiável precisa recalcular os vínculos das entradas efetivamente examinadas. Quando a resolução exigir executar código de build candidato, isso ocorre como entrada não confiável do scanner; não pode substituir o avaliador nem sua política. A implementação deverá demonstrar essa separação e a correspondência entre o que foi medido e o que foi avaliado.

## Verificação antes de consumir decisões

- Um controle positivo aplica uma decisão exata e mantém finding/CRITICAL visíveis; não autoriza os outros sete.
- Controles negativos para cada identidade/digest, advisory alterado, arquivo relevante novo, prova ausente, runtime necessário não observado, revogação, alias ambíguo e execução final diferente. Todos bloqueiam.
- JSON, avaliador ou configuração alterados no candidato não ampliam autorização; digest declarado pelo candidato não substitui recálculo. Base ausente, SHA diferente ou avaliador inexistente bloqueiam.
- Preservar falhas de scanner/parse, retorno inconsistente, UNKNOWN/NaN/fora de faixa e cobertura das nove fontes. Conferir que o artefato pertence ao run/SHA final; ausência ou skip não é aprovação.
- Revisão Neo do delta e CI no SHA exato. Testes e revisão da implementação deste desenho: **não executados**; esta revisão foi documental.

Custo adicional: snapshots e oito decisões individuais, extensão restrita do avaliador, sequência de PRs e nova execução comum. Registrar como intervenção de recuperação, sem atribuição arbitrária a cenários. Alternativa vigente: manter o gate bloqueado. Não há aceite de risco inventado, dispensa global ou mudança do protocolo, configurações congeladas, resultados ou controles externos.

## Emenda de execução — correção de cenário após o snapshot

A proposta inicial situava a admissão do SHA em dev antes da ativação. Uma correção de aplicação muda a árvore do cenário: o avaliador preservado exige igualdade entre a árvore real no checkout confiável, a declaração do manifest e o candidato. Uma policy isolada contendo a árvore nova, mas código antigo, seria inconsistente; integrar código com gate antigo reprovado também é recusado.

Para essa correção, o snapshot P3 conterá código/teste, política, manifest e prova do próprio PR crítico para dev, em SHA completo imutável. Neo e Oráculo precisam admitir expressamente esse SHA e seus vínculos antes da ativação; não basta o candidato declarar aprovação. O filho K3 altera apenas os dois pins do workflow para P3, com avaliador/helper/instalador idênticos à base anterior e checkouts separados/limpos. Merge em dev continua condicionado à CI real verde no head K3 e à revisão independente do delta. Não usar branch flutuante, pular gate ou alterar o avaliador para dispensar árvores divergentes.

Somente C4 muda: dois digests de fonte e o binding de sua árvore, com nova evidência nos dois registros C4; os seis registros C1–C3 permanecem íntegros. Os quatro grafos/POMs e advisories são preservados; observed_at do manifest mantém a coleta original dos grafos, enquanto source_reference_commit registra a fonte atual cujas árvores coincidem com os bindings. A resolução corrente será novamente verificada pelo consumidor real antes de integrar. O componente continua afetado, com oito CRITICAL e prazo original preservados.

Essa admissão ocorre antes da integração do snapshot em dev, por revisão explícita do commit do PR, sem reduzir as provas de código/fonte/grafo/advisory. Não é garantia de proteção remota ou autorização concedida por auto-hash. Os 16 imports de A1 continuam os da main v0.1.2; a correção não modifica os controles do dono, o protocolo funcional, a configuração congelada ou os critérios do experimento.
