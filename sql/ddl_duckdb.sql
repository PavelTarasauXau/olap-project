-- З03/З06. DDL для DuckDB с поддержкой SCD2 для товаров.

DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_promotion;
DROP TABLE IF EXISTS dim_store;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_date;

-- Справочник магазинов
CREATE TABLE dim_store (
    store_id    INTEGER PRIMARY KEY,
    store_name  VARCHAR NOT NULL,
    city        VARCHAR NOT NULL,
    region      VARCHAR NOT NULL,
    store_type  VARCHAR NOT NULL,
    area_sq_m   INTEGER NOT NULL
);

-- Справочник товаров (SCD2: есть суррогатный ключ, бизнес-ключ и интервалы действия)
CREATE TABLE dim_product (
    product_surrogate_id INTEGER PRIMARY KEY,
    product_bk           INTEGER NOT NULL,
    product_name         VARCHAR NOT NULL,
    category             VARCHAR NOT NULL,
    brand                VARCHAR NOT NULL,
    production_date      DATE NOT NULL,
    shelf_life_days      INTEGER NOT NULL,
    unit_cost            DECIMAL(12, 2) NOT NULL,
    unit_price           DECIMAL(12, 2) NOT NULL,
    valid_from           DATE NOT NULL,
    valid_to             DATE NOT NULL,
    is_current           BOOLEAN NOT NULL
);

-- Справочник дат
CREATE TABLE dim_date (
    date_id     INTEGER PRIMARY KEY,
    full_date   DATE NOT NULL,
    year        SMALLINT NOT NULL,
    month       TINYINT NOT NULL,
    month_name  VARCHAR NOT NULL,
    day_of_week TINYINT NOT NULL
);

-- Справочник промоакций
CREATE TABLE dim_promotion (
    promo_id          INTEGER PRIMARY KEY,
    promo_name        VARCHAR NOT NULL,
    discount_percent  INTEGER NOT NULL,
    promo_type        VARCHAR NOT NULL
);

-- Таблица фактов продаж (ссылается на версию товара через product_surrogate_id)
CREATE TABLE fact_sales (
    sale_id              BIGINT PRIMARY KEY,
    date_id              INTEGER NOT NULL,
    store_id             INTEGER NOT NULL,
    product_surrogate_id INTEGER NOT NULL,
    promo_id             INTEGER NOT NULL,
    qty                  INTEGER NOT NULL,
    amount               DECIMAL(12, 2) NOT NULL
);