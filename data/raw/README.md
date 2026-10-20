# Исходные файлы (data/raw)

Домен: розничные продажи. Копия учебного sample курса.

| Файл | Строк | Поля |
|------|-------|------|
| `fact_sales.csv` | 15 | `sale_id` — id продажи; `date_id` — ключ даты (YYYYMMDD); `store_id` — ключ магазина; `product_id` — ключ товара; `qty` — количество; `amount` — сумма продажи |
| `dim_store.csv` | 5 | `store_id`, `store_name` — название магазина, `city` — город, `region` — регион |
| `dim_product.csv` | 8 | `product_id`, `product_name` — название товара, `category` — категория, `brand` — бренд |
| `dim_date.csv` | 8 | `date_id`, `full_date` — дата, `year`, `month`, `month_name`, `day_of_week` (1 = понедельник) |

Связи: `fact_sales.date_id → dim_date`, `fact_sales.store_id → dim_store`, `fact_sales.product_id → dim_product` (схема «звезда»).
