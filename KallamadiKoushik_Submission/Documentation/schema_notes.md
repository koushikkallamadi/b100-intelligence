# B100 Data Warehouse Schema Notes

This file lists field names, data types, sample values, and obvious data issues for all 7 raw tables.

## Table: `analysis`
**Shape**: 20 rows, 6 columns

| Field Name | Pandas Type | Non-Null Count | Sample Values | Data Issues / Observations |
|---|---|---|---|---|
| `id` | int64 | 20 | `1, 10, 11` | None |
| `company_id` | str | 20 | `HDFCBANK, SBILIFE, TCS` | None |
| `compounded_sales_growth` | str | 20 | `10 Years: 21%, 5 Years:       24%, 3 Years:       17%` | None |
| `compounded_profit_growth` | str | 20 | `10 Years: 22%, 5 Years:            6%, 3 Years:            9%` | None |
| `stock_price_cagr` | str | 20 | `10 Years:     15%,      5 Years:       8%,      3 Years:       7%` | None |
| `roe` | str | 20 | `10 Years:     17%, 5 Years          14%, 3 Years:         13%` | None |

---

## Table: `balancesheet`
**Shape**: 1312 rows, 13 columns

| Field Name | Pandas Type | Non-Null Count | Sample Values | Data Issues / Observations |
|---|---|---|---|---|
| `id` | int64 | 1312 | `136, 137, 138` | None |
| `company_id` | str | 1312 | `ABB, ADANIENSOL, ADANIENT` | None |
| `year` | str | 1312 | `Dec 2012, Mar 2014, Mar 2015` | None |
| `equity_capital` | float64 | 1312 | `21.0, 0.1, 1090.0` | None |
| `reserves` | int64 | 1312 | `626, 767, 916` | None |
| `borrowings` | int64 | 1312 | `0, 175, 153` | None |
| `other_liabilities` | int64 | 1312 | `260, 351, 436` | None |
| `total_liabilities` | int64 | 1312 | `907, 1139, 1374` | None |
| `fixed_assets` | int64 | 1312 | `109, 98, 96` | None |
| `cwip` | int64 | 1312 | `1, 4, 3` | None |
| `investments` | int64 | 1312 | `0, 20, 105` | None |
| `other_asset` | int64 | 1312 | `798, 1040, 1274` | None |
| `total_assets` | int64 | 1312 | `907, 1139, 1374` | None |

---

## Table: `cashflow`
**Shape**: 1187 rows, 7 columns

| Field Name | Pandas Type | Non-Null Count | Sample Values | Data Issues / Observations |
|---|---|---|---|---|
| `id` | int64 | 1187 | `37, 38, 39` | None |
| `company_id` | str | 1187 | `TCS, ABB, ADANIENSOL` | None |
| `year` | str | 1187 | `Mar-13, Mar-14, Mar-15` | None |
| `operating_activity` | float64 | 1185 | `11615.0, 14751.0, 19369.0` | Contains 2 null values. |
| `investing_activity` | float64 | 1185 | `-6038.0, -9452.0, -1807.0` | Contains 2 null values. |
| `financing_activity` | float64 | 1185 | `-5729.0, -5673.0, -17168.0` | Contains 2 null values. |
| `net_cash_flow` | float64 | 1185 | `-152.0, -374.0, 394.0` | Contains 2 null values. |

---

## Table: `companies`
**Shape**: 92 rows, 12 columns

