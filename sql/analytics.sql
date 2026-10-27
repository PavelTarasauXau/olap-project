-- Аналитические запросы к модели из passport.md.
-- Каждый запрос отвечает на вопрос из паспорта. Запускать: python scripts/run_analytics.py

-- Вопрос 1 -> «Какой оборот по регионам за январь 2024?»
-- WHERE (январь 2024) + GROUP BY (регион)
SELECT s.region,
       sum(f.amount) AS turnover
FROM fact_sales f
JOIN dim_store s ON f.store_id = s.store_id
JOIN dim_date  d ON f.date_id  = d.date_id
WHERE d.year = 2024 AND d.month = 1
GROUP BY s.region
ORDER BY turnover DESC;

-- Вопрос 2 -> «Какие категории дают наибольший оборот?»
-- GROUP BY + окно: доля категории в общем обороте и место в рейтинге
SELECT p.category,
       sum(f.amount) AS turnover,
       round(100.0 * sum(f.amount) / sum(sum(f.amount)) OVER (), 1) AS share_pct,
       rank() OVER (ORDER BY sum(f.amount) DESC) AS rnk
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY rnk;

-- Вопрос 3 -> «Как менялись оборот и количество по месяцам?»
-- GROUP BY (месяц) + окно lag(): оборот предыдущего месяца
SELECT d.year,
       d.month,
       sum(f.amount) AS turnover,
       sum(f.qty)    AS total_qty,
       lag(sum(f.amount)) OVER (ORDER BY d.year, d.month) AS prev_month_turnover
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
