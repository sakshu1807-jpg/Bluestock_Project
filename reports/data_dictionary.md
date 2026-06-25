# Day 2: Bluestock Mutual Fund Warehouse Data Dictionary

This document serves as the data dictionary for the Star Schema architecture deployed inside `bluestock_mf.db`. It outlines columns, relational attributes, data types, and core business rules.

---

## 1. Dimension Table: dim_fund
The `dim_fund` table acts as a central master register tracking all available mutual fund asset schemes. It is generated directly from a processed copy of `01_fund_master.csv`. 

The primary key is `amfi_code`, which holds the unique association code assigned by the Association of Mutual Funds in India. Text fields include `fund_house` (the managing Asset Management Company), `scheme_name` (the commercial market name), `category` (the regulatory class like Equity or Debt), and `sub_category` (the core strategy group like Large Cap) etc. It also tracks descriptive textual metrics such as the fund's `plan`, `launch_date`, `benchmark` index, `risk_category`, and `sebi_category_code`. The numeric field `expense_ratio_pct` captures the annual operating fee charged to investors, which is strictly constrained to a range of 0.1% to 2.5%.

---

## 2. Dimension Table: dim_date
The `dim_date` table serves as the time-series dimension mapping continuous day-by-day calendar attributes to ensure accurate date slicing. It is generated dynamically via the automated Python pipeline boundaries.

The table is indexed by `date_id`, a text string serving as the primary key formatted in the pattern `YYYY-MM-DD`. It breaks down dates into explicit numeric slots including `calendar_year` and `calendar_month`. For specialized reporting, it logs the textual `month_name` and the explicit `day_of_week`. A binary integer flag named `is_weekend` is applied to every row, evaluating to 1 for Saturdays and Sundays, and 0 for standard working weekdays.

---

## 3. Fact Table: fact_transactions
The `fact_transactions` table captures individual-scale transaction activity records made by investors across different mutual fund schemes. It is transformed from a processed copy of `08_investor_transactions.csv`.

The table uses `investor_id` as a primary identifier for tracking distinct investor profile accounts. It establishes clean relational boundaries using two foreign keys: `amfi_code` (which points back to `dim_fund`) and `transaction_date` (which anchors chronologically to `dim_date`). The `transaction_type` text field is strictly bounded by a database check rule to only allow 'SIP', 'Lumpsum', or 'Redemption'. Financial and volume metrics are tracked via `amount_inr` (the monetary value in Indian Rupees, which must be strictly greater than 0). It also captures profile details including the investor's compliance `kyc_status` and the originating geographic `state`.

---

## 4. Fact Table: fact_nav
The `fact_nav` table is a high-volume time-series ledger tracking the day-by-day continuous closing pricing metrics for all tracked fund groups. It is compiled directly from a processed copy of `02_nav_history.csv`.

This table uses a relational layout driven by two vital foreign keys: `amfi_code` links the record back to the fund profile master, while `date` binds the record to the main calendar timeline. The core metric is `nav`, a floating-point real number representing the daily Net Asset Value per share unit. Business rules require that all missing NAV values from weekends or market holidays are automatically forward-filled from the last valid market session, and all final entries must be strictly greater than 0.

---

## 5. Fact Table: fact_performance
The `fact_performance` table isolates and tracks the historical trailing compound annualized return rates across different fund structures. It is derived from a processed copy of `07_scheme_performance.csv`.

The table utilizes `amfi_code` as both its primary key and a foreign key relating directly back to the `dim_fund` register to ensure one-to-one data mapping integrity. Performance metrics are stored as real floating-point numeric percentages representing compound growth across distinct horizons, specifically `return_1y_pct`, `return_3y_pct`, and `return_5y_pct`. 

---

## 6. Fact Table: fact_aum
The `fact_aum` table monitors the systemic asset volume size weights distributed across different asset management houses over time. It is built from a processed copy of `03_aum_by_fund_house.csv`.

The table includes the `fund_house` text block, which is used to associate metrics with specific AMC entities. The primary numeric measurement is `aum_amount`, which records the aggregate total Asset Under Management evaluation as a real floating-point value that cannot be null. Each snapshot is anchored to the global timeline via the `date` column, which functions as a foreign key connecting directly to the calendar register.