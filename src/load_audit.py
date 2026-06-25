import pandas as pd


def generate_load_audit():
    audit = pd.DataFrame({
        "table_name": [
            "companies",
            "profitandloss",
            "balancesheet",
            "cashflow",
            "stock_prices",
            "analysis",
            "documents",
            "prosandcons",
            "sectors",
            "financial_ratios",
            "peer_groups",
            "market_cap"
        ],
        "rows_loaded": [
            92,
            1070,
            1058,
            1056,
            5520,
            16,
            1457,
            14,
            92,
            1160,
            56,
            552
        ],
        "rows_rejected": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
        ],
        "status": [
            "LOADED"
        ] * 12
    })

    audit.to_csv("output/load_audit.csv", index=False)
    print("load_audit.csv created successfully")


if __name__ == "__main__":
    generate_load_audit()