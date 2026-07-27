import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from src.analytics.clustering import OUTPUT_DIR
from src.api.schemas.cluster import (
    ClusterListResponse,
    ClusterProfile,
    ClusterReport,
    ClusterSectorDistribution,
)

router = APIRouter()


def read_csv(filename: str) -> pd.DataFrame:
    """
    Read a CSV file from the analytics output directory.
    """

    path = OUTPUT_DIR / filename

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"{filename} not found.",
        )

    return pd.read_csv(path)


@router.get(
    "/clusters",
    response_model=ClusterListResponse,
    summary="Get clustered companies",
    description="Returns clustered companies with optional filtering.",
)
def get_clusters(
    cluster_id: int | None = Query(default=None, description="Filter by cluster ID"),
    sector: str | None = Query(default=None, description="Filter by broad sector"),
    search: str | None = Query(
        default=None, description="Search by company ID or company name"
    ),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of records per page"
    ),
    sort_by: str | None = Query(default=None, description="Column to sort by"),
    order: str = Query(
        default="asc", pattern="^(asc|desc)$", description="Sort order: asc or desc"
    ),
):
    """Return clustered companies with filtering and pagination."""
    df = read_csv("cluster_labels.csv")

    if cluster_id is not None:
        df = df[df["cluster_id"] == cluster_id]

    if sector is not None:
        df = df[df["broad_sector"].str.lower() == sector.lower()]

    if search is not None:
        search = search.lower()

        df = df[
            df["company_id"].str.lower().str.contains(search, na=False)
            | df["company_name"].str.lower().str.contains(search, na=False)
        ]

    if sort_by is not None:
        if sort_by not in df.columns:
            raise HTTPException(
                status_code=400, detail=f"Invalid sort column: {sort_by}"
            )

        df = df.sort_values(by=sort_by, ascending=(order == "asc"))

    total_records = len(df)

    total_pages = (
        (total_records + page_size - 1) // page_size if total_records > 0 else 0
    )

    start = (page - 1) * page_size
    end = start + page_size

    paged_df = df.iloc[start:end]

    return {
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": total_pages,
        "data": paged_df.to_dict(orient="records"),
    }


@router.get(
    "/clusters/report",
    response_model=list[ClusterReport],
    summary="Cluster summary report",
    description="Returns aggregated statistics for each cluster.",
)
def get_cluster_report():
    """Return the cluster summary report."""
    df = read_csv("cluster_report.csv")
    return df.to_dict(orient="records")


@router.get(
    "/clusters/profiles",
    response_model=list[ClusterProfile],
    summary="Cluster feature profiles",
    description="Returns the average value of each feature for every cluster.",
)
def get_cluster_profiles():
    """Return feature profiles for each cluster."""
    df = read_csv("cluster_profiles.csv")
    return df.to_dict(orient="records")


@router.get(
    "/clusters/sectors",
    response_model=list[ClusterSectorDistribution],
    summary="Cluster sector distribution",
    description="Returns the sector-wise company distribution for every cluster.",
)
def get_cluster_sector_distribution():
    """Return sector distribution for each cluster."""
    df = read_csv("cluster_sector_distribution.csv")
    return df.to_dict(orient="records")
