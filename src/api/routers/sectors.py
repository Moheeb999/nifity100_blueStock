import statistics
from collections import defaultdict

from fastapi import APIRouter, HTTPException

from src.api.database import get_db_connection

router = APIRouter()


@router.get("/sectors")
def get_sectors():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            s.broad_sector,
            fr.return_on_equity_pct,
            mc.pe_ratio,
            fr.debt_to_equity
        FROM sectors s
        JOIN financial_ratios fr
            ON s.company_id = fr.company_id
        LEFT JOIN market_cap mc
            ON fr.company_id = mc.company_id
            AND fr.year = mc.year
        WHERE fr.year = (
            SELECT MAX(year)
            FROM financial_ratios f2
            WHERE f2.company_id = fr.company_id
        )
        """
    )

    rows = cursor.fetchall()
    conn.close()

    sector_data = defaultdict(list)

    for row in rows:
        sector_data[row["broad_sector"]].append(row)

    result = []

    for sector, companies in sector_data.items():
        roe = [
            r["return_on_equity_pct"]
            for r in companies
            if r["return_on_equity_pct"] is not None
        ]

        pe = [
            r["pe_ratio"]
            for r in companies
            if r["pe_ratio"] is not None
        ]

        de = [
            r["debt_to_equity"]
            for r in companies
            if r["debt_to_equity"] is not None
        ]

        result.append({
            "sector": sector,
            "company_count": len(companies),
            "median_roe": round(statistics.median(roe), 2) if roe else None,
            "median_pe": round(statistics.median(pe), 2) if pe else None,
            "median_de": round(statistics.median(de), 2) if de else None
        })

    return sorted(result, key=lambda x: x["sector"])


@router.get("/sectors/{sector}/companies")
def get_sector_companies(sector: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check sector exists
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM sectors
        WHERE LOWER(broad_sector)=LOWER(?)
        """,
        (sector,),
    )

    if cursor.fetchone()[0] == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Sector '{sector}' not found."
        )

    cursor.execute(
        """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            fr.year,
            fr.return_on_equity_pct,
            fr.return_on_capital_employed_pct,
            fr.debt_to_equity,
            fr.free_cash_flow_cr,
            mc.pe_ratio,
            mc.pb_ratio
        FROM companies c
        JOIN sectors s
            ON c.id = s.company_id
        LEFT JOIN financial_ratios fr
            ON fr.company_id = c.id
        LEFT JOIN market_cap mc
            ON mc.company_id = c.id
           AND mc.year = fr.year
        WHERE
            LOWER(s.broad_sector)=LOWER(?)
            AND fr.year = (
                SELECT MAX(fr2.year)
                FROM financial_ratios fr2
                WHERE fr2.company_id=c.id
            )
        ORDER BY c.company_name
        """,
        (sector,),
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]