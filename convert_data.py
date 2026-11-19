from pathlib import Path
import pandas as pd

# Project paths
project = Path.home() / "Documents" / "DA Project"
source = project / "data" / "raw" / "Data.xlsx"
output_dir = project / "data" / "raw"
output = output_dir / "Data.csv"

# Check the source file
if not source.exists():
    raise FileNotFoundError(f"Dataset not found: {source}")

# Inspect available worksheets
excel = pd.ExcelFile(source, engine="openpyxl")
print("Worksheets:", excel.sheet_names)

# Read the first worksheet
df = pd.read_excel(source, sheet_name=0, engine="openpyxl")

# Display initial data profile
print("\nDataset dimensions:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst five rows:")
print(df.head().to_string())

print("\nMissing values per column:")
print(df.isnull().sum())

# Export without modifying the original workbook
df.to_csv(output, index=False, encoding="utf-8-sig")

print(f"\nCSV successfully exported to: {output}")
print(f"Rows exported: {len(df):,}")
