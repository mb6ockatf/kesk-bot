CREATE TABLE IF NOT EXISTS market (
    id        SERIAL,
    dish_name varchar(50) NOT NULL UNIQUE,
    quantity  int DEFAULT 0
);