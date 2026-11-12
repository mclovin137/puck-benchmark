Ficha: tarefa=benchmark-recovery agente=neo modelo=gpt-6.1-sol (adaptador declarado; runtime não inspecionado) esforço=high skill=security-audit,verificar-antes-de-concluir,humanizer.

# Revisão da ativação da auditoria de dependências

Chamada conferida: tarefa, aceite e escopo presentes; segurança de CI dentro do papel. Revisão A0 em 12/11/2026, base `4735d70d4e55535fca7335b6e4807d7c756b7451`. Escopo: novo workflow auditoria-dependencias.yml, delta ci-rapida.yml e documentação em docs/verificacao.md. Não reabre a R2 do helper ou os pareceres dos cenários. Somente este relatório foi escrito. Sem alteração de código, workflows, policy, provas, aplicações ou controles remotos; sem scan, aplicação, A1, commit ou push. O quadro persistente foi consultado; memória externa segue indisponível.

**CONCLUSÃO:** nenhum achado substanciado de segurança no delta revisado. A integração dos workflows e da documentação é sustentada no alcance estático abaixo, sujeita à CI exigida. Isso não aprova execução real da ativação, gate remoto, A1, controles do owner, promoção ou segurança global. Uma tentativa local informada terminou em falha e permanece explícita.

## Confiança, código e entradas

- **FATO:** o candidato é obtido em candidate, com ref do head do PR ou github.sha em push. O outro checkout fica em trusted e usa o SHA literal `4735d70d4e55535fca7335b6e4807d7c756b7451`. Ambos desativam persistência de credenciais. Não há path compartilhado, checkout de policy a partir do candidato ou base escolhida por argumento de PR.
- **FATO:** instalador e avaliador são chamados com python3 -I e caminho em trusted. --root aponta somente para candidate; --trusted-root e --trusted-sha apontam à mesma base admitida. O scanner relativo .private/tools/osv-scanner é resolvido no trusted root pelo avaliador revisado. O instalador nessa base gera o binário no próprio trusted root e confere seu pin; não é executado instalador candidato.
- **FATO:** os objetos Git da base fixa contêm os hashes da R2 aprovada: avaliador `b98530807b83c5c1661eba3b3bd1124d2a470cb6ed0f0874d3bce47dbb78b58c`, helper `e77109f4b0f0621be19841909662a94ea70f4547e60ceee2c063eb5ad1d6d0e8`, instalador `f417b21e0b77b21fdf2332747b3da8a812c02513a2919e011773d879184dbbb0`. A policy é `8530c564ed3c0823575515173ee1525c09bb026af4f42338e609a9965d3d4ea5`, com oito records active/neo e prazo original, sem renovação. As verificações do helper, configurações neutras OSV e limites das decisões são reaproveitados; sua suíte não foi repetida por mudança de workflow.
- **FATO:** TARGETS no avaliador desse mesmo objeto Git contém nove fontes obrigatórias: quatro Maven, quatro npm e uma PyPI. O workflow não filtra cenários ou reduz essa cobertura. Setup usa Java 21/Python 3.12; Maven resolve conforme isolamento já revisado. Diferenças de rede/toolchain/grafo no runner devem falhar pelas guardas, não ser presumidas equivalentes.

## Eventos, permissões e estados terminais

**FATO:** auditoria-dependencias recebe PRs e pushes para dev/main; ci-rapida recebe PRs e pushes para dev. Runner hospedado, contents:read, Actions por SHA, sem secrets, self-hosted, pull_request_target, dispatch ofensivo ou novo environment. Inputs de evento usados como refs não são interpolados como comandos livres. O caminho do relatório vem de runner.temp, fora do checkout candidato. Upload em always exige arquivo presente: falha/ausência de relatório não vira resultado verde.

O push para dev permite produzir os dois checks no SHA integrado, além dos checks do head do PR. A CI rápida usa event.before/github.sha no push e preserva base/head do PR; somente o limite de 30 arquivos fica condicionado a pull_request. Infraestrutura, segredos, sintaxe e testes não receberam skip novo. test-review.sh continua executando a suíte de infraestrutura e valida os refs para selecionar componentes. Base ausente/inválida não deve ser tratada como teste aprovado; o diff/check subprocess falha.

No evento PR, github.sha pode identificar o merge de teste, enquanto o checkout candidato é explicitamente o head. O nome do artefato usa github.sha; não basta interpretá-lo como identidade do código escaneado. Usar head do run, evento, checkout configurado e metadados do relatório para a proveniência; no push a identidade corresponde ao commit enviado. Essa distinção segue a [documentação GitHub dos eventos](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).

Os jobs auditoria e testes-e-segredos correspondem aos nomes exigidos na política de preflight existente. cancel-in-progress ou timeout reprovam uma execução incompleta; não equivalem a sucesso. Os controles de A1 continuam exigindo os runs mais recentes e jobs bem-sucedidos no SHA exato, além do bootstrap e aprovação do owner. Os novos gatilhos tornam essa evidência possível, sem prová-la antecipadamente.

## Evidência própria e limites

Neo fez parse dos dois YAMLs com PyYAML BaseLoader e asserções dirigidas de eventos, permissões, duas raízes, refs, pins, python isolado, scanner, condicionamento do limite de PR e fallback dos refs. Isso valida a estrutura observada; não substitui interpretação do GitHub. actionlint não está disponível e não foi executado.

Quatorze controles próprios chamaram somente a função pura successful_runs com metadados sintéticos: para cada um dos dois gates, sucesso no SHA/job correto foi aceito; SHA incorreto, falha, fila, job pulado, caminho divergente e run mais recente falho foram rejeitados. Nenhuma API, preflight online, scanner ou A1 foi chamado. Os testes não comprovam runs reais ou configuração remota.

**FATO atribuído ao Oráculo:** durante a revisão, o CLI real local terminou com código 2 e sem relatório. A reprodução direta do scanner no checkout sob ancestor privado retornou 128/nenhuma fonte reconhecida. A comparação com checkout sem esse ancestor está em investigação pelo dono. Neo não repetiu scans, não atribui causa confirmada e não apresenta essa tentativa como sucesso. O código e a configuração da CI usam candidate/trusted sem esse ancestor; isso é diferença de ambiente, não prova de execução remota bem-sucedida.

docs/verificacao.md identifica a base, o prazo original, os gatilhos e a distinção entre admissão, ativação e execução. Não declara que PR 25 sozinho comprovou o novo gate. A pergunta do owner sobre branch padrão/bootstrap continua pendente; environment e variáveis não foram criados ou consultados por caminhos alternativos. Mudar esses controles ou aprovar A1 permanece fora do parecer.

## Identidade do delta

| Arquivo | SHA-256 |
| --- | --- |
| .github/workflows/auditoria-dependencias.yml | `288301b4ba7c6c66305fe1e16ff266f3ba15dceb7fadf9b965ba3711a387ad3f` |
| .github/workflows/ci-rapida.yml | `e3971bf7d17bd341d9b733fa10650173b889458fa3629791521b225c54e106a8` |
| docs/verificacao.md | `387676e350a5ee11df3cd06564f62ebe482538f8f79a5d4e173173f77bd745f0` |

git diff --check do delta rastreado retornou zero; os arquivos novos foram lidos e conferidos separadamente, inclusive whitespace. Alteração posterior requer conferência apenas do delta afetado. Integração e execução da CI devem preservar essas identidades ou registrar a revisão correspondente; a aprovação estática não substitui os resultados.
