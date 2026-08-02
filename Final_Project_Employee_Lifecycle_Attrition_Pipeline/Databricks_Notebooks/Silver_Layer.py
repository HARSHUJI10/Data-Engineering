# Databricks notebook source
# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS employee_data.silver_employee (
# MAGIC     emp_id INT,
# MAGIC     name STRING,
# MAGIC     department STRING,
# MAGIC     salary DOUBLE,
# MAGIC     join_date DATE,
# MAGIC     status STRING,
# MAGIC     effective_start_date DATE,
# MAGIC     effective_end_date DATE,
# MAGIC     is_current BOOLEAN
# MAGIC ) USING DELTA

# COMMAND ----------

bronze_df = spark.table("employee_data.bronze_employee")
bronze_df.createOrReplaceTempView("bronze_source")

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE employee_data.silver_employee

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS employee_data.silver_employee

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.functions import lit

bronze_df = spark.table("employee_data.bronze_employee")
first_day = bronze_df.agg(F.min("snapshot_date")).collect()[0][0]

initial_df = bronze_df.filter(F.col("snapshot_date") == first_day)

initial_scd_df = initial_df.select(
    F.col("emp_id").cast("int"),
    F.col("name").cast("string"),
    F.col("department").cast("string"),
    F.col("salary").cast("double"),
    F.col("join_date").cast("date"),
    F.col("status").cast("string")
).withColumn("effective_start_date", F.lit(first_day).cast("date")) \
 .withColumn("effective_end_date", lit(None).cast("date")) \
 .withColumn("is_current", lit(True))

# COMMAND ----------

initial_scd_df.write.format("delta").mode("overwrite").saveAsTable("employee_data.silver_employee")

# COMMAND ----------

print(spark.table("employee_data.silver_employee").count())
spark.table("employee_data.silver_employee").printSchema()
display(spark.table("employee_data.silver_employee").limit(5))

# COMMAND ----------

from pyspark.sql import functions as F

bronze_df = spark.table("employee_data.bronze_employee")

# Get the second earliest date (Day 2)
all_dates = [row.snapshot_date for row in bronze_df.select("snapshot_date").distinct().orderBy("snapshot_date").collect()]
day2 = all_dates[1]
print(day2)  # confirm this prints Day 2's date

# COMMAND ----------

day_df = bronze_df.filter(F.col("snapshot_date") == day2)
day_df.createOrReplaceTempView("day_source")
print(day_df.count())  # sanity check

# COMMAND ----------

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
        target.effective_end_date = '{day2}',
        target.is_current = false
""")

# COMMAND ----------

current_ids = spark.table("employee_data.silver_employee").filter("is_current = true").select("emp_id")

new_rows_df = day_df.join(current_ids, "emp_id", "left_anti")
print(new_rows_df.count())  # how many new/changed rows today

# COMMAND ----------

from pyspark.sql.functions import lit

insert_df = new_rows_df.select(
    F.col("emp_id").cast("int"),
    F.col("name").cast("string"),
    F.col("department").cast("string"),
    F.col("salary").cast("double"),
    F.col("join_date").cast("date"),
    F.col("status").cast("string")
).withColumn("effective_start_date", F.lit(day2).cast("date")) \
 .withColumn("effective_end_date", lit(None).cast("date")) \
 .withColumn("is_current", lit(True))

insert_df.write.format("delta").mode("append").saveAsTable("employee_data.silver_employee")

# COMMAND ----------

print(spark.table("employee_data.silver_employee").count())
display(spark.table("employee_data.silver_employee").filter("is_current = false"))

# COMMAND ----------

day3 = all_dates[2]   # index 2 = third date = Day 3
print(day3)

# COMMAND ----------

day_df = bronze_df.filter(F.col("snapshot_date") == day3)
day_df.createOrReplaceTempView("day_source")
print(day_df.count())

# COMMAND ----------

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
        target.effective_end_date = '{day3}',
        target.is_current = false
""")

