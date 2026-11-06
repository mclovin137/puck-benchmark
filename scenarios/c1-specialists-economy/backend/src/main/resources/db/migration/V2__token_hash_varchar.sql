-- Tarefa C1: alinhar o tipo físico token_hash ao mapeamento JPA (Model Token).
-- Pré-condição: V1 aplicada; PostgreSQL 17.x; coluna contém SHA-256 hexadecimal de 64 chars.
-- Compatibilidade: CHAR(64) -> VARCHAR(64), preserva os valores existentes.
ALTER TABLE auth_token
  ALTER COLUMN token_hash TYPE VARCHAR(64)
  USING token_hash::VARCHAR(64);
