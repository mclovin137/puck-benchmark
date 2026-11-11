# ADR001 — Sessões revogáveis e moeda decimal
Status: decisão de implementação dentro do contrato autorizado, revisão independente pendente. Fonte: protocol.md. Dono C4.

O contrato permite bearer opaco ou assinado e exige revogação efetiva. Escolha: token opaco aleatório, digest no banco e expiração8h. Alternativa JWT precisaria denylist para logout, acrescentando estado e chaves. Custo aceito: consulta por requisição, recarga da UI exige login pois token fica em memória. Reabrir se houver requisito de sessão persistente ou escala medido.

Moeda utiliza BigDecimal no backend e strings no JSON/UI; cálculos só no backend. Comparado a números JSON/Number, preserva os14 dígitos inteiros e centavos exigidos. Sem cache ou saldo redundante. Frameworks e bibliotecas são os fixados pelo experimento, sem nova stack.
