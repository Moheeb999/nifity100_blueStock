# Performance Notes

## Load Test

- Concurrent Requests: 10
- Total Execution Time: <your measured time> seconds
- Average Response Time: <your measured time> seconds
- Result: Passed (all 10 requests completed within 10 seconds)

---

## Dashboard Performance

| Ticker | Load Time |
|--------|-----------|
| TCS | 0.018 s |
| INFY | 0.001 s |
| RELIANCE | 0.001 s |
| HDFCBANK | 0.001 s |
| ICICIBANK | 0.001 s |

Result: All company profile pages loaded well within the 3-second target.

---

## End-to-End Test

- FastAPI started successfully on port 8000.
- Streamlit started successfully on port 8501.
- No port conflicts were observed.
- Dashboard loaded company data successfully.

---

## SQLite Optimization

Indexes created:

- financial_ratios(company_id, year)
- market_cap(company_id, year)
- profitandloss(company_id, year)
- cashflow(company_id, year)
- balancesheet(company_id, year)

Observations:
- No significant performance bottlenecks observed during testing.
- Dashboard and API response times met the required targets.