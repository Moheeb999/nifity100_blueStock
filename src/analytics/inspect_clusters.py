"""
inspect_clusters.py

Sprint 6 - Day 36/37 diagnostic

Investigates small or imbalanced clusters produced by clustering.py.
Merges cluster assignments back onto the RAW (pre-scaling) financial
ratios so extreme values driving a small cluster are visible in their
original units, not standardized units.

Usage
-----
    python -m src.analytics.inspect_clusters
    python -m src.analytics.inspect_clusters --max-size 5
    python -m src.analytics.inspect_clusters --cluster-id 4
"""

import argparse

import pandas as pd

from src.analytics.clustering import (
    FEATURES,
    OUTPUT_DIR,
    fill_sector_medians,
    load_latest_ratios,
)


def load_cluster_labels() -> pd.DataFrame:
    path = OUTPUT_DIR / "cluster_labels.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run clustering.py first."
        )

    return pd.read_csv(path)


def build_diagnostic_frame() -> pd.DataFrame:
    """Merge cluster assignments back onto raw (imputed) feature values."""

    ratios_df = load_latest_ratios()
    ratios_df = fill_sector_medians(ratios_df)

    labels_df = load_cluster_labels()

    merged = labels_df.merge(
        ratios_df[["company_id"] + FEATURES],
        on="company_id",
        how="left",
        suffixes=("", "_raw"),
    )

    if merged[FEATURES].isna().any().any():
        raise ValueError(
            "Some cluster assignments could not be matched to raw feature data."
        )

    return merged


def cluster_size_summary(df: pd.DataFrame) -> pd.Series:
    return df["cluster_id"].value_counts().sort_index()


def flag_small_clusters(df: pd.DataFrame, max_size: int) -> list[int]:
    sizes = cluster_size_summary(df)
    return sizes[sizes <= max_size].index.tolist()


def inspect_cluster(df: pd.DataFrame, cluster_id: int) -> pd.DataFrame:
    cols = [
        "company_id",
        "company_name",
        "broad_sector",
        "cluster_id",
        "distance_from_centroid",
    ] + FEATURES

    subset = df[df["cluster_id"] == cluster_id][cols]

    return subset.sort_values("distance_from_centroid")


def cluster_profile(df: pd.DataFrame, cluster_id: int) -> pd.DataFrame:
    """Descriptive statistics (mean, quartiles, range) for one cluster."""

    return (
        df[df["cluster_id"] == cluster_id][FEATURES]
        .describe()
        .round(2)
    )


def flag_extreme_features(
    df: pd.DataFrame,
    z_threshold: float = 3.0,
) -> pd.DataFrame:
    """
    Flag companies whose RAW feature values are extreme outliers
    relative to the full (imputed) population -- independent of
    which cluster they landed in.
    """

    flags = pd.DataFrame({
        "company_id": df["company_id"],
        "company_name": df["company_name"],
        "cluster_id": df["cluster_id"],
    })

    any_extreme = pd.Series(False, index=df.index)

    for col in FEATURES:
        std = df[col].std()

        if std == 0:
            z = pd.Series(0.0, index=df.index)
        else:
            z = (df[col] - df[col].mean()) / std

        flags[f"{col}_z"] = z.round(2)

        any_extreme |= z.abs() > z_threshold

    flags["is_extreme_outlier"] = any_extreme

    triggered = []

    for idx in df.index:
        cols = [
            col
            for col in FEATURES
            if abs(flags.loc[idx, f"{col}_z"]) > z_threshold
        ]
        triggered.append(", ".join(cols))

    flags["trigger_features"] = triggered

    return flags[flags["is_extreme_outlier"]].sort_values(
        "company_id"
    )


def main():

    parser = argparse.ArgumentParser(
        description="Inspect small/imbalanced KMeans clusters."
    )

    parser.add_argument(
        "--max-size",
        type=int,
        default=5,
        help="Clusters with this many companies or fewer are flagged as small.",
    )

    parser.add_argument(
        "--cluster-id",
        type=int,
        default=None,
        help="Inspect one specific cluster id directly.",
    )

    parser.add_argument(
        "--z-threshold",
        type=float,
        default=3.0,
        help="Z-score magnitude above which a raw feature is flagged extreme.",
    )

    args = parser.parse_args()

    df = build_diagnostic_frame()

    print("Cluster sizes:")
    print(cluster_size_summary(df))

    if args.cluster_id is not None:
        target_clusters = [args.cluster_id]
    else:
        target_clusters = flag_small_clusters(df, args.max_size)

        if not target_clusters:
            print(
                f"\nNo clusters at or below size {args.max_size}. "
                "Nothing further to inspect."
            )

    for cid in target_clusters:
        print(f"\n--- Cluster {cid} ---")

        cluster_rows = inspect_cluster(df, cid)

        print(cluster_rows.to_string(index=False))

        print(f"\nCluster {cid} profile:")
        profile = cluster_profile(df, cid)

        print(profile)

        cluster_rows.to_csv(
            OUTPUT_DIR / f"cluster_{cid}_inspection.csv",
            index=False,
        )

        profile.to_csv(
            OUTPUT_DIR / f"cluster_{cid}_profile.csv"
        )

    summary = (
        df.groupby("cluster_id")[FEATURES]
          .mean()
          .round(2)
    )

    summary.to_csv(
        OUTPUT_DIR / "cluster_summary.csv"
    )

    print("\nCluster Summary:")
    print(summary)

    print("\nRaw-feature outliers (|z| > {:.1f}), regardless of cluster:".format(
        args.z_threshold
    ))

    extreme = flag_extreme_features(df, z_threshold=args.z_threshold)

    if extreme.empty:
        print("None found.")
    else:
        print(extreme.to_string(index=False))

        extreme.to_csv(
            OUTPUT_DIR / "cluster_outliers.csv",
            index=False,
        )


if __name__ == "__main__":
    main()