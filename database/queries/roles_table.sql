CREATE TABLE IF NOT EXISTS roles (
    id            SERIAL,
    account_name  varchar(50) UNIQUE NOT NULL,
    account_role  varchar(30),
    password_hash varchar(60)
);