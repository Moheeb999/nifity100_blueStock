"""
cluster_profiles.py

Sprint 6 - Day 37

Generates descriptive statistics and sector composition
for each KMeans cluster.

Outputs
-------
output/
    cluster_profiles.csv
    cluster_sector_distribution.csv
    cluster_report.csv
"""

from pathlib import Path

import pandas as pd

from src.analytics.clustering import (
    FEATURES,
    OUTPUT_DIR,
    fill_sector_medians,
    load_latest_ratios,
)
from src.analytics.inspect_clusters import load_cluster_labels


def build_profile_frame() -> pd.DataFrame:
    """
    Merge cluster assignments with raw financial ratios.
    """

    ratios_df = load_latest_ratios()
    ratios_df = fill_sector_medians(ratios_df)

    labels_df = load_cluster_labels()

    merged = labels_df[
        [
            "company_id",
            "cluster_id",
            "cluster_name",
            "distance_from_centroid",
        ]
    ].merge(
        ratios_df,
        on="company_id",
        how="left",
    )

    if merged[FEATURES].isna().any().any():
        raise ValueError(
            "Some cluster assignments could not be matched to financial ratios."
        )

    required_columns = {
        "cluster_id",
        "broad_sector",
        *FEATURES,
    }

    missing = required_columns - set(merged.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    return merged


def generate_cluster_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate descriptive statistics for each feature within every cluster.
    Statistics:
        - mean
        - median
        - std
        - min
        - max
    """
    profiles = (
        df.groupby("cluster_id")[FEATURES]
        .agg(["mean", "median", "std", "min", "max"])
        .round(2)
        .sort_index()
    )
    return profiles


def save_cluster_profiles(profiles: pd.DataFrame) -> Path:
    """
    Save cluster profile statistics to CSV.
    """
    output_path = OUTPUT_DIR / "cluster_profiles.csv"
    profiles.to_csv(output_path)
    print(f"Saved cluster profiles to: {output_path}")
    return output_path


def generate_sector_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate sector composition for each cluster.
    """
    sector_distribution = (
        df.groupby(["cluster_id", "broad_sector"])
        .size()
        .reset_index(name="company_count")
        .sort_values(
            ["cluster_id", "company_count"],
            ascending=[True, False],
        )
    )
    return sector_distribution


def save_sector_distribution(
    sector_distribution: pd.DataFrame,
) -> Path:
    """
    Save cluster sector composition.
    """
    output_path = OUTPUT_DIR / "cluster_sector_distribution.csv"
    sector_distribution.to_csv(
        output_path,
        index=False,
    )
    print(f"Saved sector distribution to: {output_path}")
    return output_path


def generate_cluster_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate one-row summary for each cluster.
    """
    cluster_size = df.groupby("cluster_id").size().rename("company_count")
    cluster_names = (
        df.groupby("cluster_id")["cluster_name"].first().rename("cluster_name")
    )
    feature_means = df.groupby("cluster_id")[FEATURES].mean().round(2)
    dominant_sector = (
        df.groupby(["cluster_id", "broad_sector"])
        .size()
        .reset_index(name="count")
        .sort_values(
            ["cluster_id", "count"],
            ascending=[True, False],
        )
        .drop_duplicates("cluster_id")
        .set_index("cluster_id")["broad_sector"]
        .rename("dominant_sector")
    )
    report = pd.concat(
        [
            cluster_size,
            cluster_names,
            dominant_sector,
            feature_means,
        ],
        axis=1,
    ).reset_index()

    report = report.sort_values("cluster_id")

    return report


def save_cluster_report(report: pd.DataFrame) -> Path:
    """
    Save cluster summary report.
    """
    output_path = OUTPUT_DIR / "cluster_report.csv"
    report.to_csv(
        output_path,
        index=False,
    )
    print(f"Saved cluster report to: {output_path}")
    return output_path


if __name__ == "__main__":
    df = build_profile_frame()
    print(f"Loaded {len(df)} clustered companies.")

    profiles = generate_cluster_profiles(df)
    print(f"Generated {len(profiles)} profile rows.")

    save_cluster_profiles(profiles)

    sector_distribution = generate_sector_distribution(df)
    print(
        f"Generated sector distribution for " f"{df['cluster_id'].nunique()} clusters."
    )

    save_sector_distribution(sector_distribution)

    report = generate_cluster_report(df)
    print(f"Generated cluster report for {len(report)} clusters.")

    save_cluster_report(report)
