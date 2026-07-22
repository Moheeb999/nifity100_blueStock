from pathlib import Path

import matplotlib.pyplot as plt


class PortfolioCharts:

    @staticmethod
    def sector_allocation_chart(sectors, output_file):

        labels = list(sectors.keys())
        values = list(sectors.values())

        plt.figure(figsize=(7,7))

        plt.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140
        )

        plt.title("Sector Allocation")

        plt.tight_layout()

        Path(output_file).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        plt.savefig(output_file)

        plt.close()

    @staticmethod
    def valuation_chart(pe, pb, roe, output_file):

        metrics = [
            "PE",
            "PB",
            "ROE"
        ]

        values = [
            pe,
            pb,
            roe
        ]

        plt.figure(figsize=(6,4))

        plt.bar(metrics, values)

        plt.title("Portfolio Valuation Metrics")

        plt.ylabel("Value")

        plt.tight_layout()

        Path(output_file).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        plt.savefig(output_file)

        plt.close()