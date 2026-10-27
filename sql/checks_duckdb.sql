-- 1. Число строк (в CSV: 5, 8, 8, 15)
SELECT 'dim_store' AS tbl, count(*) AS rows FROM dim_store
UNION ALL SELECT 'dim_product', count(*) FROM dim_product
UNION ALL SELECT 'dim_date',    count(*) FROM dim_date
UNION ALL SELECT 'fact_sales',  count(*) FROM fact_sales;

-- 2. Пустые и «висячие» ключи (везде должно быть 0)
SELECT
    count(*) FILTER (WHERE f.date_id    IS NULL OR f.store_id IS NULL OR f.product_id IS NULL) AS null_keys,
    count(*) FILTER (WHERE d.date_id    IS NULL) AS orphan_date,
    count(*) FILTER (WHERE s.store_id   IS NULL) AS orphan_store,
    count(*) FILTER (WHERE p.product_id IS NULL) AS orphan_product
FROM fact_sales f
LEFT JOIN dim_date    d ON f.date_id    = d.date_id
LEFT JOIN dim_store   s ON f.store_id   = s.store_id
LEFT JOIN dim_product p ON f.product_id = p.product_id;

-- 3. Главная метрика: оборот (в sample: 264.00)
SELECT sum(amount) AS turnover, sum(qty) AS total_qty FROM fact_sales;
