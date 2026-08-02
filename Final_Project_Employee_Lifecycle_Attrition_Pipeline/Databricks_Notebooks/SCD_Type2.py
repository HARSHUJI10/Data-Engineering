# Databricks notebook source
# ==========================================
# Employee Lifecycle & Attrition Pipeline
# SCD Type 2 — Incremental Merge
# ==========================================

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.functions import lit

bronze_df = spark.table("employee_data.bronze_employee")
bronze_dates = set(row.snapshot_date for row in bronze_df.select("snapshot_date").distinct().collect())

silver_df = spark.table("employee_data.silver_employee")
processed_dates = set(row.effective_start_date for row in silver_df.select("effective_start_date").distinct().collect())

new_dates = sorted(bronze_dates - processed_dates)
print(f"Dates to process: {new_dates}")

# COMMAND ----------

for day in new_dates:
    day_df = bronze_df.filter(F.col("snapshot_date") == day)
    day_df.createOrReplaceTempView("day_source")

    spark.sql(f"""
        MERGE INTO employee_data.silver_employee AS target
        USING day_source AS source
        ON target.emp_id = source.emp_id AND target.is_current = true
        WHEN MATCHED AND (
            target.department != source.department OR
            target.salary != source.salary OR
            target.status != source.status
        )
        THEN UPDATE SET
            target.effective_end_date = '{day}',
            target.is_current = false
    """)

    current_ids = spark.table("employee_data.silver_employee").filter("is_current = true").select("emp_id")
    new_rows_df = day_df.join(current_ids, "emp_id", "left_anti")

    insert_df = new_rows_df.select(
        F.col("emp_id").cast("int"), F.col("name").cast("string"),
        F.col("department").cast("string"), F.col("salary").cast("double"),
        F.col("join_date").cast("date"), F.col("status").cast("string")
    ).withColumn("effective_start_date", F.lit(day).cast("date")) \
     .withColumn("effective_end_date", lit(None).cast("date")) \
     .withColumn("is_current", lit(True))

    insert_df.write.format("delta").mode("append").saveAsTable("employee_data.silver_employee")
    print(f"  → {day} processed")

print("Done.")

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.functions import lit

bronze_df = spark.table("employee_data.bronze_employee")
first_day = bronze_df.agg(F.min("snapshot_date")).collect()[0][0]
initial_df = bronze_df.filter(F.col("snapshot_date") == first_day)

initial_scd_df = initial_df.select(
    F.col("emp_id").cast("int"), F.col("name").cast("string"),
    F.col("department").cast("string"), F.col("salary").cast("double"),
    F.col("join_date").cast("date"), F.col("status").cast("string")
).withColumn("effective_start_date", F.lit(first_day).cast("date")) \
 .withColumn("effective_end_date", lit(None).cast("date")) \
 .withColumn("is_current", lit(True))

initial_scd_df.write.format("delta").mode("append").saveAsTable("employee_data.silver_employee")
print(spark.table("employee_data.silver_employee").count())  # should be 200

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS total_rows, SUM(CASE WHEN is_current THEN 1 ELSE 0 END) AS current_employees
# MAGIC FROM employee_data.silver_employee

# COMMAND ----------

bronze_dates = set(row.snapshot_date for row in bronze_df.select("snapshot_date").distinct().collect())
silver_df = spark.table("employee_data.silver_employee")
processed_dates = set(row.effective_start_date for row in silver_df.select("effective_start_date").distinct().collect())
new_dates = sorted(bronze_dates - processed_dates)
print(f"Dates to process: {new_dates}")

# COMMAND ----------

for day in new_dates:
    day_df = bronze_df.filter(F.col("snapshot_date") == day)
    day_df.createOrReplaceTempView("day_source")

    spark.sql(f"""
        MERGE INTO employee_data.silver_employee AS target
        USING day_source AS source
        ON target.emp_id = source.emp_id AND target.is_current = true
        WHEN MATCHED AND (
            target.department != source.department OR
            target.salary != source.salary OR
            target.status != source.status
        )
        THEN UPDATE SET
            target.effective_end_date = '{day}',
            target.is_current = false
    """)

    current_ids = spark.table("employee_data.silver_employee").filter("is_current = true").select("emp_id")
    new_rows_df = day_df.join(current_ids, "emp_id", "left_anti")

    insert_df = new_rows_df.select(
        F.col("emp_id").cast("int"), F.col("name").cast("string"),
        F.col("department").cast("string"), F.col("salary").cast("double"),
        F.col("join_date").cast("date"), F.col("status").cast("string")
    ).withColumn("effective_start_date", F.lit(day).cast("date")) \
     .withColumn("effective_end_date", lit(None).cast("date")) \
     .withColumn("is_current", lit(True))

    insert_df.write.format("delta").mode("append").saveAsTable("employee_data.silver_employee")
    print(f"  → {day} processed")

print("Done.")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS total_rows, SUM(CASE WHEN is_current THEN 1 ELSE 0 END) AS current_employees
# MAGIC FROM employee_data.silver_employee