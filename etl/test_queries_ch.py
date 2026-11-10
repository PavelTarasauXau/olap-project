"""
Скрипт проверки аналитических запросов в ClickHouse (З08).
Выполняет эталонную метрику и бизнес-запросы из витрины retail_dw.
"""

from pathlib import Path
import os
import clickhouse_connect

def test_queries():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    
    print("[*] Подключение к ClickHouse (localhost:8123)...")
    ch_client = clickhouse_connect.get_client(host='localhost', port=8123, username='default', password='')

    queries = {
        "1. Эталон главной метрики (Оборот и кол-во)": """
            SELECT 
                sum(amount) AS total_turnover, 
                sum(qty) AS total_qty 
            FROM retail_dw.fact_sales
        """,
        
        "2. Оборот и маржинальность по типам магазинов": """
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
            ORDER BY turnover DESC
        """,
        
        "3. Оборот по категориям и брендам (с учетом версий SCD2)": """
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
            ORDER BY p.category, turnover DESC
        """
    }

    for title, query in queries.items():
        print(f"\n==============================================")
        print(f" {title}")
        print(f"==============================================")
        result = ch_client.query(query)
        
        # Выводим заголовки
        print(" | ".join(result.column_names))
        print("-" * 50)
        
        # Выводим строки результата
        for row in result.result_rows:
            print(" | ".join(str(val) for val in row))

    print("\n[SUCCESS] Все аналитические запросы в ClickHouse выполнены успешно!")

if __name__ == "__main__":
    test_queries()