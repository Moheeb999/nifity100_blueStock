# Nifty 100 Analytics Dashboard

## Project Overview

The Nifty 100 Analytics Dashboard is a financial analytics platform built using Python, Streamlit, FastAPI, and SQLite. It enables users to analyze Nifty 100 companies through interactive dashboards, financial statement analysis, valuation metrics, peer comparison, sector insights, and stock screening.

The project combines an ETL pipeline, REST API, analytics engine, and Streamlit dashboard into a single end-to-end financial analytics solution.

---

## Features

- Interactive Streamlit Dashboard
- Company Profile Analysis
- Stock Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation
- Annual Reports Viewer
- Valuation Engine
- REST API
- PDF Tearsheet Generation
- Excel & CSV Export

---

## Technologies Used

- Python 3.x
- Streamlit
- FastAPI
- SQLite
- Pandas
- Plotly
- OpenPyXL
- Pytest
- Black
- Ruff

---

## Project Structure

```
nifty100_project/
│
├── db/
├── docs/
├── output/
├── reports/
├── src/
│   ├── analytics/
│   ├── api/
│   ├── dashboard/
│   └── etl/
├── tests/
├── README.md
└── requirements.txt
```

---

## Installation

Clone the repository and create a virtual environment.

```bash
python -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

---

## Run the ETL Pipeline

```bash
python -m src.etl.main
```

---

## Run the Dashboard

```bash
streamlit run src/dashboard/app.py
```

The dashboard will be available at:

```
http://localhost:8501
```

---

## Run the API

```bash
uvicorn src.api.main:app --reload
```

API Documentation:

```
http://localhost:8000/docs
```

---

## Generate Valuation Report

```bash
python -m src.analytics.valuation
```

---

## Run the Test Suite

Execute all tests:

```bash
pytest
```

Generate HTML report:

```bash
pytest --html=reports/pytest_report.html
```

---

## Performance Testing

Run API load test:

```bash
python tests/performance/load_test.py
```

Run dashboard performance test:

```bash
python -m tests.performance.dashboard_perf
```

---

## Code Quality

Format the project:

```bash
black src/ tests/
```

Run lint checks:

```bash
ruff check src/ tests/
```

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

## Output Files

Generated reports and exports are stored in the `output/` directory, including:

- valuation_summary.xlsx
- valuation_flags.csv
- perf_notes.md
- PDF tearsheets
- Exported CSV and Excel files

---

## Author

**Mohammad Esa Mohibuddin**