-- З06. Демонстрация SCD2: вывод двух версий товара с бизнес-ключом 101 (Молоко 1л)
SELECT 
    product_surrogate_id,
    product_bk,
    product_name,
    category,
    unit_price,
    valid_from,
    valid_to,
    is_current
FROM dim_product
WHERE product_bk = 101;