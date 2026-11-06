# Verificação

- `python3 -m unittest discover -s benchmark/tests -v`: testa infraestrutura e cliente HTTP com fixtures locais; não prova aceite das aplicações. A CI pública executa esta suíte sem depender de leitura do Puck privado.
- `python3 benchmark/scripts/telemetry.py collect --puck <checkout-fixado> --parent <id-privado>`: extrai metadados nativos dos descendentes desta execução; IDs, conteúdo e credenciais não vão para os relatórios. `--watch 30` mantém coleta a cada 30 segundos.
- `python3 benchmark/scripts/render_metrics.py`: produz métricas intermediárias por categoria/fase, sem inferir resultados de aplicações.
- `uv venv .private/eval-env` e `uv pip install --python .private/eval-env/bin/python -r benchmark/requirements.txt`: instalam o parser do avaliador.
- `.private/eval-env/bin/python benchmark/scripts/acceptance.py --base http://127.0.0.1:<porta>/api --scenario C1 --output experiment/results/c1-acceptance.json`: executa os mesmos 16 testes externos contra API real. Repetir com apenas base/cenário/output diferentes para C2–C4. Logs brutos ficam privados; saída JSON publica apenas identificadores/resultados sanitizados.

Builds, testes de módulo e operação de cada aplicação ficam no próprio README. UI, segurança estática, pentest, revisão e CI são gates separados; um resultado HTTP não os aprova.

`PUCK_SOURCE=<checkout-fixado> python3 -m unittest discover -s benchmark/integration -v`: integração obrigatória local com o coletor nativo, separada da suíte pública. Falha se a fonte não existir ou divergir do pin. O Puck é privado e o token restrito do GitHub Actions deste repositório não tem acesso; nenhuma credencial foi ampliada e código privado não foi publicado. A execução local e a CI pública têm alcances distintos, registrados como tais.
