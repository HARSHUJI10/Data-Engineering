-- ===========================================
-- STEP 1 : SETUP DATA
-- ===========================================

-- Create Database
CREATE DATABASE superstoredb;

USE superstoredb;

-- ===========================================
-- Create Raw Table
-- ===========================================

CREATE TABLE superstore_raw (
    Row_ID INT,
    Order_ID VARCHAR(30),
    Order_Date VARCHAR(20),
    Ship_Date VARCHAR(20),
    Ship_Mode VARCHAR(50),
    Customer_ID VARCHAR(30),
    Customer_Name VARCHAR(100),
    Segment VARCHAR(50),
    Country VARCHAR(50),
    City VARCHAR(50),
    State VARCHAR(50),
    Postal_Code VARCHAR(20),
    Region VARCHAR(50),
    Product_ID VARCHAR(50),
    Category VARCHAR(50),
    Sub_Category VARCHAR(50),
    Product_Name VARCHAR(255),
    Sales DECIMAL(10,2),
    Quantity INT,
    Discount DECIMAL(5,2),
    Profit DECIMAL(10,2)
);

-- ===========================================
-- Import CSV
-- ===========================================

LOAD DATA LOCAL INFILE 'C:/Users/janhv/Downloads/archive (1)/Sample - Superstore.csv'
INTO TABLE superstore_raw
CHARACTER SET latin1
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
Row_ID,
Order_ID,
Order_Date,
Ship_Date,
Ship_Mode,
Customer_ID,
Customer_Name,
Segment,
Country,
City,
State,
Postal_Code,
Region,
Product_ID,
Category,
Sub_Category,
Product_Name,
Sales,
Quantity,
Discount,
Profit
);

-- Verify Import

SELECT COUNT(*) AS Total_Rows
FROM superstore_raw;

-- ===========================================
-- Create Customers Table
-- ===========================================

CREATE TABLE customers (
    customer_id VARCHAR(30) PRIMARY KEY,
    customer_name VARCHAR(100),
    segment VARCHAR(50),
    country VARCHAR(50),
    city VARCHAR(50),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    region VARCHAR(50)
);

-- Insert Customer Data

INSERT INTO customers
SELECT
    Customer_ID,
    MAX(Customer_Name),
    MAX(Segment),
    MAX(Country),
    MAX(City),
    MAX(State),
    MAX(Postal_Code),
    MAX(Region)
FROM superstore_raw
GROUP BY Customer_ID;

-- Verify

SELECT COUNT(*) AS Total_Customers
FROM customers;

-- ===========================================
-- Create Products Table
-- ===========================================

CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(50),
    sub_category VARCHAR(50)
);

-- Insert Product Data

INSERT INTO products
SELECT
    Product_ID,
    MAX(Product_Name),
    MAX(Category),
    MAX(Sub_Category)
FROM superstore_raw
GROUP BY Product_ID;

-- Verify

SELECT COUNT(*) AS Total_Products
FROM products;

-- ===========================================
-- Create Orders Table
-- ===========================================

CREATE TABLE orders (
    row_id INT PRIMARY KEY,
    order_id VARCHAR(30),
    order_date VARCHAR(20),
    ship_date VARCHAR(20),
    ship_mode VARCHAR(50),
    customer_id VARCHAR(30),
    product_id VARCHAR(50),
    sales DECIMAL(10,2),
    quantity INT,
    discount DECIMAL(5,2),
    profit DECIMAL(10,2)
);

-- Insert Orders Data

INSERT INTO orders
SELECT
    Row_ID,
    Order_ID,
    Order_Date,
    Ship_Date,
    Ship_Mode,
    Customer_ID,
    Product_ID,
    Sales,
    Quantity,
    Discount,
    Profit
FROM superstore_raw;

-- Verify

SELECT COUNT(*) AS Total_Orders
FROM orders;