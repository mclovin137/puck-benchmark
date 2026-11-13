# Bibliotecas e ferramentas conferidas

Host: Python 3 (stdlib), Git e Node 24. O manifest/lock em benchmark/pentest fixa Playwright 1.56.1 e suas transitivas; o runner.Dockerfile instala pypdf==6.21.4, python3 e python3-venv. Imagem-base e apt não são integralmente fixados por esse lock e sua cobertura não é alegada neste gate.

OSV-Scanner 2.7.0 é obtido pelo instalador importado com SHA256 fixado. A auditoria usa configuração neutra e duas fontes, sem triagens das aplicações: package-lock e requisito pypdf extraído do Dockerfile. Qualquer advisory, erro ou cobertura incompleta reprova. Nenhum scanner verde comprova ausência global de vulnerabilidades.

Gitleaks 8.30.1 usa a configuração padrão, sem nova allowlist. Actions da CI usam os SHAs já utilizados na infraestrutura revisada. actionlint não está disponível localmente; essa limitação será registrada sem inventar execução. Nenhuma biblioteca de produção é adicionada às aplicações.
