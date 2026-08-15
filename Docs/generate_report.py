"""
generate_report.py
-------------------
Builds docs/Project_Report.pdf from the cleaned/featured dataset and the
EDA charts in images/. Not part of the core analysis pipeline — this is a
one-off utility to produce the polished PDF report for the repo.

Run:
    python docs/generate_report.py
"""

import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle,
    PageBreak, HRFlowable,
)

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "processed" / "Featured_NEFT.csv"
IMG_DIR = ROOT / "images"
OUT_PATH = ROOT / "docs" / "Project_Report.pdf"

NAVY = colors.HexColor("#0b2447")
BLUE = colors.HexColor("#2e75b6")
LIGHT = colors.HexColor("#eaf2fb")


def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["transaction_date"])


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", fontSize=26, leading=32,
                               textColor=NAVY, spaceAfter=6, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="ReportSubtitle", fontSize=13, leading=18,
                               textColor=BLUE, spaceAfter=20, fontName="Helvetica"))
    styles.add(ParagraphStyle(name="H1", fontSize=16, leading=20, textColor=NAVY,
                               spaceBefore=16, spaceAfter=8, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="H2", fontSize=12.5, leading=16, textColor=BLUE,
                               spaceBefore=10, spaceAfter=6, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="Body", fontSize=10.2, leading=15,
                               textColor=colors.HexColor("#222222"), spaceAfter=8))
    styles.add(ParagraphStyle(name="ReportBullet", fontSize=10.2, leading=15,
                               leftIndent=14, spaceAfter=4))
    return styles


