-- =====================================================================
-- analysis_queries.sql
-- Business-facing analysis queries against neft_transactions
-- =====================================================================

USE neft_analysis;

-- ---------------------------------------------------------------------
-- 1. Top 10 banks by total NEFT amount (debit + credit)
-- ---------------------------------------------------------------------
SELECT
    bank_name,
    SUM(total_amount) AS total_amount,
    ROUND(SUM(total_amount) * 100.0 / (SELECT SUM(total_amount) FROM neft_transactions), 2) AS pct_share
FROM neft_transactions
GROUP BY bank_name
ORDER BY total_amount DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- 2. Year-wise total debit vs credit trend
-- ---------------------------------------------------------------------
SELECT
    year,
    SUM(debit_amount)  AS total_debit_amount,
    SUM(credit_amount) AS total_credit_amount,
    SUM(debit_transactions)  AS total_debit_txn,
    SUM(credit_transactions) AS total_credit_txn
FROM neft_transactions
GROUP BY year
ORDER BY year;

-- ---------------------------------------------------------------------
-- 3. Month-over-month growth rate in total amount (all banks combined)
-- ---------------------------------------------------------------------
WITH monthly AS (
    SELECT transaction_date, SUM(total_amount) AS amount
    FROM neft_transactions
    GROUP BY transaction_date
)
SELECT
    transaction_date,
    amount,
    LAG(amount) OVER (ORDER BY transaction_date) AS prev_month_amount,
    ROUND(
        (amount - LAG(amount) OVER (ORDER BY transaction_date))
        / LAG(amount) OVER (ORDER BY transaction_date) * 100, 2
    ) AS mom_growth_pct
FROM monthly
ORDER BY transaction_date;

-- ---------------------------------------------------------------------
-- 4. Bank ranking by month using window functions
-- ---------------------------------------------------------------------
SELECT
    transaction_date,
    bank_name,
    total_amount,
    RANK() OVER (PARTITION BY transaction_date ORDER BY total_amount DESC) AS rank_in_month
FROM neft_transactions
ORDER BY transaction_date, rank_in_month;

-- ---------------------------------------------------------------------
-- 5. Banks with highest average transaction (ticket) size
-- ---------------------------------------------------------------------
SELECT
    bank_name,
    ROUND(AVG(avg_debit_ticket_size), 2)  AS avg_debit_ticket_size,
    ROUND(AVG(avg_credit_ticket_size), 2) AS avg_credit_ticket_size
FROM neft_transactions
WHERE debit_transactions > 1000   -- exclude very small / inactive banks
GROUP BY bank_name
ORDER BY avg_debit_ticket_size DESC
LIMIT 15;

-- ---------------------------------------------------------------------
-- 6. Seasonality: total transactions by calendar month (all years)
-- ---------------------------------------------------------------------
SELECT
    month_num,
    month_name,
    SUM(total_transactions) AS total_transactions
FROM neft_transactions
GROUP BY month_num, month_name
ORDER BY month_num;

-- ---------------------------------------------------------------------
-- 7. Banks with consistently negative net flow (debit-heavy banks)
-- ---------------------------------------------------------------------
SELECT
    bank_name,
    ROUND(SUM(net_amount_flow), 2) AS total_net_flow,
    COUNT(*) AS months_reported
FROM neft_transactions
GROUP BY bank_name
HAVING total_net_flow < 0
ORDER BY total_net_flow ASC
LIMIT 15;

-- ---------------------------------------------------------------------
-- 8. Year-over-year growth for the top 5 banks
-- ---------------------------------------------------------------------
WITH top_banks AS (
    SELECT bank_name FROM neft_transactions
    GROUP BY bank_name
    ORDER BY SUM(total_amount) DESC
    LIMIT 5
),
yearly AS (
    SELECT bank_name, year, SUM(total_amount) AS yearly_amount
    FROM neft_transactions
    WHERE bank_name IN (SELECT bank_name FROM top_banks)
    GROUP BY bank_name, year
)
SELECT
    bank_name,
    year,
    yearly_amount,
    ROUND(
        (yearly_amount - LAG(yearly_amount) OVER (PARTITION BY bank_name ORDER BY year))
        / LAG(yearly_amount) OVER (PARTITION BY bank_name ORDER BY year) * 100, 2
    ) AS yoy_growth_pct
FROM yearly
ORDER BY bank_name, year;

-- ---------------------------------------------------------------------
-- 9. Market concentration check: cumulative share of top N banks
-- ---------------------------------------------------------------------
WITH ranked AS (
    SELECT
        bank_name,
        SUM(total_amount) AS amount,
        ROW_NUMBER() OVER (ORDER BY SUM(total_amount) DESC) AS rn
    FROM neft_transactions
    GROUP BY bank_name
)
SELECT
    bank_name,
    amount,
    rn,
    ROUND(SUM(amount) OVER (ORDER BY rn) * 100.0
        / SUM(amount) OVER (), 2) AS cumulative_pct_share
FROM ranked
ORDER BY rn
LIMIT 20;

-- ---------------------------------------------------------------------
-- 10. Overall KPI summary (matches Power BI dashboard cards)
-- ---------------------------------------------------------------------
SELECT
    SUM(debit_amount)        AS total_debit_amount,
    SUM(credit_amount)       AS total_credit_amount,
    SUM(debit_transactions)  AS total_debit_transactions,
    SUM(credit_transactions) AS total_credit_transactions,
    SUM(total_amount)        AS total_amount,
    SUM(total_transactions)  AS total_transactions
FROM neft_transactions;
