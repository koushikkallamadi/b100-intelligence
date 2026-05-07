import pandas as pd
from sqlalchemy import create_engine
import os

CLEAN_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "b100_project", "data", "clean")

# Connect to PostgreSQL
engine = create_engine("postgresql://postgres:03112005@localhost:5432/b100")

print("Connecting to database...\n")

# Load each clean CSV into PostgreSQL
tables = {
    "companies": "companies_clean.csv",
    "balancesheet": "balancesheet_clean.csv",
    "profitandloss": "profitloss_clean.csv",
    "cashflow": "cashflow_clean.csv",
    "analysis": "analysis_clean.csv",
    "prosandcons": "prosandcons_clean.csv"
}

for table_name, csv_file in tables.items():
    df = pd.read_csv(f"{CLEAN_PATH}/{csv_file}")
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"✅ {table_name} loaded → {len(df)} rows")

print("\nScript 3 Complete! ✅")
print("All data is now in PostgreSQL database 'b100'!")