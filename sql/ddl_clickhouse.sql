-- З07. DDL для ClickHouse с принудительным пересозданием таблиц

CREATE DATABASE IF NOT EXISTS retail_dw;

-- Удаляем старые таблицы, чтобы обновить схему под новые колонки
DROP TABLE IF EXISTS retail_dw.fact_sales;
DROP TABLE IF EXISTS retail_dw.dim_product;
DROP TABLE IF EXISTS retail_dw.dim_store;
DROP TABLE IF EXISTS retail_dw.dim_date;
DROP TABLE IF EXISTS retail_dw.dim_promotion;

-- 1. Справочник магазинов
CREATE TABLE retail_dw.dim_store (
    store_id    UInt32,
    store_name  String,
    city        String,
    region      String,
    store_type  String,
    area_sq_m   UInt16
) ENGINE = MergeTree()
ORDER BY (region, city, store_id);

-- 2. Справочник товаров (с поддержкой SCD2)
-- 2. Справочник товаров (с поддержкой SCD2)
CREATE TABLE retail_dw.dim_product (
    product_surrogate_id UInt32,
    product_bk           UInt32,
    product_name         String,
    category             String,
    brand                String,
    production_date      Date,
    shelf_life_days      UInt16,
    unit_cost            Decimal(12, 2),
    unit_price           Decimal(12, 2),
    valid_from           Date,
    valid_to             Date32,          -- <--- Изменили Date на Date32
    is_current           UInt8
) ENGINE = MergeTree()
ORDER BY (category, brand, product_bk);

-- 3. Справочник дат
CREATE TABLE retail_dw.dim_date (
    date_id     UInt32,
    full_date   Date,
    year        UInt16,
    month       UInt8,
    month_name  String,
    day_of_week UInt8
) ENGINE = MergeTree()
ORDER BY date_id;

-- 4. Справочник промоакций
CREATE TABLE retail_dw.dim_promotion (
    promo_id          UInt32,
    promo_name        String,
    discount_percent  UInt8,
    promo_type        String
) ENGINE = MergeTree()
ORDER BY promo_id;

-- 5. Таблица фактов продаж
CREATE TABLE retail_dw.fact_sales (
    sale_id              UInt64,
    date_id              UInt32,
    store_id             UInt32,
    product_surrogate_id UInt32,
    promo_id             UInt32,
    qty                  Int32,
    amount               Decimal(12, 2)
) ENGINE = MergeTree()
ORDER BY (date_id, store_id, product_surrogate_id);