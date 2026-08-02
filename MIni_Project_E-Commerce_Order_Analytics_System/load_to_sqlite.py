"""
load_to_sqlite.py
------------------
Creates the SQLite schema (with PK / FK / NOT NULL constraints) and
loads the cleaned CSV files into ecommerce.db. Prints row counts at
the end to verify the load.
"""

import sqlite3
import pandas as pd
import os

DB_PATH = "ecommerce.db"
CLEAN_DIR = "cleaned_data"

SCHEMA = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id        INTEGER PRIMARY KEY,
    customer_name       TEXT NOT NULL,
    email               TEXT,
    registration_date   TEXT NOT NULL,
    customer_type       TEXT NOT NULL CHECK (customer_type IN ('REGULAR','PREMIUM','VIP'))
);

CREATE TABLE products (
    product_id      INTEGER PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category        TEXT NOT NULL,
    subcategory     TEXT NOT NULL,
    cost_price      REAL NOT NULL
);

CREATE TABLE orders (
    order_id        INTEGER PRIMARY KEY,
    customer_id     INTEGER,
    order_date      TEXT NOT NULL,
    status          TEXT NOT NULL CHECK (status IN ('PLACED','SHIPPED','DELIVERED','CANCELLED','RETURNED')),
    region_code     TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    item_id             INTEGER PRIMARY KEY,
    order_id            INTEGER NOT NULL,
    product_id          INTEGER NOT NULL,
    quantity            INTEGER NOT NULL,
    unit_price          REAL NOT NULL,
    discount_percent    REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_items_order ON order_items(order_id);
CREATE INDEX idx_items_product ON order_items(product_id);
"""


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    conn.commit()

    # Load in dependency order: customers, products -> orders -> order_items
    customers = pd.read_csv(f"{CLEAN_DIR}/customers_clean.csv")
    products = pd.read_csv(f"{CLEAN_DIR}/products_clean.csv")
    orders = pd.read_csv(f"{CLEAN_DIR}/orders_clean.csv")
    order_items = pd.read_csv(f"{CLEAN_DIR}/order_items_clean.csv")

    # customer_id may be float (NaN present) after CSV round-trip; normalize
    orders["customer_id"] = orders["customer_id"].astype("Int64")

    customers.to_sql("customers", conn, if_exists="append", index=False)
    products.to_sql("products", conn, if_exists="append", index=False)
    orders.to_sql("orders", conn, if_exists="append", index=False)
    order_items.to_sql("order_items", conn, if_exists="append", index=False)

    conn.commit()

    print("Load complete. Row counts:")
    for table in ["customers", "products", "orders", "order_items"]:
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:15s} {count}")

    conn.close()
    print(f"\nDatabase written to {DB_PATH}")


if __name__ == "__main__":
    main()
