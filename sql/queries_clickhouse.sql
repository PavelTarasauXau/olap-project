-- З08. Аналитические запросы для ClickHouse

-- 1. Эталон главной метрики (оборот и количество)
SELECT 
    sum(amount) AS total_turnover, 
    sum(qty) AS total_qty 
FROM retail_dw.fact_sales;

-- 2. Оборот и маржинальность по типам магазинов
SELECT 
    s.store_type,
    count(DISTINCT s.store_id) AS stores_count,
    sum(f.amount) AS turnover,
    sum(f.qty) AS total_qty,
    round(sum(f.amount) - sum(p.unit_cost * f.qty), 2) AS total_margin
FROM retail_dw.fact_sales f
JOIN retail_dw.dim_store s ON f.store_id = s.store_id
JOIN retail_dw.dim_product p ON f.product_surrogate_id = p.product_surrogate_id
GROUP BY s.store_type
ORDER BY turnover DESC;

-- 3. Оборот по категориям и брендам с учетом версий товаров (SCD2)
SELECT 
    p.category,
    p.brand,
    p.shelf_life_days,
    sum(f.amount) AS turnover,
    sum(f.qty) AS total_qty,
    rank() OVER (PARTITION BY p.category ORDER BY sum(f.amount) DESC) AS brand_rank_in_category
FROM retail_dw.fact_sales f
JOIN retail_dw.dim_product p ON f.product_surrogate_id = p.product_surrogate_id
GROUP BY p.category, p.brand, p.shelf_life_days
ORDER BY p.category, turnover DESC;