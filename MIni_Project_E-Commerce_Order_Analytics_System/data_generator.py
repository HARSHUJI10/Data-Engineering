"""
data_generator.py
------------------
Generates 4 raw CSV files for the E-Commerce Order Analytics System:
  - customers.csv
  - products.csv
  - orders.csv
  - order_items.csv

Intentional data quality issues are injected on purpose so that the
cleaning phase (data_cleaning.py) has real problems to solve:
  - 5% of orders have a NULL/empty customer_id
  - 3% of order_items have a negative quantity (returns)
  - Some order_date values use the wrong format (DD-MM-YYYY instead of
    YYYY-MM-DD HH:MM:SS)
  - Some product names have extra whitespace / inconsistent casing
  - 2% of customer emails are invalid (missing '@' or missing domain)

Every order_id used in order_items.csv is guaranteed to exist in
orders.csv, so referential integrity holds by construction (the
cleaning script still checks for it, since in a real pipeline that
guarantee wouldn't exist).
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

N_CUSTOMERS = 600
N_PRODUCTS = 550
N_ORDERS = 3000
# order_items will end up being roughly 2-4 line items per order (~7500 rows)

OUT_DIR = "raw_data"

FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh",
               "Ishaan", "Kabir", "Ananya", "Diya", "Isha", "Myra", "Sara",
               "Aisha", "Priya", "Neha", "Rohan", "Karan", "Meera", "Tanvi",
               "Yash", "Nisha", "Rahul", "Simran", "Aman", "Pooja", "Rajat"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Iyer", "Nair", "Reddy", "Singh",
              "Khan", "Patel", "Mehta", "Kapoor", "Chopra", "Joshi", "Rao",
              "Das", "Bose", "Malhotra", "Bhatt", "Ahluwalia", "Menon"]

CATEGORIES = {
    "Electronics": ["Mobiles", "Laptops", "Headphones", "Cameras", "Accessories"],
    "Clothing": ["Men", "Women", "Kids", "Footwear", "Winterwear"],
    "Home": ["Kitchen", "Furniture", "Decor", "Bedding", "Storage"],
    "Books": ["Fiction", "Non-Fiction", "Academic", "Comics", "Self-Help"],
}

PRODUCT_ADJ = ["Premium", "Classic", "Ultra", "Pro", "Eco", "Smart", "Compact",
               "Deluxe", "Essential", "Portable"]
PRODUCT_NOUN = {
    "Mobiles": "Smartphone", "Laptops": "Laptop", "Headphones": "Headphone",
    "Cameras": "Camera", "Accessories": "Charger",
    "Men": "T-Shirt", "Women": "Dress", "Kids": "Playsuit",
    "Footwear": "Sneakers", "Winterwear": "Jacket",
    "Kitchen": "Cookware Set", "Furniture": "Chair", "Decor": "Wall Art",
    "Bedding": "Bedsheet Set", "Storage": "Storage Box",
    "Fiction": "Novel", "Non-Fiction": "Biography", "Academic": "Textbook",
    "Comics": "Comic Book", "Self-Help": "Guidebook",
}

ORDER_STATUSES = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
STATUS_WEIGHTS = [0.15, 0.15, 0.5, 0.1, 0.1]
CUSTOMER_TYPES = ["REGULAR", "PREMIUM", "VIP"]
CUSTOMER_TYPE_WEIGHTS = [0.6, 0.3, 0.1]
REGIONS = ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL"]

START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2026, 7, 31)


def random_date(start, end):
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def make_email(name, idx, bad=False):
    base = name.lower().replace(" ", ".")
    if bad:
        choice = random.choice(["no_at", "no_domain"])
        if choice == "no_at":
            return f"{base}{idx}gmail.com"          # missing '@'
        else:
            return f"{base}{idx}@"                   # missing domain
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "rediffmail.com"])
    return f"{base}{idx}@{domain}"


def generate_customers():
    rows = []
    for cid in range(1, N_CUSTOMERS + 1):
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        full_name = f"{fname} {lname}"
        is_bad_email = random.random() < 0.02          # 2% invalid emails
        email = make_email(full_name, cid, bad=is_bad_email)
        reg_date = random_date(START_DATE, END_DATE - timedelta(days=1))
        ctype = random.choices(CUSTOMER_TYPES, weights=CUSTOMER_TYPE_WEIGHTS)[0]
        rows.append({
            "customer_id": cid,
            "customer_name": full_name,
            "email": email,
            "registration_date": reg_date.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_type": ctype,
        })
    with open(f"{OUT_DIR}/customers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def generate_products():
    rows = []
    for pid in range(1, N_PRODUCTS + 1):
        category = random.choice(list(CATEGORIES.keys()))
        subcategory = random.choice(CATEGORIES[category])
        adj = random.choice(PRODUCT_ADJ)
        noun = PRODUCT_NOUN[subcategory]
        name = f"{adj} {noun} {pid}"

        # Inject messy formatting into ~15% of product names
        if random.random() < 0.15:
            style = random.choice(["upper", "lower", "spaces"])
            if style == "upper":
                name = name.upper()
            elif style == "lower":
                name = name.lower()
            else:
                name = f"  {name}   "

        cost_price = round(random.uniform(50, 25000), 2)
        rows.append({
            "product_id": pid,
            "product_name": name,
            "category": category,
            "subcategory": subcategory,
            "cost_price": cost_price,
        })
    with open(f"{OUT_DIR}/products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def generate_orders(customers):
    rows = []
    customer_ids = [c["customer_id"] for c in customers]
    for oid in range(1, N_ORDERS + 1):
        has_customer = random.random() >= 0.05          # 5% missing customer_id
        customer_id = random.choice(customer_ids) if has_customer else ""
        order_dt = random_date(START_DATE, END_DATE)
        status = random.choices(ORDER_STATUSES, weights=STATUS_WEIGHTS)[0]
        region = random.choice(REGIONS)

        # ~8% of orders get the wrong date format (DD-MM-YYYY, no time)
        if random.random() < 0.08:
            date_str = order_dt.strftime("%d-%m-%Y")
        else:
            date_str = order_dt.strftime("%Y-%m-%d %H:%M:%S")

        rows.append({
            "order_id": oid,
            "customer_id": customer_id,
            "order_date": date_str,
            "status": status,
            "region_code": region,
            "_sort_dt": order_dt,   # helper only, stripped before writing
        })

    with open(f"{OUT_DIR}/orders.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = ["order_id", "customer_id", "order_date", "status", "region_code"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r[k] for k in fieldnames})
    return rows


def generate_order_items(orders, products):
    rows = []
    item_id = 1
    product_ids = [p["product_id"] for p in products]
    for order in orders:
        n_items = random.randint(1, 4)
        chosen_products = random.sample(product_ids, k=min(n_items, len(product_ids)))
        for pid in chosen_products:
            is_return = random.random() < 0.03           # 3% negative quantity
            quantity = -random.randint(1, 3) if is_return else random.randint(1, 5)
            unit_price = round(random.uniform(100, 30000), 2)
            discount_percent = round(random.uniform(0, 50), 1)
            rows.append({
                "item_id": item_id,
                "order_id": order["order_id"],
                "product_id": pid,
                "quantity": quantity,
                "unit_price": unit_price,
                "discount_percent": discount_percent,
            })
            item_id += 1
    with open(f"{OUT_DIR}/order_items.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main():
    print("Generating customers.csv ...")
    customers = generate_customers()
    print(f"  -> {len(customers)} rows")

    print("Generating products.csv ...")
    products = generate_products()
    print(f"  -> {len(products)} rows")

    print("Generating orders.csv ...")
    orders = generate_orders(customers)
    print(f"  -> {len(orders)} rows")

    print("Generating order_items.csv ...")
    order_items = generate_order_items(orders, products)
    print(f"  -> {len(order_items)} rows")

    print("\nAll raw CSV files written to ./raw_data/")


if __name__ == "__main__":
    main()
