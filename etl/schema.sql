-- B100 Data Warehouse Star Schema

-- Drop tables if they exist (clean slate)
DROP TABLE IF EXISTS ml_sales_forecast CASCADE;
DROP TABLE IF EXISTS ml_peer_group CASCADE;
DROP TABLE IF EXISTS ml_anomaly_flag CASCADE;
DROP TABLE IF EXISTS ml_company_score CASCADE;
DROP TABLE IF EXISTS fact_documents CASCADE;
DROP TABLE IF EXISTS fact_prosandcons CASCADE;
DROP TABLE IF EXISTS fact_analysis CASCADE;
DROP TABLE IF EXISTS fact_cashflow CASCADE;
DROP TABLE IF EXISTS fact_profitandloss CASCADE;
DROP TABLE IF EXISTS fact_balancesheet CASCADE;
DROP TABLE IF EXISTS dim_company CASCADE;
DROP TABLE IF EXISTS dim_year CASCADE;
DROP TABLE IF EXISTS dim_sector CASCADE;

-- 1. Dim Company Table
CREATE TABLE dim_company (
    symbol VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    company_logo TEXT,
    chart_link TEXT,
    about_company TEXT,
    website TEXT,
    nse_profile TEXT,
    bse_profile TEXT,
    face_value NUMERIC(10, 2),
    book_value NUMERIC(15, 2),
    roce_percentage NUMERIC(15, 2),
    roe_percentage NUMERIC(15, 2),
    sector_name VARCHAR(100),
    is_banking BOOLEAN DEFAULT FALSE
);

-- 2. Dim Year Table
CREATE TABLE dim_year (
    year_str VARCHAR(20) PRIMARY KEY, -- e.g., 'Mar 2024', 'TTM'
    sort_order INT NOT NULL,          -- chronological ordering ID
    is_ttm BOOLEAN DEFAULT FALSE
);

-- 3. Dim Sector Table
CREATE TABLE dim_sector (
    sector_name VARCHAR(100) PRIMARY KEY,
    sector_desc TEXT
);

-- 4. Fact Balance Sheet Table
CREATE TABLE fact_balancesheet (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) REFERENCES dim_company(symbol) ON DELETE CASCADE,
    year_str VARCHAR(20) REFERENCES dim_year(year_str) ON DELETE CASCADE,
    equity_capital NUMERIC(15, 2),
    reserves NUMERIC(15, 2),
    borrowings NUMERIC(15, 2),
    other_liabilities NUMERIC(15, 2),
    total_liabilities NUMERIC(15, 2),
    fixed_assets NUMERIC(15, 2),
    cwip NUMERIC(15, 2),
    investments NUMERIC(15, 2),
    other_assets NUMERIC(15, 2),
    total_assets NUMERIC(15, 2),
    debt_to_equity NUMERIC(10, 4)
);

-- 5. Fact Profit & Loss Table
CREATE TABLE fact_profitandloss (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) REFERENCES dim_company(symbol) ON DELETE CASCADE,
    year_str VARCHAR(20) REFERENCES dim_year(year_str) ON DELETE CASCADE,
    sales NUMERIC(15, 2),
    expenses NUMERIC(15, 2),
    operating_profit NUMERIC(15, 2),
    opm_percentage NUMERIC(15, 2),
    other_income NUMERIC(15, 2),
    interest NUMERIC(15, 2),
    depreciation NUMERIC(15, 2),
    profit_before_tax NUMERIC(15, 2),
    tax_percentage NUMERIC(15, 2),
    net_profit NUMERIC(15, 2),
    eps NUMERIC(10, 2),
    dividend_payout NUMERIC(15, 2),
    net_profit_margin_pct NUMERIC(10, 4)
);

-- 6. Fact Cash Flow Table
CREATE TABLE fact_cashflow (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) REFERENCES dim_company(symbol) ON DELETE CASCADE,
    year_str VARCHAR(20) REFERENCES dim_year(year_str) ON DELETE CASCADE,
    operating_activity NUMERIC(15, 2),
    investing_activity NUMERIC(15, 2),
    financing_activity NUMERIC(15, 2),
    net_cash_flow NUMERIC(15, 2),
    free_cash_flow NUMERIC(15, 2)
);

-- 7. Fact Analysis Table (ML / CAGR Metrics)
CREATE TABLE fact_analysis (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) REFERENCES dim_company(symbol) ON DELETE CASCADE,
    compounded_sales_growth TEXT,
    compounded_profit_growth TEXT,
    stock_price_cagr TEXT,
    roe TEXT
);

-- 8. Fact Pros & Cons Table
CREATE TABLE fact_prosandcons (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) REFERENCES dim_company(symbol) ON DELETE CASCADE,
    pros TEXT,
    cons TEXT
);

-- 9. Fact Documents Table (Annual Reports)
CREATE TABLE fact_documents (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) REFERENCES dim_company(symbol) ON DELETE CASCADE,
    year_int INT,
    annual_report_url TEXT
);

-- 10. ML Company Scores Table
CREATE TABLE ml_company_score (
    symbol VARCHAR(50) PRIMARY KEY REFERENCES dim_company(symbol) ON DELETE CASCADE,
    health_score NUMERIC(5, 2),
    health_label VARCHAR(20),
    profitability_score NUMERIC(5, 2),
    growth_score NUMERIC(5, 2),
    solvency_score NUMERIC(5, 2),
    liquidity_score NUMERIC(5, 2),
    efficiency_score NUMERIC(5, 2),
    scale_score NUMERIC(5, 2)
);

-- 11. ML Anomaly Flags Table
CREATE TABLE ml_anomaly_flag (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) REFERENCES dim_company(symbol) ON DELETE CASCADE,
    year_str VARCHAR(20),
    sales NUMERIC(15, 2),
    debt_to_equity NUMERIC(10, 4),
    anomaly_reason TEXT
);

-- 12. ML Peer Groups Table
CREATE TABLE ml_peer_group (
    symbol VARCHAR(50) PRIMARY KEY REFERENCES dim_company(symbol) ON DELETE CASCADE,
    peer_1 VARCHAR(50) REFERENCES dim_company(symbol) ON DELETE CASCADE,
    peer_2 VARCHAR(50) REFERENCES dim_company(symbol) ON DELETE CASCADE,
    peer_3 VARCHAR(50) REFERENCES dim_company(symbol) ON DELETE CASCADE
);

-- 13. ML Revenue Forecasts Table
CREATE TABLE ml_sales_forecast (
    symbol VARCHAR(50) PRIMARY KEY REFERENCES dim_company(symbol) ON DELETE CASCADE,
    current_year INT,
    current_sales NUMERIC(15, 2),
    forecast_year INT,
    forecasted_sales NUMERIC(15, 2)
);

-- Indexes for performance optimization
CREATE INDEX idx_balancesheet_symbol ON fact_balancesheet(symbol);
CREATE INDEX idx_balancesheet_year ON fact_balancesheet(year_str);
CREATE INDEX idx_profitloss_symbol ON fact_profitandloss(symbol);
CREATE INDEX idx_profitloss_year ON fact_profitandloss(year_str);
CREATE INDEX idx_cashflow_symbol ON fact_cashflow(symbol);
CREATE INDEX idx_cashflow_year ON fact_cashflow(year_str);
CREATE INDEX idx_documents_symbol ON fact_documents(symbol);
