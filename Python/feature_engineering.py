"""
feature_engineering.py
-----------------------
Builds analysis-ready features on top of the cleaned NEFT dataset:
  - Month-over-month growth rates
  - Year-over-year growth rates
  - Rolling 3-month averages
  - Bank market-share ranking
  - Debit/credit ratio

Input : data/processed/Cleaned_NEFT.csv
Output: data/processed/Featured_NEFT.csv

Run:
    python python/feature_engineering.py
"""

import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "Cleaned_NEFT.csv"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "Featured_NEFT.csv"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["transaction_date"])
    return df.sort_values(["bank_name", "transaction_date"])


def add_growth_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Month-over-month and year-over-year growth per bank."""
    df["mom_amount_growth_pct"] = (
        df.groupby("bank_name")["total_amount"].pct_change(1) * 100
    ).round(2)

    df["yoy_amount_growth_pct"] = (
        df.groupby("bank_name")["total_amount"].pct_change(12) * 100
    ).round(2)

    return df


def add_rolling_averages(df: pd.DataFrame) -> pd.DataFrame:
    """3-month rolling average of total amount, per bank."""
    df["rolling_3m_avg_amount"] = (
        df.groupby("bank_name")["total_amount"]
        .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
        .round(2)
    )
    return df


def add_market_share(df: pd.DataFrame) -> pd.DataFrame:
    """Each bank's share of total NEFT amount within its own month."""
    monthly_total = df.groupby("transaction_date")["total_amount"].transform("sum")
    df["market_share_pct"] = (df["total_amount"] / monthly_total * 100).round(4)

    # Overall rank of the bank across the full dataset (1 = largest)
    bank_totals = df.groupby("bank_name")["total_amount"].sum().rank(ascending=False, method="min")
    df["overall_bank_rank"] = df["bank_name"].map(bank_totals).astype(int)

    return df


def add_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """Debit-to-credit ratios to flag inflow- vs outflow-heavy banks."""
    import numpy as np

    df["debit_credit_txn_ratio"] = (
        df["debit_transactions"] / df["credit_transactions"].replace(0, np.nan)
    ).round(3)

    df["debit_credit_amount_ratio"] = (
        df["debit_amount"] / df["credit_amount"].replace(0, np.nan)
    ).round(3)

    return df


def main():
    df = load_data()
    df = add_growth_rates(df)
    df = add_rolling_averages(df)
    df = add_market_share(df)
    df = add_ratios(df)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    print(f"Feature engineering complete. Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"Saved to: {OUT_PATH}")
    print("\nSample of new features:")
    cols = [
        "bank_name", "transaction_date", "mom_amount_growth_pct",
        "yoy_amount_growth_pct", "rolling_3m_avg_amount",
        "market_share_pct", "overall_bank_rank",
    ]
    print(df[cols].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
