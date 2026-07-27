import time

from fastapi import APIRouter

from src.api.config import APP_START_TIME, VERSION
from src.api.database import get_db_connection

router = APIRouter()


@router.get("/health")
def health_check():
    """Return API health status and database statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    tables = [
        "analysis",
        "balancesheet",
        "cashflow",
        "companies",
        "documents",
        "financial_ratios",
        "market_cap",
        "peer_groups",
        "peer_percentiles",
        "profitandloss",
        "prosandcons",
        "sectors",
        "stock_prices",
    ]

    db_row_counts = {}

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        db_row_counts[table] = cursor.fetchone()[0]

    conn.close()

    return {
        "status": "ok",
        "db_row_counts": db_row_counts,
        "uptime_seconds": round(time.time() - APP_START_TIME, 2),
        "version": VERSION,
    }