| Field Name | Pandas Type | Non-Null Count | Sample Values | Data Issues / Observations |
|---|---|---|---|---|
| `id` | str | 92 | `ABB, ADANIENSOL, ADANIENT` | None |
| `company_logo` | str | 91 | `https://mkt.in/static/mkt-icons/nifty100/ABB.png, https://m.economictimes.com/thumb/msid-117371599,width-1200,height-900,resizemode-4,imgsize-5642/the-growth-story-remains-intact-for-adani-energy-solutions-says-jefferies.jpg, https://mkt.in/static/mkt-icons/nifty100/ADANIENT.png` | Contains 1 null values. |
| `company_name` | str | 92 | `Abbott India Ltd, Adani Energy Solutions Ltd, Adani Enterprises Ltd` | None Key field. Needs cleaning. |
| `chart_link` | str | 92 | `https://in.tradingview.com/chart/?symbol=NSE%3AABBOTINDIA, https://in.tradingview.com/chart/?symbol=NSE%3AADANIENSOL, https://in.tradingview.com/chart/?symbol=ADANIENT` | None |
| `about_company` | str | 92 | `Abbott India Ltd is one of the leading multinational pharmaceutical companies in India and sells its products through independent distributors primarily within India., AESL, part of the Adani portfolio, is a multidimensional organization with presence in various facets of the energy domain, namely power transmission, distribution, smart metering, and cooling solutions. AESL is India's largest private transmission company, Adani Enterprises Ltd is an Indian multinational public company and a subsidiary of Adani Group. It is headquartered in Ahmedabad and has business interests in coal mining and trading, airport operations, edible oils, road, rail and water infrastructure, data centers, hydrocarbon exploration, defence and aerospace, multimodal logistics, and agro commodities.` | None |
| `website` | str | 91 | `https://www.abbott.co.in/, https://www.adanienergysolutions.com/, https://www.adanienterprises.com/` | Contains 1 null values. |
| `nse_profile` | str | 91 | `https://www.nseindia.com/get-quotes/equity?symbol=ABBOTINDIA, https://www.nseindia.com/get-quotes/equity?symbol=ADANIENSOL, https://www.nseindia.com/get-quotes/equity?symbol=ADANIENT` | Contains 1 null values. |
| `bse_profile` | str | 91 | `https://www.bseindia.com/stock-share-price/abbott-india-ltd/ABBOTINDIA/500488/, https://www.bseindia.com/stock-share-price/adani-energy-solutions-ltd/ADANIENSOL/539254/, https://www.bseindia.com/stock-share-price/adani-enterprises-ltd/adanient/512` | Contains 1 null values. |
| `face_value` | float64 | 91 | `10.0, 1.0, 2.0` | Contains 1 null values. |
| `book_value` | float64 | 91 | `1657.0, 175.0, 363.0` | Contains 1 null values. |
| `roce_percentage` | float64 | 91 | `46.0, 9.0, 11.6` | Contains 1 null values. |
| `roe_percentage` | float64 | 90 | `34.9, 8.59, 13.64` | Contains 2 null values. |

---

## Table: `documents`
**Shape**: 1585 rows, 4 columns

| Field Name | Pandas Type | Non-Null Count | Sample Values | Data Issues / Observations |
|---|---|---|---|---|
| `id` | int64 | 1585 | `1, 2, 3` | None |
| `company_id` | str | 1585 | `ABB, ADANIENSOL, ADANIENT` | None |
| `Year` | int64 | 1585 | `2024, 2023, 2022` | None |
| `Annual_Report` | str | 1533 | `https://www.bseindia.com/xml-data/corpfiling/AttachHis/270738a5-1a37-4f0f-9de6-e16dc27ff432.pdf, https://www.bseindia.com/xml-data/corpfiling/AttachHis//68827cf7-67af-4209-91f5-3854d3e1e8a2.pdf, https://www.bseindia.com/bseplus/AnnualReport/500488/73779500488.pdf` | Contains 52 null values. |

---

## Table: `profitandloss`
**Shape**: 1276 rows, 15 columns

| Field Name | Pandas Type | Non-Null Count | Sample Values | Data Issues / Observations |
|---|---|---|---|---|
| `id` | int64 | 1276 | `61, 62, 63` | None |
| `company_id` | str | 1276 | `ABB, ADANIENSOL, ADANIENT` | None |
| `year` | str | 1276 | `Dec 2012, Mar 2014, Mar 2015` | None |
| `sales` | int64 | 1276 | `1653, 2276, 2289` | None |
| `expenses` | int64 | 1276 | `1451, 2009, 1977` | None |
| `operating_profit` | float64 | 1263 | `202.0, 267.0, 312.0` | Contains 13 null values. |
| `opm_percentage` | float64 | 1261 | `12.0, 14.0, 16.0` | Contains 15 null values. |
| `other_income` | int64 | 1276 | `33, 49, 48` | None |
| `interest` | int64 | 1276 | `0, 3, 2` | None |
| `depreciation` | int64 | 1276 | `19, 22, 15` | None |
| `profit_before_tax` | int64 | 1276 | `215, 295, 344` | None |
| `tax_percentage` | float64 | 1181 | `33.0, 34.0, 36.0` | Contains 95 null values. |
| `net_profit` | int64 | 1276 | `145, 198, 229` | None |
| `eps` | float64 | 1271 | `68.0, 93.0, 108.0` | Contains 5 null values. |
| `dividend_payout` | float64 | 1173 | `25.0, 29.0, 31.0` | Contains 103 null values. |

---

## Table: `prosandcons`
**Shape**: 16 rows, 4 columns

| Field Name | Pandas Type | Non-Null Count | Sample Values | Data Issues / Observations |
|---|---|---|---|---|
| `id` | int64 | 16 | `1, 2, 3` | None |
| `company_id` | str | 16 | `HDFCBANK, SBILIFE, INFY` | None |
| `pros` | str | 11 | `Company is expected to give good quarter, Company has delivered good profit growth of 23.4% CAGR over last 5 years, Company has been maintaining a healthy dividend payout of 22.9%` | Contains 5 null values. |
| `cons` | str | 15 | `Stock is trading at 2.76 times its book value, Company has low interest coverage ratio., Contingent liabilities of Rs.24,09,821 Cr.` | Contains 1 null values. |

---

