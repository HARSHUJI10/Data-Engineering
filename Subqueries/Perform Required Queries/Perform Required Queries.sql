-- ===========================================
-- STEP 2: PERFORM REQUIRED QUERIES
-- ===========================================

-- Task 1: Find all orders where sales are greater than the average sales (Subquery)

SELECT *
FROM orders
WHERE sales >
(
    SELECT AVG(sales)
    FROM orders
);

-- ===========================================

-- Task 2: Find the highest sales order for each customer (Subquery)

SELECT *
FROM orders o
WHERE sales =
(
    SELECT MAX(sales)
    FROM orders
    WHERE customer_id = o.customer_id
);

-- ===========================================

-- Task 3: Calculate total sales for each customer (CTE)

WITH CustomerSales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)

SELECT *
FROM CustomerSales;

-- ===========================================

-- Task 4: Find customers whose total sales are above average (CTE + Subquery)

WITH CustomerSales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)

SELECT *
FROM CustomerSales
WHERE total_sales >
(
    SELECT AVG(total_sales)
    FROM CustomerSales
);

-- ===========================================

-- Task 5: Rank all customers based on total sales (Window Function)

WITH CustomerSales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)

SELECT
    customer_id,
    total_sales,
    RANK() OVER (ORDER BY total_sales DESC) AS sales_rank
FROM CustomerSales;

-- ===========================================

-- Task 6: Assign row numbers to each order within a customer (Window Function + PARTITION BY)

SELECT
    customer_id,
    order_id,
    sales,
    ROW_NUMBER() OVER
    (
        PARTITION BY customer_id
        ORDER BY sales DESC
    ) AS order_number
FROM orders;

-- ===========================================

-- Task 7: Display Top 3 Customers based on Total Sales (Window Function)

WITH CustomerSales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
),

RankedCustomers AS
(
    SELECT
        customer_id,
        total_sales,
        RANK() OVER (ORDER BY total_sales DESC) AS sales_rank
    FROM CustomerSales
)

SELECT *
FROM RankedCustomers
WHERE sales_rank <= 3;