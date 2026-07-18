import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = "db/nifty100.db"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    fr.company_id,
    fr.return_on_equity_pct,
    fr.return_on_capital_employed_pct,
    fr.net_profit_margin_pct,
    fr.operating_profit_margin_pct,
    fr.debt_to_equity,
    fr.interest_coverage,
    fr.revenue_cagr_5yr,
    fr.pat_cagr_5yr,
    fr.eps_cagr_5yr,
    fr.free_cash_flow_cr,
    fr.composite_quality_score,
    mc.dividend_yield_pct
FROM financial_ratios fr
LEFT JOIN market_cap mc
ON fr.company_id = mc.company_id
AND fr.year = mc.year
WHERE fr.year = (
    SELECT MAX(year)
    FROM financial_ratios f2
    WHERE f2.company_id = fr.company_id
)
"""

df = pd.read_sql(query, conn)
conn.close()

results = []


def add(company, typ, rule, text, confidence):
    results.append({
        "company_id": company,
        "type": typ,
        "rule_id": rule,
        "text": text,
        "confidence_pct": confidence
    })


for _, r in df.iterrows():

    c = r.company_id

    # ---------- PROS ----------

    if r.return_on_equity_pct > 20:
        add(c, "PRO", "P1", "High ROE indicates efficient capital utilization.", 95)

    if r.return_on_capital_employed_pct > 20:
        add(c, "PRO", "P2", "Excellent ROCE demonstrates efficient business operations.", 95)

    if r.net_profit_margin_pct > 15:
        add(c, "PRO", "P3", "Strong profit margins support healthy earnings.", 90)

    if r.operating_profit_margin_pct > 20:
        add(c, "PRO", "P4", "High operating margin reflects operational efficiency.", 90)

    if r.debt_to_equity < 0.5:
        add(c, "PRO", "P5", "Low debt improves financial stability.", 93)

    if r.interest_coverage > 5:
        add(c, "PRO", "P6", "Comfortable interest coverage reduces financial risk.", 92)

    if r.revenue_cagr_5yr > 15:
        add(c, "PRO", "P7", "Revenue has grown consistently over five years.", 92)

    if r.pat_cagr_5yr > 15:
        add(c, "PRO", "P8", "Profit growth has remained consistently strong.", 92)

    if r.eps_cagr_5yr > 15:
        add(c, "PRO", "P9", "EPS growth indicates increasing shareholder value.", 92)

    if r.free_cash_flow_cr > 0:
        add(c, "PRO", "P10", "Positive free cash flow strengthens future growth.", 90)

    if pd.notna(r.dividend_yield_pct) and r.dividend_yield_pct > 1:
        add(c, "PRO", "P11", "Healthy dividend yield rewards shareholders.", 80)

    if r.composite_quality_score > 80:
        add(c, "PRO", "P12", "Excellent overall quality score.", 96)

    # ---------- CONS ----------

    if r.return_on_equity_pct < 10:
        add(c, "CON", "C1", "Low ROE reflects weak capital efficiency.", 95)

    if r.return_on_capital_employed_pct < 10:
        add(c, "CON", "C2", "Low ROCE indicates inefficient capital utilization.", 95)

    if r.net_profit_margin_pct < 5:
        add(c, "CON", "C3", "Weak profit margins reduce profitability.", 90)

    if r.operating_profit_margin_pct < 10:
        add(c, "CON", "C4", "Low operating margin signals operational weakness.", 90)

    if r.debt_to_equity > 1.5:
        add(c, "CON", "C5", "High debt increases financial risk.", 93)

    if r.interest_coverage < 2:
        add(c, "CON", "C6", "Poor interest coverage raises repayment concerns.", 92)

    if r.revenue_cagr_5yr < 5:
        add(c, "CON", "C7", "Revenue growth has been weak.", 92)

    if r.pat_cagr_5yr < 5:
        add(c, "CON", "C8", "Profit growth has remained weak.", 92)

    if r.eps_cagr_5yr < 5:
        add(c, "CON", "C9", "EPS growth has been limited.", 92)

    if r.free_cash_flow_cr < 0:
        add(c, "CON", "C10", "Negative free cash flow may constrain future growth.", 90)

    if pd.notna(r.dividend_yield_pct) and r.dividend_yield_pct == 0:
        add(c, "CON", "C11", "No dividend is currently being paid.", 80)

    if r.composite_quality_score < 40:
        add(c, "CON", "C12", "Overall quality score is relatively weak.", 96)


output = pd.DataFrame(results)

output.to_csv(
    OUTPUT_DIR / "pros_cons_generated.csv",
    index=False
)

print("=" * 60)
print("AUTO PROS / CONS GENERATOR")
print("=" * 60)
print(f"Companies Processed : {df.company_id.nunique()}")
print(f"Pros Generated      : {(output.type=='PRO').sum()}")
print(f"Cons Generated      : {(output.type=='CON').sum()}")
print(f"Total Insights      : {len(output)}")
print("Generated")
print("output/pros_cons_generated.csv")
print("=" * 60)