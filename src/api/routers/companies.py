from io import BytesIO

import requests
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from src.api.database import get_db_connection

router = APIRouter()


def parse_year_month(value: str, param_name: str) -> int:
    """
    Parse a YYYY-MM string and return the year as an int.
    Raises HTTPException(400) if the format is invalid.
    """

    try:
        year_str, month_str = value.split("-")
        year = int(year_str)
        month = int(month_str)

        if not (1 <= month <= 12):
            raise ValueError("Month out of range")

    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {param_name} format: '{value}'. Expected YYYY-MM.",
        )

    return year


@router.get("/companies")
def get_companies(
    sector: str | None = Query(
        default=None,
        description="Filter by broad sector",
    ),
    market_cap_category: str | None = Query(
        default=None,
        description="Filter by market cap category",
    ),
    search: str | None = Query(
        default=None,
        description="Search by company name or ticker",
    ),
):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        c.id,
        c.company_name,
        s.broad_sector,
        s.sub_sector,
        c.roe_percentage,
        c.roce_percentage,
        s.market_cap_category
    FROM companies c
    LEFT JOIN sectors s
        ON c.id = s.company_id
    WHERE 1=1
    """

    params = []

    if sector:
        query += " AND s.broad_sector = ?"
        params.append(sector)

    if market_cap_category:
        query += " AND s.market_cap_category = ?"
        params.append(market_cap_category)

    if search:
        query += """
        AND (
            LOWER(c.company_name) LIKE ?
            OR LOWER(c.id) LIKE ?
        )
        """
        keyword = f"%{search.lower()}%"
        params.extend([keyword, keyword])

    query += " ORDER BY c.company_name"

    cursor.execute(query, params)

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row["id"],
            "company_name": row["company_name"],
            "broad_sector": row["broad_sector"],
            "sub_sector": row["sub_sector"],
            "roe_pct": row["roe_percentage"],
            "roce_pct": row["roce_percentage"],
            "market_cap_category": row["market_cap_category"],
        }
        for row in rows
    ]


@router.get("/companies/{ticker}")
def get_company_profile(ticker: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            c.*,
            s.broad_sector,
            s.sub_sector,
            s.market_cap_category,
            s.index_weight_pct
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE c.id = ?
        """,
        (ticker.upper(),),
    )

    company = cursor.fetchone()

    if company is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found."
        )

    cursor.execute(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year DESC
        LIMIT 1
        """,
        (ticker.upper(),),
    )

    latest_kpis = cursor.fetchone()

    conn.close()

    return {
        "company": dict(company),
        "latest_kpis": dict(latest_kpis) if latest_kpis else None,
    }


@router.get("/companies/{ticker}/pl")
def get_profit_loss(
    ticker: str,
    from_year: str | None = Query(
        default=None,
        description="Start period in YYYY-MM format",
    ),
    to_year: str | None = Query(
        default=None,
        description="End period in YYYY-MM format",
    ),
):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
    """

    params = [ticker.upper()]

    if from_year is not None:
        from_year_int = parse_year_month(from_year, "from_year")
        query += " AND year >= ?"
        params.append(from_year_int)

    if to_year is not None:
        to_year_int = parse_year_month(to_year, "to_year")
        query += " AND year <= ?"
        params.append(to_year_int)

    query += " ORDER BY year"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


@router.get("/companies/{ticker}/bs")
def get_balance_sheet(
    ticker: str,
    from_year: str | None = Query(
        default=None,
        description="Start period in YYYY-MM format",
    ),
    to_year: str | None = Query(
        default=None,
        description="End period in YYYY-MM format",
    ),
):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
    """

    params = [ticker.upper()]

    if from_year is not None:
        from_year_int = parse_year_month(from_year, "from_year")
        query += " AND year >= ?"
        params.append(from_year_int)

    if to_year is not None:
        to_year_int = parse_year_month(to_year, "to_year")
        query += " AND year <= ?"
        params.append(to_year_int)

    query += " ORDER BY year"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


@router.get("/companies/{ticker}/cashflow")
def get_cashflow(
    ticker: str,
    from_year: str | None = Query(
        default=None,
        description="Start period in YYYY-MM format",
    ),
    to_year: str | None = Query(
        default=None,
        description="End period in YYYY-MM format",
    ),
):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
    """

    params = [ticker.upper()]

    if from_year is not None:
        from_year_int = parse_year_month(from_year, "from_year")
        query += " AND year >= ?"
        params.append(from_year_int)

    if to_year is not None:
        to_year_int = parse_year_month(to_year, "to_year")
        query += " AND year <= ?"
        params.append(to_year_int)

    query += " ORDER BY year"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


@router.get("/companies/{ticker}/ratios")
def get_ratios(
    ticker: str,
    year: int | None = Query(default=None),
):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
    """

    params = [ticker.upper()]

    if year is not None:
        query += " AND year = ?"
        params.append(year)

    query += " ORDER BY year"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


@router.get("/companies/{ticker}/tearsheet")
def get_tearsheet(ticker: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT annual_report
        FROM documents
        WHERE company_id = ?
        ORDER BY year DESC
        LIMIT 1
        """,
        (ticker.upper(),),
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"No annual report found for '{ticker}'."
        )

    pdf_url = row["annual_report"]

    try:
        response = requests.get(pdf_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch annual report for '{ticker}' from source.",
        )

    return StreamingResponse(
        BytesIO(response.content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{ticker}_tearsheet.pdf"'
        },
    )