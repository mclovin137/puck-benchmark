-- C4 task1, ADR001. Pré-condição: schema vazio. Migração aditiva transacional.
CREATE TABLE app_user (id UUID PRIMARY KEY, name VARCHAR(120) NOT NULL, email VARCHAR(254) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL);
CREATE TABLE auth_session (token_hash VARCHAR(64) PRIMARY KEY, owner_id UUID NOT NULL REFERENCES app_user(id), expires_at TIMESTAMP WITH TIME ZONE NOT NULL);
CREATE INDEX session_expiry ON auth_session(expires_at);
CREATE TABLE movement (id UUID PRIMARY KEY, owner_id UUID NOT NULL REFERENCES app_user(id), type VARCHAR(7) NOT NULL CHECK(type IN ('INCOME','EXPENSE')), description VARCHAR(255) NOT NULL, category VARCHAR(80) NOT NULL, amount NUMERIC(16,2) NOT NULL CHECK(amount > 0), date DATE NOT NULL, created_at TIMESTAMP WITH TIME ZONE NOT NULL, updated_at TIMESTAMP WITH TIME ZONE NOT NULL);
CREATE INDEX movement_owner_date ON movement(owner_id,date,id);
CREATE INDEX movement_owner_amount ON movement(owner_id,amount,id);
