-- ===========================================
-- STEP 3 : FINAL COMBINED QUERY
-- (JOIN + CTE + WINDOW FUNCTION)
-- ===========================================

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
    cs.total_sales,
    RANK() OVER(ORDER BY cs.total_sales DESC) AS sales_rank
FROM CustomerSales cs
JOIN customers c
ON cs.customer_id = c.customer_id
ORDER BY sales_rank;