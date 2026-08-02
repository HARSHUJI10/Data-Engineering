-- Databricks notebook source
-- ==========================================
-- Employee Lifecycle & Attrition Pipeline
-- SQL Analytics
-- ==========================================

-- COMMAND ----------

USE employee_data;

-- COMMAND ----------

-- Sanity check: should be 594 total, 220 current
SELECT
  COUNT(*) AS total_rows,
  SUM(CASE WHEN is_current THEN 1 ELSE 0 END) AS current_employees
FROM silver_employee;

-- COMMAND ----------

-- Correct headcount by department (current only)
SELECT department, COUNT(*) AS employee_count
FROM silver_employee
WHERE is_current = true
GROUP BY department
ORDER BY employee_count DESC;

-- COMMAND ----------

-- Correct average salary by department (current only)
SELECT department, ROUND(AVG(salary), 2) AS avg_salary
FROM silver_employee
WHERE is_current = true
GROUP BY department
ORDER BY avg_salary DESC;

-- COMMAND ----------

-- Top 5 highest-paid CURRENT employees
SELECT emp_id, name, department, salary
FROM silver_employee
WHERE is_current = true
ORDER BY salary DESC
LIMIT 5;

-- COMMAND ----------

-- Which department has the highest attrition (resigned, currently)?
SELECT department, COUNT(*) AS resigned_count
FROM silver_employee
WHERE status = 'Resigned' AND is_current = true
GROUP BY department
ORDER BY resigned_count DESC;

-- COMMAND ----------

-- Employees who changed jobs/status the most (job mobility)
SELECT emp_id, name, COUNT(*) AS record_versions
FROM silver_employee
GROUP BY emp_id, name
HAVING COUNT(*) > 1
ORDER BY record_versions DESC
LIMIT 10;

-- COMMAND ----------

SELECT
  COUNT(*) AS total_rows,
  SUM(CASE WHEN is_current THEN 1 ELSE 0 END) AS current_employees
FROM silver_employee;

-- COMMAND ----------

SHOW TABLES IN employee_data