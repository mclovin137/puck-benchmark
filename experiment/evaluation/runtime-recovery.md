# Avaliação comum na retomada

Em 11/11/2026, as quatro aplicações foram construídas e avaliadas a partir de `1f552f1d5cbf014d3ed1da644cdc11d4e6262e3d`, em projetos Compose separados, com dados sintéticos. Cada execução confirmou fontes limpas e remoção dos recursos próprios. Os arquivos `experiment/results/system-c*.json` identificam horários, commit e alcance.

| Cenário | Aceite HTTP comum | Casos de fronteira | Restore sintético |
|---|---|---|---|
| C1 | 16 testes, sucesso | 4 testes, sucesso | Sucesso |
| C2 | 16 testes, sucesso | 4 testes, sucesso | Sucesso |
| C3 | 16 testes, sucesso | 4 testes, sucesso | Sucesso |
| C4 | 16 testes, 1 falha e 11 erros, incluindo subcasos | 4 testes, sucesso | Sucesso |

Os números de falhas/erros de C4 incluem subcasos e não devem ser subtraídos diretamente dos 16 métodos. Há dois comportamentos pendentes de correção: respostas de autenticação cujo JSON não pode ser decodificado como UTF-8 e login com credencial incorreta curta respondendo 400 onde o contrato exige 401. Os arquivos `*-initial.json` preservam essa primeira execução, mesmo se houver nova tentativa. A retomada do gerente original encontrou limite de uso antes de alterar a aplicação; isso não constitui correção nem aprovação.

O restore comparou contagens e hashes dos dados entre snapshot e banco restaurado, verificando também que a origem permaneceu igual durante a prova. Não mede recuperação de desastre, carga ou tempo de produção. As provas HTTP não abrangem navegador, acessibilidade, pentest ou aprovação de versão.

Reprodução: executar `benchmark/scripts/check_applications.py --scenario Cx` e depois `benchmark/scripts/run_system_evaluation.py --scenario Cx --subnet <rede-livre-/24>` com as dependências do avaliador instaladas. Conferir previamente ausência de sobreposição com redes e rotas do ambiente. Na execução registrada foram usadas redes próprias de `10.254.244.0/24` a `10.254.247.0/24`; elas não são uma reserva permanente. O launcher realiza a limpeza do seu projeto. O probe de restore deve rodar enquanto o projeto sintético correspondente estiver ativo.

`architecture-final.md` é uma avaliação estática independente com proveniência própria. `media-validation.json` registra leitura/remux de três vídeos históricos, sem validar visualmente a jornada; o registro não significa que os vídeos já estejam publicados. C1 não tem vídeo localizado. Pentest A1, demonstrações completas, consolidação das métricas e promoção continuam pendentes.
