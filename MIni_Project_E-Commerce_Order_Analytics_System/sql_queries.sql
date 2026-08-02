-- ============================================================
-- sql_queries.sql
-- E-Commerce Order Analytics System - Part 3: SQL Analysis
-- Target: SQLite (ecommerce.db)
-- ============================================================


-- ============================================================
-- BASIC QUERIES
-- ============================================================

-- 1. Total revenue per category
--    revenue = quantity * unit_price * (1 - discount_percent/100)
--    (only counts positive-quantity line items as "sales" revenue)
SELECT
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
WHERE oi.quantity > 0
GROUP BY p.category
ORDER BY total_revenue DESC;


-- 2. Top 10 customers by total order value
SELECT
    c.customer_id,
    c.customer_name,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_order_value
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE oi.quantity > 0
GROUP BY c.customer_id, c.customer_name
ORDER BY total_order_value DESC
LIMIT 10;


-- 3. Month-wise order count for the last 12 months
SELECT
    strftime('%Y-%m', order_date) AS order_month,
    COUNT(*) AS order_count
FROM orders
WHERE order_date >= date((SELECT MAX(order_date) FROM orders), '-12 months')
GROUP BY order_month
ORDER BY order_month;


-- ============================================================
-- INTERMEDIATE QUERIES
-- ============================================================

-- 4. Customers who placed orders but never had any item delivered
SELECT DISTINCT c.customer_id, c.customer_name
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE c.customer_id NOT IN (
    SELECT customer_id FROM orders WHERE status = 'DELIVERED' AND customer_id IS NOT NULL
);


-- 5. Products that were ordered but had more returns than purchases
--    (negative quantity rows = returns, positive quantity rows = purchases)
SELECT
    p.product_id,
    p.product_name,
    SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS total_purchased,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS total_returned
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name
HAVING total_returned > total_purchased;


-- 6. Return rate (returned items / total items) per category
SELECT
    p.category,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS returned_items,
    SUM(ABS(oi.quantity)) AS total_items,
    ROUND(
        1.0 * SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END)
        / NULLIF(SUM(ABS(oi.quantity)), 0), 4
    ) AS return_rate
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY return_rate DESC;


-- ============================================================
-- ADVANCED QUERIES (Window Functions, CTEs, Subqueries)
-- ============================================================

