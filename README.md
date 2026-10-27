# Проект по дисциплине «Оперативный анализ данных»

- **ФИО:** _<впишите>_
- **Группа:** _<впишите>_
- **Домен:** розничные продажи (`retail_dw`)

## Что считаем (метрика и вопросы)

Используется учебный sample курса. Своя часть работы — аналитические вопросы:

- **Метрика:** выручка (`sum(amount)`) и количество проданных единиц (`sum(qty)`).
- Выручка по регионам и городам.
- Выручка по категориям товаров и по месяцам.
- Топ магазинов и брендов по выручке.

## Как поднять стенд

Нужен Docker Desktop (запущенный).

```bash
docker compose up -d
chmod +x scripts/init_ch.sh
./scripts/init_ch.sh                 # создаёт схему retail_dw и грузит CSV (обязательный шаг)
curl http://localhost:8123/ping      # → Ok.
docker exec -it olap_clickhouse clickhouse-client \
  --query "SELECT count() FROM retail_dw.fact_sales"   # → 15
```

Остановка: `docker compose down` (с удалением данных: `docker compose down -v`).

## Порты

| Сервис | Порт |
|--------|------|
| ClickHouse HTTP | 8123 |
| ClickHouse native | 9000 |
| Metabase | 3000 |

## DuckDB (локальная проверка окружения)

```bash
pip install duckdb
python scripts/duckdb_smoke.py
```

Ожидаемый вывод: `Запад: 153.50`, `Центр: 110.50`.

## Где лежит сырьё

`data/raw/` — CSV-файлы (копия sample курса). Описание полей — в [data/raw/README.md](data/raw/README.md).

## Структура

```
docker-compose.yml     # ClickHouse + Metabase
init/01_schema.sql     # DDL таблиц ClickHouse
scripts/               # init_ch.sh, duckdb_smoke.py
data/raw/              # исходные CSV
```

## DuckDB: таблицы и загрузка (З03)

```bash
python scripts/build_duckdb.py
```

Скрипт выполняет `sql/ddl_duckdb.sql` (создание таблиц), `sql/load_duckdb.sql` (загрузка из `data/raw/`) и `sql/checks_duckdb.sql` (проверки), результат пишет в `olap.duckdb`.

Повторный запуск безопасен: DDL сначала удаляет таблицы (`DROP TABLE IF EXISTS`) и создаёт их заново, поэтому продажи не удваиваются.

## Аналитический SQL (З04)

```bash
python scripts/build_duckdb.py      # собрать базу (если ещё нет)
python scripts/run_analytics.py     # выполнить sql/canonical_metric.sql и sql/analytics.sql
```

`sql/analytics.sql` — три запроса по вопросам из `passport.md` (в запросах 2 и 3 оконные функции), `sql/canonical_metric.sql` — эталон оборота.
