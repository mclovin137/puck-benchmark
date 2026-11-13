Ficha: tarefa=benchmark-recovery/pentest-bootstrap agente=neo modelo=gpt-6.1-sol (adaptador declarado; runtime não inspecionado) esforço=high skill=security-audit,pr-audit,verificar-antes-de-concluir.

# Revisão de segurança da versão preparatória

**Estado: em revisão, sem recomendação de admissão.** Chamada conferida: tarefa, aceite e escopo presentes; papel adequado. Nível crítico por CI e base confiável de autorização. Revisão local em 13/11/2026, HEAD inicial `c5d985cbb5adff2983325bc3feeb4c90856d2b3a`; arquivos novos ainda não commitados. Quadro e desenho foram confrontados com Git; memória externa indisponível. Ownership exclusivo deste parecer; nenhum controle remoto, scanner ofensivo ou A1 acionado.

## Fase 1 — imports e contrato estáveis

**FATO:** os 16 imports do manifesto correspondem byte a byte aos objetos Git de `219d50f920ba9fbcd107e202d5661185d11e5676`; SHA-256 e modos `100644` do manifesto correspondem à origem. Arquivos locais regulares, sem symlinks. A main inicial contém somente README. A árvore observada tinha 29 arquivos antes deste parecer, incluindo helper/testes ainda sob implementação. A contagem não substitui a futura verificação das árvores commitadas e de sua ancestralidade.

**FATO:** bootstrap-a0 dispara somente em PR/push para main ou linha temporária, usa runner hospedado, contents:read, Actions por SHA, checkout sem credenciais persistidas e histórico completo. Dados de base/head passam por variáveis e argumentos entre aspas. O gate final em always exige sucesso do job obrigatório; upload ausente falha. Não há environment, secrets, dispatch ou nome de gate A1 no workflow A0. O npm ci usa cópia temporária, ignore-scripts e supressão de download do navegador. Gitleaks usa regras padrão, sem allowlist nova; sua imagem está fixada por versão, sem alegação de digest imutável.

**FATO:** a política importada continua exigindo ci-rapida/testes-e-segredos e auditoria-dependencias/auditoria no SHA candidato. As guardas continuam exigindo owner exclusivo, ausência de bypass, imagens por digest e aprovação real antes do runtime. Importar as fixtures não chama main do runtime. Nenhum desses controles remotos foi consultado, criado ou aprovado nesta revisão.

**CONCLUSÃO PARCIAL:** nenhum achado substanciado nos imports/workflow/contrato desta fase. O primeiro workflow/verificador pode alterar a si próprio; manifesto autoeditável não estabelece confiança por si. A admissão depende da revisão independente dos bytes exatos e da CI real, sem alegação de proteção de branch ou enforcement imutável. O contrato preserva aplicações/A1 e prevê retirada dos controles exclusivos de bootstrap na integração posterior com dev.

## Evidência e pendências

Comparação independente de 16 blobs/digests/modos e parse estrutural PyYAML BaseLoader passaram; o parse não substitui a interpretação pelo GitHub. Inventário estático de superfície executado. Não executados nesta fase: helper, testes novos, suíte A0, npm ci, auditoria real OSV/Gitleaks, CI remota e actionlint. Provas anteriores informadas pelo Oráculo não são atribuídas a Neo.

Fase 2 pendente de entrega estável do helper/testes: contexto do evento e fork, bindings repositório/refs/SHA, head e merge, fonte de objetos fixa, 30 arquivos, ancestralidade, sanitização e falha fechada de scanner/gates. Sem conclusão antecipada enquanto esses arquivos forem mutáveis. A cobertura de dependências pretendida restringe-se a npm lock e pypdf do Dockerfile; apt/imagens não estão cobertos.

Identidades estáveis desta fase: bootstrap-a0.yml SHA-256 `719d907f5baff946361562f07ca2ab1a5c39aebcfaf9144d9d74edc900507e48`; bootstrap-manifest.json `0cf4bb610ab13785353210e13f406451fb1aeec4f973498387e9cc845be3d8d9`. Os hashes dos imports estão no manifesto, cuja correspondência à origem foi conferida independentemente. Helper/testes ainda não recebem identidade de aprovação.
