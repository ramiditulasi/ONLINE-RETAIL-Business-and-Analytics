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

queries = {
    "product_performance": """
        SELECT * FROM product_performance
        ORDER BY total_sales DESC
    """,
    "country_performance": """
        SELECT * FROM country_performance
        ORDER BY total_sales DESC
    """,
    "customer_rfm": """
        SELECT * FROM customer_rfm
        ORDER BY monetary_value DESC
    """,
    "monthly_sales": """
        SELECT
            DATE_FORMAT(InvoiceDate, '%Y-%m') AS sales_month,
            ROUND(SUM(Quantity * UnitPrice), 2) AS monthly_sales,
            COUNT(DISTINCT InvoiceNo) AS invoice_count
        FROM clean_sales
        GROUP BY DATE_FORMAT(InvoiceDate, '%Y-%m')
        ORDER BY sales_month
    """,
}

with engine.connect() as connection:
    for name, query in queries.items():
        df = pd.read_sql(text(query), connection)
        path = REPORTS / f"{name}.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"Exported {name}: {len(df):,} rows -> {path}")

engine.dispose()
print("\nAll report exports completed.")
