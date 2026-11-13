# Puck Benchmark — base preparatória de pentest

Esta versão instala em `main` somente a infraestrutura comum de validação A0. Não contém aplicações e não representa pentest executado ou promoção dos quatro cenários.

O [contrato](docs/rules.md) delimita a versão, os [comandos de verificação](docs/verificacao.md) explicam o alcance e o [manifesto](bootstrap-manifest.json) identifica os imports preservados. A suíte comum e as barreiras de autorização estão em [benchmark/pentest](benchmark/pentest/README.md). Os relatos históricos desse README foram preservados byte a byte; não são resultados novos desta versão.

As aplicações e os resultados consolidados continuam em [dev](https://github.com/mclovin137/puck-benchmark/tree/dev). O gate `gate-bootstrap-a0` valida somente esta preparação e não substitui CI funcional, auditoria de dependências das aplicações, pentest A1 ou triagem.

Depois da admissão desta base, ainda são necessários o environment protegido e as imagens por digest mantidos pelo dono, os gates do SHA candidato e o acionamento/aprovação do pentest pelo dono. Não há autorização de compra, release ou deploy.

## Patch v0.1.3

O contexto de build frontend C1 passa à raiz do próprio cenário, para incluir o design original. A fonte admitida na dev é `908047555ea8808d7c263f42adb62692a043a225` (PR #44). Somente a policy de contexto muda entre os 16 imports; guardas, workflow, suíte, limites e controles são preservados. Dockerfiles e compose das aplicações continuam fora desta árvore preparatória.

Builds limpos, smoke e aceite C1 foram conferidos antes da admissão da fonte. Isso não é A1; o run43503520863 falhou Docker sem relatório. Revisão do transporte, CI A0 e tag continuam exigidos antes de consumir esta base. O smoke do frontend C3 revelou outro bloqueio de escrita do servidor Vite sob readonly, tratado separadamente na dev antes do próximo candidato.
