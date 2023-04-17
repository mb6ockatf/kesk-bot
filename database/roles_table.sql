CREATE TABLE IF NOT EXISTS roles (
    id SERIAL,
    accoount_name varchar(50) UNIQUE NOT NULL,
    account_password varchar(32)
);