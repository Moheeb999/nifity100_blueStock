from fastapi import APIRouter, HTTPException
import requests

from src.api.database import get_db_connection

router = APIRouter()


def is_valid_url(url: str) -> bool:
    try:
        response = requests.head(
            url,
            allow_redirects=True,
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0"},
        )

        if response.status_code == 405:
            response = requests.get(
                url,
                stream=True,
                timeout=5,
                headers={"User-Agent": "Mozilla/5.0"},
            )

        return response.status_code == 200

    except Exception:
        return False


@router.get("/companies/{ticker}/documents")
def get_documents(ticker: str):

    conn = get_db_connection()
    cursor = conn.cursor()

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
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    cursor.execute(
        """
        SELECT
            year,
            annual_report
        FROM documents
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        (ticker,),
    )

    rows = cursor.fetchall()

    conn.close()

    documents = []

    for row in rows:
        documents.append(
            {
                "year": row["year"],
                "annual_report": row["annual_report"],
                "is_url_valid": is_valid_url(row["annual_report"]),
            }
        )

    return {
        "company_id": ticker,
        "company_name": company["company_name"],
        "documents": documents,
    }