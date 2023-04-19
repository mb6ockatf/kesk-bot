CREATE TABLE IF NOT EXISTS users (
    id       SERIAL,
    userid   bigint,
    username varchar(64),
    lang     char(2),
    UNIQUE   (userid)
);
