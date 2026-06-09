import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# ── 1. Configuration & Setup ──────────────────────────────────
try:
    from decouple import config
    DATABASE_URL = config("DATABASE_URL", default="postgresql://postgres:03112005@localhost:5432/b100")
except ImportError:
    DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:03112005@localhost:5432/b100")

# Compute base path relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH = os.path.join(BASE_DIR, "data", "clean")
SCHEMA_SQL_PATH = os.path.join(BASE_DIR, "etl", "schema.sql")

print("Initializing Data Warehouse Load...")
print(f"Target DB Connection: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    # Test connection
    with engine.connect() as conn:
        print("[SUCCESS] Connected to PostgreSQL successfully!")
except Exception as e:
    print("\n[ERROR] Connection Error: Could not connect to PostgreSQL.")
    print("Please make sure PostgreSQL is running, the database 'b100' exists, and the credentials are correct.")
    print(f"Error details: {e}")
    print("\n[TIP] You can set a custom connection string in a `.env` file like:")
    print("DATABASE_URL=postgresql://user:password@host:port/dbname\n")
    import sys
    sys.exit(1)

# ── 2. Run schema.sql to initialize tables ────────────────────
print("\nInitializing Star Schema tables...")
try:
    with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    with engine.connect() as conn:
        conn.execute(text(schema_sql))
        conn.commit()
    print("[SUCCESS] Star Schema tables created successfully!")
except Exception as e:
    print(f"[ERROR] Error executing schema.sql: {e}")
    import sys
    sys.exit(1)

# ── 3. Load & Clean Data for Warehouse ─────────────────────────
print("\nLoading datasets from CSV...")
try:
    companies = pd.read_csv(os.path.join(CLEAN_PATH, "companies_clean.csv"))
    balancesheet = pd.read_csv(os.path.join(CLEAN_PATH, "balancesheet_clean.csv"))
    profitloss = pd.read_csv(os.path.join(CLEAN_PATH, "profitloss_clean.csv"))
    cashflow = pd.read_csv(os.path.join(CLEAN_PATH, "cashflow_clean.csv"))
    analysis = pd.read_csv(os.path.join(CLEAN_PATH, "analysis_clean.csv"))
    prosandcons = pd.read_csv(os.path.join(CLEAN_PATH, "prosandcons_clean.csv"))
    documents = pd.read_csv(os.path.join(CLEAN_PATH, "documents.csv"))
    
    # ML Outputs
    scores = pd.read_csv(os.path.join(CLEAN_PATH, "scores_clean.csv"))
    anomalies = pd.read_csv(os.path.join(CLEAN_PATH, "anomalies_clean.csv"))
    peer_mapping = pd.read_csv(os.path.join(CLEAN_PATH, "peer_mapping.csv"))
    forecasts = pd.read_csv(os.path.join(CLEAN_PATH, "forecasts_clean.csv"))
except Exception as e:
    print(f"[ERROR] Error loading cleaned CSV files: {e}")
    import sys
    sys.exit(1)

# ── 4. Sector Classification Dictionary ───────────────────────
sector_map = {
    "TCS": "IT & Software", "INFY": "IT & Software", "WIPRO": "IT & Software", 
    "HCLTECH": "IT & Software", "TECHM": "IT & Software", "LTIM": "IT & Software",
    "COFORGE": "IT & Software",
    "HDFCBANK": "Banking & Financial Services", "AXISBANK": "Banking & Financial Services",
    "BANKBARODA": "Banking & Financial Services", "SBIN": "Banking & Financial Services",
    "ICICIBANK": "Banking & Financial Services", "KOTAKBANK": "Banking & Financial Services",
    "PNB": "Banking & Financial Services", "PFC": "Banking & Financial Services",
    "RECLTD": "Banking & Financial Services", "LICI": "Banking & Financial Services",
    "SBILIFE": "Banking & Financial Services", "HDFCLIFE": "Banking & Financial Services",
    "BAJFINANCE": "Banking & Financial Services", "BAJAJFINSV": "Banking & Financial Services",
    "CHOLAFIN": "Banking & Financial Services", "MUTHOOTFIN": "Banking & Financial Services",
    "SHRIRAMFIN": "Banking & Financial Services",
    "MARUTI": "Automobile & Components", "TATAMOTORS": "Automobile & Components",
    "M&M": "Automobile & Components", "HEROMOTOCO": "Automobile & Components",
    "BAJAJ-AUTO": "Automobile & Components", "EICHERMOT": "Automobile & Components",
    "TIINDIA": "Automobile & Components",
    "NTPC": "Power & Utilities", "POWERGRID": "Power & Utilities",
    "ADANIPOWER": "Power & Utilities", "TATAPOWER": "Power & Utilities",
    "NHPC": "Power & Utilities", "SJVN": "Power & Utilities",
    "TATASTEEL": "Metals & Mining", "JSWSTEEL": "Metals & Mining",
    "HINDALCO": "Metals & Mining", "COALINDIA": "Metals & Mining",
    "NMDC": "Metals & Mining", "NATIONALUM": "Metals & Mining",
    "ITC": "Consumer Goods & Retail", "HINDUNILVR": "Consumer Goods & Retail",
    "NESTLEIND": "Consumer Goods & Retail", "BRITANNIA": "Consumer Goods & Retail",
    "VBL": "Consumer Goods & Retail", "DMART": "Consumer Goods & Retail",
    "TATACONSUM": "Consumer Goods & Retail", "COLPAL": "Consumer Goods & Retail",
    "SUNPHARMA": "Pharmaceuticals & Healthcare", "CIPLA": "Pharmaceuticals & Healthcare",
    "DRREDDY": "Pharmaceuticals & Healthcare", "DIVISLAB": "Pharmaceuticals & Healthcare",
    "APOLLOHOSP": "Pharmaceuticals & Healthcare", "ABBOTINDIA": "Pharmaceuticals & Healthcare",
    "MAXHEALTH": "Pharmaceuticals & Healthcare", "TORNTPHARM": "Pharmaceuticals & Healthcare"
}

def get_sector(symbol, about=""):
    symbol = str(symbol).strip().upper()
    if symbol in sector_map:
        return sector_map[symbol]
    
    about_lower = str(about).lower()
    if "bank" in about_lower or "finance" in about_lower or "insurance" in about_lower:
        return "Banking & Financial Services"
    elif "software" in about_lower or "technology" in about_lower or "digital" in about_lower:
        return "IT & Software"
    elif "power" in about_lower or "electricity" in about_lower or "energy" in about_lower:
        return "Power & Utilities"
    elif "pharma" in about_lower or "healthcare" in about_lower or "medical" in about_lower:
        return "Pharmaceuticals & Healthcare"
    elif "steel" in about_lower or "metal" in about_lower or "mining" in about_lower:
        return "Metals & Mining"
    elif "motor" in about_lower or "automobil" in about_lower:
        return "Automobile & Components"
    
    return "Industrial & Materials"

banking_symbols = {"HDFCBANK", "AXISBANK", "BANKBARODA", "SBIN", "ICICIBANK", "KOTAKBANK", "PNB"}

# ── 5. Populate dim_sector ────────────────────────────────────
print("Populating dim_sector...")
sectors = set()
for idx, row in companies.iterrows():
    sect = get_sector(row['id'], row.get('about_company', ''))
    sectors.add(sect)

dim_sector_df = pd.DataFrame([{"sector_name": s, "sector_desc": f"{s} sector companies"} for s in sectors])
dim_sector_df.to_sql("dim_sector", engine, if_exists="append", index=False)
print(f"[SUCCESS] Loaded {len(dim_sector_df)} sectors")

# ── 6. Populate dim_company ───────────────────────────────────
print("Populating dim_company...")
dim_company_rows = []
for idx, row in companies.iterrows():
    symbol = row['id']
    sect = get_sector(symbol, row.get('about_company', ''))
    is_bank = symbol in banking_symbols or str(symbol).endswith("BANK")
    
    dim_company_rows.append({
        "symbol": symbol,
        "company_name": row['company_name'],
        "company_logo": row.get('company_logo', None),
        "chart_link": row.get('chart_link', None),
        "about_company": row.get('about_company', None),
        "website": row.get('website', None),
        "nse_profile": row.get('nse_profile', None),
        "bse_profile": row.get('bse_profile', None),
        "face_value": row.get('face_value', None),
        "book_value": row.get('book_value', None),
        "roce_percentage": row.get('roce_percentage', None),
        "roe_percentage": row.get('roe_percentage', None),
        "sector_name": sect,
        "is_banking": is_bank
    })
dim_company_df = pd.DataFrame(dim_company_rows)
dim_company_df.to_sql("dim_company", engine, if_exists="append", index=False)
print(f"[SUCCESS] Loaded {len(dim_company_df)} companies")

# ── 7. Populate dim_year ──────────────────────────────────────
print("Populating dim_year...")
all_years = set(balancesheet['year'].dropna().unique()) | \
            set(profitloss['year'].dropna().unique()) | \
            set(cashflow['year'].dropna().unique())

def get_year_sort_order(y_str):
    y_str = str(y_str).strip()
    if y_str == "TTM" or "ttm" in y_str.lower():
        return 999999
    
    try:
        parts = y_str.replace("-", " ").split()
        if len(parts) == 2:
            m, y = parts[0], parts[1]
            if len(y) == 2:
                y = "20" + y
            year_val = int(y)
            month_map = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, 
                         "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
            month_val = month_map.get(m.lower()[:3], 1)
            return year_val * 100 + month_val
    except:
        pass
    
    import re
    nums = re.findall(r'\d+', y_str)
    if nums:
        val = int(nums[0])
        if val < 100:
            val = 2000 + val
        return val * 100
    return 0

dim_year_rows = []
for y in all_years:
    is_ttm = "ttm" in str(y).lower()
    dim_year_rows.append({
        "year_str": y,
        "sort_order": get_year_sort_order(y),
        "is_ttm": is_ttm
    })
dim_year_df = pd.DataFrame(dim_year_rows).sort_values("sort_order")
dim_year_df.to_sql("dim_year", engine, if_exists="append", index=False)
print(f"[SUCCESS] Loaded {len(dim_year_df)} years")

# ── 8. Populate Fact Tables ───────────────────────────────────
print("\nPopulating fact tables...")
valid_symbols = set(dim_company_df['symbol'])
valid_years = set(dim_year_df['year_str'])

# Balance Sheet
print("fact_balancesheet...")
bs_warehouse = balancesheet[
    balancesheet['company_id'].isin(valid_symbols) & balancesheet['year'].isin(valid_years)
].copy()
bs_warehouse.rename(columns={"company_id": "symbol", "year": "year_str", "other_asset": "other_assets"}, inplace=True)
bs_cols = ["symbol", "year_str", "equity_capital", "reserves", "borrowings", "other_liabilities", 
           "total_liabilities", "fixed_assets", "cwip", "investments", "other_assets", "total_assets", "debt_to_equity"]
bs_warehouse[bs_cols].to_sql("fact_balancesheet", engine, if_exists="append", index=False)
print(f"[SUCCESS] Loaded {len(bs_warehouse)} rows to fact_balancesheet")

# Profit & Loss
print("fact_profitandloss...")
pl_warehouse = profitloss[
    profitloss['company_id'].isin(valid_symbols) & profitloss['year'].isin(valid_years)
].copy()
pl_warehouse.rename(columns={"company_id": "symbol", "year": "year_str"}, inplace=True)
pl_cols = ["symbol", "year_str", "sales", "expenses", "operating_profit", "opm_percentage", "other_income", 
           "interest", "depreciation", "profit_before_tax", "tax_percentage", "net_profit", "eps", 
           "dividend_payout", "net_profit_margin_pct"]
pl_warehouse[pl_cols].to_sql("fact_profitandloss", engine, if_exists="append", index=False)
print(f"[SUCCESS] Loaded {len(pl_warehouse)} rows to fact_profitandloss")

# Cash Flow
print("fact_cashflow...")
cf_warehouse = cashflow[
    cashflow['company_id'].isin(valid_symbols) & cashflow['year'].isin(valid_years)
].copy()
cf_warehouse.rename(columns={"company_id": "symbol", "year": "year_str"}, inplace=True)
cf_cols = ["symbol", "year_str", "operating_activity", "investing_activity", "financing_activity", 
           "net_cash_flow", "free_cash_flow"]
cf_warehouse[cf_cols].to_sql("fact_cashflow", engine, if_exists="append", index=False)
print(f"[SUCCESS] Loaded {len(cf_warehouse)} rows to fact_cashflow")

# Analysis
print("fact_analysis...")
an_warehouse = analysis[analysis['company_id'].isin(valid_symbols)].copy()
an_warehouse.rename(columns={"company_id": "symbol"}, inplace=True)
an_cols = ["symbol", "compounded_sales_growth", "compounded_profit_growth", "stock_price_cagr", "roe"]
an_warehouse[an_cols].to_sql("fact_analysis", engine, if_exists="append", index=False)
print(f"[SUCCESS] Loaded {len(an_warehouse)} rows to fact_analysis")

# Pros & Cons
print("fact_prosandcons...")
pc_warehouse = prosandcons[prosandcons['company_id'].isin(valid_symbols)].copy()
pc_warehouse.rename(columns={"company_id": "symbol"}, inplace=True)
pc_cols = ["symbol", "pros", "cons"]
pc_warehouse[pc_cols].to_sql("fact_prosandcons", engine, if_exists="append", index=False)
print(f"[SUCCESS] Loaded {len(pc_warehouse)} rows to fact_prosandcons")

# Documents (Annual Reports)
print("fact_documents...")
doc_warehouse = documents[documents['company_id'].isin(valid_symbols)].copy()
doc_warehouse.rename(columns={"company_id": "symbol", "Year": "year_int", "Annual_Report": "annual_report_url"}, inplace=True)
doc_cols = ["symbol", "year_int", "annual_report_url"]
doc_warehouse[doc_cols].to_sql("fact_documents", engine, if_exists="append", index=False)
print(f"[SUCCESS] Loaded {len(doc_warehouse)} rows to fact_documents")

# ── 9. Load ML Outputs into Warehouse ─────────────────────────
print("\nLoading ML tables...")

# ml_company_score
print("ml_company_score...")
scores_warehouse = scores[scores['symbol'].isin(valid_symbols)].copy()
score_cols = ["symbol", "health_score", "health_label", "profitability_score", "growth_score", 
              "solvency_score", "liquidity_score", "efficiency_score", "scale_score"]
scores_warehouse[score_cols].to_sql("ml_company_score", engine, if_exists="append", index=False)
print(f"[SUCCESS] Loaded {len(scores_warehouse)} rows to ml_company_score")

# ml_anomaly_flag
print("ml_anomaly_flag...")
anomalies_warehouse = anomalies[anomalies['symbol'].isin(valid_symbols)].copy()
anomaly_cols = ["symbol", "year_str", "sales", "debt_to_equity", "anomaly_reason"]
anomalies_warehouse[anomaly_cols].to_sql("ml_anomaly_flag", engine, if_exists="append", index=False)
print(f"[SUCCESS] Loaded {len(anomalies_warehouse)} rows to ml_anomaly_flag")

# ml_peer_group
print("ml_peer_group...")
peer_warehouse = peer_mapping[
    peer_mapping['symbol'].isin(valid_symbols) & 
    peer_mapping['peer_1'].isin(valid_symbols) & 
    peer_mapping['peer_2'].isin(valid_symbols) & 
    peer_mapping['peer_3'].isin(valid_symbols)
].copy()
peer_cols = ["symbol", "peer_1", "peer_2", "peer_3"]
peer_warehouse[peer_cols].to_sql("ml_peer_group", engine, if_exists="append", index=False)
print(f"[SUCCESS] Loaded {len(peer_warehouse)} rows to ml_peer_group")

# ml_sales_forecast
print("ml_sales_forecast...")
forecasts_warehouse = forecasts[forecasts['symbol'].isin(valid_symbols)].copy()
forecast_cols = ["symbol", "current_year", "current_sales", "forecast_year", "forecasted_sales"]
forecasts_warehouse[forecast_cols].to_sql("ml_sales_forecast", engine, if_exists="append", index=False)
print(f"[SUCCESS] Loaded {len(forecasts_warehouse)} rows to ml_sales_forecast")


# ── 10. Data Quality Checks ───────────────────────────────────
print("\nRunning Data Quality Checks...")
dq_passed = True

with engine.connect() as conn:
    c_count = conn.execute(text("SELECT count(*) FROM dim_company")).scalar()
    f_bs_count = conn.execute(text("SELECT count(*) FROM fact_balancesheet")).scalar()
    f_pl_count = conn.execute(text("SELECT count(*) FROM fact_profitandloss")).scalar()
    ml_score_count = conn.execute(text("SELECT count(*) FROM ml_company_score")).scalar()
    
    print(f"DQ 1: dim_company count = {c_count}")
    print(f"DQ 1: fact_balancesheet count = {f_bs_count}")
    print(f"DQ 1: fact_profitandloss count = {f_pl_count}")
    print(f"DQ 1: ml_company_score count = {ml_score_count}")
    
    if c_count == 0 or f_bs_count == 0 or f_pl_count == 0 or ml_score_count == 0:
        print("[FAIL] DQ Check 1 FAILED: Empty tables detected!")
        dq_passed = False
    else:
        print("[PASS] DQ Check 1 Passed: Record counts look normal.")

with engine.connect() as conn:
    orphan_bs = conn.execute(text("SELECT count(*) FROM fact_balancesheet WHERE symbol NOT IN (SELECT symbol FROM dim_company)")).scalar()
    orphan_pl = conn.execute(text("SELECT count(*) FROM fact_profitandloss WHERE symbol NOT IN (SELECT symbol FROM dim_company)")).scalar()
    orphan_ml = conn.execute(text("SELECT count(*) FROM ml_company_score WHERE symbol NOT IN (SELECT symbol FROM dim_company)")).scalar()
    
    if orphan_bs > 0 or orphan_pl > 0 or orphan_ml > 0:
        print(f"[FAIL] DQ Check 2 FAILED: Orphan rows detected! BS: {orphan_bs}, PL: {orphan_pl}, ML: {orphan_ml}")
        dq_passed = False
    else:
        print("[PASS] DQ Check 2 Passed: No orphan records in fact tables.")

with engine.connect() as conn:
    mismatched_bs = conn.execute(text("SELECT count(*) FROM fact_balancesheet WHERE abs(total_assets - total_liabilities) > 1")).scalar()
    if mismatched_bs > 0:
        print(f"[WARNING] DQ Warning: {mismatched_bs} rows show slight total assets vs. liabilities mismatch. This is common in raw source files.")
    else:
        print("[PASS] DQ Check 3 Passed: Total Assets match Total Liabilities perfectly.")

if dq_passed:
    print("\n[SUCCESS] ALL DATA QUALITY CHECKS PASSED!")
    print("Warehouse Load Completed successfully! [OK]")
else:
    print("\n[ERROR] DATA QUALITY CHECKS FAILED. Please review output logs above.")
