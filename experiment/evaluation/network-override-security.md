Ficha: tarefa=benchmark-recovery agente=neo modelo=gpt-6.1-sol (adaptador declarado; runtime não inspecionado) esforço=high skill=security-audit,verificar-antes-de-concluir,humanizer

# Revisão de segurança do override de rede

**Conclusão:** nenhum achado de segurança substanciado no delta auditado. Foram executados 21 testes focados, configuração real do Compose com duas fixtures e uma simulação independente de colisão. Não houve startup real, coleta ou alteração de redes. Este parecer não aprova globalmente o experimento nem comprova disponibilidade das subnets no instante da avaliação.

Base: `6313ed25692f14d33cfaf8fd94a3db2861e2d7e4`, branch `fix/isolated-evaluation-network`, mais delta não commitado. Escopo exclusivo: `benchmark/scripts/run_system_evaluation.py`, `benchmark/tests/test_runtime_fail_closed.py`, `benchmark/tests/test_runtime_routing.py` e documentação correspondente em `docs/verificacao.md`.

Chamada conferida: tarefa, aceite e escopo presentes; revisão dentro do papel do Neo. Nenhuma correção, commit ou push. Sem leitura de cenários, conversas, outros projetos ou resultados comparativos. Único arquivo criado pelo revisor: este parecer; fixtures temporárias foram descartadas.

## Fronteiras revisadas

**FATO:** `private_subnet` exige endereço IPv4 alinhado em `/24` contido em uma das três faixas RFC1918. Valores públicos, loopback, IPv6, prefixo amplo e endereço não alinhado são rejeitados. O argumento não é interpolado em shell.

**FATO:** o override contém somente `networks.default.ipam.config`. `NamedTemporaryFile` cria arquivo de nome imprevisível dentro de `.private`, cujo diretório é ajustado para `0700`; a fixture conferiu arquivo `0600`. O arquivo é fechado antes de o Compose ler e continua disponível até o teardown.

**FATO:** a configuração efetiva precisa conter somente a rede `default` com exatamente a subnet solicitada. Em seguida continuam sendo aplicadas as guardas originais: rede não externa, driver bridge, ausência de opções de driver, nome dentro do projeto efêmero e portas publicadas em loopback. O delta não adiciona modo host, rede compartilhada, privilégio ou acesso a socket.

**FATO:** rejeição antes de comprovar ownership não chama `up` nem `down`. Após a validação, o teardown usa o mesmo projeto aleatório e os mesmos arquivos Compose. O override é removido nos fluxos usuais de sucesso, rejeição por guarda e falha de subprocesso durante startup. A falha simulada não produz sucesso nem inicia o aceite.

## Evidência própria

- `python3 -m unittest discover -s benchmark/tests -p test_runtime_fail_closed.py -v`: **15/15 passaram**.
- `python3 -m unittest discover -s benchmark/tests -p test_runtime_routing.py -v`: **6/6 passaram**.
- `git diff --check` dos quatro arquivos: código zero, sem saída.
- Docker Compose **2.40.3+ds1-0ubuntu1**, somente `config --no-env-resolution --format json`, com serviços e imagens inertes em diretório temporário: rede final exclusiva `benchmark-eval-c1-neo-fixture_default`, subnet esperada, ausência de `external` e URLs em `127.0.0.1`. A configuração passou pelas mesmas guardas do launcher. Não foram iniciados containers ou consultadas aplicações.
- Segunda fixture Compose: a configuração inicial declarava `10.217.44.0/24`; o overlay solicitou `10.254.247.0/24`. A configuração efetiva retornou **somente** `[{"subnet":"10.254.247.0/24"}]`, aceita por `assert_subnet`. A sequência não acumulou a subnet antiga nessa versão do Compose. Nenhum manifesto real foi lido ou alterado.
- Reprodução independente com `subprocess.run` simulado: `up` lançou `CalledProcessError` representando colisão de IPAM. Resultado: código 1, `success=false`, etapa `startup`, nenhum aceite executado, teardown do projeto tentado e override `0600` removido. Prova a reação do launcher ao erro; não reproduz o IPAM real.

## Limites e riscos residuais

O launcher valida formato e configuração resultante; **não detecta colisões com rotas do host nem reserva a faixa previamente**. A documentação exige conferência de IPAM/rotas pelo operador antes do uso. A simulação demonstra falha fechada quando o Docker recusa a criação, mas não demonstra que toda colisão com rota externa será recusada. O diagnóstico anterior é um snapshot, não uma reserva.

O cleanup não é garantia contra término abrupto. Pela leitura do `finally`, uma exceção ao invocar o próprio `down`, antes de retornar um processo, também impede alcançar `unlink` e a escrita final do resultado. Esse limite de robustez não foi reproduzido nesta rodada; o temporário contém somente a subnet e permanece no diretório privado. Não foi demonstrado comprometimento de isolamento por esse caminho.

Não foram reexecutados os 53 testes integrais informados pelo Oráculo. Também não foram verificados builds, DNS, conectividade, HTTP, CI remota, limpeza real pelo daemon ou disponibilidade atual das faixas. As guardas existentes limitam o launcher e não oferecem sandbox integral contra código de build/aplicação. Nenhum resultado sintético foi tratado como aceite funcional.

Hashes SHA256 do candidato revisado:

- Launcher: `8bc9ce5cc22fdecd81e0a42bfa3678f3347035dc8e559fdba24ce4b4f317856b`.
- Teste fail-closed: `4193f7abbcfa2f0f91d2d6954e554b184aecc0bf11f349ba192623365097f2a8`.
- Teste routing: `6a2d0a85985c6a4047f08474173f70b35c3072e6ebdebe0dfa8b3230badbad37`.
- Documentação: `3e2aa0b74d53375107a497dd314f5b45c58bf32220207456549fff3fb2345836`.
