# Roadmap da preparação

## v0.1.3 — contexto de build C1 — em revisão

1. Admitir na dev o empacotamento C1 e os oito vínculos exatos afetados pelo contexto comum, com provas de build limpo, inicialização restrita, HTTP e revisão.
2. Importar somente a policy de contexto e fixar a proveniência, preservando os outros 15 imports, as guardas e a árvore fechada de 30 arquivos; revisão e CI A0.
3. Promover infraestrutura, conferir CI main e tag; integrar de volta à dev sem bootstrap-only, congelar candidato e conferir gates antes de novo A1 pelo dono.

## v0.1.2 — ciclo global e atividade do job — lançado no conteúdo da promoção

1. Admitir o delta da guarda e os vínculos exatos da política, com revisão Neo e gates próprios.
2. Transportar somente os dois imports alterados para a base confiável, preservando os outros 14 e a árvore de 30 arquivos.
3. Promover a versão com CI A0 e tag após CI verde na main; integrar de volta à dev e renovar os gates do candidato antes de novo A1 pelo dono.

## v0.1.1 — autorização por job ativo — lançado no conteúdo da promoção

1. Admitir na dev a correção e os testes da autorização por cenário.
2. Importar somente o delta revisado, com origem e baseline fixados, revisão Neo e gates A0 no patch.
3. Promover a infraestrutura para main; tag após merge e CI verde. A integração posterior na dev renova os gates do candidato; A1 depende de novo acionamento/aprovação do dono.

## v0.1.0 — base confiável de pentest — lançado

1. Infraestrutura e integridade integradas pelo PR #30: 16 imports preservados, árvore sem aplicações e contrato de bootstrap.
2. Gates A0 e revisão Neo concluídos no PR #30, incluindo revisão extra focada autorizada pelo dono. CI `43416095428` aprovada no candidato integrado.
3. Esta versão preparatória é o conteúdo da promoção para main. A tag só é criada após merge e CI verde na main; a integração posterior das aplicações preserva A1 e triagem.

O escopo funcional do experimento não mudou. A1, environment, imagens e aprovação do dono continuam pendentes; esta versão não os dá como concluídos.

O marcador v0.1.1 descreve o conteúdo preparado para a promoção. A entrega só se efetiva após merge, CI verde na main e tag; nenhuma anotação substitui esses gates ou aprova A1.

O marcador v0.1.2 descreve o conteúdo preparado para a promoção. A entrega depende do merge e da CI verde na main, seguida da tag; nenhum marcador substitui gates ou execução A1.
