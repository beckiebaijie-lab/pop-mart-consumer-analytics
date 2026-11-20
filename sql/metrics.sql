CREATE VIEW sales AS
SELECT invoice, at, customer, quantity * price AS gross
FROM lines
WHERE at >= '2010-12-01' AND at < '2011-12-01'
  AND upper(invoice) NOT LIKE 'C%' AND quantity > 0 AND price > 0;

CREATE VIEW orders AS
SELECT invoice, min(at) AS at, max(customer) AS customer, sum(gross) AS gross
FROM sales
GROUP BY invoice;

CREATE VIEW monthly AS
WITH RECURSIVE months(month) AS (
    VALUES ('2010-12-01')
    UNION ALL SELECT date(month, '+1 month') FROM months WHERE month < '2011-11-01'
), totals AS (
    SELECT month, round(coalesce(sum(gross), 0), 2) AS gross_gbp,
           count(invoice) AS orders, count(DISTINCT customer) AS buyers,
           count(customer) AS identified_orders,
           round(coalesce(sum(CASE WHEN customer IS NOT NULL THEN gross END), 0), 2)
               AS identified_gross_gbp
    FROM months LEFT JOIN orders ON date(at, 'start of month') = month
    GROUP BY month
)
SELECT *, round(gross_gbp / nullif(orders, 0), 2) AS aov_gbp,
       round(gross_gbp / nullif(lag(gross_gbp) OVER (ORDER BY month), 0) - 1, 6) AS mom
FROM totals;

CREATE VIEW buyer_first AS
SELECT customer, min(at) AS first_at, date(min(at), 'start of month') AS cohort
FROM orders WHERE customer IS NOT NULL GROUP BY customer;

CREATE VIEW retention AS
WITH RECURSIVE months(month) AS (
    VALUES ('2010-12-01')
    UNION ALL SELECT date(month, '+1 month') FROM months WHERE month < '2011-11-01'
), sizes AS (
    SELECT cohort, count(*) AS size FROM buyer_first GROUP BY cohort
), active AS (
    SELECT cohort, date(at, 'start of month') AS month, count(DISTINCT orders.customer) AS buyers
    FROM orders JOIN buyer_first USING(customer) GROUP BY cohort, month
)
SELECT cohort, months.month,
       12 * (strftime('%Y', months.month) - strftime('%Y', cohort))
        + strftime('%m', months.month) - strftime('%m', cohort) AS age,
       size, coalesce(buyers, 0) AS active_buyers,
       round(1.0 * coalesce(buyers, 0) / size, 6) AS rate
FROM sizes CROSS JOIN months LEFT JOIN active USING(cohort, month)
WHERE months.month >= cohort;

CREATE VIEW repeat_30d AS
WITH eligible AS (
    SELECT * FROM buyer_first WHERE datetime(first_at, '+30 days') < '2011-12-01'
), flags AS (
    SELECT eligible.customer, exists (
        SELECT 1 FROM orders WHERE orders.customer = eligible.customer
          AND orders.at > eligible.first_at
          AND orders.at <= datetime(eligible.first_at, '+30 days')
    ) AS returned
    FROM eligible
)
SELECT count(*) AS eligible_buyers, coalesce(sum(returned), 0) AS repeat_buyers,
       round(avg(returned), 6) AS rate
FROM flags;
