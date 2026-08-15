-- =====================================================================
-- data_cleaning.sql
-- Transforms stg_neft_raw -> neft_transactions
-- Run AFTER database_schema.sql and after loading NEFT.csv into
-- stg_neft_raw
-- =====================================================================

USE neft_analysis;

-- ---------------------------------------------------------------------
-- 1. Trim / standardize bank names in staging
-- ---------------------------------------------------------------------
UPDATE stg_neft_raw
SET bank_name = UPPER(TRIM(bank_name));

-- ---------------------------------------------------------------------
-- 2. Remove exact duplicate bank/month combinations, keep the lowest id
-- ---------------------------------------------------------------------
DELETE r1 FROM stg_neft_raw r1
JOIN stg_neft_raw r2
  ON r1.bank_name = r2.bank_name
 AND r1.month     = r2.month
 AND r1.id        > r2.id;

-- ---------------------------------------------------------------------
-- 3. Fill NULL numeric fields with 0
-- ---------------------------------------------------------------------
UPDATE stg_neft_raw
SET debit_transactions  = COALESCE(debit_transactions, 0),
    debit_amount        = COALESCE(debit_amount, 0),
    credit_transactions = COALESCE(credit_transactions, 0),
    credit_amount       = COALESCE(credit_amount, 0);

-- ---------------------------------------------------------------------
-- 4. Remove rows with an unparsable month (defensive check)
-- ---------------------------------------------------------------------
DELETE FROM stg_neft_raw
WHERE STR_TO_DATE(CONCAT('01 ', month), '%d %M %Y') IS NULL;

-- ---------------------------------------------------------------------
-- 5. Insert cleaned + derived data into neft_transactions
-- ---------------------------------------------------------------------
TRUNCATE TABLE neft_transactions;

INSERT INTO neft_transactions (
    bank_name, transaction_date, year, month_num, month_name,
    debit_transactions, debit_amount, credit_transactions, credit_amount,
    total_transactions, total_amount,
    avg_debit_ticket_size, avg_credit_ticket_size, net_amount_flow
)
SELECT
    bank_name,
    STR_TO_DATE(CONCAT('01 ', month), '%d %M %Y')                       AS transaction_date,
    YEAR(STR_TO_DATE(CONCAT('01 ', month), '%d %M %Y'))                 AS year,
    MONTH(STR_TO_DATE(CONCAT('01 ', month), '%d %M %Y'))                AS month_num,
    MONTHNAME(STR_TO_DATE(CONCAT('01 ', month), '%d %M %Y'))            AS month_name,
    debit_transactions,
    debit_amount,
    credit_transactions,
    credit_amount,
    (debit_transactions + credit_transactions)                         AS total_transactions,
    (debit_amount + credit_amount)                                     AS total_amount,
    CASE WHEN debit_transactions  > 0 THEN debit_amount  / debit_transactions  ELSE 0 END AS avg_debit_ticket_size,
    CASE WHEN credit_transactions > 0 THEN credit_amount / credit_transactions ELSE 0 END AS avg_credit_ticket_size,
    (credit_amount - debit_amount)                                     AS net_amount_flow
FROM stg_neft_raw;

-- ---------------------------------------------------------------------
-- 6. Populate the optional star-schema tables
-- ---------------------------------------------------------------------
INSERT IGNORE INTO dim_bank (bank_name)
SELECT DISTINCT bank_name FROM neft_transactions;

TRUNCATE TABLE fact_neft_monthly;

INSERT INTO fact_neft_monthly (
    bank_id, transaction_date, debit_transactions, debit_amount,
    credit_transactions, credit_amount
)
SELECT
    db.bank_id,
    nt.transaction_date,
    nt.debit_transactions,
    nt.debit_amount,
    nt.credit_transactions,
    nt.credit_amount
FROM neft_transactions nt
JOIN dim_bank db ON db.bank_name = nt.bank_name;

-- ---------------------------------------------------------------------
-- 7. Quick sanity checks
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS total_rows FROM neft_transactions;
SELECT COUNT(DISTINCT bank_name) AS unique_banks FROM neft_transactions;
SELECT MIN(transaction_date) AS earliest, MAX(transaction_date) AS latest FROM neft_transactions;
