"""
ELT-скрипт для загрузки витрины данных розницы в DuckDB.
Порядок выполнения:
1. Пересоздание структуры таблиц (DDL) — защита от задвоения при повторных прогонах.
2. Поочередная загрузка справочников, затем таблицы фактов.
3. Проверка качества данных (Data Quality): поиск пустых и "висячих" ключей.
4. Расчет главной метрики (оборот).
"""

from pathlib import Path
import os
import duckdb

def run_pipeline():
    # Определяем корневую папку проекта (на уровень выше папки etl)
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    
    db_path = root / "olap.duckdb"
    print(f"[*] Подключение к базе данных: {db_path}")
    con = duckdb.connect(str(db_path))

    print("\n--- ШАГ 1: Создание структуры таблиц (DDL) ---")
    # Переинициализация таблиц защищает от удвоения данных при повторном запуске
    ddl_path = root / "sql" / "ddl_duckdb.sql"
    con.execute(ddl_path.read_text(encoding="utf-8"))
    print("[+] Таблицы успешно пересозданы (старые данные очищены).")

    print("\n--- ШАГ 2: Загрузка сырых данных (Сначала справочники, потом факт) ---")
    load_path = root / "sql" / "load_duckdb.sql"
    con.execute(load_path.read_text(encoding="utf-8"))
    print("[+] Данные из CSV успешно загружены в витрину.")

    print("\n--- ШАГ 3: Проверка качества данных (Data Quality Checks) ---")
    
    # 1. Проверка количества строк
    print("\n[Проверка 1] Количество строк в таблицах:")
    row_counts_query = """
        SELECT 'dim_store' AS tbl, count(*) AS rows FROM dim_store
        UNION ALL SELECT 'dim_product', count(*) FROM dim_product
        UNION ALL SELECT 'dim_date', count(*) FROM dim_date
        UNION ALL SELECT 'dim_promotion', count(*) FROM dim_promotion
        UNION ALL SELECT 'fact_sales', count(*) FROM fact_sales;
    """
    for row in con.execute(row_counts_query).fetchall():
        print(f"   -> Таблица {row[0]}: {row[1]} строк")

    # 2. Проверка на пустые и «висячие» ключи (orphan keys)
    print("\n[Проверка 2] Поиск битых связей и пустых ключей (должно быть 0):")
    dq_query = """
        SELECT
            count(*) FILTER (WHERE f.date_id IS NULL OR f.store_id IS NULL OR f.product_id IS NULL OR f.promo_id IS NULL) AS null_keys,
            count(*) FILTER (WHERE d.date_id IS NULL) AS orphan_date,
            count(*) FILTER (WHERE s.store_id IS NULL) AS orphan_store,
            count(*) FILTER (WHERE p.product_id IS NULL) AS orphan_product,
            count(*) FILTER (WHERE pr.promo_id IS NULL) AS orphan_promo
        FROM fact_sales f
        LEFT JOIN dim_date      d  ON f.date_id    = d.date_id
        LEFT JOIN dim_store     s  ON f.store_id   = s.store_id
        LEFT JOIN dim_product   p  ON f.product_id = p.product_id
        LEFT JOIN dim_promotion pr ON f.promo_id   = pr.promo_id;
    """
    dq_result = con.execute(dq_query).fetchone()
    print(f"   -> Null-ключи в фактах: {dq_result[0]}")
    print(f"   -> Сироты по датам: {dq_result[1]}")
    print(f"   -> Сироты по магазинам: {dq_result[2]}")
    print(f"   -> Сироты по товарам: {dq_result[3]}")
    print(f"   -> Сироты по промоакциям: {dq_result[4]}")
    
    # Если найдены битые ключи — аварийно прерываем процесс
    if sum(dq_result) > 0:
        raise ValueError("[!] ОШИБКА КАЧЕСТВА ДАННЫХ: Обнаружены битые ключи или NULL! Загрузка прервана.")
    else:
        print("   [+] Проверка целостности успешно пройдена (ошибок нет).")

    print("\n--- ШАГ 4: Расчет главной метрики ---")
    metric_query = "SELECT sum(amount) AS total_turnover, sum(qty) AS total_qty FROM fact_sales;"
    metric_result = con.execute(metric_query).fetchone()
    print(f"   -> Суммарный оборот (total_turnover): {metric_result[0]}")
    print(f"   -> Общее количество проданных товаров (total_qty): {metric_result[1]}")

    print("\n[SUCCESS] ELT-пайплайн успешно завершен!")
    con.close()

if __name__ == "__main__":
    run_pipeline()