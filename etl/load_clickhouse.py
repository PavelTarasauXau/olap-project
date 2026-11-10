"""
Скрипт загрузки витрины данных в ClickHouse и сверки с DuckDB (З07).
- Полная очистка таблиц перед заливкой (защита от дублей).
- Загрузка справочников и фактов из CSV с обработкой дат и пустых значений.
- Автоматическая сверка count(*) и суммарного оборота с DuckDB.
"""

from pathlib import Path
import os
import duckdb
import pandas as pd
import clickhouse_connect

def run_clickhouse_etl():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    
    duck_path = root / "olap.duckdb"
    print(f"[*] Подключение к локальной DuckDB: {duck_path}")
    duck_con = duckdb.connect(str(duck_path), read_only=True)

    print("[*] Подключение к ClickHouse (localhost:8123)...")
    ch_client = clickhouse_connect.get_client(host='localhost', port=8123, username='default', password='')

    print("\n--- ШАГ 1: Создание структуры таблиц в ClickHouse (DDL) ---")
    ddl_path = root / "sql" / "ddl_clickhouse.sql"
    for statement in ddl_path.read_text(encoding="utf-8").split(';'):
        if statement.strip():
            ch_client.command(statement)
    print("[+] DDL для ClickHouse успешно выполнен.")

    print("\n--- ШАГ 2: Очистка таблиц в ClickHouse (защита от дублей) ---")
    tables = ['fact_sales', 'dim_promotion', 'dim_date', 'dim_product', 'dim_store']
    for tbl in tables:
        ch_client.command(f"TRUNCATE TABLE IF EXISTS retail_dw.{tbl}")
    print("[+] Таблицы очищены.")

    print("\n--- ШАГ 3: Загрузка данных из CSV в ClickHouse ---")
    
    csv_mapping = [
            ('dim_store', root / 'data/dim_store.csv', []),
            ('dim_product', root / 'data/dim_product.csv', ['production_date', 'valid_from', 'valid_to']),
            ('dim_date', root / 'data/dim_date.csv', ['full_date']),
            ('dim_promotion', root / 'data/dim_promotion.csv', []),
            ('fact_sales', root / 'data/fact_sales.csv', [])
        ]

    for tbl_name, csv_path, date_cols in csv_mapping:
        print(f"   -> Загрузка {tbl_name} из {csv_path.name}...")
        with open(csv_path, 'rb') as f:
            df = pd.read_csv(f)
            
            # Конвертируем даты
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col]).dt.date
            
            # Заменяем пустые значения (NaN/None) на пустые строки для текста и 0 для чисел
            df = df.fillna({
                col: "" for col in df.select_dtypes(include=['object', 'string']).columns
            }).fillna(0)
            
            ch_client.insert_df(f"retail_dw.{tbl_name}", df)
            
    print("[+] Все данные успешно залиты в ClickHouse.")

    print("\n--- ШАГ 4: Сверка метрик DuckDB <-> ClickHouse ---")
    
    validation_queries = {
        "fact_sales count": ("SELECT count(*) FROM fact_sales", "SELECT count(*) FROM retail_dw.fact_sales"),
        "total_turnover": ("SELECT sum(amount) FROM fact_sales", "SELECT sum(amount) FROM retail_dw.fact_sales"),
        "total_qty": ("SELECT sum(qty) FROM fact_sales", "SELECT sum(qty) FROM retail_dw.fact_sales")
    }

    all_matched = True
    for metric_name, (duck_q, ch_q) in validation_queries.items():
        duck_val = duck_con.execute(duck_q).fetchone()[0]
        ch_val = ch_client.query(ch_q).result_rows[0][0]
        
        match = (str(duck_val) == str(ch_val))
        status = "[OK] Сходятся" if match else "[FAIL] РАСХОЖДЕНИЕ!"
        print(f"   -> {metric_name}: DuckDB = {duck_val} | ClickHouse = {ch_val} --> {status}")
        
        if not match:
            all_matched = False

    duck_con.close()
    
    if all_matched:
        print("\n[SUCCESS] Сверка прошла идеально! ClickHouse полностью синхронизирован с DuckDB.")
    else:
        print("\n[!] ВНИМАНИЕ: Обнаружены расхождения в метриках.")

if __name__ == "__main__":
    run_clickhouse_etl()