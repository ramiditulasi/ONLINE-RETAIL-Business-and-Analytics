from pathlib import Path
import getpass

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Project folders
PROJECT = Path.home() / "Documents" / "DA Project"
REPORTS = PROJECT / "reports"
FIGURES = REPORTS / "figures"

REPORTS.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

# Connect to MySQL without saving the password in the script
password = getpass.getpass("MySQL root password: ")

connection_url = URL.create(
    drivername="mysql+mysqlconnector",
    username="root",
    password=password,
    host="localhost",
    database="online_retail",
)

engine = create_engine(connection_url, pool_pre_ping=True)

# 1. Dataset profile
with engine.connect() as conn:
    profile = pd.read_sql(
        text("""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(DISTINCT InvoiceNo) AS distinct_invoices,
                COUNT(DISTINCT StockCode) AS distinct_products,
                COUNT(DISTINCT Country) AS countries,
                COUNT(DISTINCT CustomerID) AS identifiable_customers
            FROM raw_invoice_lines
        """),
        conn,
    )

    quality = pd.read_sql(
        text("""
            SELECT
                COUNT(*) AS total_rows,
                SUM(Description IS NULL) AS missing_descriptions,
                SUM(CustomerID IS NULL OR CustomerID = '')
                    AS missing_customer_ids,
                SUM(Quantity < 0) AS negative_quantity_rows,
                SUM(UnitPrice <= 0) AS nonpositive_price_rows,
                SUM(InvoiceNo LIKE 'C%') AS cancellation_rows
            FROM raw_invoice_lines
        """),
        conn,
    )

    monthly = pd.read_sql(
        text("""
            SELECT
                DATE_FORMAT(InvoiceDate, '%Y-%m') AS sales_month,
                ROUND(SUM(Quantity * UnitPrice), 2) AS monthly_sales
            FROM raw_invoice_lines
            WHERE Quantity > 0
              AND UnitPrice > 0
              AND InvoiceNo NOT LIKE 'C%'
            GROUP BY DATE_FORMAT(InvoiceDate, '%Y-%m')
            ORDER BY sales_month
        """),
        conn,
    )

    countries = pd.read_sql(
        text("""
            SELECT
                Country,
                ROUND(SUM(Quantity * UnitPrice), 2) AS sales
            FROM raw_invoice_lines
            WHERE Quantity > 0
              AND UnitPrice > 0
              AND InvoiceNo NOT LIKE 'C%'
            GROUP BY Country
            ORDER BY sales DESC
            LIMIT 10
        """),
        conn,
    )

    rfm = pd.read_sql(
        text("""
            SELECT CustomerID, recency_days, frequency, monetary_value
            FROM customer_rfm
            ORDER BY monetary_value DESC
        """),
        conn,
    )

# 2. Display and export results
print("\nDATASET PROFILE")
print(profile.to_string(index=False))

print("\nDATA QUALITY")
print(quality.to_string(index=False))

print("\nTOP COUNTRIES")
print(countries.to_string(index=False))

profile.to_csv(REPORTS / "dataset_profile.csv", index=False)
quality.to_csv(REPORTS / "data_quality.csv", index=False)
monthly.to_csv(REPORTS / "monthly_sales.csv", index=False)
countries.to_csv(REPORTS / "top_countries.csv", index=False)
rfm.to_csv(REPORTS / "customer_rfm.csv", index=False)

# 3. Monthly sales chart
monthly["sales_month"] = pd.to_datetime(monthly["sales_month"])

plt.figure(figsize=(11, 5))
plt.plot(monthly["sales_month"], monthly["monthly_sales"], marker="o")
plt.title("Monthly Gross Positive Sales")
plt.xlabel("Month")
plt.ylabel("Sales (currency unconfirmed)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(FIGURES / "monthly_sales.png", dpi=150)
plt.close()

# 4. Top countries chart
country_chart = countries.sort_values("sales")

plt.figure(figsize=(10, 6))
plt.barh(country_chart["Country"], country_chart["sales"])
plt.title("Top 10 Countries by Gross Positive Sales")
plt.xlabel("Sales (currency unconfirmed)")
plt.tight_layout()
plt.savefig(FIGURES / "top_countries.png", dpi=150)
plt.close()

# 5. Customer frequency chart
frequency_groups = pd.cut(
    rfm["frequency"],
    bins=[0, 1, 5, 10, float("inf")],
    labels=["One invoice", "2-5 invoices",
            "6-10 invoices", "More than 10 invoices"],
)

frequency_counts = frequency_groups.value_counts().reindex(
    ["One invoice", "2-5 invoices",
     "6-10 invoices", "More than 10 invoices"],
    fill_value=0,
)

plt.figure(figsize=(9, 5))
plt.bar(frequency_counts.index.astype(str), frequency_counts.values)
plt.title("Customers by Purchase Frequency")
plt.xlabel("Number of eligible invoices")
plt.ylabel("Customers")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(FIGURES / "customer_frequency.png", dpi=150)
plt.close()

engine.dispose()

print("\nEDA completed successfully.")
print(f"Reports saved in: {REPORTS}")
print(f"Charts saved in: {FIGURES}")
