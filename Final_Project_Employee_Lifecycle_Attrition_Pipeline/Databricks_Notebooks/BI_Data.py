# Databricks notebook source
# ==========================================
# Employee Lifecycle & Attrition Pipeline
# BI Data Preparation
# ==========================================

# COMMAND ----------

spark.sql("USE employee_data")

# COMMAND ----------

hr_summary = spark.sql("""
    SELECT
        department,
        COUNT(*) AS total_employees,
        ROUND(AVG(salary), 2) AS average_salary,
        ROUND(MAX(salary), 2) AS highest_salary,
        ROUND(MIN(salary), 2) AS lowest_salary
    FROM silver_employee
    WHERE is_current = true
    GROUP BY department
""")

display(hr_summary)

# COMMAND ----------

hr_summary.write.format("delta").mode("overwrite").saveAsTable("hr_summary")

# COMMAND ----------

display(spark.table("employee_data.hr_summary"))

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN employee_data

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN employee_data

# COMMAND ----------

hr_summary.write.format("delta").mode("overwrite").saveAsTable("hr_summary")

# COMMAND ----------

spark.sql("USE employee_data")

hr_summary = spark.sql("""
    SELECT
        department,
        COUNT(*) AS total_employees,
        ROUND(AVG(salary), 2) AS average_salary,
        ROUND(MAX(salary), 2) AS highest_salary,
        ROUND(MIN(salary), 2) AS lowest_salary
    FROM silver_employee
    WHERE is_current = true
    GROUP BY department
""")

display(hr_summary)

# COMMAND ----------

hr_summary.write.format("delta").mode("overwrite").saveAsTable("hr_summary")

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN employee_data

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT SUM(total_employees) AS total_check FROM employee_data.hr_summary

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT SUM(total_employees) AS check_220 FROM employee_data.hr_summary

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT SUM(employee_count) AS check_220 FROM employee_data.gold_avg_tenure