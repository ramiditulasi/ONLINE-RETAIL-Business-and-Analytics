import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
import getpass

project = Path.home() / "Documents" / "DA Project"
csv_file = project / "data" / "raw" / "Data.csv"

password = getpass.getpass("MySQL root password: ")

# Connect to the database
engine = create_engine(
    "mysql+mysqlconnector://root:"
    + password.replace("@", "%40").replace(":", "%3A").replace("/", "%2F")
    + "@localhost/online_retail",
    pool_pre_ping=True
)

# Verify the connection
with engine.connect() as conn:
    print("Connected to online_retail!")

# Read and import data in batches
chunksize = 5000
total_rows = 0

for chunk in pd.read_csv(
    csv_file,
    chunksize=chunksize,
    dtype={"InvoiceNo": str, "StockCode": str, "CustomerID": str},
    keep_default_na=True
):
    chunk.to_sql(
        "raw_invoice_lines",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi"
    )
    total_rows += len(chunk)
    print(f"Imported {total_rows:,} rows")

with engine.connect() as conn:
    count = conn.execute(
        text("SELECT COUNT(*) FROM raw_invoice_lines")
    ).scalar()

print(f"Import finished. Rows in table: {count:,}")
