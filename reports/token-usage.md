# Uso de tokens por atividade

Snapshot: 2026-11-13T02:19:47.330840+00:00.

Entrada inclui cache; saída inclui raciocínio. Não somar esses subconjuntos novamente. Categorias indicam associação por resposta, não a causa de cada token de contexto. Fases declaradas são uma dimensão separada da atividade detectada.

As seis categorias solicitadas aparecem primeiro como fases explicitamente marcadas. A tabela de atividade usa exclusivamente o coletor Puck sem alterações. Ele reconhece patches e algumas escritas diretas; wrappers functions.exec e scripts dinâmicos podem permanecer sem atividade observável. O complemento estático JS foi retirado após falsos positivos na revisão; registros de fase não interpretam JavaScript.

O overhead inclui coordenação, instrumentação e avaliação externas; não é rateado arbitrariamente entre cenários. Custos faturados, tempo ativo e atribuição causal por skill não estão disponíveis neste estágio.

## overhead

| Fase declarada | Respostas | Entrada | Saída |
| --- | ---: | ---: | ---: |
| Código | 264 | 57941140 | 294464 |
| Documentação | 152 | 24222000 | 73738 |
| Testes | 599 | 98699306 | 391945 |
| Planejamento | 45 | 7460764 | 46569 |
| Revisão | 54 | 11775564 | 32442 |
| Busca | 0 | n/d | n/d |
| Configuração | 0 | n/d | n/d |
| Mista | 0 | n/d | n/d |
| Não disponível | 956 | 105244388 | 513808 |

| Atividade nativa observada | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 54 | 9244794 | 115140 | 8.51 |
| Documentação | 71 | 10447643 | 107480 | 7.94 |
| Testes | 615 | 100090985 | 411384 | 30.41 |
| Planejamento | 37 | 6109505 | 32241 | 2.38 |
| Revisão | 45 | 9801730 | 18587 | 1.37 |
| Busca | 0 | n/d | n/d | n/d |
| Configuração | 4 | 562939 | 7266 | 0.54 |
| Mista | 18 | 2593789 | 30898 | 2.28 |
| Não disponível | 1226 | 166491777 | 629970 | 46.56 |

## C1

| Fase declarada | Respostas | Entrada | Saída |
| --- | ---: | ---: | ---: |
| Código | 89 | 5513560 | 43514 |
| Documentação | 278 | 36829342 | 81362 |
| Testes | 221 | 25568267 | 69241 |
| Planejamento | 12 | 389784 | 4309 |
| Revisão | 203 | 16297921 | 80745 |
| Busca | 122 | 9853651 | 15682 |
| Configuração | 0 | n/d | n/d |
| Mista | 0 | n/d | n/d |
| Não disponível | 29 | 1047448 | 9686 |

| Atividade nativa observada | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 1 | 54624 | 823 | 0.27 |
| Documentação | 3 | 263300 | 8734 | 2.87 |
| Testes | 221 | 25568267 | 69241 | 22.74 |
| Planejamento | 12 | 389784 | 4309 | 1.41 |
| Revisão | 201 | 16099325 | 75144 | 24.67 |
| Busca | 122 | 9853651 | 15682 | 5.15 |
| Configuração | 4 | 545788 | 865 | 0.28 |
| Mista | 0 | n/d | n/d | n/d |
| Não disponível | 390 | 42725234 | 129741 | 42.6 |

## C2

| Fase declarada | Respostas | Entrada | Saída |
| --- | ---: | ---: | ---: |
| Código | 55 | 4293086 | 52076 |
| Documentação | 66 | 7611689 | 26949 |
| Testes | 204 | 24261465 | 99764 |
| Planejamento | 24 | 931599 | 10644 |
| Revisão | 58 | 5531505 | 28514 |
| Busca | 11 | 468831 | 5283 |
| Configuração | 0 | n/d | n/d |
| Mista | 0 | n/d | n/d |
| Não disponível | 14 | 352439 | 2188 |

| Atividade nativa observada | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 1 | 99148 | 2072 | 0.92 |
| Documentação | 6 | 539483 | 14247 | 6.32 |
| Testes | 201 | 23959848 | 91858 | 40.75 |
| Planejamento | 23 | 892365 | 7264 | 3.22 |
| Revisão | 56 | 5332873 | 25553 | 11.34 |
| Busca | 10 | 422727 | 3733 | 1.66 |
| Configuração | 1 | 46104 | 1550 | 0.69 |
| Mista | 0 | n/d | n/d | n/d |
| Não disponível | 134 | 12158066 | 79141 | 35.11 |

## C3

| Fase declarada | Respostas | Entrada | Saída |
| --- | ---: | ---: | ---: |
| Código | 56 | 5930522 | 23025 |
| Documentação | 48 | 4639512 | 9615 |
| Testes | 98 | 6749358 | 29210 |
| Planejamento | 5 | 151016 | 600 |
| Revisão | 64 | 4579705 | 15979 |
| Busca | 0 | n/d | n/d |
| Configuração | 0 | n/d | n/d |
| Mista | 0 | n/d | n/d |
| Não disponível | 4 | 88088 | 543 |

| Atividade nativa observada | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 0 | n/d | n/d | n/d |
| Documentação | 0 | n/d | n/d | n/d |
| Testes | 98 | 6749358 | 29210 | 36.99 |
| Planejamento | 5 | 151016 | 600 | 0.76 |
| Revisão | 64 | 4579705 | 15979 | 20.23 |
| Busca | 0 | n/d | n/d | n/d |
| Configuração | 0 | n/d | n/d | n/d |
| Mista | 0 | n/d | n/d | n/d |
| Não disponível | 108 | 10658122 | 33183 | 42.02 |

## C4

| Fase declarada | Respostas | Entrada | Saída |
| --- | ---: | ---: | ---: |
| Código | 12 | 643043 | 24412 |
| Documentação | 0 | n/d | n/d |
| Testes | 141 | 19144410 | 62941 |
| Planejamento | 4 | 183656 | 5623 |
| Revisão | 24 | 1924517 | 14706 |
| Busca | 0 | n/d | n/d |
| Configuração | 0 | n/d | n/d |
| Mista | 0 | n/d | n/d |
| Não disponível | 5 | 121905 | 1153 |

| Atividade nativa observada | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 1 | 55742 | 3670 | 3.37 |
| Documentação | 5 | 397268 | 11797 | 10.84 |
| Testes | 139 | 19012942 | 58427 | 53.68 |
| Planejamento | 4 | 183656 | 5623 | 5.17 |
| Revisão | 21 | 1658717 | 7423 | 6.82 |
| Busca | 0 | n/d | n/d | n/d |
| Configuração | 0 | n/d | n/d | n/d |
| Mista | 1 | 49614 | 3428 | 3.15 |
| Não disponível | 15 | 659592 | 18467 | 16.97 |
