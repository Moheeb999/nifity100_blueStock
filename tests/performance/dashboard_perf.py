import time

from src.dashboard.utils.db import get_company_profile

tickers = [
    "TCS",
    "INFY",
    "RELIANCE",
    "HDFCBANK",
    "ICICIBANK",
]

print("Company Profile Performance Test")
print("-" * 45)

for ticker in tickers:
    start = time.perf_counter()

    df = get_company_profile(ticker)

    elapsed = time.perf_counter() - start

    print(f"{ticker:<12} {elapsed:.3f} sec ({len(df)} rows)")
