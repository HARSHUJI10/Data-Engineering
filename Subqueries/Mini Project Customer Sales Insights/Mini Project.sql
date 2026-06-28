-- ===========================================
-- MINI PROJECT : CUSTOMER SALES INSIGHTS
-- ===========================================

-- 1. Top 5 Customers

WITH CustomerSales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)

SELECT
    c.customer_name,
    cs.total_sales
FROM CustomerSales cs
JOIN customers c
ON cs.customer_id = c.customer_id
ORDER BY cs.total_sales DESC
LIMIT 5;

-- ===========================================
-- 2. Bottom 5 Customers

WITH CustomerSales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)

SELECT
    c.customer_name,
    cs.total_sales
FROM CustomerSales cs
JOIN customers c
ON cs.customer_id = c.customer_id
ORDER BY cs.total_sales
LIMIT 5;

-- ===========================================
-- 3. Customers Who Made Only One Order

SELECT
    c.customer_name,
    COUNT(o.order_id) AS total_orders
FROM customers c
JOIN orders o
ON c.customer_id = o.customer_id
GROUP BY c.customer_id,c.customer_name
HAVING COUNT(o.order_id)=1;

-- ===========================================
-- 4. Customers With Above Average Sales

WITH CustomerSales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)

SELECT
    c.customer_name,
    cs.total_sales
FROM CustomerSales cs
JOIN customers c
ON cs.customer_id=c.customer_id
WHERE cs.total_sales >
(
    SELECT AVG(total_sales)
    FROM CustomerSales
)
ORDER BY cs.total_sales DESC;

-- ===========================================
-- 5. Highest Order Value Per Customer

SELECT
    c.customer_name,
    MAX(o.sales) AS highest_order_value
FROM customers c
JOIN orders o
ON c.customer_id=o.customer_id
GROUP BY c.customer_id,c.customer_name
ORDER BY highest_order_value DESC;
