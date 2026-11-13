# Puck Benchmark — base preparatória de pentest

Esta versão instala em `main` somente a infraestrutura comum de validação A0. Não contém aplicações e não representa pentest executado ou promoção dos quatro cenários.

O [contrato](docs/rules.md) delimita a versão, os [comandos de verificação](docs/verificacao.md) explicam o alcance e o [manifesto](bootstrap-manifest.json) identifica os imports preservados. A suíte comum e as barreiras de autorização estão em [benchmark/pentest](benchmark/pentest/README.md). Os relatos históricos desse README foram preservados byte a byte; não são resultados novos desta versão.

As aplicações e os resultados consolidados continuam em [dev](https://github.com/mclovin137/puck-benchmark/tree/dev). O gate `gate-bootstrap-a0` valida somente esta preparação e não substitui CI funcional, auditoria de dependências das aplicações, pentest A1 ou triagem.

Depois da admissão desta base, ainda são necessários o environment protegido e as imagens por digest mantidos pelo dono, os gates do SHA candidato e o acionamento/aprovação do pentest pelo dono. Não há autorização de compra, release ou deploy.
