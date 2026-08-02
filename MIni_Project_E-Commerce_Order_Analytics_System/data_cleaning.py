"""
data_cleaning.py
------------------
Cleans the 4 raw CSV files and writes cleaned versions + an issues report.

Functions:
    clean_orders()               -> fixes date formats, handles NULL customer_id
    clean_products()              -> normalizes product names (trim + title case)
    validate_emails()             -> returns list of customer_ids with invalid emails
    check_referential_integrity() -> finds order_items referencing non-existent orders

Run directly:  python3 data_cleaning.py
"""

import re
import pandas as pd
from datetime import datetime

RAW_DIR = "raw_data"
CLEAN_DIR = "cleaned_data"

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _parse_order_date(value):
    """Try multiple known formats; return pd.NaT if none match."""
    if pd.isna(value) or str(value).strip() == "":
        return pd.NaT
    value = str(value).strip()
    formats = ["%Y-%m-%d %H:%M:%S", "%d-%m-%Y", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return pd.NaT


def clean_orders(orders_df=None):
    """
    Fix date formats (accepts 'YYYY-MM-DD HH:MM:SS' and 'DD-MM-YYYY',
    normalizes everything to 'YYYY-MM-DD HH:MM:SS') and handle NULL
    customer_ids by flagging them with a boolean column instead of
    dropping the row (orders are still valid business events even
    without a known customer).
    """
    df = orders_df.copy() if orders_df is not None else pd.read_csv(
        f"{RAW_DIR}/orders.csv", dtype={"customer_id": "object"}
    )

    issues = {"missing_customer_id": 0, "bad_date_format": 0}

    # --- customer_id ---
    df["customer_id"] = df["customer_id"].replace("", pd.NA)
    df["has_missing_customer_id"] = df["customer_id"].isna()
    issues["missing_customer_id"] = int(df["has_missing_customer_id"].sum())

    # --- order_date ---
    raw_dates = df["order_date"]
    parsed = raw_dates.apply(_parse_order_date)
    # count rows that were in the "wrong" (DD-MM-YYYY) format specifically
    issues["bad_date_format"] = int(
        raw_dates.apply(lambda v: bool(re.match(r"^\d{2}-\d{2}-\d{4}$", str(v).strip()))).sum()
    )
    df["order_date"] = parsed.dt.strftime("%Y-%m-%d %H:%M:%S")
    df["order_date_invalid"] = parsed.isna()

    return df, issues


def clean_products(products_df=None):
    """
    Normalize product names: trim leading/trailing whitespace, collapse
    internal double-spaces, and apply title case.
    """
    df = products_df.copy() if products_df is not None else pd.read_csv(f"{RAW_DIR}/products.csv")

    original = df["product_name"]
    cleaned = (
        original.str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )
    changed = int((original != cleaned).sum())
    df["product_name"] = cleaned

    issues = {"product_names_normalized": changed}
    return df, issues


def validate_emails(customers_df=None):
    """
    Returns a list of customer_ids whose email fails a basic
    'user@domain.tld' pattern check (missing '@' or missing domain).
    """
    df = customers_df.copy() if customers_df is not None else pd.read_csv(f"{RAW_DIR}/customers.csv")

    invalid_mask = ~df["email"].astype(str).apply(lambda e: bool(EMAIL_REGEX.match(e)))
    invalid_ids = df.loc[invalid_mask, "customer_id"].tolist()
    return invalid_ids


def check_referential_integrity(orders_df=None, order_items_df=None):
    """
    Returns the subset of order_items rows whose order_id does not
    exist in the orders table.
    """
    orders = orders_df.copy() if orders_df is not None else pd.read_csv(f"{RAW_DIR}/orders.csv")
    items = order_items_df.copy() if order_items_df is not None else pd.read_csv(f"{RAW_DIR}/order_items.csv")

    valid_order_ids = set(orders["order_id"])
    orphaned = items[~items["order_id"].isin(valid_order_ids)]
    return orphaned


def main():
    report_lines = []
    report_lines.append("DATA CLEANING REPORT")
    report_lines.append("=" * 50)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    # --- orders ---
    orders_raw = pd.read_csv(f"{RAW_DIR}/orders.csv", dtype={"customer_id": "object"})
    orders_clean, order_issues = clean_orders(orders_raw)
    report_lines.append("[orders.csv]")
    report_lines.append(f"  Total rows: {len(orders_clean)}")
    report_lines.append(f"  Missing customer_id: {order_issues['missing_customer_id']}")
    report_lines.append(f"  Rows with DD-MM-YYYY format (fixed): {order_issues['bad_date_format']}")
    report_lines.append(f"  Rows where date could not be parsed at all: {int(orders_clean['order_date_invalid'].sum())}")
    report_lines.append("")

    # --- products ---
    products_raw = pd.read_csv(f"{RAW_DIR}/products.csv")
    products_clean, product_issues = clean_products(products_raw)
    report_lines.append("[products.csv]")
    report_lines.append(f"  Total rows: {len(products_clean)}")
    report_lines.append(f"  Product names normalized: {product_issues['product_names_normalized']}")
    report_lines.append("")

    # --- customers / emails ---
    customers_raw = pd.read_csv(f"{RAW_DIR}/customers.csv")
    invalid_email_ids = validate_emails(customers_raw)
    report_lines.append("[customers.csv]")
    report_lines.append(f"  Total rows: {len(customers_raw)}")
    report_lines.append(f"  Invalid emails: {len(invalid_email_ids)}")
    report_lines.append(f"  Affected customer_ids (first 20 shown): {invalid_email_ids[:20]}")
    report_lines.append("")

    # --- order_items / referential integrity ---
    order_items_raw = pd.read_csv(f"{RAW_DIR}/order_items.csv")
    orphaned = check_referential_integrity(orders_raw, order_items_raw)
    negative_qty = order_items_raw[order_items_raw["quantity"] < 0]
    report_lines.append("[order_items.csv]")
    report_lines.append(f"  Total rows: {len(order_items_raw)}")
    report_lines.append(f"  Rows with negative quantity (returns): {len(negative_qty)}")
    report_lines.append(f"  Orphaned rows (order_id not in orders.csv): {len(orphaned)}")
    report_lines.append("")

    # --- write cleaned CSVs ---
    orders_out = orders_clean.drop(columns=["has_missing_customer_id", "order_date_invalid"])
    orders_out.to_csv(f"{CLEAN_DIR}/orders_clean.csv", index=False)
    products_clean.to_csv(f"{CLEAN_DIR}/products_clean.csv", index=False)
    customers_raw.to_csv(f"{CLEAN_DIR}/customers_clean.csv", index=False)
    # keep negative-quantity rows (they are legitimate returns) but drop orphans
    order_items_clean = order_items_raw.drop(index=orphaned.index)
    order_items_clean.to_csv(f"{CLEAN_DIR}/order_items_clean.csv", index=False)

    report_lines.append("Cleaned files written to ./cleaned_data/")
    report_text = "\n".join(report_lines)

    with open("reports/data_cleaning_report.txt", "w") as f:
        f.write(report_text)

    print(report_text)


if __name__ == "__main__":
    main()
