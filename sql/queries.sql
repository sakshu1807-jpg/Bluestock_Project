-- Day 2: 10 Analytical SQL Queries for Bluestock Mutual Fund Warehouse

-- 1. Top 5 Funds by Asset Under Management (AUM) Amount
SELECT fund_house, SUM(aum_crore) AS total_aum_in_crore
FROM fact_aum
GROUP BY fund_house
ORDER BY total_aum_in_crore DESC
LIMIT 5;

-- 2. Average NAV Performance per Month across timelines
SELECT d.calendar_year, d.month_name, ROUND(AVG(n.nav), 4) AS avg_nav_price
FROM fact_nav as n
JOIN dim_date as d ON n.date = d.date_id
GROUP BY d.calendar_year, d.calendar_month
ORDER BY d.calendar_year, d.calendar_month;

-- 3. Systematic Investment Plan (SIP) Year-over-Year (YoY) Transaction Value Growth
SELECT d.calendar_year, SUM(t.amount_inr) AS total_sip_value
FROM fact_transactions t
JOIN dim_date d ON t.transaction_date = d.date_id
WHERE t.transaction_type = 'SIP'
GROUP BY d.calendar_year
ORDER BY d.calendar_year;

-- 4. Total Investor Transaction Volumes segmented by Geographic State
SELECT state, COUNT(investor_id) AS total_transactions, ROUND(SUM(amount_inr), 2) AS total_invested_value
FROM fact_transactions
GROUP BY state
ORDER BY total_invested_value DESC;

-- 5. Identify Funds with a highly efficient Expense Ratio strictly under 1%
SELECT amfi_code, fund_house, scheme_name, category, plan, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct;

-- 6. Total Capital Outflow via Lumpsums per Fund House
SELECT f.fund_house, ROUND(SUM(t.amount), 2) AS total_lumpsum_outflow
FROM fact_transactions t
JOIN dim_fund f ON t.amfi_code = f.amfi_code
WHERE t.transaction_type = 'Lumpsum'
GROUP BY f.fund_house
ORDER BY total_lumpsum_outflow DESC;

-- 7. High-Value Transaction Alert (Transactions > 5,000,000 INR)
SELECT amfi_code, transaction_date, transaction_type, amount_inr, investor_id
FROM fact_transactions
WHERE amount_inr > 580000
ORDER BY amount_inr DESC;

-- 8. Identify Volume and Value of Transactions Processed on Weekends
SELECT d.day_of_week, COUNT(t.investor_id) AS transaction_count, ROUND(SUM(t.amount), 2) AS total_value
FROM fact_transactions t
JOIN dim_date d ON t.transaction_date = d.date_id
WHERE d.is_weekend = 1
GROUP BY d.day_of_week;

-- 9. Top 5 Equity Schemes with the Highest 3-Year Annualized Returns
SELECT f.scheme_name, f.sub_category, p.return_3yr_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE f.category = 'Equity'
ORDER BY p.return_3yr_pct DESC
LIMIT 5;

-- 10. Distribution of Investment Capital between SIP vs Lumpsum Vehicles
SELECT t.transaction_type, COUNT(*) AS total_transaction_count, ROUND(SUM(t.amount_inr), 2) AS total_capital
FROM fact_transactions t
GROUP BY t.transaction_type;