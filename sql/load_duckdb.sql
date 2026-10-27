-- Загрузка из data/raw/. Запускать после ddl_duckdb.sql (пути — от корня проекта).
COPY dim_store   FROM 'data/raw/dim_store.csv'   (HEADER, DELIMITER ',');
COPY dim_product FROM 'data/raw/dim_product.csv' (HEADER, DELIMITER ',');
COPY dim_date    FROM 'data/raw/dim_date.csv'    (HEADER, DELIMITER ',');
COPY fact_sales  FROM 'data/raw/fact_sales.csv'  (HEADER, DELIMITER ',');
