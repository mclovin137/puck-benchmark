# Bibliotecas

A infraestrutura do benchmark usa Python 3 (stdlib), Git, GitHub CLI e Gitleaks. O parser PDF externo é `pypdf==6.21.4`, conforme benchmark/requirements.txt; é usado somente pelo avaliador, não pelas aplicações. Consulta OSV sem advisories retornados para essa versão no momento da preparação, sem representar garantia geral de segurança.

Versões primárias de aplicação: experiment/configs.yaml com substituições explícitas da emenda A-001. Manifests de cada cenário provarão uso real. Bibliotecas adicionais de cada implementação ficam no respectivo docs/lib.md, conferidas contra manifests/lockfiles. Diferenças de toolchain auxiliar não congelado serão registradas como limitação.

OSV-Scanner 2.7.0 é ferramenta externa comum, obtida da release oficial com SHA-256 fixado em benchmark/scripts/install_tools.py. O probe neutro benchmark/baseline/pom.xml verifica a baseline Java efetiva; não contém implementação compartilhada. A emenda A-002 registra patches transitivos e os dois alertas de componentes Spring que exigem triagem por aplicação.

A integração da base v0.1.0 não adiciona dependências às aplicações. O runtime e o lock do pentest comum permanecem byte a byte iguais à fonte revisada em 219d50f; as limitações de cobertura de imagens/apt e dos suplementos PyPI constam no parecer histórico `docs/bootstrap-security.md`.
