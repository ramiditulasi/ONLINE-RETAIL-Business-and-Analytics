
from pathlib import Path
import pandas as pd

project = Path.home() / "Documents" / "DA Project"
reports = project / "reports"

files = {
    "product_performance.csv": 3812,
    "country_performance.csv": 38,
    "customer_rfm.csv": 4338,
    "monthly_sales.csv": 13,
}

failed = False

for filename, expected_rows in files.items():
    path = reports / filename

    if not path.exists():
        print(f"FAIL: Missing file: {filename}")
        failed = True
        continue

    df = pd.read_csv(path)

    row_ok = len(df) == expected_rows
    columns_ok = len(df.columns) > 0
    null_rows = df.isnull().any(axis=1).sum()

    print(f"\nFile: {filename}")
    print(f"Rows: {len(df)} (expected {expected_rows})")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Rows with missing values: {null_rows}")
    print("Status:", "PASS" if row_ok and columns_ok else "FAIL")

    if not row_ok or not columns_ok:
        failed = True

print("\nOverall:", "CHECK FAILED" if failed else "ALL FILE CHECKS PASSED")

