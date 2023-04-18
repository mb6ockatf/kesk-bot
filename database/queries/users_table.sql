CREATE TABLE IF NOT EXISTS users (
    id       SERIAL,
    userid   int,
    username varchar(64),
    lang     char(2),
    UNIQUE   (userid)
);
