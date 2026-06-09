# Power BI Data Model & DAX Measures Library

This document provides the exact data model configuration, relationship schema, and copy-pasteable DAX measures required to build the 7 standard dashboards in Power BI Desktop.

---

## 1. Data Model Relationships

Configure the following relationships in the **Model View** of Power BI Desktop:

| From Table | From Column | To Table | To Column | Cardinality | Cross Filter Direction |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `dim_company` | `symbol` | `fact_balancesheet` | `symbol` | `1 to *` | Single |
| `dim_company` | `symbol` | `fact_profitandloss` | `symbol` | `1 to *` | Single |
| `dim_company` | `symbol` | `fact_cashflow` | `symbol` | `1 to *` | Single |
| `dim_company` | `symbol` | `fact_analysis` | `symbol` | `1 to *` | Single |
| `dim_company` | `symbol` | `fact_prosandcons` | `symbol` | `1 to *` | Single |
| `dim_company` | `symbol` | `fact_documents` | `symbol` | `1 to *` | Single |
| `dim_year` | `year_str` | `fact_balancesheet` | `year_str` | `1 to *` | Single |
| `dim_year` | `year_str` | `fact_profitandloss` | `year_str` | `1 to *` | Single |
| `dim_year` | `year_str` | `fact_cashflow` | `year_str` | `1 to *` | Single |

*Make sure to configure the `dim_year[sort_order]` column to sort the `dim_year[year_str]` column so that charts correctly plot chronologically.*

---

## 2. Power BI Theme & Style Guidelines

Apply these theme settings to align all dashboards into a single cohesive product:

* **Primary Dark Blue**: `#1F4E79`
* **Secondary Medium Blue**: `#2E75B6`
* **Positive Status (Green)**: `#2ECC71`
* **Warning Status (Orange)**: `#F39C12`
* **Negative Status (Red)**: `#E74C3C`
* **App Background**: `#F8F9FA`
* **Visual Card Background**: `#FFFFFF`
* **Typography**: Font family `Segoe UI`. Card Values: `20 pt Bold`. Table/Axis: `10-12 pt`.
* **Number Format**: Show standard currency format with prefix `₹` and suffix ` Cr` (INR Crores).
* **Footer Rule**: Include a text box on every page: 
  * *"Data as of: [current date]. For educational purposes only. Not financial advice. Bluestock Fintech — Nifty 100 Financial Intelligence Platform."*

---

## 3. DAX Measures Library

Create a blank table named `_Measures` and add the following DAX calculations:

### 3.1 Financial Scale Measures
```dax
Total Sales = 
SUM(fact_profitandloss[sales])
```

```dax
Total Net Profit = 
SUM(fact_profitandloss[net_profit])
```

```dax
Total Borrowings = 
SUM(fact_balancesheet[borrowings])
```

```dax
Total Reserves = 
SUM(fact_balancesheet[reserves])
```

```dax
Total Equity = 
SUM(fact_balancesheet[equity_capital]) + [Total Reserves]
```

### 3.2 Margin & Profitability Measures
```dax
Operating Profit Margin % = 
AVERAGE(fact_profitandloss[opm_percentage])
```

```dax
Net Profit Margin % = 
DIVIDE([Total Net Profit], [Total Sales], 0) * 100
```

```dax
Return on Equity (ROE) % = 
DIVIDE([Total Net Profit], [Total Equity], 0) * 100
```

```dax
Return on Capital Employed (ROCE) % = 
AVERAGE(dim_company[roce_percentage])
```

### 3.3 Cash Flow Measures
```dax
Operating Cash Flow = 
SUM(fact_cashflow[operating_activity])
```

```dax
Investing Cash Flow = 
SUM(fact_cashflow[investing_activity])
```

```dax
Financing Cash Flow = 
SUM(fact_cashflow[financing_activity])
```

```dax
Free Cash Flow (FCF) = 
[Operating Cash Flow] + [Investing Cash Flow]
```

