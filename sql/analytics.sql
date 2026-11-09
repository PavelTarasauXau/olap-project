-- З04. Аналитические запросы к модели с учетом SCD2.

-- Вопрос 1 -> Оборот и маржинальность по типам магазинов
SELECT 
    s.store_type,
    count(DISTINCT s.store_id) AS stores_count,
    sum(f.amount) AS turnover,
    sum(f.qty) AS total_qty,
    round(sum(f.amount) - sum(p.unit_cost * f.qty), 2) AS total_margin
FROM fact_sales f
JOIN dim_store s ON f.store_id = s.store_id
JOIN dim_product p ON f.product_surrogate_id = p.product_surrogate_id
GROUP BY s.store_type
ORDER BY turnover DESC;

-- Вопрос 2 -> Влияние промоакций
SELECT 
    pr.promo_type,
    pr.promo_name,
    count(f.sale_id) AS sales_transactions,
    sum(f.qty) AS total_qty,
    round(avg(f.qty), 2) AS avg_qty_per_pos,
    sum(f.amount) AS turnover,
    round(100.0 * sum(f.amount) / sum(sum(f.amount)) OVER (), 1) AS turnover_share_pct
FROM fact_sales f
JOIN dim_promotion pr ON f.promo_id = pr.promo_id
GROUP BY pr.promo_type, pr.promo_name
ORDER BY turnover DESC;

-- Вопрос 3 -> Оборот по категориям и брендам с учетом версий товаров
SELECT 
    p.category,
    p.brand,
    p.shelf_life_days,
    sum(f.amount) AS turnover,
    sum(f.qty) AS total_qty,
    rank() OVER (PARTITION BY p.category ORDER BY sum(f.amount) DESC) as brand_rank_in_category
FROM fact_sales f
JOIN dim_product p ON f.product_surrogate_id = p.product_surrogate_id
GROUP BY p.category, p.brand, p.shelf_life_days
ORDER BY p.category, turnover DESC;