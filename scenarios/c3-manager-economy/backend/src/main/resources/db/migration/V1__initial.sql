create table app_user (id bigserial primary key, name varchar(120) not null, email varchar(254) not null unique, password_hash varchar(100) not null);
create table session_token (id bigserial primary key, token_hash varchar(64) not null unique, user_id bigint not null references app_user(id), expires_at timestamptz not null);
create table transaction_record (id bigserial primary key, user_id bigint not null references app_user(id), type varchar(7) not null, description varchar(255) not null, category varchar(80) not null, amount numeric(16,2) not null check(amount > 0), date date not null, created_at timestamptz not null, updated_at timestamptz not null);
create index transaction_owner_date on transaction_record(user_id,date,id);
