# Roadmap da preparação

## v0.1.1 — autorização por job ativo — em revisão

1. Admitir na dev a correção e os testes da autorização por cenário.
2. Importar somente o delta revisado, com origem e baseline fixados, revisão Neo e gates A0 no patch.
3. Promover a infraestrutura para main; tag após merge e CI verde. A integração posterior na dev renova os gates do candidato; A1 depende de novo acionamento/aprovação do dono.

## v0.1.0 — base confiável de pentest — lançado

1. Infraestrutura e integridade integradas pelo PR #30: 16 imports preservados, árvore sem aplicações e contrato de bootstrap.
2. Gates A0 e revisão Neo concluídos no PR #30, incluindo revisão extra focada autorizada pelo dono. CI `43416095428` aprovada no candidato integrado.
3. Esta versão preparatória é o conteúdo da promoção para main. A tag só é criada após merge e CI verde na main; a integração posterior das aplicações preserva A1 e triagem.

O escopo funcional do experimento não mudou. A1, environment, imagens e aprovação do dono continuam pendentes; esta versão não os dá como concluídos.
