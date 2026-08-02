"""
run_reports.py
------------------
Command-line reporting tool (Part 4: Python + SQL Integration).

Usage (interactive):
    python3 run_reports.py

Usage (non-interactive, via CLI args):
    python3 run_reports.py --report daily   --start 2026-06-01 --end 2026-06-30
    python3 run_reports.py --report weekly  --start 2026-06-01 --end 2026-06-30
    python3 run_reports.py --report monthly --start 2026-01-01 --end 2026-06-30

Generates a summary report for the given date range showing:
  - Total orders, revenue, unique customers
  - Top 3 products (by revenue)
  - Comparison with the previous period of equal length (% change)

No external libraries are used besides sqlite3 and the standard library.
"""

import sqlite3
import argparse
from datetime import datetime, timedelta

DB_PATH = "ecommerce.db"


def get_period_stats(conn, start_date, end_date):
    """Returns (total_orders, total_revenue, unique_customers, top_3_products list)."""
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(DISTINCT o.order_id), COUNT(DISTINCT o.customer_id)
        FROM orders o
        WHERE DATE(o.order_date) BETWEEN ? AND ?
    """, (start_date, end_date))
    total_orders, unique_customers = cur.fetchone()
    total_orders = total_orders or 0
    unique_customers = unique_customers or 0

    cur.execute("""
        SELECT COALESCE(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 0)
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE DATE(o.order_date) BETWEEN ? AND ? AND oi.quantity > 0
    """, (start_date, end_date))
    total_revenue = cur.fetchone()[0] or 0.0

    cur.execute("""
        SELECT p.product_name,
               SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        JOIN products p ON p.product_id = oi.product_id
        WHERE DATE(o.order_date) BETWEEN ? AND ? AND oi.quantity > 0
        GROUP BY p.product_name
        ORDER BY revenue DESC
        LIMIT 3
    """, (start_date, end_date))
    top_products = cur.fetchall()

    return total_orders, total_revenue, unique_customers, top_products


def pct_change(current, previous):
    if previous in (0, None):
        return None
    return round((current - previous) * 100.0 / previous, 2)


def previous_period(start_date, end_date):
    """Given a date range, return the immediately preceding period of equal length."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    length = (end - start).days + 1
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=length - 1)
    return prev_start.strftime("%Y-%m-%d"), prev_end.strftime("%Y-%m-%d")


def print_report(report_type, start_date, end_date):
    conn = sqlite3.connect(DB_PATH)

    orders, revenue, customers, top_products = get_period_stats(conn, start_date, end_date)
    prev_start, prev_end = previous_period(start_date, end_date)
    p_orders, p_revenue, p_customers, _ = get_period_stats(conn, prev_start, prev_end)

    conn.close()

    print("=" * 60)
    print(f"{report_type.upper()} REPORT: {start_date} to {end_date}")
    print("=" * 60)
    print(f"Total Orders       : {orders}")
    print(f"Total Revenue       : Rs. {revenue:,.2f}")
    print(f"Unique Customers    : {customers}")
    print()
    print("Top 3 Products (by revenue):")
    if top_products:
        for i, (name, rev) in enumerate(top_products, start=1):
            print(f"  {i}. {name:35s} Rs. {rev:,.2f}")
    else:
        print("  (no sales in this period)")
    print()
    print(f"Previous period     : {prev_start} to {prev_end}")
    print(f"  Orders    : {p_orders}   (change: {pct_change(orders, p_orders)}%)")
    print(f"  Revenue    : Rs. {p_revenue:,.2f}   (change: {pct_change(revenue, p_revenue)}%)")
    print(f"  Customers  : {p_customers}   (change: {pct_change(customers, p_customers)}%)")
    print("=" * 60)


def validate_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date '{value}', expected YYYY-MM-DD")


def main():
    parser = argparse.ArgumentParser(description="E-Commerce order summary report tool")
    parser.add_argument("--report", choices=["daily", "weekly", "monthly"],
                         help="Report type")
    parser.add_argument("--start", type=validate_date, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=validate_date, help="End date (YYYY-MM-DD)")
    args = parser.parse_args()

    if args.report and args.start and args.end:
        report_type, start_date, end_date = args.report, args.start, args.end
    else:
        # interactive fallback
        print("E-Commerce Order Analytics - Report Generator")
        report_type = input("Report type (daily/weekly/monthly): ").strip().lower()
        while report_type not in ("daily", "weekly", "monthly"):
            report_type = input("Please enter daily, weekly, or monthly: ").strip().lower()

        start_date = input("Start date (YYYY-MM-DD): ").strip()
        while True:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                break
            except ValueError:
                start_date = input("Invalid format. Start date (YYYY-MM-DD): ").strip()

        end_date = input("End date (YYYY-MM-DD): ").strip()
        while True:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
                break
            except ValueError:
                end_date = input("Invalid format. End date (YYYY-MM-DD): ").strip()

    if start_date > end_date:
        print("Error: start date must be before end date.")
        return

    try:
        print_report(report_type, start_date, end_date)
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        print("Have you run load_to_sqlite.py yet?")


if __name__ == "__main__":
    main()
