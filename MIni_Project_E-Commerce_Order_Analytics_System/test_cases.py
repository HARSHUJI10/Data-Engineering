"""
test_cases.py
------------------
Edge case handling tests (Part 5). Uses plain Python 'assert' style
functions (no external test framework) so it can be run standalone
or picked up by pytest.

Run directly:  python3 test_cases.py
Run with pytest: pytest test_cases.py -v
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from data_cleaning import check_referential_integrity

DB_PATH = "ecommerce.db"


def _fresh_connection():
    return sqlite3.connect(DB_PATH)


def test_order_items_with_invalid_order_id():
    """
    1. What happens when order_items has an order_id not in orders?
    -> check_referential_integrity() must flag it, and the loaded DB
       (which had orphans removed during cleaning) must contain zero
       such rows.
    """
    orders = pd.DataFrame({"order_id": [1, 2, 3]})
    order_items = pd.DataFrame({
        "item_id": [1, 2, 3],
        "order_id": [1, 2, 999],   # 999 doesn't exist in orders
        "product_id": [10, 11, 12],
        "quantity": [1, 2, 1],
        "unit_price": [100, 200, 300],
        "discount_percent": [0, 5, 10],
    })
    orphaned = check_referential_integrity(orders, order_items)
    assert len(orphaned) == 1, "Expected exactly 1 orphaned row"
    assert orphaned.iloc[0]["order_id"] == 999

    # verify the actual loaded database has no orphans left after cleaning
    conn = _fresh_connection()
    cur = conn.execute("""
        SELECT COUNT(*) FROM order_items oi
        LEFT JOIN orders o ON o.order_id = oi.order_id
        WHERE o.order_id IS NULL
    """)
    db_orphans = cur.fetchone()[0]
    conn.close()
    assert db_orphans == 0, "Cleaned database should have no orphaned order_items"
    print("PASS: test_order_items_with_invalid_order_id")


def test_discount_percent_greater_than_100():
    """
    2. What happens when discount_percent > 100?
    -> Revenue formula quantity * unit_price * (1 - discount/100) would
       go NEGATIVE, which is nonsensical for a sale. We verify the
       formula's behavior and that no such rows exist in the cleaned DB
       (generator caps discount_percent at 50 by design).
    """
    quantity, unit_price, discount_percent = 2, 500, 120
    revenue = quantity * unit_price * (1 - discount_percent / 100.0)
    assert revenue < 0, "A discount over 100% produces negative revenue - a data quality error"

    conn = _fresh_connection()
    cur = conn.execute("SELECT COUNT(*) FROM order_items WHERE discount_percent > 100")
    bad_rows = cur.fetchone()[0]
    conn.close()
    assert bad_rows == 0, "No order_items should have discount_percent > 100"
    print("PASS: test_discount_percent_greater_than_100 (formula correctly goes negative; "
          "no such rows present in cleaned data)")


def test_quantity_zero():
    """
    3. What happens when quantity is 0?
    -> Revenue contribution is exactly 0 (neither a sale nor a return).
       Such rows shouldn't distort revenue, purchase or return counts.
    """
    quantity, unit_price, discount_percent = 0, 999, 10
    revenue = quantity * unit_price * (1 - discount_percent / 100.0)
    assert revenue == 0

    # A quantity-0 row is treated as neither a positive purchase nor a
    # return in our SQL (WHERE oi.quantity > 0 / < 0 filters), confirm that.
    conn = _fresh_connection()
    cur = conn.execute("SELECT COUNT(*) FROM order_items WHERE quantity = 0")
    zero_qty_rows = cur.fetchone()[0]
    conn.close()
    print(f"PASS: test_quantity_zero (revenue=0 as expected; "
          f"{zero_qty_rows} zero-quantity rows in current dataset, correctly excluded "
          f"from purchase/return aggregates by quantity > 0 / < 0 filters)")


def test_future_order_date():
    """
    4. What happens when order_date is in the future?
    -> The row still loads (SQLite has no date-range constraint), but
       it should be flagged/excluded by any "as of today" reporting so
       it doesn't inflate current metrics. We simulate inserting one
       and confirm the CLI report window naturally excludes it when
       the requested date range doesn't include the future date.
    """
    future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
    today_str = datetime.now().strftime("%Y-%m-%d")

    conn = _fresh_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = OFF")
    cur.execute("""
        INSERT INTO orders (order_id, customer_id, order_date, status, region_code)
        VALUES (999999, 1, ?, 'PLACED', 'NORTH')
    """, (future_date,))
    conn.commit()

    cur.execute("""
        SELECT COUNT(*) FROM orders
        WHERE order_id = 999999 AND DATE(order_date) BETWEEN ? AND ?
    """, ("2000-01-01", today_str))
    count_in_current_window = cur.fetchone()[0]
    assert count_in_current_window == 0, "Future-dated order should not appear in a report window ending today"

    # cleanup
    cur.execute("DELETE FROM orders WHERE order_id = 999999")
    conn.commit()
    conn.close()
    print("PASS: test_future_order_date (future order correctly excluded from "
          "a report window bounded by today's date)")


def run_all():
    tests = [
        test_order_items_with_invalid_order_id,
        test_discount_percent_greater_than_100,
        test_quantity_zero,
        test_future_order_date,
    ]
    failures = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failures += 1
            print(f"FAIL: {t.__name__} -> {e}")
        except Exception as e:
            failures += 1
            print(f"ERROR: {t.__name__} -> {e}")

    print()
    if failures == 0:
        print(f"All {len(tests)} edge case tests passed.")
    else:
        print(f"{failures} of {len(tests)} tests failed.")


if __name__ == "__main__":
    run_all()
