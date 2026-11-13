# Contrato da versão preparatória

Segurança > desempenho > qualidade de código > tempo de desenvolvimento. Nível crítico por CI e estabelecimento da base confiável de autorização. Toda alteração de CI/guardas recebe revisão independente Neo antes da integração; a promoção da versão exige CI A0 e revisão/QA do bloco. Falha, ausência ou job pulado não conta como aprovação. Sem compras, release ou deploy autorizados.

## Decisão de bootstrap — aceita para implementação

O dono autorizou seguir a versão separada de infraestrutura após a recomendação explícita dessa rota. A main inicial é `c5d985cbb5adff2983325bc3feeb4c90856d2b3a`, com apenas README; a dev contém aplicações que ainda precisam de A1. A política existente obtém guardas exclusivamente da branch padrão. Esta versão remove a dependência circular sem promover aplicações e sem mudar a branch padrão ou os controles de autorização.

Exceção única ao nome da linha de integração: tasks → `integration/pentest-bootstrap` → versão `main`. A linha temporária parte da main inicial; a dev do experimento e sua história são preservadas. O prefixo dev/pentest-bootstrap é inviável em Git porque a ref dev já existe. Merges do benchmark foram autorizados pelo dono após os gates pertinentes; esta decisão não autoriza controles nem execução A1. Até 30 arquivos por PR, incluindo os 16 imports byteidênticos e o parecer Neo. Primeira tag proposta: v0.1.0, somente após merge e CI verde em main; sem GitHub Release ou deploy.

Alternativas consideradas: manter o bloqueio; tornar dev a branch padrão com proteções efetivas; promover apps sem A1; reescrever dev. A rota separada preserva a fronteira entre preparação e execução, ao custo de uma integração posterior. A aprovação da implementação depende das provas reais, não deste registro.

## Arquitetura e fronteiras

O workflow pentest resolve a branch padrão por SHA, usa guardas/política/suíte/triagem dessa base e faz checkout separado das fontes candidatas. Preflight e job protegido exigem controles reais e gates estáticos do SHA candidato. Nada no bootstrap executa esse fluxo A1. Os 16 arquivos comuns são idênticos aos objetos da fonte `219d50f920ba9fbcd107e202d5661185d11e5676`.

O workflow bootstrap-a0 e seu verificador têm escopo fechado: árvore completa, imports contra objetos Git da fonte fixa, contexto/ref/repositório do evento, limite de arquivos e ausência de história de aplicações. Fixtures e sintaxe são A0; OSV cobre somente lock npm e pypdf do runner. Nenhum sucesso substitui os workflows/nomes exigidos pela política A1 das aplicações. Como o primeiro gate ainda não existe na base, ele pode alterar a si próprio; a admissão depende da revisão independente dos arquivos exatos e conferência de origem. Não alegar enforcement imutável ou proteção remota não observada.

## Lifecycle e recuperação

Após admissão em main, integrar main em uma task da dev de aplicações sem reescrever história. Preservar os imports e a CI completa das apps; retirar nessa integração o workflow, verificador, manifesto e testes exclusivos de bootstrap. Não ampliar a allowlist para admitir aplicações. A retirada exige revisão Neo e CI rápida/dependências; a promoção das apps mantém CI completa, A1 e triagem no candidato pertinente. Se um check bootstrap for exigido remotamente, cabe ao dono resolver a proteção; não contornar ou fabricar job verde.

Antes do merge, ajustar/fechar o PR sem tocar dev/main. Depois, defeito bloqueia A1 e exige correção ou reversão em versão revisada, com evidência e nova tag após merge. Não remover environment/variáveis do dono, fazer prune ou prometer rollback automático. Nenhum dado ou recurso de aplicação é criado por este bootstrap.
