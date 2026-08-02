# Employee Lifecycle Attrition Pipeline

An HR analytics data engineering pipeline built on **Databricks (Free Edition) + PySpark + Delta Lake**, using **Medallion Architecture** (Bronze → Silver → Gold) and **SCD Type 2** to track employee history over time — promotions, transfers, salary changes, and resignations.

---

## Overview

**Source data:** 5 days of daily HR snapshot CSVs (`emp_id`, `name`, `department`, `salary`, `join_date`, `status`), with headcount growing from 200 → 220 and resignations increasing across the days.

**Architecture pattern:** Medallion (Bronze / Silver / Gold), with SCD Type 2 in the Silver layer to preserve historical employee records instead of overwriting them.

**Local project folder** (`Employee_Lifecycle_Attrition_Pipeline/` on disk):
```
Employee_Lifecycle_Attrition_Pipeline/
├── Data/
│   ├── 1.hr_data/
│   │   ├── day 1/
│   │   ├── day 2/
│   │   ├── day 3/
│   │   ├── day 4/
│   │   └── day 5/
│   └── 2.bi_data/
├── Databricks_Notebooks/
│   ├── Data_Ingestion.py
│   ├── Bronze_Layer.py
│   ├── Silver_Layer.py
│   ├── SCD_Type2.py
│   ├── Gold_Layer.py
│   ├── BI_Data.py
│   ├── SQL_Analytics.sql
│   └── Dashboard.py
├── Output/                                        (Gold/BI CSV exports + dashboard exports go here)
├── Employee_Lifecycle_Attrition_Pipeline_Report.pdf
└── README.md
```

**Databricks workspace structure** (`Employee_Lifecycle_Attrition_Pipeline` in the workspace browser):
```
Employee_Lifecycle_Attrition_Pipeline/
├── Data/
├── Databricks_Notebooks/
│   ├── Data_Ingestion
│   ├── Bronze_Layer
│   ├── Silver_Layer
│   ├── SCD_Type2
│   ├── Gold_Layer
│   ├── BI_Data
│   ├── SQL_Analytics
│   └── Dashboard
├── Output/
├── Employee Lifecycle & Attrition Analytics Dashboard
└── README.md
```

---

## Pipeline Layers

### 1. Bronze Layer — `employee_data.bronze_employee`
- Ingests the 5 raw daily CSV snapshots as-is
- Adds `snapshot_date` to each record
- **Row count:** 1,050 (5 days × ~210 avg headcount)
- Columns: `emp_id, name, department, salary, join_date, status, snapshot_date`

### 2. Silver Layer — `employee_data.silver_employee`
- Implements **SCD Type 2** merge logic on top of Bronze
- For each `emp_id`, compares the current day's snapshot to the previous tracked version (`department`, `salary`, `status`)
  - No change → do nothing
  - Change detected → expire the old record (`effective_end_date`, `is_current = false`) and insert a new current record
- Tracking columns: `effective_start_date`, `effective_end_date`, `is_current`
- **Final state:** 594 total rows, 220 current employees (verified correct)

**Process used:**
1. Rebuild schema + reload Day 1 baseline correctly (fixed an `effective_start_date` mismatch bug)
2. Identify unprocessed dates by diffing Bronze snapshot dates against Silver's processed dates
3. Run the merge loop (`MERGE INTO ... WHEN MATCHED ... THEN UPDATE`) followed by an insert of new/changed rows for each remaining day

### 3. Gold Layer
- `employee_data.gold_avg_tenure` — average tenure by department
- `employee_data.gold_attrition_rate` — attrition rate calculations
- Also exports CSVs to the `Output/` folder for downstream BI consumption

### 4. BI / Dashboard Layer
- `hr_summary` table — powers the dashboard
- Databricks Dashboard with charts refreshed from `hr_summary`

---

## Data Quality Checks

After any Silver rebuild, downstream layers (Gold, BI) must be re-run and reconciled:

```sql
SELECT SUM(total_employees) AS check_220 FROM employee_data.hr_summary;
SELECT SUM(employee_count) AS check_220 FROM employee_data.gold_avg_tenure;
```

Both should return **220** (current employee count). ✅ Verified passing as of the latest run.

---

## Known Issues & Fixes

| Issue | Root Cause | Fix |
|---|---|---|
| Silver row counts wrong after rebuild | Day 1's `effective_start_date` wasn't stamped correctly, causing it to be reprocessed | Rebuilt schema, reloaded Day 1 baseline with correct date, then re-ran the merge loop for Days 2–5 |
| `NameError: avg_tenure_by_dept not defined` | Gold_Layer notebook cells run out of order (write cell run before the aggregation cell) | Run all Gold_Layer cells top-to-bottom in the same session |
| Obsolete `bronze_day1` table missing `snapshot_date` | Leftover table from an earlier iteration | Dropped and rebuilt from the corrected ingestion notebook |

---

## Current Status

- [x] Bronze ingestion verified (1,050 rows, correct schema)
- [x] Silver SCD2 rebuild verified (594 total / 220 current)
- [x] Gold layer refreshed and re-saved
- [x] BI `hr_summary` refreshed and re-saved
- [x] CSV exports re-run
- [x] Dashboard refreshed
- [x] Sanity checks passing (220 / 220)
- [ ] Scheduled as an automated Databricks Job
- [ ] Automated data-quality checks (pre-downstream validation)

---

## Suggested Next Steps

1. **Schedule as a Job** — chain `Data_Ingestion` (Bronze) → `Silver_Layer` (SCD2) → `Gold_Layer` → `BI_Data` as dependent tasks, triggered on the daily snapshot cadence.
2. **Add automated data-quality checks** — a validation task (e.g., asserting `current_employees` counts match across Gold and BI) that runs before the dashboard is refreshed, to catch drift like the `effective_start_date` bug automatically instead of manually.
3. **Guard against out-of-order notebook execution** — consider converting notebooks to parameterized jobs/tasks rather than manually run cells, to avoid `NameError`-type issues from partial runs.

---

## Tech Stack

- **Platform:** Databricks (Free Edition)
- **Compute:** Serverless
- **Storage:** Delta Lake (Databricks-managed)
- **Processing:** PySpark
- **Pattern:** Medallion Architecture + Slowly Changing Dimension (Type 2)
