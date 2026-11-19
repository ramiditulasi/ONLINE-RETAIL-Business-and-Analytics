from pathlib import Path
import getpass

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

PROJECT = Path.home() / "Documents" / "DA Project"
REPORTS = PROJECT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

password = getpass.getpass("MySQL root password: ")

engine = create_engine(
    URL.create(
        drivername="mysql+mysqlconnector",
        username="root",
        password=password,
        host="localhost",
        database="online_retail",
    ),
    pool_pre_ping=True,
)

quality_sql = text("""
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT StockCode) AS distinct_stock_codes,
    SUM(Description IS NULL OR TRIM(Description) = '')
        AS missing_descriptions,
    SUM(CustomerID IS NULL OR CustomerID = '')
        AS missing_customer_ids,
    SUM(Quantity < 0) AS negative_quantity_rows,
    SUM(UnitPrice <= 0) AS nonpositive_price_rows,
    SUM(InvoiceNo LIKE 'C%') AS cancellation_rows
FROM raw_invoice_lines
""")

with engine.connect() as conn:
    quality = pd.read_sql(quality_sql, conn)

quality.to_csv(REPORTS / "data_quality_summary.csv", index=False)

print("\nData-quality summary:")
print(quality.to_string(index=False))
print(f"\nSaved: {REPORTS / 'data_quality_summary.csv'}")

engine.dispose()
