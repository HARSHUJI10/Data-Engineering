# Databricks notebook source
# ==========================================
# Employee Lifecycle & Attrition Pipeline
# Data Ingestion Notebook 
# ==========================================

from pyspark.sql.functions import *

print("Libraries Imported Successfully")

# COMMAND ----------

# --------------------------------------------------------
# STEP 1: Read all 5 days of CSV files and combine them
# --------------------------------------------------------

day_folders = {
    1: "2026-05-01",
    2: "2026-05-02",
    3: "2026-05-03",
    4: "2026-05-04",
    5: "2026-05-05"
}

all_days_df = None

for day_num, snapshot_date in day_folders.items():
    df = spark.read \
        .option("header", True) \
        .option("inferSchema", True) \
        .csv(f"/Volumes/workspace/employee_data/hr_data/day {day_num}/*.csv") \
        .withColumn("snapshot_date", to_date(lit(snapshot_date)))

    all_days_df = df if all_days_df is None else all_days_df.unionByName(df)

display(all_days_df)

# COMMAND ----------

print(all_days_df.columns)

# COMMAND ----------

# --------------------------------------------------------
# STEP 2: Sanity-check the combined data
# --------------------------------------------------------

print("Total Records across all days:", all_days_df.count())
print("Distinct employees:", all_days_df.select("emp_id").distinct().count())

# COMMAND ----------

# --------------------------------------------------------
# STEP 3: Check for missing (null) values in any column
# --------------------------------------------------------

all_days_df.select(
    [sum(col(c).isNull().cast("int")).alias(c) for c in all_days_df.columns]
).show()

# COMMAND ----------

# --------------------------------------------------------
# STEP 4: Write the combined data into ONE Bronze table
# --------------------------------------------------------

all_days_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("employee_data.bronze_employee")

# COMMAND ----------

display(spark.table("employee_data.bronze_employee"))

# COMMAND ----------

print(spark.table("employee_data.bronze_employee").columns)

# COMMAND ----------

print(spark.table("employee_data.bronze_employee").count())

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS employee_data.bronze_day1;