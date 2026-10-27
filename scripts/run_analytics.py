"""Запускает sql/canonical_metric.sql и sql/analytics.sql на olap.duckdb и печатает результаты.
Сначала должна быть собрана база: python scripts/build_duckdb.py"""
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[1]
con = duckdb.connect(str(root / "olap.duckdb"), read_only=True)

for name in ("canonical_metric", "analytics"):
    print("=====", name)
    text = (root / "sql" / f"{name}.sql").read_text(encoding="utf-8")
    for stmt in [s.strip() for s in text.split(";") if "SELECT" in s]:
        cur = con.execute(stmt)
        print([c[0] for c in cur.description])
        for row in cur.fetchall():
            print(row)
        print()
