-- =====================================================================
-- database_schema.sql
-- NEFT Banking Transaction Analysis
-- Creates the database and staging + cleaned tables used by the project
-- Compatible with MySQL 8.0+
-- =====================================================================

CREATE DATABASE IF NOT EXISTS neft_analysis;
USE neft_analysis;

-- ---------------------------------------------------------------------
-- Staging table: raw structure, mirrors NEFT.csv exactly
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS stg_neft_raw;
CREATE TABLE stg_neft_raw (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    bank_name             VARCHAR(150) NOT NULL,
    debit_transactions    BIGINT       NULL,
    debit_amount          DECIMAL(18,3) NULL,
    credit_transactions   BIGINT       NULL,
    credit_amount         DECIMAL(18,3) NULL,
    month                 VARCHAR(20)  NOT NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Cleaned / production table used by all analysis queries
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS neft_transactions;
CREATE TABLE neft_transactions (
    transaction_id        INT AUTO_INCREMENT PRIMARY KEY,
    bank_name             VARCHAR(150) NOT NULL,
    transaction_date      DATE         NOT NULL,
    year                  SMALLINT     NOT NULL,
    month_num             TINYINT      NOT NULL,
    month_name            VARCHAR(15)  NOT NULL,
    debit_transactions    BIGINT       NOT NULL DEFAULT 0,
    debit_amount          DECIMAL(18,3) NOT NULL DEFAULT 0,
    credit_transactions   BIGINT       NOT NULL DEFAULT 0,
    credit_amount         DECIMAL(18,3) NOT NULL DEFAULT 0,
    total_transactions    BIGINT       NOT NULL DEFAULT 0,
    total_amount          DECIMAL(18,3) NOT NULL DEFAULT 0,
    avg_debit_ticket_size DECIMAL(18,4) NULL,
    avg_credit_ticket_size DECIMAL(18,4) NULL,
    net_amount_flow       DECIMAL(18,3) NULL,
    UNIQUE KEY uq_bank_month (bank_name, transaction_date),
    INDEX idx_bank_name (bank_name),
    INDEX idx_transaction_date (transaction_date),
    INDEX idx_year (year)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Reference/dimension table for a tidy star-schema alternative
-- (optional, useful if you want to model this as bank_dim + fact_neft)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS dim_bank;
CREATE TABLE dim_bank (
    bank_id     INT AUTO_INCREMENT PRIMARY KEY,
    bank_name   VARCHAR(150) NOT NULL UNIQUE
) ENGINE=InnoDB;

DROP TABLE IF EXISTS fact_neft_monthly;
CREATE TABLE fact_neft_monthly (
    fact_id              INT AUTO_INCREMENT PRIMARY KEY,
    bank_id              INT NOT NULL,
    transaction_date     DATE NOT NULL,
    debit_transactions   BIGINT NOT NULL DEFAULT 0,
    debit_amount         DECIMAL(18,3) NOT NULL DEFAULT 0,
    credit_transactions  BIGINT NOT NULL DEFAULT 0,
    credit_amount        DECIMAL(18,3) NOT NULL DEFAULT 0,
    FOREIGN KEY (bank_id) REFERENCES dim_bank(bank_id),
    UNIQUE KEY uq_bank_date (bank_id, transaction_date)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Load raw data (adjust path / use MySQL Workbench's Table Data Import
-- Wizard if LOCAL INFILE is disabled on your server)
-- ---------------------------------------------------------------------
-- LOAD DATA LOCAL INFILE '/path/to/data/raw/NEFT.csv'
-- INTO TABLE stg_neft_raw
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (bank_name, debit_transactions, debit_amount, credit_transactions, credit_amount, month);
