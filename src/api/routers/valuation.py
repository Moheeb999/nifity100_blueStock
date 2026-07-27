from fastapi import APIRouter, HTTPException

from src.api.database import get_db_connection

router = APIRouter()


@router.get("/market-cap/{ticker}")
def get_market_cap_history(ticker: str):
    """Return historical market valuation metrics for a company."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check company exists
    cursor.execute(
        """
        SELECT company_name
        FROM companies
        WHERE id = ?
        """,
        (ticker,),
    )

    company = cursor.fetchone()

    if not company:
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found.")

    # Fetch valuation history
    cursor.execute(
        """
        SELECT
            year,
            market_cap_crore,
            enterprise_value_crore,
            pe_ratio,
            pb_ratio,
            ev_ebitda,
            dividend_yield_pct
        FROM market_cap
        WHERE company_id = ?
          AND year BETWEEN 2019 AND 2024
        ORDER BY year
        """,
        (ticker,),
    )

    history = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "company_id": ticker,
        "company_name": company["company_name"],
        "valuation_history": history,
    }
