-- DDL для DuckDB. Модель — по passport.md.
-- Скрипт можно запускать повторно: сначала таблицы удаляются, потом создаются заново.

DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_store;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_store (
    store_id   INTEGER PRIMARY KEY,
    store_name VARCHAR NOT NULL,
    city       VARCHAR NOT NULL,
    region     VARCHAR NOT NULL
);

CREATE TABLE dim_product (
    product_id   INTEGER PRIMARY KEY,
    product_name VARCHAR NOT NULL,
    category     VARCHAR NOT NULL,
    brand        VARCHAR NOT NULL
);

CREATE TABLE dim_date (
    date_id     INTEGER PRIMARY KEY,   -- YYYYMMDD
    full_date   DATE NOT NULL,
    year        SMALLINT NOT NULL,
    month       TINYINT NOT NULL,
    month_name  VARCHAR NOT NULL,
    day_of_week TINYINT NOT NULL       -- 1 = понедельник
);

-- Одна строка = одна позиция в чеке: товар в магазине за день (см. passport.md)
CREATE TABLE fact_sales (
    sale_id    BIGINT PRIMARY KEY,
    date_id    INTEGER NOT NULL,
    store_id   INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    qty        INTEGER NOT NULL,
    amount     DECIMAL(12, 2) NOT NULL
);
