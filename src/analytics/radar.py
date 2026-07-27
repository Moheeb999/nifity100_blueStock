import os
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

METRICS = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "composite_quality_score",
]


class RadarChartGenerator:
    """Generate radar charts for company financial comparisons."""

    def __init__(self):
        """Initialize the radar chart generator."""

        self.conn = sqlite3.connect("db/nifty100.db")

        os.makedirs("reports/radar_charts", exist_ok=True)

    def load_data(self):
        """Load company and peer comparison data."""

        ratios = pd.read_sql("SELECT * FROM financial_ratios", self.conn)

        peers = pd.read_sql("SELECT * FROM peer_groups", self.conn)

        ratios = (
            ratios.sort_values(["company_id", "year"])
            .groupby("company_id")
            .tail(1)
            .reset_index(drop=True)
        )

        df = ratios.merge(peers, on="company_id", how="left")

        return df

    @staticmethod
    def normalize(series):
        """Normalize a metric to a 0-100 scale."""

        s = series.fillna(series.median())

        mn = s.min()
        mx = s.max()

        if mn == mx:
            return pd.Series([50] * len(s), index=s.index)

        return (s - mn) / (mx - mn) * 100

    def generate_chart(self, company_row, reference_df, reference_label):
        """Generate a radar chart for a company."""

        labels = [
            "ROE",
            "ROCE",
            "NPM",
            "D/E",
            "FCF",
            "PAT CAGR",
            "Revenue CAGR",
            "Quality",
        ]

        company_values = []
        reference_values = []

        for metric in METRICS:

            normalized = self.normalize(reference_df[metric])

            if metric == "debt_to_equity":
                normalized = 100 - normalized

            company_value = company_row[metric]

            if pd.isna(company_value):
                company_values.append(0)
            else:
                mn = reference_df[metric].min()
                mx = reference_df[metric].max()

                if mn == mx:
                    company_values.append(50)
                else:
                    score = (company_value - mn) / (mx - mn) * 100

                    if metric == "debt_to_equity":
                        score = 100 - score

                    company_values.append(score)

            reference_values.append(normalized.mean())

        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()

        company_values += company_values[:1]
        reference_values += reference_values[:1]
        angles += angles[:1]

        fig = plt.figure(figsize=(7, 7))
        ax = plt.subplot(111, polar=True)

        ax.plot(angles, company_values, linewidth=2, label=company_row["company_id"])

        ax.fill(angles, company_values, alpha=0.25)

        ax.plot(
            angles, reference_values, linestyle="--", linewidth=2, label=reference_label
        )

        ax.set_xticks(angles[:-1])

        ax.set_xticklabels(labels)

        ax.set_ylim(0, 100)

        ax.set_title(f'{company_row["company_id"]}')

        ax.legend(loc="upper right")

        filename = f"reports/radar_charts/" f"{company_row['company_id']}_radar.png"

        plt.savefig(filename, dpi=150, bbox_inches="tight")

        plt.close()

    def run(self):
        """Generate radar charts for all companies."""

        df = self.load_data()

        overall_df = df.copy()

        peer_count = 0
        standalone_count = 0

        for _, row in df.iterrows():

            if pd.notna(row["peer_group_name"]):

                peer_df = df[df["peer_group_name"] == row["peer_group_name"]]

                self.generate_chart(row, peer_df, "Peer Average")

                peer_count += 1

            else:

                self.generate_chart(row, overall_df, "Nifty100 Average")

                standalone_count += 1

        print(f"Peer Charts: {peer_count}")

        print(f"Standalone Charts: {standalone_count}")

        print(f"Total Charts: {peer_count + standalone_count}")

        self.conn.close()


def main():
    """Run the peer ranking engine."""

    RadarChartGenerator().run()


if __name__ == "__main__":
    main()
