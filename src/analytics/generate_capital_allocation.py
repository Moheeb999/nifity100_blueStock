import sqlite3
import pandas as pd
from src.analytics.cashflow_kpis import capital_allocation_pattern


def main():
    conn = sqlite3.connect("db/nifty100.db")

    query = """
    SELECT company_id, year,
           operating_activity,
           investing_activity,
           financing_activity
    FROM cashflow
    """

    df = pd.read_sql(query, conn)

    # Signs
    df["cfo_sign"] = df["operating_activity"].apply(lambda x: "+" if x > 0 else "-")
    df["cfi_sign"] = df["investing_activity"].apply(lambda x: "+" if x > 0 else "-")
    df["cff_sign"] = df["financing_activity"].apply(lambda x: "+" if x > 0 else "-")

    # Pattern label
    df["pattern_label"] = df.apply(
        lambda row: capital_allocation_pattern(
            row["operating_activity"],
            row["investing_activity"],
            row["financing_activity"]
        ),
        axis=1
    )

    output_df = df[
        ["company_id", "year", "cfo_sign", "cfi_sign", "cff_sign", "pattern_label"]
    ]

    output_df.to_csv("output/capital_allocation.csv", index=False)

    print("capital_allocation.csv generated")
    print("Rows:", len(output_df))

    conn.close()


if __name__ == "__main__":
    main()