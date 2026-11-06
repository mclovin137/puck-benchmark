-- C2: ADR 001/002. Migração inicial aditiva em PostgreSQL 17.11.
-- Pré-condição: schema novo; transação Flyway, sem backfill ou dados anteriores.
CREATE TABLE app_user (
 id UUID PRIMARY KEY, name VARCHAR(120) NOT NULL CHECK (length(trim(name)) BETWEEN 1 AND 120),
 email VARCHAR(254) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL, created_at TIMESTAMPTZ NOT NULL
);
CREATE TABLE auth_session (
 id UUID PRIMARY KEY, user_id UUID NOT NULL REFERENCES app_user(id), token_hash VARCHAR(64) NOT NULL UNIQUE,
 expires_at TIMESTAMPTZ NOT NULL, revoked_at TIMESTAMPTZ
);
CREATE INDEX session_user_idx ON auth_session(user_id);
CREATE TABLE financial_transaction (
 id UUID PRIMARY KEY, owner_id UUID NOT NULL REFERENCES app_user(id),
 type VARCHAR(7) NOT NULL CHECK (type IN ('INCOME','EXPENSE')),
 description VARCHAR(255) NOT NULL CHECK (length(trim(description)) BETWEEN 1 AND 255),
 category VARCHAR(80) NOT NULL CHECK (length(trim(category)) BETWEEN 1 AND 80),
 amount NUMERIC(16,2) NOT NULL CHECK (amount > 0), date DATE NOT NULL,
 created_at TIMESTAMPTZ NOT NULL, updated_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX transaction_owner_date_idx ON financial_transaction(owner_id,date,id);
