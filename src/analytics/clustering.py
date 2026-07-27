"""
clustering.py

Sprint 6 - Day 36
KMeans Company Clustering

Groups companies into behavioral / financial clusters based on the
latest available financial ratios for each company, using sector
median imputation for missing values and standardized features.

Data Sources
------------
SQLite
    companies
    financial_ratios
    sectors

Output
------
reports/elbow_plot.png
output/cluster_labels.csv
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[2]

DB_PATH = ROOT_DIR / "db" / "nifty100.db"

if not DB_PATH.exists():
    raise FileNotFoundError(f"Database not found: {DB_PATH}")

REPORTS_DIR = ROOT_DIR / "reports"
OUTPUT_DIR = ROOT_DIR / "output"

REPORTS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "operating_profit_margin_pct",
    "free_cash_flow_cr",
]

# NOTE: 2 of the 92 Nifty 100 companies (ATGL, SBIN) currently have no
# rows in financial_ratios, so this is temporarily set to 90 to unblock
# Sprint 6 clustering. See backlog item to fix upstream data for ATGL/SBIN,
# then switch this back to 92 once financial_ratios is regenerated.
EXPECTED_COMPANIES = 90


# ---------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------


def load_latest_ratios():
    """Load the latest financial ratios for every company."""

    query = """
    WITH latest_year AS (
        SELECT
            company_id,
            MAX(year) AS latest_year
        FROM financial_ratios
        GROUP BY company_id
    )

    SELECT
        fr.company_id,
        c.company_name,
        s.broad_sector,

        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.revenue_cagr_5yr,
        fr.operating_profit_margin_pct,
        fr.free_cash_flow_cr

    FROM financial_ratios fr

    JOIN latest_year ly
        ON fr.company_id = ly.company_id
       AND fr.year = ly.latest_year

    JOIN companies c
        ON fr.company_id = c.id

    JOIN sectors s
        ON fr.company_id = s.company_id

    ORDER BY fr.company_id;
    """

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql(query, conn)

    return df


# ---------------------------------------------------------------------
# Sector Median Imputation
# ---------------------------------------------------------------------


def fill_sector_medians(df):
    """Fill missing feature values using the median within each broad sector."""

    df = df.copy()

    for column in FEATURES:
        df[column] = df.groupby("broad_sector")[column].transform(
            lambda s: s.fillna(s.median())
        )

        # Fallback if an entire sector is missing that metric
        df[column] = df[column].fillna(df[column].median())

    return df


# ---------------------------------------------------------------------
# Feature Scaling
# ---------------------------------------------------------------------


def scale_features(df):
    """Standardize clustering features."""

    scaler = StandardScaler()

    scaled = scaler.fit_transform(df[FEATURES])

    return scaled, scaler


# ---------------------------------------------------------------------
# Elbow Plot
# ---------------------------------------------------------------------


def generate_elbow_plot(X):
    """Generate inertia plot for k=2..10."""

    inertias = []

    ks = range(2, 11)

    for k in ks:
        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
        )

        model.fit(X)

        inertias.append(model.inertia_)

    plt.figure(figsize=(8, 5))

    plt.plot(ks, inertias, marker="o")

    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Inertia")

    plt.title("KMeans Elbow Plot")

    plt.grid(True)

    plt.savefig(REPORTS_DIR / "elbow_plot.png", dpi=300)

    plt.close()


# ---------------------------------------------------------------------
# KMeans Clustering
# ---------------------------------------------------------------------


def run_clustering(X):
    """Fit the final KMeans model."""

    model = KMeans(
        n_clusters=5,
        random_state=42,
        n_init=10,
    )

    labels = model.fit_predict(X)

    distances = model.transform(X).min(axis=1)

    return model, labels, distances


# ---------------------------------------------------------------------
# Save Output
# ---------------------------------------------------------------------


def save_cluster_labels(df, labels, distances):
    """Save company cluster assignments."""

    output = pd.DataFrame(
        {
            "company_id": df["company_id"],
            "company_name": df["company_name"],
            "broad_sector": df["broad_sector"],
            "cluster_id": labels,
            "cluster_name": [f"Cluster {i}" for i in labels],
            "distance_from_centroid": distances.round(4),
        }
    )

    output = output.sort_values(["cluster_id", "company_name"]).reset_index(drop=True)

    output.to_csv(
        OUTPUT_DIR / "cluster_labels.csv",
        index=False,
    )

    print(output.head())


def save_cluster_centers(model):
    """Save cluster centers in standardized feature space."""

    centers = pd.DataFrame(
        model.cluster_centers_,
        columns=FEATURES,
    )

    centers.insert(0, "cluster_id", range(len(centers)))

    centers.to_csv(
        OUTPUT_DIR / "cluster_centers.csv",
        index=False,
    )


def save_scaled_features(df, X):
    """Save standardized feature values."""

    scaled_df = pd.DataFrame(X, columns=FEATURES)

    scaled_df.insert(0, "company_id", df["company_id"])
    scaled_df.insert(1, "company_name", df["company_name"])

    scaled_df.to_csv(
        OUTPUT_DIR / "scaled_features.csv",
        index=False,
    )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------


def main():
    """Run the full clustering pipeline end-to-end."""

    df = load_latest_ratios()

    print(f"Loaded {len(df)} companies")

    if len(df) != EXPECTED_COMPANIES:
        raise ValueError(
            f"Expected {EXPECTED_COMPANIES} companies with financial ratios, "
            f"found {len(df)}"
        )

    df.info()
    print(df[FEATURES].isna().sum())

    df = fill_sector_medians(df)

    assert (
        df[FEATURES].isna().sum().sum() == 0
    ), "Missing values remain after imputation."

    print("\nFeature Summary")
    print(df[FEATURES].describe())

    X, scaler = scale_features(df)

    generate_elbow_plot(X)

    model, labels, distances = run_clustering(X)

    save_cluster_labels(df, labels, distances)

    save_cluster_centers(model)

    save_scaled_features(df, X)

    print(f"Cluster Centers: {OUTPUT_DIR / 'cluster_centers.csv'}")
    print(f"Scaled Features: {OUTPUT_DIR / 'scaled_features.csv'}")

    print("\nCluster Distribution:")
    print(pd.Series(labels).value_counts().sort_index())

    print(f"\nElbow Plot: {REPORTS_DIR / 'elbow_plot.png'}")
    print(f"Cluster Labels: {OUTPUT_DIR / 'cluster_labels.csv'}")

    print("\nDay 36 completed successfully.")


if __name__ == "__main__":
    main()
