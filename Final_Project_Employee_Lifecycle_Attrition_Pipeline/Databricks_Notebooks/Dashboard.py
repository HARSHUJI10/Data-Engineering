# Databricks notebook source
# MAGIC %sql
# MAGIC SHOW TABLES IN employee_data

# COMMAND ----------

# ==========================================
# Employee Lifecycle & Attrition Pipeline
# Dashboard
# ==========================================

# COMMAND ----------

spark.sql("USE employee_data")

# COMMAND ----------

# Chart 1: Average Tenure by Department
display(spark.table("gold_avg_tenure"))
# → set chart type: Bar, X=department, Y=avg_tenure_years

# COMMAND ----------

# Chart 2: Attrition Rate Trend
display(spark.table("gold_attrition_rate"))
# → set chart type: Line, X=snapshot_date, Y=attrition_rate_pct

# COMMAND ----------

# Chart 3: Current Headcount by Department
display(
    spark.table("silver_employee")
    .filter("is_current = true")
    .groupBy("department")
    .count()
    .orderBy("department")
)
# → set chart type: Bar, X=department, Y=count

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN employee_data

# COMMAND ----------

spark.sql("USE employee_data")

# COMMAND ----------

display(spark.table("gold_avg_tenure"))

# COMMAND ----------

display(spark.table("gold_attrition_rate"))

# COMMAND ----------

display(
    spark.table("silver_employee")
    .filter("is_current = true")
    .groupBy("department")
    .count()
    .orderBy("department")
)

# COMMAND ----------

display(spark.table("gold_avg_tenure"))

# COMMAND ----------

display(spark.table("gold_attrition_rate"))

# COMMAND ----------

display(
    spark.table("silver_employee")
    .filter("status = 'Resigned' AND is_current = true")
    .groupBy("department")
    .count()
    .orderBy("department")
)

# COMMAND ----------

display(
    spark.table("silver_employee")
    .filter("is_current = true")
    .groupBy("department")
    .count()
    .orderBy("department")
)