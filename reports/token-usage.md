# Uso de tokens por atividade

Snapshot: 2026-11-06T02:00:58.839543+00:00.

Entrada inclui cache; saída inclui raciocínio. Não somar esses subconjuntos novamente. Categorias indicam associação por resposta, não a causa de cada token de contexto. Fases declaradas são uma dimensão separada da atividade detectada.

O coletor Puck reconhece escritas diretas e patches. O complemento reconhece comandos literais no wrapper functions.exec sem executar o conteúdo; scripts Python dinâmicos e comandos construídos em runtime podem permanecer sem classificação. Revisão, planejamento e busca sem escrita dependem da fase explícita.

O overhead inclui coordenação, instrumentação e avaliação externas; não é rateado arbitrariamente entre cenários. Custos faturados, tempo ativo e atribuição causal por skill não estão disponíveis neste estágio.

## overhead

| Atividade | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 7 | 836509 | 13135 | 19.81 |
| Documentação | 3 | 265705 | 7005 | 10.57 |
| Testes | 21 | 2801153 | 12840 | 19.37 |
| Planejamento | 16 | 1671539 | 4066 | 6.13 |
| Revisão | 0 | n/d | n/d | n/d |
| Busca | 0 | n/d | n/d | n/d |
| Configuração | 0 | n/d | n/d | n/d |
| Mista | 5 | 599106 | 7767 | 11.72 |
| Não disponível | 41 | 2868682 | 21482 | 32.4 |

## C1

| Atividade | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 7 | 393489 | 14017 | 27.07 |
| Documentação | 5 | 316521 | 6403 | 12.36 |
| Testes | 31 | 2848890 | 9441 | 18.23 |
| Planejamento | 11 | 360254 | 2135 | 4.12 |
| Revisão | 0 | n/d | n/d | n/d |
| Busca | 43 | 2940222 | 4611 | 8.9 |
| Configuração | 3 | 183008 | 2211 | 4.27 |
| Mista | 2 | 149036 | 1290 | 2.49 |
| Não disponível | 64 | 3374371 | 11676 | 22.55 |

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

