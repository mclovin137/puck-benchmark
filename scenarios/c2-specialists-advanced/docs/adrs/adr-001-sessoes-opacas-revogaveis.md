---
date: 2026-11-06
status: aceita
---
# ADR 001: sessões opacas revogáveis no banco

## Para o futuro agente

Logout deve invalidar o token no backend imediatamente para requisições futuras. Token do browser fica só em memória; recarregar a página exige login.

## Contexto e critérios

O [protocolo](../../../../experiment/protocol.md) exige expiração e revogação efetiva. Projeto local, único backend e PostgreSQL já obrigatório; sem custo novo. Senhas aceitam 12–128 caracteres, inclusive entradas que excedem 72 bytes.

## Opções consideradas

- **Sessão opaca persistida — escolhida:** revogação e auditoria simples, ao custo de consulta ao banco em cada requisição privada.
- **JWT com lista de revogação — descartada:** também pode satisfazer contrato, porém exige estado adicional e validação criptográfica sem benefício comprovado neste escopo.
- **JWT só com expiração — descartada:** não satisfaz logout imediato. O cenário ainda não tinha implementação de autenticação para preservar.

## Decisão

Gerar 32 bytes por `SecureRandom`, codificar base64url e devolver somente no login. Armazenar SHA-256 do token, user_id, expires_at (12 h após emissão) e revoked_at. Validar ausência de revogação e expiração a cada requisição, sem cache de sessão; logout marca revoked_at transacionalmente antes de 204. Comparar digest via busca indexada; nunca registrar token/digest em logs. Requisição já autorizada em andamento no instante do logout pode terminar; usos posteriores falham 401.

Hash de senha: PBKDF2-HMAC-SHA256, salt aleatório 16 bytes, 600000 iterações e resultado 32 bytes, com algoritmo/parâmetros versionados no armazenamento. Comparação em tempo constante. Evita truncamento de 72 bytes do BCrypt direto; senha jamais aparada ou truncada. E-mail é aparado/normalizado; senha permanece conforme enviada e validada. Transporte de produção exigiria TLS; o escopo atual é loopback local.

## Consequências e revisão

Banco é dependência de autenticação; indisponibilidade falha fechada. Token furtado permanece válido até revogação/expiração, exigindo prevenir XSS e vazamento. Múltiplas sessões por usuário são permitidas; logout revoga apenas a apresentada. Rever se surgirem múltiplos serviços, federação ou exigência de sessão persistente no navegador. Não adicionar limpeza agendada de sessões sem necessidade; expiradas já não autorizam.

## Relações, aceite e histórico

Afeta auth, filtro de segurança, schema e [HLD](../hlds/financas.md). Decisão técnica rotineira autorizada pela seção 12 da especificação e briefing do Oráculo em 2026-11-06; status aceita registra esse mandato, sem equivaler a revisão independente. Validação de segurança permanece pendente de Neo. Criada em 2026-11-06; não substitui ADR anterior.
