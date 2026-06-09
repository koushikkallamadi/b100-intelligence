import pandas as pd
import os

# Paths
RAW_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "b100_project", "data", "raw")
CLEAN_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "b100_project", "data", "clean")

# All 7 files
files = [
    "analysis",
    "balancesheet",
    "cashflow",
    "companies",
    "documents",
    "profitandloss",
    "prosandcons"
]

print("Starting extraction...\n")

for file in files:
    xlsx_path = os.path.join(RAW_PATH, f"{file}.xlsx")
    csv_path = os.path.join(CLEAN_PATH, f"{file}.csv")
    
    df = pd.read_excel(xlsx_path, skiprows=1)
    df.to_csv(csv_path, index=False)
    
    print(f"[SUCCESS] {file}.xlsx -> {file}.csv | Rows: {len(df)} | Columns: {list(df.columns)}")

print("\nDone! All files saved to data/clean/")
