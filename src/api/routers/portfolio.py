from statistics import quantiles

from fastapi import APIRouter

from src.api.database import get_db_connection

router = APIRouter()


@router.get("/portfolio/stats")
def portfolio_stats():
    """Return portfolio metric deciles based on financial ratios."""

    metrics = [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "net_profit_margin_pct",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
    ]

    conn = get_db_connection()
    cursor = conn.cursor()

    result = {}

    for metric in metrics:

        cursor.execute(f"""
            SELECT {metric}
            FROM financial_ratios
            WHERE year = (
                SELECT MAX(fr2.year)
                FROM financial_ratios fr2
                WHERE fr2.company_id = financial_ratios.company_id
            )
            AND {metric} IS NOT NULL
            """)

        values = [row[0] for row in cursor.fetchall()]

        if len(values) < 10:
            result[metric] = None
            continue

        values.sort()

        deciles = quantiles(values, n=10)

        result[metric] = {
            "P10": round(deciles[0], 2),
            "P20": round(deciles[1], 2),
            "P30": round(deciles[2], 2),
            "P40": round(deciles[3], 2),
            "P50": round(deciles[4], 2),
            "P60": round(deciles[5], 2),
            "P70": round(deciles[6], 2),
            "P80": round(deciles[7], 2),
            "P90": round(deciles[8], 2),
        }

    conn.close()

    return result
