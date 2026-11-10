-- Загрузка из data/. Запускать после ddl_duckdb.sql (пути — от корня проекта).
COPY dim_store     FROM 'data/dim_store.csv'     (HEADER, DELIMITER ',');
COPY dim_product   FROM 'data/dim_product.csv'   (HEADER, DELIMITER ',');
COPY dim_date      FROM 'data/dim_date.csv'      (HEADER, DELIMITER ',');
COPY dim_promotion FROM 'data/dim_promotion.csv' (HEADER, DELIMITER ',');
COPY fact_sales    FROM 'data/fact_sales.csv'    (HEADER, DELIMITER ',');