# Uso de tokens por atividade

Snapshot: 2026-11-06T02:05:35.415118+00:00.

Entrada inclui cache; saída inclui raciocínio. Não somar esses subconjuntos novamente. Categorias indicam associação por resposta, não a causa de cada token de contexto. Fases declaradas são uma dimensão separada da atividade detectada.

O coletor Puck reconhece escritas diretas e patches. O complemento reconhece chamadas literais tools.exec_command no wrapper functions.exec, ignorando comentários, strings e comandos dinâmicos sem executar o conteúdo; scripts Python dinâmicos e comandos construídos em runtime podem permanecer sem classificação. Revisão, planejamento e busca sem escrita dependem da fase explícita.

O overhead inclui coordenação, instrumentação e avaliação externas; não é rateado arbitrariamente entre cenários. Custos faturados, tempo ativo e atribuição causal por skill não estão disponíveis neste estágio.

## overhead

| Atividade | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 9 | 1163853 | 15730 | 19.17 |
| Documentação | 4 | 396220 | 9089 | 11.08 |
| Testes | 27 | 3777450 | 17930 | 21.85 |
| Planejamento | 16 | 1671539 | 4066 | 4.96 |
| Revisão | 0 | n/d | n/d | n/d |
| Busca | 0 | n/d | n/d | n/d |
| Configuração | 1 | 154883 | 1331 | 1.62 |
| Mista | 6 | 765519 | 9189 | 11.2 |
| Não disponível | 48 | 3725210 | 24714 | 30.12 |

## C1

| Atividade | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 7 | 393489 | 14017 | 23.03 |
| Documentação | 5 | 316521 | 6403 | 10.52 |
| Testes | 60 | 6176836 | 17575 | 28.88 |
| Planejamento | 11 | 360254 | 2135 | 3.51 |
| Revisão | 0 | n/d | n/d | n/d |
| Busca | 56 | 3906678 | 5550 | 9.12 |
| Configuração | 3 | 183008 | 2211 | 3.63 |
| Mista | 2 | 149036 | 1290 | 2.12 |
| Não disponível | 64 | 3374371 | 11676 | 19.19 |

## C2

| Atividade | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 0 | n/d | n/d | n/d |
| Documentação | 1 | 42965 | 947 | 46.24 |
| Testes | 0 | n/d | n/d | n/d |
| Planejamento | 5 | 207882 | 601 | 29.35 |
| Revisão | 0 | n/d | n/d | n/d |
| Busca | 0 | n/d | n/d | n/d |
| Configuração | 0 | n/d | n/d | n/d |
| Mista | 0 | n/d | n/d | n/d |
| Não disponível | 4 | 116804 | 500 | 24.41 |

## C3

| Atividade | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 0 | n/d | n/d | n/d |
| Documentação | 0 | n/d | n/d | n/d |
| Testes | 0 | n/d | n/d | n/d |
| Planejamento | 0 | n/d | n/d | n/d |
| Revisão | 0 | n/d | n/d | n/d |
| Busca | 0 | n/d | n/d | n/d |
| Configuração | 0 | n/d | n/d | n/d |
| Mista | 0 | n/d | n/d | n/d |
| Não disponível | 0 | n/d | n/d | n/d |

## C4

| Atividade | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 0 | n/d | n/d | n/d |
| Documentação | 0 | n/d | n/d | n/d |
| Testes | 0 | n/d | n/d | n/d |
| Planejamento | 0 | n/d | n/d | n/d |
| Revisão | 0 | n/d | n/d | n/d |
| Busca | 0 | n/d | n/d | n/d |
| Configuração | 0 | n/d | n/d | n/d |
| Mista | 0 | n/d | n/d | n/d |
| Não disponível | 0 | n/d | n/d | n/d |
