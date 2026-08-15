"""
data_cleaning.py
-----------------
Cleans and standardizes the raw RBI NEFT banking transaction dataset.

Input : data/raw/NEFT.csv
Output: data/processed/Cleaned_NEFT.csv

Run:
    python python/data_cleaning.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "NEFT.csv"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "Cleaned_NEFT.csv"


def load_data(path: Path) -> pd.DataFrame:
    """Load the raw CSV file."""
    df = pd.read_csv(path)
    print(f"Loaded raw data: {df.shape[0]:,} rows, {df.shape[1]} columns")
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lower-case and snake_case all column names."""
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def clean_bank_names(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace and standardize casing of bank names."""
    df["bank_name"] = (
        df["bank_name"]
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(r"\s+", " ", regex=True)
    )
    return df


def parse_month(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the 'month' text column (e.g. 'January 2020') into a proper date."""
    df["transaction_date"] = pd.to_datetime(df["month"], format="%B %Y", errors="coerce")
    df["year"] = df["transaction_date"].dt.year
    df["month_num"] = df["transaction_date"].dt.month
    df["month_name"] = df["transaction_date"].dt.strftime("%B")
    return df


def handle_missing_and_invalid(df: pd.DataFrame) -> pd.DataFrame:
    """Handle nulls and invalid numeric values."""
    numeric_cols = ["debit_transactions", "debit_amount", "credit_transactions", "credit_amount"]

    before = len(df)

    # Drop rows where the date could not be parsed
    df = df.dropna(subset=["transaction_date"])

    # Fill missing numeric values with 0 (a missing amount means no reported activity)
    for col in numeric_cols:
        n_missing = df[col].isna().sum()
        if n_missing:
            print(f"  Filling {n_missing} missing values in '{col}' with 0")
        df[col] = df[col].fillna(0)

    # Remove negative values (data entry errors)
    for col in numeric_cols:
        neg = (df[col] < 0).sum()
        if neg:
            print(f"  Found {neg} negative values in '{col}' -> converting to absolute value")
            df[col] = df[col].abs()

    after = len(df)
    print(f"Removed {before - after} unparsable rows")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate bank/month records, keeping the first occurrence."""
    before = len(df)
    df = df.drop_duplicates(subset=["bank_name", "month"], keep="first")
    after = len(df)
    if before - after:
        print(f"Removed {before - after} duplicate bank/month rows")
    return df


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add analysis-friendly derived columns."""
    df["total_transactions"] = df["debit_transactions"] + df["credit_transactions"]
    df["total_amount"] = df["debit_amount"] + df["credit_amount"]

    # Average ticket size (amount per transaction), avoiding divide-by-zero
    df["avg_debit_ticket_size"] = np.where(
        df["debit_transactions"] > 0, df["debit_amount"] / df["debit_transactions"], 0
    )
    df["avg_credit_ticket_size"] = np.where(
        df["credit_transactions"] > 0, df["credit_amount"] / df["credit_transactions"], 0
    )

    # Net flow (credit - debit) amount, useful for spotting inflow/outflow-heavy banks
    df["net_amount_flow"] = df["credit_amount"] - df["debit_amount"]

    return df


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    ordered = [
        "bank_name", "transaction_date", "year", "month_num", "month_name",
        "debit_transactions", "debit_amount", "credit_transactions", "credit_amount",
        "total_transactions", "total_amount",
        "avg_debit_ticket_size", "avg_credit_ticket_size", "net_amount_flow",
    ]
    return df[ordered]


def main():
    df = load_data(RAW_PATH)
    df = standardize_columns(df)
    df = clean_bank_names(df)
    df = parse_month(df)
    df = handle_missing_and_invalid(df)
    df = remove_duplicates(df)
    df = add_derived_columns(df)
    df = reorder_columns(df)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    print("\nCleaning complete.")
    print(f"Final shape: {df.shape[0]:,} rows, {df.shape[1]} columns")
    print(f"Saved cleaned file to: {OUT_PATH}")


if __name__ == "__main__":
    main()
