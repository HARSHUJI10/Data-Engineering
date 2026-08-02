# Databricks notebook source
from pyspark.sql import functions as F

silver_df = spark.table("employee_data.silver_employee")

# Get the latest snapshot date directly from the data (no dependency on other notebooks)
latest_date = silver_df.agg(F.max("effective_start_date")).collect()[0][0]
print(latest_date)  # sanity check

# Only look at CURRENT records (latest known status per employee)
current_df = silver_df.filter("is_current = true")

# Tenure = latest date minus join_date, in days/years
tenure_df = current_df.withColumn(
    "tenure_days", F.datediff(F.lit(latest_date), F.col("join_date"))
).withColumn(
    "tenure_years", F.round(F.col("tenure_days") / 365.25, 2)
)

avg_tenure_by_dept = tenure_df.groupBy("department").agg(
    F.round(F.avg("tenure_years"), 2).alias("avg_tenure_years"),
    F.count("*").alias("employee_count")
).orderBy("department")

display(avg_tenure_by_dept)

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS employee_data.gold_avg_tenure

# COMMAND ----------

avg_tenure_by_dept.write.format("delta").mode("overwrite").saveAsTable("employee_data.gold_avg_tenure")

# COMMAND ----------

display(spark.table("employee_data.gold_avg_tenure"))

# COMMAND ----------

# Attrition rate based on total workforce known as of each snapshot day
bronze_df = spark.table("employee_data.bronze_employee")

attrition_df = bronze_df.groupBy("snapshot_date").agg(
    F.count("*").alias("total_employees"),
    F.sum(F.when(F.col("status") == "Resigned", 1).otherwise(0)).alias("resigned_count")
).withColumn(
    "attrition_rate_pct", F.round((F.col("resigned_count") / F.col("total_employees")) * 100, 2)
).orderBy("snapshot_date")

display(attrition_df)

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS employee_data.gold_attrition_rate

# COMMAND ----------

attrition_df.write.format("delta").mode("overwrite").saveAsTable("employee_data.gold_attrition_rate")

# COMMAND ----------

display(spark.table("employee_data.gold_attrition_rate"))

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW CATALOGS

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW SCHEMAS IN workspace

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW VOLUMES IN workspace.employee_data

# COMMAND ----------

spark.table("employee_data.gold_avg_tenure").coalesce(1).write.mode("overwrite").option("header", True).csv("/Volumes/workspace/employee_data/bi_dataset/hr_dashboard/avg_tenure")

spark.table("employee_data.gold_attrition_rate").coalesce(1).write.mode("overwrite").option("header", True).csv("/Volumes/workspace/employee_data/bi_dataset/hr_summary/attrition_rate")

# COMMAND ----------

# MAGIC %fs ls /Volumes/workspace/employee_data/bi_dataset/hr_dashboard/avg_tenure

# COMMAND ----------

# MAGIC %fs ls /Volumes/workspace/employee_data/bi_dataset/hr_summary/attrition_rate