def kpi_table(df):
    total_debit_amt = df["debit_amount"].sum()
    total_credit_amt = df["credit_amount"].sum()
    total_debit_txn = df["debit_transactions"].sum()
    total_credit_txn = df["credit_transactions"].sum()
    total_amt = df["total_amount"].sum()
    total_txn = df["total_transactions"].sum()

    data = [
        ["Metric", "Value"],
        ["Total Debit Amount", f"{total_debit_amt:,.0f} Cr"],
        ["Total Credit Amount", f"{total_credit_amt:,.0f} Cr"],
        ["Total Debit Transactions", f"{total_debit_txn:,.0f}"],
        ["Total Credit Transactions", f"{total_credit_txn:,.0f}"],
        ["Total Amount (Debit + Credit)", f"{total_amt:,.0f} Cr"],
        ["Total Transactions (Debit + Credit)", f"{total_txn:,.0f}"],
        ["Unique Reporting Banks", f"{df['bank_name'].nunique()}"],
        ["Date Range", f"{df['transaction_date'].min().strftime('%b %Y')} - {df['transaction_date'].max().strftime('%b %Y')}"],
    ]
    t = Table(data, colWidths=[9 * cm, 6 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def top_bank_table(df):
    top = (
        df.groupby("bank_name")["total_amount"].sum()
        .sort_values(ascending=False).head(10)
    )
    total = df["total_amount"].sum()
    data = [["Rank", "Bank", "Total Amount (Cr)", "Market Share"]]
    for i, (bank, amt) in enumerate(top.items(), start=1):
        data.append([str(i), bank.title(), f"{amt:,.0f}", f"{amt/total*100:.2f}%"])
    t = Table(data, colWidths=[1.5 * cm, 7.5 * cm, 3.5 * cm, 2.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 0), (3, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def main():
    df = load_data()
    styles = build_styles()
    doc = SimpleDocTemplate(str(OUT_PATH), pagesize=A4,
                             topMargin=1.6 * cm, bottomMargin=1.6 * cm,
                             leftMargin=1.8 * cm, rightMargin=1.8 * cm)
    story = []

    # ---- Cover ----
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("NEFT Banking Transaction Analysis", styles["ReportTitle"]))
    story.append(Paragraph("Project Report — End-to-End Data Analytics Case Study", styles["ReportSubtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=14))
    story.append(Paragraph(
        "Author: Mannat &nbsp;|&nbsp; Tools: Python, MySQL, Power BI &nbsp;|&nbsp; "
        "Data: RBI NEFT Statistics (June 2008 - June 2020)", styles["Body"]))
    story.append(Spacer(1, 0.6 * cm))
    banner = IMG_DIR / "banner.png"
    if banner.exists():
        story.append(RLImage(str(banner), width=17 * cm, height=17 * cm * (320 / 1280)))
    story.append(PageBreak())

    # ---- Executive Summary ----
    story.append(Paragraph("1. Executive Summary", styles["H1"]))
    story.append(Paragraph(
        "This project analyzes 12+ years of India's NEFT (National Electronic Funds Transfer) "
        "banking data, covering 267 banks and over 21,000 bank-month records between June 2008 and "
        "June 2020. The goal was to build a full analytics pipeline &mdash; from raw data cleaning "
        "through SQL-based analysis to an interactive Power BI dashboard &mdash; to understand how "
        "NEFT adoption grew over time, which banks dominate transaction volume, and what seasonal "
        "or structural patterns exist in the data.", styles["Body"]))
    story.append(Paragraph("Key headline numbers:", styles["H2"]))
    story.append(kpi_table(df))
    story.append(Spacer(1, 0.4 * cm))

    # ---- Methodology ----
    story.append(Paragraph("2. Methodology", styles["H1"]))
    story.append(Paragraph(
        "The project follows a standard analytics-engineering workflow, mirrored in the folder "
        "structure of this repository:", styles["Body"]))
    steps = [
        "<b>Data Cleaning (Python & SQL):</b> standardized bank names, parsed the 'Month YYYY' text field into proper dates, filled missing numeric values, removed duplicate bank/month records, and derived total transaction/amount fields.",
        "<b>Database Design (MySQL):</b> a staging table mirrors the raw CSV; a cleaned production table (neft_transactions) holds analysis-ready data; an optional star-schema (dim_bank / fact_neft_monthly) supports BI-tool style modelling.",
        "<b>Feature Engineering (Python):</b> month-over-month and year-over-year growth rates, 3-month rolling averages, market share per month, overall bank ranking, and debit/credit ratios.",
        "<b>Exploratory Data Analysis (Python):</b> summary statistics and trend/distribution charts (see images/ folder).",
        "<b>Dashboard (Power BI):</b> an interactive report with bank/year/month slicers, KPI cards, and trend/composition visuals (see powerbi/NEFT_Analysis.pbix and dashboard/dashboard.png).",
    ]
    for s in steps:
        story.append(Paragraph("&bull; " + s, styles["ReportBullet"]))
    story.append(Spacer(1, 0.3 * cm))

    # ---- Key Findings ----
    story.append(Paragraph("3. Key Findings", styles["H1"]))

    top5_pct = (
        df.groupby("bank_name")["total_amount"].sum().sort_values(ascending=False).head(5).sum()
        / df["total_amount"].sum() * 100
    )
    story.append(Paragraph("3.1 Market Concentration", styles["H2"]))
    story.append(Paragraph(
        f"NEFT transaction value is highly concentrated: the top 5 banks (State Bank of India, HDFC "
        f"Bank, ICICI Bank, Axis Bank, and Citi Bank) account for approximately "
        f"<b>{top5_pct:.1f}%</b> of total NEFT amount across the full 2008-2020 period, while the top "
        f"10 banks account for roughly 64%. This reflects the outsized role of India's largest "
        f"public-sector and private-sector banks in digital payment infrastructure.", styles["Body"]))
    story.append(top_bank_table(df))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("3.2 Growth Trend", styles["H2"]))
    story.append(Paragraph(
        "Total NEFT transaction amount grew from roughly 2.1 million Cr in 2008 to over 465 million "
        "Cr in 2019, before a partial dip in 2020 (data through June only, coinciding with COVID-19 "
        "disruption). Between 2009 and 2019, the compound annual growth rate (CAGR) of total NEFT "
        "amount was approximately <b>59.5% per year</b>, reflecting rapid digitization of retail and "
        "corporate payments in India over the decade.", styles["Body"]))
    yearly_chart = IMG_DIR / "eda_yearly_trend.png"
    if yearly_chart.exists():
        story.append(RLImage(str(yearly_chart), width=15 * cm, height=15 * cm * 0.6))
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph("3.3 Top Banks by Volume", styles["H2"]))
    top_banks_chart = IMG_DIR / "eda_top_banks.png"
    if top_banks_chart.exists():
        story.append(RLImage(str(top_banks_chart), width=15 * cm, height=15 * cm * 0.6))
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph("3.4 Seasonality", styles["H2"]))
    story.append(Paragraph(
        "Aggregating transaction counts by calendar month (across all years) shows month-to-month "
        "variation consistent with typical business and fiscal-year-end payment cycles, with March "
        "(the end of the Indian financial year) among the busier months. This is a useful signal for "
        "banks and payment infrastructure teams when planning capacity.", styles["Body"]))
    seasonality_chart = IMG_DIR / "eda_monthly_seasonality.png"
    if seasonality_chart.exists():
        story.append(RLImage(str(seasonality_chart), width=15 * cm, height=15 * cm * 0.6))

    story.append(PageBreak())

    # ---- Dashboard ----
    story.append(Paragraph("4. Power BI Dashboard", styles["H1"]))
    story.append(Paragraph(
        "The interactive dashboard (powerbi/NEFT_Analysis.pbix) exposes the same data through KPI "
        "cards, a debit-vs-credit trend line, a bank-contribution treemap, a top-10 donut chart, and "
        "a monthly debit-vs-credit column chart, all filterable by bank, year, and month.", styles["Body"]))
    dash_png = ROOT / "dashboard" / "dashboard.png"
    if dash_png.exists():
        story.append(RLImage(str(dash_png), width=16.5 * cm, height=16.5 * cm * (790 / 1291)))
    story.append(Spacer(1, 0.3 * cm))

    # ---- Tech Stack ----
    story.append(Paragraph("5. Tech Stack", styles["H1"]))
    tech = [
        "<b>Python</b> (pandas, numpy, matplotlib) &mdash; data cleaning, feature engineering, EDA",
        "<b>MySQL</b> &mdash; schema design, cleaning transforms, analytical SQL (window functions, CTEs)",
        "<b>Power BI</b> &mdash; interactive dashboard and DAX-based KPI cards",
        "<b>Git / GitHub</b> &mdash; version control and project hosting",
    ]
    for t in tech:
        story.append(Paragraph("&bull; " + t, styles["ReportBullet"]))

    # ---- Conclusion ----
    story.append(Paragraph("6. Conclusion & Next Steps", styles["H1"]))
    story.append(Paragraph(
        "This analysis confirms strong, sustained growth in NEFT adoption over 2008-2019 and a "
        "market structure dominated by a handful of large banks. Potential extensions include: "
        "forecasting future transaction volume with a time-series model, joining in RTGS/IMPS/UPI "
        "data for a full digital-payments comparison, and building bank-level anomaly detection to "
        "flag unusual month-over-month swings.", styles["Body"]))

    doc.build(story)
    print(f"Report generated: {OUT_PATH}")


if __name__ == "__main__":
    main()