### 3.4 Leverage & Liquidity Measures
```dax
Debt to Equity Ratio = 
DIVIDE([Total Borrowings], [Total Equity], 0)
```

```dax
Interest Coverage Ratio = 
DIVIDE(
    SUM(fact_profitandloss[profit_before_tax]) + SUM(fact_profitandloss[interest]), 
    SUM(fact_profitandloss[interest]), 
    999
)
```

### 3.5 Growth & Trend Measures (CAGR)
*Ensure `dim_year[is_ttm] = FALSE` is filtered out when plotting historical trend lines to avoid distorting growth rate calculations.*

```dax
Sales Growth YoY % = 
VAR PreviousYearSales = 
    CALCULATE(
        [Total Sales],
        SAMEPERIODLASTYEAR(dim_year[year_str])
    )
RETURN
    DIVIDE([Total Sales] - PreviousYearSales, PreviousYearSales, 0) * 100
```

```dax
Sales CAGR 3Y % = 
VAR Sales_Current = [Total Sales]
VAR Sales_Past = 
    CALCULATE(
        [Total Sales],
        DATEADD(dim_year[year_str], -3, YEAR)
    )
RETURN
    IF(
        NOT(ISBLANK(Sales_Past)) && Sales_Past > 0,
        (POWER(DIVIDE(Sales_Current, Sales_Past, 0), 1/3) - 1) * 100,
        BLANK()
    )
```

```dax
Sales CAGR 5Y % = 
VAR Sales_Current = [Total Sales]
VAR Sales_Past = 
    CALCULATE(
        [Total Sales],
        DATEADD(dim_year[year_str], -5, YEAR)
    )
RETURN
    IF(
        NOT(ISBLANK(Sales_Past)) && Sales_Past > 0,
        (POWER(DIVIDE(Sales_Current, Sales_Past, 0), 1/5) - 1) * 100,
        BLANK()
    )
```

### 3.6 Shareholder Returns & Valuation Measures
```dax
Dividend Payout Ratio % = 
AVERAGE(fact_profitandloss[dividend_payout])
```

```dax
Book Value Per Share = 
AVERAGE(dim_company[book_value])
```

### 3.7 ML Score & Anomaly Metrics
```dax
Company Health Score = 
AVERAGE(ml_company_score[health_score])
```

```dax
Is Anomaly Flagged = 
IF(
    CALCULATE(COUNTROWS(ml_anomaly_flag)) > 0,
    1,
    0
)
```

---

## 4. Dashboards Definition Cheat-Sheet

Use this quick guide to configure the pages for each dashboard:

1. **Executive Overview**:
   * *KPI Cards*: Total Nifty 100 Revenue, Total Net Profit, Average ROE.
   * *Bar Chart*: Top 10 companies by Sales.
   * *Donut Chart*: Count of companies by Health Rating Zone (Green / Orange / Red).
2. **Company Deep Dive**:
   * *Slicer*: Select Company Symbol.
   * *Visuals*: Stacked BS chart, Cash Flow Waterfall, EPS vs. Dividend line chart, Debt vs. Equity Area Chart.
3. **Sector Comparison**:
   * *Slicer*: Sector selection.
   * *Visuals*: Sector Average OPM% comparison, Boxplot of Sector returns.
4. **Financial Health Scorecard**:
   * *Gauge*: Speedometer displaying Company Health Score.
   * *List Visual*: Anomaly details table (Anomaly flags + reasons).
5. **Growth & Valuation Analytics**:
   * *Radar Chart*: Sales CAGR vs. Profit CAGR vs. Stock CAGR overlay.
   * *Scatter Plot*: Valuation (P/E or Book Value) vs. ROE.
6. **Debt & Leverage Monitor**:
   * *KPI Card*: Average D/E.
   * *Area Chart*: Borrowings vs. Reserves trends.
7. **Dividend & Shareholder Returns**:
   * *Columns*: Top 10 dividend paying companies.
   * *Line Chart*: Dividend Payout % vs. Profit growth over years.
