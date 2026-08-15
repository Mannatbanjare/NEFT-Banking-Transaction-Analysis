# Data Dictionary

## Source File: `data/raw/NEFT.csv`

Monthly bank-wise NEFT (National Electronic Funds Transfer) transaction data, sourced in the format published by the Reserve Bank of India (RBI). Each row represents one bank's activity for one calendar month.

| Column | Type | Description |
|---|---|---|
| `bank_name` | Text | Name of the participating bank / financial institution |
| `debit_transactions` | Integer | Number of NEFT outward (debit) transactions initiated by the bank's customers in that month |
| `debit_amount` | Decimal | Total value of outward transactions, in **Rs. crore** |
| `credit_transactions` | Integer | Number of NEFT inward (credit) transactions received by the bank's customers in that month |
| `credit_amount` | Decimal | Total value of inward transactions, in **Rs. crore** |
| `month` | Text | Reporting month, formatted as `"Month YYYY"` (e.g. `"January 2020"`) |

**Coverage:** 267 unique banks, June 2008 – June 2020, 21,405 rows.

---

## Processed File: `data/processed/Cleaned_NEFT.csv`

Output of `python/data_cleaning.py`. Adds standardized types and derived columns.

| Column | Type | Description |
|---|---|---|
| `bank_name` | Text | Upper-cased, whitespace-normalized bank name |
| `transaction_date` | Date | First-of-month date parsed from `month` (e.g. `2020-01-01`) |
| `year` | Integer | Calendar year extracted from `transaction_date` |
| `month_num` | Integer | Calendar month number (1–12) |
| `month_name` | Text | Full month name (e.g. `January`) |
| `debit_transactions` | Integer | See above |
| `debit_amount` | Decimal | See above (Rs. crore) |
| `credit_transactions` | Integer | See above |
| `credit_amount` | Decimal | See above (Rs. crore) |
| `total_transactions` | Integer | `debit_transactions + credit_transactions` |
| `total_amount` | Decimal | `debit_amount + credit_amount` |
| `avg_debit_ticket_size` | Decimal | `debit_amount / debit_transactions` — average value per outward transaction |
| `avg_credit_ticket_size` | Decimal | `credit_amount / credit_transactions` — average value per inward transaction |
| `net_amount_flow` | Decimal | `credit_amount - debit_amount` — positive means the bank is a net receiver of NEFT funds that month |

---

## Feature File: `data/processed/Featured_NEFT.csv`

Output of `python/feature_engineering.py`. Adds time-series and ranking features on top of `Cleaned_NEFT.csv`.

| Column | Type | Description |
|---|---|---|
| `mom_amount_growth_pct` | Decimal | Month-over-month % change in `total_amount` for that bank |
| `yoy_amount_growth_pct` | Decimal | Year-over-year (12-month) % change in `total_amount` for that bank |
| `rolling_3m_avg_amount` | Decimal | Trailing 3-month rolling average of `total_amount` for that bank |
| `market_share_pct` | Decimal | Bank's share of total NEFT amount **within that specific month**, across all banks |
| `overall_bank_rank` | Integer | Bank's rank (1 = largest) by total `total_amount` summed across the full 2008–2020 period |
| `debit_credit_txn_ratio` | Decimal | `debit_transactions / credit_transactions` |
| `debit_credit_amount_ratio` | Decimal | `debit_amount / credit_amount` |

---

## Units & Conventions

- All monetary columns are in **Rs. crore** (1 crore = 10,000,000 / 10 million), matching RBI's published NEFT statistics.
- Transaction counts are raw counts (not in thousands/millions).
- Dates represent the reporting month; no day-level granularity exists in the source data.
- Missing amounts are treated as `0` (no reported activity), not as unknown/null, after cleaning.
