# Uso de tokens por atividade

Snapshot: 2026-11-06T02:01:59.345874+00:00.

Entrada inclui cache; saída inclui raciocínio. Não somar esses subconjuntos novamente. Categorias indicam associação por resposta, não a causa de cada token de contexto. Fases declaradas são uma dimensão separada da atividade detectada.

O coletor Puck reconhece escritas diretas e patches. O complemento reconhece comandos literais no wrapper functions.exec sem executar o conteúdo; scripts Python dinâmicos e comandos construídos em runtime podem permanecer sem classificação. Revisão, planejamento e busca sem escrita dependem da fase explícita.

O overhead inclui coordenação, instrumentação e avaliação externas; não é rateado arbitrariamente entre cenários. Custos faturados, tempo ativo e atribuição causal por skill não estão disponíveis neste estágio.

## overhead

| Atividade | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 8 | 995884 | 14394 | 20.9 |
| Documentação | 3 | 265705 | 7005 | 10.17 |
| Testes | 21 | 2801153 | 12840 | 18.64 |
| Planejamento | 16 | 1671539 | 4066 | 5.9 |
| Revisão | 0 | n/d | n/d | n/d |
| Busca | 0 | n/d | n/d | n/d |
| Configuração | 1 | 154883 | 1331 | 1.93 |
| Mista | 5 | 599106 | 7767 | 11.28 |
| Não disponível | 41 | 2868682 | 21482 | 31.19 |

## C1

| Atividade | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 7 | 393489 | 14017 | 25.55 |
| Documentação | 5 | 316521 | 6403 | 11.67 |
| Testes | 35 | 3263707 | 12095 | 22.05 |
| Planejamento | 11 | 360254 | 2135 | 3.89 |
| Revisão | 0 | n/d | n/d | n/d |
| Busca | 48 | 3309075 | 5030 | 9.17 |
| Configuração | 3 | 183008 | 2211 | 4.03 |
| Mista | 2 | 149036 | 1290 | 2.35 |
| Não disponível | 64 | 3374371 | 11676 | 21.28 |

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