-- 7. Running Totals with Window Functions
--    Running total of revenue per region, ordered by date
WITH daily_region_revenue AS (
    SELECT
        o.region_code,
        DATE(o.order_date) AS order_date,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE oi.quantity > 0
    GROUP BY o.region_code, DATE(o.order_date)
)
SELECT
    region_code,
    order_date,
    ROUND(daily_revenue, 2) AS daily_revenue,
    ROUND(SUM(daily_revenue) OVER (
        PARTITION BY region_code ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS running_total
FROM daily_region_revenue
ORDER BY region_code, order_date;


-- 8. Ranking with DENSE_RANK
--    For each category, rank products by total revenue (ties share a rank)
WITH product_revenue AS (
    SELECT
        p.category,
        p.product_name,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_revenue
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    WHERE oi.quantity > 0
    GROUP BY p.category, p.product_name
)
SELECT
    category,
    product_name,
    ROUND(total_revenue, 2) AS total_revenue,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category
FROM product_revenue
ORDER BY category, rank_in_category;


-- 9. LAG/LEAD Analysis
--    Days between consecutive orders per customer; flag "At Risk" if avg gap > 30 days
WITH order_gaps AS (
    SELECT
        customer_id,
        order_date,
        LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date,
        JULIANDAY(order_date) - JULIANDAY(
            LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date)
        ) AS days_gap
    FROM orders
    WHERE customer_id IS NOT NULL
),
customer_avg_gap AS (
    SELECT customer_id, AVG(days_gap) AS avg_gap
    FROM order_gaps
    WHERE days_gap IS NOT NULL
    GROUP BY customer_id
)
SELECT
    og.customer_id,
    og.order_date,
    og.previous_order_date,
    ROUND(og.days_gap, 2) AS days_gap,
    CASE WHEN cag.avg_gap > 30 THEN 'At Risk' ELSE 'Active' END AS risk_flag
FROM order_gaps og
JOIN customer_avg_gap cag ON cag.customer_id = og.customer_id
ORDER BY og.customer_id, og.order_date;


-- 10. CTE with Multiple Levels
--     Monthly revenue per customer -> category (High/Medium/Low) -> count per month
WITH monthly_customer_revenue AS (
    SELECT
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS order_month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE oi.quantity > 0 AND o.customer_id IS NOT NULL
    GROUP BY o.customer_id, order_month
),
categorized AS (
    SELECT
        customer_id,
        order_month,
        revenue,
        CASE
            WHEN revenue > 10000 THEN 'High'
            WHEN revenue >= 5000 THEN 'Medium'
            ELSE 'Low'
        END AS spend_category
    FROM monthly_customer_revenue
)
SELECT
    order_month,
    spend_category,
    COUNT(DISTINCT customer_id) AS customer_count
FROM categorized
GROUP BY order_month, spend_category
ORDER BY order_month, spend_category;


-- 11. NTILE for Segmentation
--     Divide customers into 4 quartiles by total lifetime value
WITH customer_ltv AS (
    SELECT
        c.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_value
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE oi.quantity > 0
    GROUP BY c.customer_id
)
SELECT
    customer_id,
    ROUND(total_value, 2) AS total_value,
    NTILE(4) OVER (ORDER BY total_value DESC) AS quartile,
    CASE NTILE(4) OVER (ORDER BY total_value DESC)
        WHEN 1 THEN 'Platinum'
        WHEN 2 THEN 'Gold'
        WHEN 3 THEN 'Silver'
        ELSE 'Bronze'
    END AS quartile_label
FROM customer_ltv
ORDER BY quartile, total_value DESC;


-- 12. Year-over-Year Comparison
--     Compare each month's revenue with the same month in the previous year
WITH monthly_revenue AS (
    SELECT
        CAST(strftime('%Y', o.order_date) AS INTEGER) AS year,
        CAST(strftime('%m', o.order_date) AS INTEGER) AS month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE oi.quantity > 0
    GROUP BY year, month
)
SELECT
    curr.year,
    curr.month,
    ROUND(curr.revenue, 2) AS revenue,
    ROUND(prev.revenue, 2) AS prev_year_revenue,
    CASE
        WHEN prev.revenue IS NULL OR prev.revenue = 0 THEN NULL
        ELSE ROUND((curr.revenue - prev.revenue) * 100.0 / prev.revenue, 2)
    END AS yoy_growth_percent
FROM monthly_revenue curr
LEFT JOIN monthly_revenue prev
    ON prev.year = curr.year - 1 AND prev.month = curr.month
ORDER BY curr.year, curr.month;


-- 13. First/Last Value Analysis
--     First purchased category vs most recent purchased category per customer
WITH customer_purchases AS (
    SELECT
        o.customer_id,
        o.order_date,
        p.category,
        FIRST_VALUE(p.category) OVER (
            PARTITION BY o.customer_id ORDER BY o.order_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS first_category,
        LAST_VALUE(p.category) OVER (
            PARTITION BY o.customer_id ORDER BY o.order_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_category
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.customer_id IS NOT NULL
)
SELECT DISTINCT
    customer_id,
    first_category,
    last_category,
    CASE WHEN first_category != last_category THEN 'Yes' ELSE 'No' END AS category_shift
FROM customer_purchases
ORDER BY customer_id;


-- 14. Cumulative Distribution
--     What % of total revenue comes from the top N% of customers
WITH customer_revenue AS (
    SELECT
        c.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE oi.quantity > 0
    GROUP BY c.customer_id
),
ranked AS (
    SELECT
        customer_id,
        revenue,
        SUM(revenue) OVER (ORDER BY revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue,
        SUM(revenue) OVER () AS grand_total
    FROM customer_revenue
)
SELECT
    customer_id,
    ROUND(revenue, 2) AS revenue,
    ROUND(cumulative_revenue, 2) AS cumulative_revenue,
    ROUND(cumulative_revenue * 100.0 / grand_total, 2) AS cumulative_percent
FROM ranked
ORDER BY revenue DESC;


-- 15. Complex CTE: Cohort Analysis
--     Group customers by registration month, track ordering activity in months 0-3
WITH cohorts AS (
    SELECT
        customer_id,
        strftime('%Y-%m', registration_date) AS cohort_month,
        DATE(registration_date) AS reg_date
    FROM customers
),
customer_orders AS (
    SELECT
        o.customer_id,
        DATE(o.order_date) AS order_date
    FROM orders o
    WHERE o.customer_id IS NOT NULL
),
cohort_activity AS (
    SELECT
        c.cohort_month,
        c.customer_id,
        CAST((JULIANDAY(co.order_date) - JULIANDAY(c.reg_date)) / 30 AS INTEGER) AS month_number
    FROM cohorts c
    JOIN customer_orders co ON co.customer_id = c.customer_id
    WHERE JULIANDAY(co.order_date) - JULIANDAY(c.reg_date) >= 0
)
SELECT
    cohort_month,
    SUM(CASE WHEN month_number = 0 THEN 1 ELSE 0 END) AS month_0_orderers,
    SUM(CASE WHEN month_number = 1 THEN 1 ELSE 0 END) AS month_1_orderers,
    SUM(CASE WHEN month_number = 2 THEN 1 ELSE 0 END) AS month_2_orderers,
    SUM(CASE WHEN month_number = 3 THEN 1 ELSE 0 END) AS month_3_orderers,
    ROUND(100.0 * SUM(CASE WHEN month_number = 1 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN month_number = 0 THEN 1 ELSE 0 END), 0), 2) AS retention_month_1_pct,
    ROUND(100.0 * SUM(CASE WHEN month_number = 2 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN month_number = 0 THEN 1 ELSE 0 END), 0), 2) AS retention_month_2_pct,
    ROUND(100.0 * SUM(CASE WHEN month_number = 3 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN month_number = 0 THEN 1 ELSE 0 END), 0), 2) AS retention_month_3_pct
FROM cohort_activity
GROUP BY cohort_month
ORDER BY cohort_month;


-- 16. Self-Join with Window Function
--     Products frequently bought together (same order), A-B pair appears once
WITH order_products AS (
    SELECT DISTINCT o.order_id, oi.product_id
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE oi.quantity > 0
)
SELECT
    pa.product_id AS product_a,
    pb.product_id AS product_b,
    COUNT(*) AS times_bought_together
FROM order_products pa
JOIN order_products pb
    ON pa.order_id = pb.order_id
    AND pa.product_id < pb.product_id     -- ensures A-B appears once, no self-pairs
GROUP BY pa.product_id, pb.product_id
HAVING times_bought_together > 1
ORDER BY times_bought_together DESC
LIMIT 50;
