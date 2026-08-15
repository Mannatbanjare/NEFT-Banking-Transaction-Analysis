"""
eda.py
------
Exploratory Data Analysis on the cleaned NEFT transaction dataset.
Generates summary statistics and saves chart images to the images/ folder.

Input : data/processed/Cleaned_NEFT.csv
Output: images/eda_*.png, printed summary stats

Run:
    python python/eda.py
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "Cleaned_NEFT.csv"
IMG_DIR = Path(__file__).resolve().parent.parent / "images"

plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3


def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["transaction_date"])
    return df


def print_summary(df: pd.DataFrame):
    print("=" * 60)
    print("DATASET OVERVIEW")
    print("=" * 60)
    print(f"Rows: {df.shape[0]:,} | Columns: {df.shape[1]}")
    print(f"Date range: {df['transaction_date'].min().date()} -> {df['transaction_date'].max().date()}")
    print(f"Unique banks: {df['bank_name'].nunique()}")
    print()
    print("Total debit amount (Rs. crore):", round(df["debit_amount"].sum(), 2))
    print("Total credit amount (Rs. crore):", round(df["credit_amount"].sum(), 2))
    print("Total debit transactions:", int(df["debit_transactions"].sum()))
    print("Total credit transactions:", int(df["credit_transactions"].sum()))
    print()
    print("Top 10 banks by total amount:")
    top10 = (
        df.groupby("bank_name")["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    print(top10.to_string())


def plot_yearly_trend(df: pd.DataFrame):
    yearly = df.groupby("year")[["debit_amount", "credit_amount"]].sum()
    ax = yearly.plot(kind="line", marker="o")
    ax.set_title("NEFT Debit vs Credit Amount by Year")
    ax.set_ylabel("Amount (Rs. crore)")
    ax.set_xlabel("Year")
    plt.tight_layout()
    plt.savefig(IMG_DIR / "eda_yearly_trend.png", dpi=150)
    plt.close()


def plot_top_banks(df: pd.DataFrame):
    top10 = (
        df.groupby("bank_name")["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )
    ax = top10.plot(kind="barh", color="#1f4e79")
    ax.set_title("Top 10 Banks by Total NEFT Amount")
    ax.set_xlabel("Total Amount (Rs. crore)")
    plt.tight_layout()
    plt.savefig(IMG_DIR / "eda_top_banks.png", dpi=150)
    plt.close()


def plot_monthly_seasonality(df: pd.DataFrame):
    monthly = df.groupby("month_num")["total_transactions"].sum()
    ax = monthly.plot(kind="bar", color="#2e75b6")
    ax.set_title("Total Transactions by Calendar Month (All Years Combined)")
    ax.set_xlabel("Month Number")
    ax.set_ylabel("Total Transactions")
    plt.tight_layout()
    plt.savefig(IMG_DIR / "eda_monthly_seasonality.png", dpi=150)
    plt.close()


def plot_distribution(df: pd.DataFrame):
    fig, ax = plt.subplots()
    df[df["total_amount"] > 0]["total_amount"].apply(lambda x: x).plot(
        kind="hist", bins=60, ax=ax, color="#548235", log=True
    )
    ax.set_title("Distribution of Total Transaction Amount (log scale)")
    ax.set_xlabel("Total Amount (Rs. crore)")
    plt.tight_layout()
    plt.savefig(IMG_DIR / "eda_amount_distribution.png", dpi=150)
    plt.close()


def main():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    print_summary(df)
    plot_yearly_trend(df)
    plot_top_banks(df)
    plot_monthly_seasonality(df)
    plot_distribution(df)
    print("\nSaved charts to images/ folder:")
    for f in sorted(IMG_DIR.glob("eda_*.png")):
        print(" -", f.name)


if __name__ == "__main__":
    main()
