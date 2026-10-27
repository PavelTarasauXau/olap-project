-- Эталон главной метрики: ОБОРОТ.
-- Оборот = сумма amount по всем строкам fact_sales (возвратов в данных нет).
-- Это же определение записано в passport.md. Если меняется одно — менять и другое.
SELECT sum(amount) AS turnover
FROM fact_sales;
-- на sample: 264.00
