-- З04. Эталон главной метрики: СУММАРНЫЙ ОБОРОТ.
-- Оборот = сумма amount по всем строкам fact_sales с учетом промоакций.
-- Это же определение записано в passport.md. Если меняется одно — менять и другое.

SELECT sum(amount) AS total_turnover
FROM fact_sales;