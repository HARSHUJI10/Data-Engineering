# Databricks notebook source
# ==========================================
# Employee Lifecycle & Attrition Pipeline
# Bronze Layer Notebook
# ==========================================

# COMMAND ----------

from pyspark.sql.functions import *

print("Bronze Layer Started Successfully")

# COMMAND ----------

bronze_df = spark.table("employee_data.bronze_employee")

display(bronze_df)

# COMMAND ----------

bronze_df.printSchema()

# COMMAND ----------

print("Total Records :", bronze_df.count())

# COMMAND ----------

bronze_df.show(10)