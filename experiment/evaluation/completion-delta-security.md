Ficha: tarefa=benchmark-recovery agente=neo modelo=gpt-6.1-sol (adaptador declarado; runtime não inspecionado) esforço=high skill=security-audit,contexto-tarefa,verificar-antes-de-concluir,humanizer.

# Revisão do complemento documental e visual

Chamada conferida: tarefa, aceite e escopo presentes; revisão independente de sanitização e proveniência dentro do papel. Observação A0 em 12/11/2026, HEAD `c2703749ec119e77f439d87cbfed38d6ffc1cadf`. Este é um novo bloco documental, sem reiniciar as revisões anteriores. Somente este relatório foi escrito. Não foram lidos arquivos da CI de dependências em implementação, código de aplicação, testes privados, conversas, downloads ou marcadores privados. Sem browser, scanner externo, container, A1, alteração de ambiente, commit ou push. Memória indisponível conforme quadro.

**CONCLUSÃO:** nenhum achado substanciado de exposição ou inconsistência no delta examinado. Os doze arquivos abaixo podem integrar a publicação com os limites preservados. Isso não aprova globalmente segurança, CI, pentest, operação de produção ou promoção.

## Escopo e sanitização

Foram lidos integralmente `c1-ui-completion.md`, `operations-completion-audit.md` e `reports/c1-resumo-metricas.md`, além do diff de `qa-completion-audit.md`. Os três primeiros caminhos de avaliação são relativos a experiment/evaluation. As seis imagens PNG em experiment/evaluation/ui-c1 foram abertas individualmente: desktop-filtered, mobile-360-filtered, mobile-320, mobile-320-actions, mobile-320-final e logout-320.

Foram conferidos também os acréscimos de README.md e reports/comparison.md: links para o resumo e novos pareceres, com afirmações limitadas à jornada observada e à operação sintética. A cópia persistente do resumo indicada pelo Oráculo foi comparada somente por bytes e coincide com a versão revisada; não introduz dados adicionais ou uma nova execução.

**FATO:** os quatro textos são regulares UTF-8, sem NUL ou controles bidirecionais. Busca auxiliar por caminhos pessoais e formatos comuns de credencial retornou zero correspondências. Os textos preservam apenas metadados técnicos e resultados sintéticos; não publicam credenciais, conversas, corpos HTTP ou arquivos privados. Busca por padrões não é detector universal de segredos e não substitui a guarda completa de publicação.

**FATO:** as seis capturas mostram a aplicação, conta e transações de demonstração. Não foram observados tokens, senhas, conversas, caminhos pessoais ou dados financeiros reais. O e-mail visível no logout usa o domínio reservado `example.test`; o campo de senha está vazio. Os PNGs contêm somente IHDR, IDAT e IEND, sem chunks textuais ou EXIF. Essa inspeção cobre pixels e estrutura dos arquivos publicados; não autentica a execução histórica do navegador ou o descarte de recursos.

As dimensões são 1280×1017 no desktop; 383×1776 na captura nominal 360; 391×1861 em mobile-320 e mobile-320-actions; 391×1770 em mobile-320-final; e 320×919 em logout-320. O relatório distingue viewport de largura capturada de página inteira, conserva o overflow e não usa screenshots como prova de ausência de conteúdo fora da janela.

## Composição e proveniência do resumo C1

**FATO:** a soma independente dos eventos com scenario=C1 em `reports/token-events.jsonl` reproduz 954 respostas, 95.499.973 tokens de entrada, 304.539 de saída, 93.940.864 de leitura de cache, zero escrita de cache observada e 118.295 de raciocínio. As duas linhas por modelo, sete fases não vazias e dez agentes do resumo reproduzem a repartição desses mesmos eventos; os nomes dos agentes apenas omitem o prefixo técnico `/root/`.

As referências API por modelo e por agente coincidem com a dimensão C1 correspondente de `cost-estimates.json`; cada repartição totaliza USD 2,03292154. Não foram somadas dimensões sobrepostas. O percentual de cache 98,37% e os 27,93% de saída em planejamento mais revisão são compatíveis com os contadores publicados. A classificação de atividade permanece distinta de fase: 42,6% da saída sem atividade nativa identificada não é declarada como código entregue.

**LIMITE:** essa conferência verifica composição a partir do snapshot publicado, não reexecuta coleta nativa, deduplicação ou algoritmo tarifário por resposta. Não autentica históricos privados nem observa faturamento. O resumo conserva timestamp do snapshot, modelos mistos conforme A-003, perdas desconhecidas, overhead separado, cobrança real/tempo ativo indisponíveis e intervalo entre respostas sem interpretá-lo como duração de trabalho. Entrada/cache e saída/raciocínio permanecem relações de subconjunto.

Os 20/20 casos HTTP são separados de testes backend/frontend e ações UI. A afirmação de reexecução de 12/11 dos testes de componentes permanece atribuída ao Oráculo; este revisor não acessou logs de build nem reexecutou suítes. A nova jornada UI é posterior ao intervalo C1 do snapshot e não foi incorporada retroativamente aos seus 954 eventos.

## Alcance das novas conclusões

**FATO:** o delta QA altera somente o critério de interface C1 e sua pendência, remetendo à jornada declarada por Patrick Jane. O complemento distingue ações reais pela tela de leitura de DOM, registra tentativas falhas da automação, vídeo não executado e limites de PDF. Não transforma assinatura PDF em comprovação de conteúdo ou aprovação integral de exportação. O overflow em 320 e o alcance observado em 1280/360 continuam explícitos.

**FATO:** os registros publicados de UI e operação concordam em projeto `benchmark-c1-ui-3397336c`, commit `13f775b94ab5731a4d6ae7b93aebc55513e1c2a8` e cleanup concluído às `2026-11-12T11:46:56.692285Z`. QA e Jarvis declaram ter conferido o marcador privado; Neo não o leu nesta revisão e não inspecionou o daemon Docker. A consistência entre relatos não é prova independente de todos os recursos removidos.

O parecer operacional mantém restore histórico e tentativa C4 posterior falha separados; não atribui restauração nova ao runtime corrigido. Não alega RPO/RTO, recuperação de desastre, capacidade, ausência de recursos residuais ou causa de espera npm não observados. As pendências de scanner/triagem, A1 protegido e CI completa continuam explícitas no resumo e nos pareceres. Nenhuma dessas pendências foi dispensada por este bloco.

Snapshot dos doze arquivos anteriores a este relatório: SHA-256 `42189b97c34b812b4f17b3a8704d74d2cc0da17c21d0f48cf95045d8b552b2ab`, sobre caminhos relativos em ordem lexicográfica concatenados com NUL, SHA-256 hexadecimal do conteúdo e LF. O hash inclui QA, README e comparison completos atuais, embora a revisão de conteúdo desses arquivos se restrinja ao diff. Alteração posterior exige conferir apenas o delta afetado. `git diff --check` do delta rastreado retornou zero; os arquivos novos foram conferidos separadamente. A revisão de prosa com humanizer preservou números, hashes e limites.
