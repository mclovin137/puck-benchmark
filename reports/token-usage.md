# Uso de tokens por atividade

Snapshot: 2026-11-06T02:11:07.569941+00:00.

Entrada inclui cache; saída inclui raciocínio. Não somar esses subconjuntos novamente. Categorias indicam associação por resposta, não a causa de cada token de contexto. Fases declaradas são uma dimensão separada da atividade detectada.

As seis categorias solicitadas aparecem primeiro como fases explicitamente marcadas. A tabela de atividade usa exclusivamente o coletor Puck sem alterações. Ele reconhece patches e algumas escritas diretas; wrappers functions.exec e scripts dinâmicos podem permanecer sem atividade observável. O complemento estático JS foi retirado após falsos positivos na revisão; registros de fase não interpretam JavaScript.

O overhead inclui coordenação, instrumentação e avaliação externas; não é rateado arbitrariamente entre cenários. Custos faturados, tempo ativo e atribuição causal por skill não estão disponíveis neste estágio.

## overhead

| Fase declarada | Respostas | Entrada | Saída |
| --- | ---: | ---: | ---: |
| Código | 0 | n/d | n/d |
| Documentação | 0 | n/d | n/d |
| Testes | 50 | 7601318 | 43593 |
| Planejamento | 22 | 2320484 | 14382 |
| Revisão | 0 | n/d | n/d |
| Busca | 0 | n/d | n/d |
| Configuração | 0 | n/d | n/d |
| Mista | 0 | n/d | n/d |
| Não disponível | 62 | 5474049 | 40449 |

| Atividade nativa observada | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 8 | 1137873 | 12022 | 12.21 |
| Documentação | 6 | 679781 | 10698 | 10.87 |
| Testes | 44 | 6651828 | 34501 | 35.05 |
| Planejamento | 19 | 1977218 | 10121 | 10.28 |
| Revisão | 0 | n/d | n/d | n/d |
| Busca | 0 | n/d | n/d | n/d |
| Configuração | 1 | 154883 | 1331 | 1.35 |
| Mista | 0 | n/d | n/d | n/d |
| Não disponível | 56 | 4794268 | 29751 | 30.23 |

## C1

| Fase declarada | Respostas | Entrada | Saída |
| --- | ---: | ---: | ---: |
| Código | 46 | 2468151 | 21541 |
| Documentação | 20 | 1433644 | 8145 |
| Testes | 100 | 11602654 | 30503 |
| Planejamento | 12 | 389784 | 4309 |
| Revisão | 0 | n/d | n/d |
| Busca | 71 | 5043677 | 7293 |
| Configuração | 0 | n/d | n/d |
| Mista | 0 | n/d | n/d |
| Não disponível | 12 | 333968 | 2315 |

| Atividade nativa observada | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 0 | n/d | n/d | n/d |
| Documentação | 0 | n/d | n/d | n/d |
| Testes | 100 | 11602654 | 30503 | 41.16 |
| Planejamento | 12 | 389784 | 4309 | 5.81 |
| Revisão | 0 | n/d | n/d | n/d |
| Busca | 71 | 5043677 | 7293 | 9.84 |
| Configuração | 0 | n/d | n/d | n/d |
| Mista | 0 | n/d | n/d | n/d |
| Não disponível | 78 | 4235763 | 32001 | 43.18 |

## C2

| Fase declarada | Respostas | Entrada | Saída |
| --- | ---: | ---: | ---: |
| Código | 0 | n/d | n/d |
| Documentação | 0 | n/d | n/d |
| Testes | 0 | n/d | n/d |
| Planejamento | 6 | 250847 | 1548 |
| Revisão | 0 | n/d | n/d |
| Busca | 0 | n/d | n/d |
| Configuração | 0 | n/d | n/d |
| Mista | 0 | n/d | n/d |
| Não disponível | 4 | 116804 | 500 |

| Atividade nativa observada | Respostas | Entrada | Saída | % da saída |
| --- | ---: | ---: | ---: | ---: |
| Código | 0 | n/d | n/d | n/d |
| Documentação | 0 | n/d | n/d | n/d |
| Testes | 0 | n/d | n/d | n/d |
| Planejamento | 6 | 250847 | 1548 | 75.59 |
| Revisão | 0 | n/d | n/d | n/d |
| Busca | 0 | n/d | n/d | n/d |
| Configuração | 0 | n/d | n/d | n/d |
| Mista | 0 | n/d | n/d | n/d |
| Não disponível | 4 | 116804 | 500 | 24.41 |

## C3

| Fase declarada | Respostas | Entrada | Saída |
| --- | ---: | ---: | ---: |
| Código | 0 | n/d | n/d |
| Documentação | 0 | n/d | n/d |
| Testes | 0 | n/d | n/d |
| Planejamento | 0 | n/d | n/d |
| Revisão | 0 | n/d | n/d |
| Busca | 0 | n/d | n/d |
| Configuração | 0 | n/d | n/d |
| Mista | 0 | n/d | n/d |
| Não disponível | 0 | n/d | n/d |

| Atividade nativa observada | Respostas | Entrada | Saída | % da saída |
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

| Fase declarada | Respostas | Entrada | Saída |
| --- | ---: | ---: | ---: |
| Código | 0 | n/d | n/d |
| Documentação | 0 | n/d | n/d |
| Testes | 0 | n/d | n/d |
| Planejamento | 0 | n/d | n/d |
| Revisão | 0 | n/d | n/d |
| Busca | 0 | n/d | n/d |
| Configuração | 0 | n/d | n/d |
| Mista | 0 | n/d | n/d |
| Não disponível | 0 | n/d | n/d |

| Atividade nativa observada | Respostas | Entrada | Saída | % da saída |
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
