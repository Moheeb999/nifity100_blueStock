from collections import defaultdict

from fastapi import APIRouter, HTTPException

from src.api.database import get_db_connection

router = APIRouter()


@router.get("/peers/{group_name}")
def get_peer_group(group_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check peer group exists
    cursor.execute(
        """
        SELECT COUNT(*) AS cnt
        FROM peer_groups
        WHERE peer_group_name = ?
        """,
        (group_name,),
    )

    if cursor.fetchone()["cnt"] == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Peer group not found."
        )

    # Fetch all companies and their percentile metrics
    cursor.execute(
        """
        SELECT
            pg.company_id,
            c.company_name,
            pg.is_benchmark,
            pp.metric,
            pp.value,
            pp.percentile_rank,
            pp.year
        FROM peer_groups pg
        JOIN companies c
            ON pg.company_id = c.id
        JOIN peer_percentiles pp
            ON pg.company_id = pp.company_id
           AND pg.peer_group_name = pp.peer_group_name
        WHERE pg.peer_group_name = ?
        ORDER BY c.company_name, pp.metric
        """,
        (group_name,),
    )

    rows = cursor.fetchall()
    conn.close()

    companies = {}
    for row in rows:
        company_id = row["company_id"]
        if company_id not in companies:
            companies[company_id] = {
                "company_id": company_id,
                "company_name": row["company_name"],
                "is_benchmark": bool(row["is_benchmark"]),
                "metrics": [],
            }
        companies[company_id]["metrics"].append(
            {
                "metric": row["metric"],
                "value": row["value"],
                "percentile_rank": row["percentile_rank"],
                "year": row["year"],
            }
        )

    return {
        "peer_group": group_name,
        "companies": list(companies.values()),
    }


@router.get("/companies/{ticker}/peers/compare")
def compare_with_peers(ticker: str):
    ticker = ticker.upper()

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
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    # Find peer group
    cursor.execute(
        """
        SELECT peer_group_name
        FROM peer_groups
        WHERE company_id = ?
        """,
        (ticker,),
    )

    peer = cursor.fetchone()

    if not peer:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Peer group not found."
        )

    peer_group = peer["peer_group_name"]

    # Benchmark company
    cursor.execute(
        """
        SELECT
            pg.company_id,
            c.company_name
        FROM peer_groups pg
        JOIN companies c
            ON pg.company_id = c.id
        WHERE
            pg.peer_group_name = ?
            AND pg.is_benchmark = 1
        """,
        (peer_group,),
    )

    benchmark = cursor.fetchone()

    if not benchmark:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Benchmark company not found."
        )

    benchmark_id = benchmark["company_id"]
    benchmark_name = benchmark["company_name"]

    # All metrics in peer group
    cursor.execute(
        """
        SELECT
            company_id,
            metric,
            value
        FROM peer_percentiles
        WHERE peer_group_name = ?
        """,
        (peer_group,),
    )

    rows = cursor.fetchall()

    peer_values = defaultdict(list)
    company_values = {}
    benchmark_values = {}

    for row in rows:
        metric = row["metric"]
        value = row["value"]

        peer_values[metric].append(value)

        if row["company_id"] == ticker:
            company_values[metric] = value

        if row["company_id"] == benchmark_id:
            benchmark_values[metric] = value

    radar = []

    for metric in sorted(peer_values.keys()):
        avg = round(
            sum(peer_values[metric]) / len(peer_values[metric]),
            2,
        )

        radar.append(
            {
                "metric": metric,
                "company": company_values.get(metric),
                "peer_average": avg,
                "benchmark": benchmark_values.get(metric),
            }
        )

    conn.close()

    return {
        "company_id": ticker,
        "company_name": company["company_name"],
        "peer_group": peer_group,
        "benchmark_company": benchmark_name,
        "radar": radar,
    }