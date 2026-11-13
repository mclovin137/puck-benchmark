# Contrato da versão preparatória

Segurança > desempenho > qualidade de código > tempo de desenvolvimento. Nível crítico por CI e estabelecimento da base confiável de autorização. Toda alteração de CI/guardas recebe revisão independente Neo antes da integração; a promoção da versão exige CI A0 e revisão/QA do bloco. Falha, ausência ou job pulado não conta como aprovação. Sem compras, release ou deploy autorizados.

## Decisão de bootstrap — aceita para implementação

O dono autorizou seguir a versão separada de infraestrutura após a recomendação explícita dessa rota. A main inicial é `c5d985cbb5adff2983325bc3feeb4c90856d2b3a`, com apenas README; a dev contém aplicações que ainda precisam de A1. A política existente obtém guardas exclusivamente da branch padrão. Esta versão remove a dependência circular sem promover aplicações e sem mudar a branch padrão ou os controles de autorização.

Exceção única ao nome da linha de integração: tasks → `integration/pentest-bootstrap` → versão `main`. A linha temporária parte da main inicial; a dev do experimento e sua história são preservadas. O prefixo dev/pentest-bootstrap é inviável em Git porque a ref dev já existe. Merges do benchmark foram autorizados pelo dono após os gates pertinentes; esta decisão não autoriza controles nem execução A1. Até 30 arquivos por PR, incluindo os 16 imports byteidênticos e o parecer Neo. Primeira tag proposta: v0.1.0, somente após merge e CI verde em main; sem GitHub Release ou deploy.

Alternativas consideradas: manter o bloqueio; tornar dev a branch padrão com proteções efetivas; promover apps sem A1; reescrever dev. A rota separada preserva a fronteira entre preparação e execução, ao custo de uma integração posterior. A aprovação da implementação depende das provas reais, não deste registro.

## Arquitetura e fronteiras

O workflow pentest resolve a branch padrão por SHA, usa guardas/política/suíte/triagem dessa base e faz checkout separado das fontes candidatas. Preflight e job protegido exigem controles reais e gates estáticos do SHA candidato. Nada no bootstrap executa esse fluxo A1. Na versão v0.1.0, os 16 arquivos comuns foram importados da fonte `219d50f920ba9fbcd107e202d5661185d11e5676`; o manifesto e as constantes fixadas identificam a fonte da versão corrente.

O workflow bootstrap-a0 e seu verificador têm escopo fechado: árvore completa, imports contra objetos Git da fonte fixa, contexto/ref/repositório do evento, limite de arquivos e ausência de história de aplicações. Fixtures e sintaxe são A0; OSV cobre somente lock npm e pypdf do runner. Nenhum sucesso substitui os workflows/nomes exigidos pela política A1 das aplicações. Como o primeiro gate ainda não existe na base, ele pode alterar a si próprio; a admissão depende da revisão independente dos arquivos exatos e conferência de origem. Não alegar enforcement imutável ou proteção remota não observada.

## Lifecycle e recuperação

Após admissão em main, integrar main em uma task da dev de aplicações sem reescrever história. Preservar os imports e a CI completa das apps; retirar nessa integração o workflow, verificador, manifesto e testes exclusivos de bootstrap. Não ampliar a allowlist para admitir aplicações. A retirada exige revisão Neo e CI rápida/dependências; a promoção das apps mantém CI completa, A1 e triagem no candidato pertinente. Se um check bootstrap for exigido remotamente, cabe ao dono resolver a proteção; não contornar ou fabricar job verde.

Antes do merge, ajustar/fechar o PR sem tocar dev/main. Depois, defeito bloqueia A1 e exige correção ou reversão em versão revisada, com evidência e nova tag após merge. Não remover environment/variáveis do dono, fazer prune ou prometer rollback automático. Nenhum dado ou recurso de aplicação é criado por este bootstrap.

## Patch v0.1.1 — atividade do job protegido

A execução 43424007867 falhou antes de construir a aplicação porque a guarda exigia o estado global in_progress enquanto outros cenários aguardavam aprovação. O patch exige um único job ativo do cenário no run e tentativa 1, vinculado ao runner hospedado atual e com aprovação protegida do dono. Waiting só é aceito junto dessa prova; estados terminais, inconsistência ou falha da API bloqueiam. O nome do runner é vínculo adicional, sem alegação de identidade única.

A linha temporária integra a task feat/pentest-runtime-fix sobre a main v0.1.0, mantendo a árvore fechada de 30 arquivos. Origem e baseline permanecem SHAs fixos no verificador/manifesto, sem parâmetros arbitrários nem importação da história das aplicações. A correção altera três dos 16 imports; os demais permanecem preservados. Nenhuma política, imagem, controle remoto ou critério funcional muda. Após admissão e CI verde, integrar de volta à dev e renovar os gates do novo candidato antes de novo dispatch do dono.

Origem fixa do patch: `b5d680d8f158d4edd60495cda9333acca1919b71`, admitida na dev pelo PR #33. Baseline da main: `98894e1e09585f9b12f07921eb4650fd3ce4f1a8`. Os 16 imports são comparados byte a byte com essa origem; somente guards.py, run-ci.py e seus testes diferem da v0.1.0. A admissão dos vínculos de dependências ocorreu no PR #34, seguida da auditoria real do código corrigido no PR #33; o patch da main não contém essa política de aplicações.
