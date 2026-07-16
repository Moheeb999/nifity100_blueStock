# Nifty 100 Analytics Dashboard

## Project Overview

Nifty 100 Analytics is a Streamlit-based financial analytics platform for analyzing Nifty 100 companies using financial statements, valuation metrics, peer comparison, stock screening, and interactive dashboards.

---

## Features

- Home Dashboard
- Company Profile
- Stock Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation
- Annual Reports
- Valuation Engine
- Excel & CSV Export

---

## Technologies Used

- Python
- Streamlit
- SQLite
- Pandas
- Plotly
- OpenPyXL

---

## Project Structure

```
nifty100_project/
│
├── db/
├── output/
├── src/
│   ├── analytics/
│   └── dashboard/
├── README.md
└── requirements.txt
```

---

## Run the Dashboard

```bash
source venv/bin/activate

streamlit run src/dashboard/app.py
```

---

## Generate Valuation Report

```bash
python -m src.analytics.valuation
```

---

## Output Files

- output/valuation_summary.xlsx
- output/valuation_flags.csv

---

## Database Tables

- companies
- financial_ratios
- market_cap
- profitandloss
- balancesheet
- cashflow
- sectors
- peer_groups
- peer_percentiles
- documents

---

## Dashboard Pages

1. Home
2. Company Profile
3. Stock Screener
4. Peer Comparison
5. Trend Analysis
6. Sector Analysis
7. Capital Allocation
8. Annual Reports

---

## Author

**Mohammad Esa Mohibuddin**