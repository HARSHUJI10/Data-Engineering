# E-Commerce Order Analytics System

Intern Mini Project — Celebal Technologies
**Skills:** Python, SQL, Problem Solving
**Duration:** 3–4 weeks

## Overview

This project simulates a company's raw, messy e-commerce order data,
cleans it, loads it into a SQL database, and produces business
analytics — from basic aggregations to window functions, CTEs, and
cohort/retention analysis. It finishes with a command-line reporting
tool and an edge-case test suite.

## Project Structure

```
MIni_Project_E-Commerce_Order_Analytics_System/
├── raw_data/
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   └── order_items.csv
├── cleaned_data/
│   ├── customers_clean.csv
│   ├── products_clean.csv
│   ├── orders_clean.csv
│   └── order_items_clean.csv
├── reports/
│   └── data_cleaning_report.txt
├── data_generator.py     # Part 1: generates raw CSVs with intentional issues
├── data_cleaning.py      # Part 2: cleans data, produces issue report
├── load_to_sqlite.py     # Part 3 setup: schema + load into SQLite
├── sql_queries.sql       # Part 3: all 16 SQL analysis queries
├── run_reports.py        # Part 4: CLI reporting tool
├── test_cases.py         # Part 5: edge case tests
├── ecommerce.db          # SQLite database (generated)
└── README.md
```

## How to Run

```bash
pip install pandas

# 1. Generate raw data (4 CSVs, 500+ rows each, with intentional issues)
python3 data_generator.py

# 2. Clean the data and produce an issues report
python3 data_cleaning.py

# 3. Load cleaned data into SQLite with schema constraints
python3 load_to_sqlite.py

# 4. Run the SQL analysis queries directly against ecommerce.db
sqlite3 ecommerce.db < sql_queries.sql

# 5. Generate a CLI summary report
python3 run_reports.py --report monthly --start 2026-01-01 --end 2026-01-31
# or run without arguments for an interactive prompt:
python3 run_reports.py

# 6. Run the edge-case test suite
python3 test_cases.py
```

## Part 1 — Data Generation

`data_generator.py` produces 4 CSVs with the schemas below and
deliberately injects the following data quality issues:

| Issue | File | Rate |
|---|---|---|
| Missing/NULL `customer_id` | orders.csv | ~5% |
| Negative `quantity` (returns) | order_items.csv | ~3% |
| Wrong date format (`DD-MM-YYYY`) | orders.csv | ~8% |
| Extra whitespace / inconsistent casing in names | products.csv | ~15% |
| Invalid email (missing `@` or domain) | customers.csv | ~2% |

Referential integrity between `orders` and `order_items` is
guaranteed by construction (every `order_id` used in `order_items.csv`
is sampled from the set of `order_id`s already written to
`orders.csv`), so `check_referential_integrity()` in the cleaning step
returns zero orphaned rows on this dataset — but the function is
written generically and will catch orphans in any other dataset.

**Schemas**

- `orders.csv`: `order_id, customer_id, order_date, status, region_code`
- `order_items.csv`: `item_id, order_id, product_id, quantity, unit_price, discount_percent`
- `products.csv`: `product_id, product_name, category, subcategory, cost_price`
- `customers.csv`: `customer_id, customer_name, email, registration_date, customer_type`

## Part 2 — Data Cleaning

`data_cleaning.py` implements four functions:

- **`clean_orders()`** — normalizes both date formats
  (`YYYY-MM-DD HH:MM:SS` and `DD-MM-YYYY`) into a single standard
  format, and flags (rather than drops) rows with a missing
  `customer_id`, since the order itself is still a valid business
  event.
- **`clean_products()`** — trims whitespace, collapses double spaces,
  and applies title case to product names.
- **`validate_emails()`** — returns the list of `customer_id`s whose
  email fails a `user@domain.tld` pattern check.
- **`check_referential_integrity()`** — returns any `order_items`
  rows whose `order_id` doesn't exist in `orders`.

Running the script writes cleaned CSVs to `cleaned_data/` and a full
issue report to `reports/data_cleaning_report.txt`.

## Part 3 — SQL Analysis

`load_to_sqlite.py` creates the schema with `PRIMARY KEY`,
`FOREIGN KEY`, `NOT NULL`, and `CHECK` constraints, then loads the
cleaned CSVs.

`sql_queries.sql` contains all 16 required queries:

**Basic:** total revenue per category · top 10 customers by order value ·
month-wise order counts (last 12 months)

**Intermediate:** customers with no delivered items · products with
more returns than purchases · return rate per category

**Advanced (window functions / CTEs / subqueries):** running revenue
totals per region · `DENSE_RANK()` product ranking per category ·
`LAG()` days-between-orders with "At Risk" flag · multi-level CTE
spend categorization · `NTILE(4)` customer quartiles · year-over-year
comparison · `FIRST_VALUE`/`LAST_VALUE` category-shift detection ·
cumulative revenue distribution · cohort/retention analysis ·
self-join "frequently bought together" analysis

Every query has been run end-to-end against the generated database
and returns results without errors.

## Part 4 — CLI Reporting Tool

`run_reports.py` accepts a report type and date range (either as CLI
flags or interactively) and prints:

- Total orders, revenue, and unique customers for the period
- Top 3 products by revenue
- Comparison against the immediately preceding period of equal
  length (% change in orders, revenue, and customers)

Uses only the standard library (`sqlite3`, `argparse`, `datetime`) —
no external dependencies.

## Part 5 — Edge Case Handling

`test_cases.py` verifies behavior for:

1. `order_items` referencing a non-existent `order_id` — caught by
   `check_referential_integrity()`, and the loaded database is
   confirmed to have zero such rows after cleaning.
2. `discount_percent > 100` — confirms the revenue formula would go
   negative (a clear data-quality signal), and that no such rows
   exist in the cleaned dataset.
3. `quantity = 0` — confirms it contributes zero revenue and is
   correctly excluded from both "purchase" and "return" aggregates.
4. `order_date` in the future — confirms a future-dated order is
   correctly excluded from a report window bounded by today's date.

All 4 tests pass (`python3 test_cases.py`).

## Notes / Design Decisions

- Rows with a missing `customer_id` are **kept, not dropped** — the
  order is a real event even if we don't know who placed it. A
  boolean flag is added during cleaning instead.
- Negative-quantity rows are treated as **returns**, not deleted —
  they're needed for return-rate analysis.
- Revenue is consistently calculated as
  `quantity * unit_price * (1 - discount_percent / 100)` across every
  query and the CLI tool, and is only counted for `quantity > 0` rows
  to avoid double-counting returns as negative sales.
