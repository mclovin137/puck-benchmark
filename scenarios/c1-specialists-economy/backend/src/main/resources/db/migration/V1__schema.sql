CREATE TABLE app_user (id UUID PRIMARY KEY, name VARCHAR(120) NOT NULL, email VARCHAR(254) NOT NULL UNIQUE, password_hash VARCHAR(100) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE auth_token (token_hash CHAR(64) PRIMARY KEY, user_id UUID NOT NULL REFERENCES app_user(id) ON DELETE CASCADE, expires_at TIMESTAMPTZ NOT NULL, revoked_at TIMESTAMPTZ);
CREATE INDEX auth_token_expiry_idx ON auth_token(expires_at);
CREATE TABLE transaction_entry (id UUID PRIMARY KEY, user_id UUID NOT NULL REFERENCES app_user(id) ON DELETE CASCADE, type VARCHAR(7) NOT NULL CHECK(type IN ('INCOME','EXPENSE')), description VARCHAR(255) NOT NULL, category VARCHAR(80) NOT NULL, amount NUMERIC(16,2) NOT NULL CHECK(amount > 0), entry_date DATE NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE INDEX transaction_owner_date_idx ON transaction_entry(user_id, entry_date DESC, id);
CREATE INDEX transaction_owner_amount_idx ON transaction_entry(user_id, amount, id);
