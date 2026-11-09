-- З03. DDL для DuckDB. Модель — по passport.md (с учетом расширенных справочников и промо).

DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_promotion;
DROP TABLE IF EXISTS dim_store;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_date;

-- Справочник магазинов (с типом и площадью)
CREATE TABLE dim_store (
    store_id    INTEGER PRIMARY KEY,
    store_name  VARCHAR NOT NULL,
    city        VARCHAR NOT NULL,
    region      VARCHAR NOT NULL,
    store_type  VARCHAR NOT NULL,
    area_sq_m   INTEGER NOT NULL
);

-- Справочник товаров (с датой производства, сроком годности, себестоимостью и ценой)
CREATE TABLE dim_product (
    product_id        INTEGER PRIMARY KEY,
    product_name      VARCHAR NOT NULL,
    category          VARCHAR NOT NULL,
    brand             VARCHAR NOT NULL,
    production_date   DATE NOT NULL,
    shelf_life_days   INTEGER NOT NULL,
    unit_cost         DECIMAL(12, 2) NOT NULL,
    unit_price        DECIMAL(12, 2) NOT NULL
);

-- Справочник дат
CREATE TABLE dim_date (
    date_id     INTEGER PRIMARY KEY,   -- YYYYMMDD
    full_date   DATE NOT NULL,
    year        SMALLINT NOT NULL,
    month       TINYINT NOT NULL,
    month_name  VARCHAR NOT NULL,
    day_of_week TINYINT NOT NULL       -- 1 = понедельник
);

-- Справочник промоакций (новая таблица)
CREATE TABLE dim_promotion (
    promo_id          INTEGER PRIMARY KEY,
    promo_name        VARCHAR NOT NULL,
    discount_percent  INTEGER NOT NULL,
    promo_type        VARCHAR NOT NULL
);

-- Таблица фактов продаж
-- Одна строка = одна позиция в чеке: товар в магазине за день с учетом промоакции
CREATE TABLE fact_sales (
    sale_id     BIGINT PRIMARY KEY,
    date_id     INTEGER NOT NULL,
    store_id    INTEGER NOT NULL,
    product_id  INTEGER NOT NULL,
    promo_id    INTEGER NOT NULL,
    qty         INTEGER NOT NULL,
    amount      DECIMAL(12, 2) NOT NULL
);