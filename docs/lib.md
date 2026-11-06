# Bibliotecas

A infraestrutura do benchmark usa Python 3 (stdlib), Git, GitHub CLI e Gitleaks. O parser PDF externo é `pypdf==6.21.4`, conforme benchmark/requirements.txt; é usado somente pelo avaliador, não pelas aplicações. Consulta OSV sem advisories retornados para essa versão no momento da preparação, sem representar garantia geral de segurança.

Versões primárias de aplicação: experiment/configs.yaml com substituições explícitas da emenda A-001. Manifests de cada cenário provarão uso real. Bibliotecas adicionais de cada implementação ficam no respectivo docs/lib.md, conferidas contra manifests/lockfiles. Diferenças de toolchain auxiliar não congelado serão registradas como limitação.
