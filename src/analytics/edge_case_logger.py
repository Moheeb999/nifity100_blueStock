import sqlite3


def main():
    conn = sqlite3.connect("db/nifty100.db")
    cursor = conn.cursor()

    # Financial sector carve-out companies
    financial_companies = {
        "AXISBANK", "BAJAJFINSV", "BAJAJHLDNG", "BAJFINANCE",
        "BANKBARODA", "CANBK", "CHOLAFIN", "HDFCBANK",
        "HDFCLIFE", "ICICIBANK", "ICICIGI", "ICICIPRULI",
        "INDUSINDBK", "IRFC", "JIOFIN", "KOTAKBANK",
        "LICI", "PFC", "PNB", "RECLTD", "SBILIFE",
        "SBIN", "SHRIRAMFIN"
    }

    query = """
    SELECT
        c.id,
        c.roce_percentage,
        c.roe_percentage,
        AVG(fr.return_on_equity_pct)
    FROM companies c
    LEFT JOIN financial_ratios fr
        ON c.id = fr.company_id
    GROUP BY c.id
    """

    results = cursor.execute(query).fetchall()

    log_lines = []

    data_source_count = 0
    sector_exception_count = 0
    formula_discrepancy_count = 0

    for company_id, source_roce, source_roe, computed_roe in results:

        if source_roe is not None and computed_roe is not None:
            diff = abs(source_roe - computed_roe)

            if diff > 5:
                # Categorization
                if company_id in financial_companies:
                    category = "SECTOR_EXCEPTION"
                    sector_exception_count += 1

                elif computed_roe > 500 or computed_roe < -100:
                    category = "FORMULA_DISCREPANCY"
                    formula_discrepancy_count += 1

                else:
                    category = "VERSION_DIFFERENCE"
                    data_source_count += 1

                log_lines.append(
                    f"{company_id} | ROE mismatch | "
                    f"source={source_roe:.2f} | "
                    f"computed={computed_roe:.2f} | "
                    f"{category}"
                )

        # Temporary ROCE anomaly check
        if source_roce is not None and source_roce < 0:
            log_lines.append(
                f"{company_id} | ROCE anomaly | "
                f"source={source_roce:.2f} | "
                f"FORMULA_REVIEW"
            )

    with open("output/ratio_edge_cases.log", "w") as f:
        for line in log_lines:
            f.write(line + "\n")

    print("ratio_edge_cases.log generated")
    print("Total Anomalies:", len(log_lines))
    print("VERSION_DIFFERENCE:", data_source_count)
    print("SECTOR_EXCEPTION:", sector_exception_count)
    print("FORMULA_DISCREPANCY:", formula_discrepancy_count)

    conn.close()


if __name__ == "__main__":
    main()