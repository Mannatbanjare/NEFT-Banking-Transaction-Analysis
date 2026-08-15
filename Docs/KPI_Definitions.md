# KPI Definitions

This document defines every KPI and visual shown on the Power BI dashboard (`powerbi/NEFT_Analysis.pbix`), so results can be reproduced from the SQL/Python layer.

## Headline Cards

| KPI | Formula | Notes |
|---|---|---|
| **Total Debit Amount** | `SUM(debit_amount)` | In Rs. crore, across all banks and all months in the filter context |
| **Total Credit Amount** | `SUM(credit_amount)` | In Rs. crore |
| **Total Debit Transaction** | `SUM(debit_transactions)` | Count of outward NEFT transactions |
| **Total Credit Transaction** | `SUM(credit_transactions)` | Count of inward NEFT transactions |
| **Total Amount** | `SUM(debit_amount) + SUM(credit_amount)` | Combined value of all NEFT activity |
| **Total Transaction** | `SUM(debit_transactions) + SUM(credit_transactions)` | Combined count of all NEFT activity |

## Visual-Level KPIs

### Total Debit vs Credit Transaction (line chart)
- **X-axis:** `transaction_date` (monthly grain)
- **Y-axis:** `SUM(debit_amount)` and `SUM(credit_amount)` plotted as two series
- **Purpose:** Show the long-run growth trajectory of NEFT adoption in India (2008–2020)

### Total Amount by Bank (bar chart)
- **Measure:** `SUM(total_amount)` grouped by `bank_name`
- **Sort:** Descending, typically filtered/sliced to the smaller regional banks in the current view
- **Purpose:** Compare individual bank contribution

### Top 10 Bank Share (donut chart)
- **Measure:** `SUM(total_amount)` for the top 10 banks by total amount, with `%` = `bank amount / SUM(total_amount) for all banks`
- **Purpose:** Visualize market concentration — the dashboard shows the top 5 banks (SBI, HDFC, ICICI, Axis, Citi) account for the majority of NEFT value

### Monthly Debit vs Credit Transactions (clustered column)
- **X-axis:** `month_name`
- **Y-axis:** `SUM(debit_transactions)` and `SUM(credit_transactions)`
- **Purpose:** Check seasonality — whether certain months (e.g. March, financial year-end) see disproportionately higher activity

### Bank Contribution (treemap)
- **Size:** `SUM(total_amount)` per bank
- **Purpose:** At-a-glance visual ranking of every bank's footprint, sized by value

## Derived / Analytical KPIs (used in Python & SQL layers, not always on the dashboard)

| KPI | Formula | Business Meaning |
|---|---|---|
| **Average Ticket Size (Debit)** | `debit_amount / debit_transactions` | Typical size of an outward transaction for a bank |
| **Average Ticket Size (Credit)** | `credit_amount / credit_transactions` | Typical size of an inward transaction for a bank |
| **Net Amount Flow** | `credit_amount - debit_amount` | Whether a bank is a net receiver (+) or net sender (-) of NEFT funds |
| **MoM Growth %** | `(current_month - prior_month) / prior_month * 100` | Short-term momentum per bank |
| **YoY Growth %** | `(current_month - same_month_prior_year) / same_month_prior_year * 100` | Year-over-year growth, removes seasonality |
| **Market Share %** | `bank total_amount (that month) / all-bank total_amount (that month) * 100` | Competitive positioning within a given month |
| **Cumulative Market Share** | Running sum of `% share` ordered by bank rank | Used to test concentration, e.g. "top 5 banks = X% of the market" |

## Filters / Slicers

- **Bank** — single or multi-select filter on `bank_name`
- **Year** — filter on `year`
- **Month Name** — filter on `month_name`

All KPIs recalculate dynamically based on the combination of slicers selected, consistent with standard Power BI filter-context behavior.
