
import sqlite3
import pandas as pd

METRICS = [
    "return_on_equity_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "interest_coverage",
    "asset_turnover",
]


class PeerRankingEngine:

    def __init__(self):
        self.conn = sqlite3.connect("db/nifty100.db")

    def load_data(self):
        ratios = pd.read_sql("SELECT * FROM financial_ratios", self.conn)
        peers = pd.read_sql("SELECT * FROM peer_groups", self.conn)

        try:
            companies = pd.read_sql(
                "SELECT id, company_name FROM companies", self.conn
            )
        except Exception:
            companies = pd.read_sql(
                "SELECT id, id AS company_name FROM companies", self.conn
            )

        ratios = (
            ratios.sort_values(["company_id", "year"])
            .groupby("company_id")
            .tail(1)
            .reset_index(drop=True)
        )

        df = ratios.merge(peers, on="company_id", how="left")
        df = df.merge(companies, left_on="company_id", right_on="id", how="left")
        return df

    @staticmethod
    def percentile_rank(series, reverse=False):
        valid = series.dropna()
        out = pd.Series(index=series.index, dtype=float)

        if len(valid) == 0:
            return out

        if len(valid) == 1:
            out.loc[valid.index] = 100.0
            return out

        pct = valid.rank(method="average", pct=True) * 100
        if reverse:
            pct = 100 - pct
        out.loc[valid.index] = pct.round(2)
        return out

    def compute_percentiles(self, df):
        rows = []

        for group in sorted(df["peer_group_name"].dropna().unique()):
            peer_df = df[df["peer_group_name"] == group].copy()

            for metric in METRICS:
                if metric not in peer_df.columns:
                    continue

                reverse = metric == "debt_to_equity"
                peer_df["percentile_rank"] = self.percentile_rank(
                    peer_df[metric], reverse=reverse
                )

                for _, row in peer_df.iterrows():
                    if pd.isna(row[metric]) or pd.isna(row["percentile_rank"]):
                        continue

                    rows.append(
                        {
                            "company_id": row["company_id"],
                            "peer_group_name": group,
                            "metric": metric,
                            "value": float(row[metric]),
                            "percentile_rank": float(row["percentile_rank"]),
                            "year": int(row["year"]),
                        }
                    )

        return pd.DataFrame(rows)

    def save_to_database(self, percentile_df):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM peer_percentiles")
        self.conn.commit()

        percentile_df.to_sql(
            "peer_percentiles",
            self.conn,
            if_exists="append",
            index=False,
        )
        self.conn.commit()

    def validate(self, df, percentile_df):
        print("\\n==============================")
        print("Peer Ranking Summary")
        print("==============================")
        print("Peer Groups:", df["peer_group_name"].nunique())
        print("Companies Assigned:", df["peer_group_name"].notna().sum())
        print("Companies Without Peer Group:", df["peer_group_name"].isna().sum())
        print("Metrics Ranked:", len(METRICS))
        print("Rows Inserted:", len(percentile_df))
        print("==============================")
        if not percentile_df.empty:
            print(percentile_df.head(20))

    def run(self):
        print("Loading data...")
        df = self.load_data()
        print("Companies:", len(df))
        print("Computing percentile ranks...")
        percentile_df = self.compute_percentiles(df)
        print("Saving to SQLite...")
        self.save_to_database(percentile_df)
        self.validate(df, percentile_df)


def main():
    engine = PeerRankingEngine()
    try:
        engine.run()
        print("\\npeer_percentiles table populated successfully.")
    finally:
        engine.conn.close()


if __name__ == "__main__":
    main()
