-- 1. Total companies
SELECT COUNT(*) FROM companies;

-- 2. Top 10 companies by sales
SELECT company_id, sales
FROM profitandloss
ORDER BY sales DESC
LIMIT 10;

-- 3. Companies with highest ROE
SELECT company_id, roe_percentage
FROM companies
ORDER BY roe_percentage DESC
LIMIT 10;

-- 4. Companies with negative profit
SELECT company_id, year, net_profit
FROM profitandloss
WHERE net_profit < 0;

-- 5. Companies with highest borrowings
SELECT company_id, year, borrowings
FROM balancesheet
ORDER BY borrowings DESC
LIMIT 10;

-- 6. Highest stock price
SELECT company_id, MAX(close_price)
FROM stock_prices
GROUP BY company_id
ORDER BY MAX(close_price) DESC
LIMIT 10;

-- 7. Missing annual reports
SELECT company_id
FROM documents
WHERE annual_report IS NULL;

-- 8. Companies with less than 5 years
SELECT company_id, COUNT(*)
FROM profitandloss
GROUP BY company_id
HAVING COUNT(*) < 5;

-- 9. Average dividend payout
SELECT AVG(dividend_payout)
FROM profitandloss;

-- 10. Financial table row counts
SELECT 'profitandloss', COUNT(*) FROM profitandloss
UNION ALL
SELECT 'balancesheet', COUNT(*) FROM balancesheet
UNION ALL
SELECT 'cashflow', COUNT(*) FROM cashflow;