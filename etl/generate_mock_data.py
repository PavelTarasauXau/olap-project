import csv
from datetime import datetime, timedelta
import random
from pathlib import Path

def generate_data():
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    data_dir.mkdir(exist_ok=True)

    print("[*] Генерация синтетических данных...")

    # 1. dim_store (20 магазинов)
    cities = [("Гродно", "Гродненская"), ("Минск", "Минская"), ("Брест", "Брестская"), ("Витебск", "Витебская")]
    store_types = ["Супермаркет", "Гипермаркет", "Дискаунтер", "Магазин у дома"]
    
    stores = []
    for store_id in range(1, 21):
        city, region = random.choice(cities)
        stores.append({
            "store_id": store_id,
            "store_name": f"Магазин №{store_id} ({city})",
            "city": city,
            "region": region,
            "store_type": random.choice(store_types),
            "area_sq_m": random.randint(150, 2500)
        })

    with open(data_dir / "dim_store.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=stores[0].keys())
        writer.writeheader()
        writer.writerows(stores)

    # 2. dim_product с SCD2 (около 150 товаров, часть с версиями)
    categories = ["Молочные продукты", "Бакалея", "Напитки", "Бытовая химия", "Сладости"]
    brands = ["Агропродукт", "Беллакт", "Савушкин", "Coca-Cola", "Лидское", "Nestle"]
    
    products = []
    surrogate_id = 1
    
    for bk in range(101, 251):
        cat = random.choice(categories)
        brand = random.choice(brands)
        name = f"Товар {bk} ({cat})"
        cost = round(random.uniform(1.0, 50.0), 2)
        price = round(cost * random.uniform(1.2, 1.8), 2)
        
        # Первая версия товара (действовала весь прошлый год)
        products.append({
            "product_surrogate_id": surrogate_id,
            "product_bk": bk,
            "product_name": name,
            "category": cat,
            "brand": brand,
            "production_date": "2025-01-10",
            "shelf_life_days": random.randint(30, 365),
            "unit_cost": cost,
            "unit_price": price,
            "valid_from": "2025-01-01",
            "valid_to": "2026-05-15",
            "is_current": 0
        })
        surrogate_id += 1

        # Вторая версия товара (актуальная с мая 2026, например, сменилась цена или категория)
        new_price = round(price * 1.1, 2) # инфляция / подорожание
        products.append({
            "product_surrogate_id": surrogate_id,
            "product_bk": bk,
            "product_name": name,
            "category": cat,
            "brand": brand,
            "production_date": "2026-04-10",
            "shelf_life_days": random.randint(30, 365),
            "unit_cost": cost,
            "unit_price": new_price,
            "valid_from": "2026-05-16",
            "valid_to": "9999-12-31",
            "is_current": 1
        })
        surrogate_id += 1

    with open(data_dir / "dim_product.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=products[0].keys())
        writer.writeheader()
        writer.writerows(products)

    # 3. dim_date (календарь за 2025-2026 годы)
    dates = []
    start_date = datetime(2025, 1, 1)
    for i in range(730): # 2 года
        cur = start_date + timedelta(days=i)
        dates.append({
            "date_id": int(cur.strftime("%Y%m%d")),
            "full_date": cur.strftime("%Y-%m-%d"),
            "year": cur.year,
            "month": cur.month,
            "month_name": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"][cur.month - 1],
            "day_of_week": cur.weekday() + 1
        })

    with open(data_dir / "dim_date.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=dates[0].keys())
        writer.writeheader()
        writer.writerows(dates)

    # 4. dim_promotion (промоакции)
    promos = [
        {"promo_id": 0, "promo_name": "Без промо", "discount_percent": 0, "promo_type": "None"},
        {"promo_id": 1, "promo_name": "Желтый ценник (-10%)", "discount_percent": 10, "promo_type": "Discount"},
        {"promo_id": 2, "promo_name": "Черная пятница (-25%)", "discount_percent": 25, "promo_type": "Sale"},
        {"promo_id": 3, "promo_name": "Товар недели (-15%)", "discount_percent": 15, "promo_type": "Weekly"}
    ]
    with open(data_dir / "dim_promotion.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=promos[0].keys())
        writer.writeheader()
        writer.writerows(promos)

    # 5. fact_sales (5000 фактов продаж)
    sales = []
    current_product_surrogates = [p["product_surrogate_id"] for p in products if p["is_current"] == 1]
    all_product_surrogates = [p["product_surrogate_id"] for p in products]
    
    for sale_id in range(1, 5001):
        date_item = random.choice(dates)
        store_id = random.randint(1, 20)
        
        # Выбираем версию товара в зависимости от даты продажи (чтобы соблюсти SCD2 историчность!)
        sale_date = datetime.strptime(date_item["full_date"], "%Y-%m-%d")
        if sale_date < datetime(2026, 5, 16):
            # Берем из старых версий (не current)
            valid_prods = [p["product_surrogate_id"] for p in products if p["is_current"] == 0]
        else:
            # Берем из актуальных версий
            valid_prods = current_product_surrogates
            
        prod_surrogate_id = random.choice(valid_prods)
        
        # Находим цену товара
        prod_info = next(p for p in products if p["product_surrogate_id"] == prod_surrogate_id)
        price = float(prod_info["unit_price"])
        
        promo = random.choice(promos)
        qty = random.randint(1, 10)
        
        # Считаем сумму с учетом скидки
        discount_factor = (100 - promo["discount_percent"]) / 100.0
        amount = round(price * qty * discount_factor, 2)

        sales.append({
            "sale_id": sale_id,
            "date_id": date_item["date_id"],
            "store_id": store_id,
            "product_surrogate_id": prod_surrogate_id,
            "promo_id": promo["promo_id"],
            "qty": qty,
            "amount": amount
        })

    with open(data_dir / "fact_sales.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=sales[0].keys())
        writer.writeheader()
        writer.writerows(sales)

    print("[+] Сгенерировано: 20 магазинов, 300 версий товаров, 730 дат, 4 промо и 5000 строк продаж!")

if __name__ == "__main__":
    generate_data()