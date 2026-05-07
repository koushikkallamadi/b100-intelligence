import pandas as pd
import os
import numpy as np

CLEAN_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "b100_project", "data", "clean")

# ── 1. Load all CSVs ──────────────────────────────────────────
companies = pd.read_csv(f"{CLEAN_PATH}/companies.csv")
balancesheet = pd.read_csv(f"{CLEAN_PATH}/balancesheet.csv")
profitloss = pd.read_csv(f"{CLEAN_PATH}/profitandloss.csv")
cashflow = pd.read_csv(f"{CLEAN_PATH}/cashflow.csv")
analysis = pd.read_csv(f"{CLEAN_PATH}/analysis.csv")
prosandcons = pd.read_csv(f"{CLEAN_PATH}/prosandcons.csv")

print("✅ All CSVs loaded\n")

# ── 2. Replace string NULLs with actual NaN ───────────────────
for df in [companies, balancesheet, profitloss, cashflow, analysis, prosandcons]:
    df.replace(['NULL', 'Null', 'null', 'N/A', ''], np.nan, inplace=True)

print("✅ NULL values cleaned\n")

# ── 3. Clean company names ────────────────────────────────────
companies['company_name'] = companies['company_name'].astype(str).str.strip()
print("✅ Company names cleaned\n")

# ── 4. Print shape of each table ─────────────────────────────
print("── Table Shapes ──")
print(f"companies     : {companies.shape}")
print(f"balancesheet  : {balancesheet.shape}")
print(f"profitandloss : {profitloss.shape}")
print(f"cashflow      : {cashflow.shape}")
print(f"analysis      : {analysis.shape}")
print(f"prosandcons   : {prosandcons.shape}")

# ── 5. Computed columns ───────────────────────────────────────

# Balance Sheet
balancesheet['debt_to_equity'] = (
    pd.to_numeric(balancesheet.get('borrowings', 0), errors='coerce') /
    (pd.to_numeric(balancesheet.get('equity_capital', 0), errors='coerce') +
     pd.to_numeric(balancesheet.get('reserves', 0), errors='coerce'))
)

# Profit & Loss
profitloss['net_profit_margin_pct'] = (
    pd.to_numeric(profitloss.get('net_profit', 0), errors='coerce') /
    pd.to_numeric(profitloss.get('sales', 0), errors='coerce') * 100
)

# Cash Flow
cashflow['free_cash_flow'] = (
    pd.to_numeric(cashflow.get('operating_activity', 0), errors='coerce') +
    pd.to_numeric(cashflow.get('investing_activity', 0), errors='coerce')
)

print("\n✅ Computed columns added\n")

# ── 6. Save cleaned files ─────────────────────────────────────
companies.to_csv(f"{CLEAN_PATH}/companies_clean.csv", index=False)
balancesheet.to_csv(f"{CLEAN_PATH}/balancesheet_clean.csv", index=False)
profitloss.to_csv(f"{CLEAN_PATH}/profitloss_clean.csv", index=False)
cashflow.to_csv(f"{CLEAN_PATH}/cashflow_clean.csv", index=False)
analysis.to_csv(f"{CLEAN_PATH}/analysis_clean.csv", index=False)
prosandcons.to_csv(f"{CLEAN_PATH}/prosandcons_clean.csv", index=False)

print("✅ All cleaned files saved to data/clean/")
print("\nScript 2 Complete! ✅")