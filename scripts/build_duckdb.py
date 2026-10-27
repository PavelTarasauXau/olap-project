"""Создаёт olap.duckdb: DDL -> загрузка из data/raw -> проверки.
Запуск из любой папки: python scripts/build_duckdb.py
Повторный запуск безопасен: таблицы пересоздаются, продажи не удваиваются."""
from pathlib import Path
import os
import duckdb

root = Path(__file__).resolve().parents[1]
os.chdir(root)  # пути в load_duckdb.sql относительные
con = duckdb.connect(str(root / "olap.duckdb"))

for name in ("ddl_duckdb", "load_duckdb"):
    con.execute((root / "sql" / f"{name}.sql").read_text(encoding="utf-8"))

checks = (root / "sql" / "checks_duckdb.sql").read_text(encoding="utf-8")
for stmt in [s.strip() for s in checks.split(";") if "SELECT" in s]:
    cur = con.execute(stmt)
    print([c[0] for c in cur.description])
    for row in cur.fetchall():
        print(row)
    print()
print("OK ->", root / "olap.duckdb")
