-- З04. Аналитические запросы к модели из passport.md (с учетом новых данных).

-- Вопрос 1 -> «Какой суммарный оборот и маржинальность приносят разные типы магазинов (store_type)?»
-- GROUP BY + расчет маржи на лету (оборот минус себестоимость * количество)
SELECT 
    s.store_type,
    count(DISTINCT s.store_id) AS stores_count,
    sum(f.amount) AS turnover,
    sum(f.qty) AS total_qty,
    round(sum(f.amount) - sum(p.unit_cost * f.qty), 2) AS total_margin
FROM fact_sales f
JOIN dim_store s ON f.store_id = s.store_id
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY s.store_type
ORDER BY turnover DESC;


-- Вопрос 2 -> «Как наличие промоакций (promo_type) влияет на средний объем проданных единиц товара за чек?»
-- GROUP BY + оконная функция для расчета доли каждого типа промо в общем обороте
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


-- Вопрос 3 -> «Какой оборот дают различные категории товаров с учетом их срока годности и брендов?»
-- GROUP BY + оконная функция rank() для ранжирования категорий и брендов внутри категорий
SELECT 
    p.category,
    p.brand,
    p.shelf_life_days,
    sum(f.amount) AS turnover,
    sum(f.qty) AS total_qty,
    rank() OVER (PARTITION BY p.category ORDER BY sum(f.amount) DESC) as brand_rank_in_category
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category, p.brand, p.shelf_life_days
ORDER BY p.category, turnover DESC;