# COMMAND ----------

current_ids = spark.table("employee_data.silver_employee").filter("is_current = true").select("emp_id")
new_rows_df = day_df.join(current_ids, "emp_id", "left_anti")
print(new_rows_df.count())

# COMMAND ----------

from pyspark.sql.functions import lit

insert_df = new_rows_df.select(
    F.col("emp_id").cast("int"),
    F.col("name").cast("string"),
    F.col("department").cast("string"),
    F.col("salary").cast("double"),
    F.col("join_date").cast("date"),
    F.col("status").cast("string")
).withColumn("effective_start_date", F.lit(day3).cast("date")) \
 .withColumn("effective_end_date", lit(None).cast("date")) \
 .withColumn("is_current", lit(True))

insert_df.write.format("delta").mode("append").saveAsTable("employee_data.silver_employee")

# COMMAND ----------

print(spark.table("employee_data.silver_employee").count())
display(spark.table("employee_data.silver_employee").filter(f"effective_end_date = '{day3}'"))

# COMMAND ----------

day4 = all_dates[3]   # index 3 = fourth date = Day 4
print(day4)

# COMMAND ----------

day_df = bronze_df.filter(F.col("snapshot_date") == day4)
day_df.createOrReplaceTempView("day_source")
print(day_df.count())

# COMMAND ----------

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
        target.effective_end_date = '{day4}',
        target.is_current = false
""")

# COMMAND ----------

current_ids = spark.table("employee_data.silver_employee").filter("is_current = true").select("emp_id")
new_rows_df = day_df.join(current_ids, "emp_id", "left_anti")
print(new_rows_df.count())

# COMMAND ----------

from pyspark.sql.functions import lit

insert_df = new_rows_df.select(
    F.col("emp_id").cast("int"),
    F.col("name").cast("string"),
    F.col("department").cast("string"),
    F.col("salary").cast("double"),
    F.col("join_date").cast("date"),
    F.col("status").cast("string")
).withColumn("effective_start_date", F.lit(day4).cast("date")) \
 .withColumn("effective_end_date", lit(None).cast("date")) \
 .withColumn("is_current", lit(True))

insert_df.write.format("delta").mode("append").saveAsTable("employee_data.silver_employee")

# COMMAND ----------

print(spark.table("employee_data.silver_employee").count())
display(spark.table("employee_data.silver_employee").filter(f"effective_end_date = '{day4}'"))

# COMMAND ----------

day5 = all_dates[4]   # index 4 = fifth date = Day 5
print(day5)

# COMMAND ----------

day_df = bronze_df.filter(F.col("snapshot_date") == day5)
day_df.createOrReplaceTempView("day_source")
print(day_df.count())

# COMMAND ----------

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
        target.effective_end_date = '{day5}',
        target.is_current = false
""")

# COMMAND ----------

current_ids = spark.table("employee_data.silver_employee").filter("is_current = true").select("emp_id")
new_rows_df = day_df.join(current_ids, "emp_id", "left_anti")
print(new_rows_df.count())

# COMMAND ----------

from pyspark.sql.functions import lit

insert_df = new_rows_df.select(
    F.col("emp_id").cast("int"),
    F.col("name").cast("string"),
    F.col("department").cast("string"),
    F.col("salary").cast("double"),
    F.col("join_date").cast("date"),
    F.col("status").cast("string")
).withColumn("effective_start_date", F.lit(day5).cast("date")) \
 .withColumn("effective_end_date", lit(None).cast("date")) \
 .withColumn("is_current", lit(True))

insert_df.write.format("delta").mode("append").saveAsTable("employee_data.silver_employee")

# COMMAND ----------

print(spark.table("employee_data.silver_employee").count())
display(spark.table("employee_data.silver_employee").filter("is_current = true").count())
display(spark.table("employee_data.silver_employee").filter("is_current = false").count())