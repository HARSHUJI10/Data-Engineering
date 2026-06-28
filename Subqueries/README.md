# Week 3 – SQL Assignment: Subqueries, CTEs, and Window Functions

## Objective

Analyze sales data from the "Superstore dataset" using subqueries, CTEs, and window functions.

\---

## Step 1: Setup

* setup.sql - Database + staging + normalized tables

  * superstore\_raw - raw imported data
  * customers - customer details
  * orders - order details
  * products - product details

Meaning: Prepare clean tables for analysis.

\---

## Step 2: Queries

* queries.sql - Required analysis queries
1. Orders above average sales - Meaning: High‑value orders
2. Highest sales order per customer - Meaning: Biggest purchase per customer
3. Total sales per customer (CTE) - Meaning: Aggregate spend per customer
4. Customers above average sales (CTE + Subquery) - Meaning: Higher‑than‑average spenders
5. Rank customers by sales (Window Function) - Meaning: Rank customers by spend
6. Row numbers per order within customer - Meaning: Sequence orders per customer
7. Top 3 customers - Meaning: Three highest spenders

\---

## Step 3: Final Insights

* final.sql - Combined query 

1.Final Combined Query - Meaning: Customer name, total sales, rank

\---



# Mini Project

1\. Top 5 customers - Meaning: Five highest spenders 

2\. Bottom 5 customers - Meaning: Five lowest spenders 

3\. Customers with one order - Meaning: One‑time buyers 

4\. Customers above average sales - Meaning: Higher‑than‑average spenders 

5\. Highest order per customer - Meaning: Largest single order per customer



## Folder Structure



Subqueries/

|

|-- Setup Data/

|   |-- Setup.sql

|   `-- Output.xlsx

|

|-- Perform Required Queries/

|   |-- Perform Required Queries.sql

|   |-- 1st output.xlsx

|   |-- 2nd output.xlsx

|   |-- 3rd output.xlsx

|   |-- 4th output.xlsx

|   |-- 5th output.xlsx

|   |-- 6th output.xlsx

|   `-- 7th output.xlsx

|

|-- Final Combined Query/

|   |-- Final Combined Query.sql

|   `-- Output.xlsx

|

|-- Mini Project Customer Sales Insights/

|   |-- Mini Project.sql

|   |-- 1st output.xlsx

|   |-- 2nd output.xlsx

|   |-- 3rd output.xlsx

|   |-- 4th output.xlsx

|   `-- 5th output.xlsx

|

`-- README.md



\---

# Conclusion

This assignment shows how subqueries, CTEs, and window functions can turn raw sales data into clear insights.  
The structure is simple: "setup - queries - final - Mini Project", each explained with short meanings for clarity.









