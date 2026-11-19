from pathlib import Path
import pandas as pd

project = Path.home() / "Documents" / "DA Project"
source = project / "data" / "raw" / "Data.xlsx"
output = project / "data" / "raw" / "Data.csv"

df = pd.read_excel(source, sheet_name="Online Retail", engine="openpyxl")

# Preserve missing IDs while removing the unwanted decimal suffix
df["CustomerID"] = df["CustomerID"].map(
    lambda x: str(int(x)) if pd.notna(x) else ""
)

df.to_csv(output, index=False, encoding="utf-8")

print("Rows:", len(df))
print("Columns:", len(df.columns))
print("CSV:", output)
print("Missing customer IDs:", df["CustomerID"].eq("").sum())
print("First customer IDs:", df["CustomerID"].head().tolist())
