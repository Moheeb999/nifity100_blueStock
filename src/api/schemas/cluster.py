from pydantic import BaseModel
from typing import List


class Cluster(BaseModel):
    company_id: str
    company_name: str
    broad_sector: str
    cluster_id: int
    cluster_name: str
    distance_from_centroid: float


class ClusterReport(BaseModel):
    cluster_id: int
    company_count: int
    cluster_name: str
    dominant_sector: str
    return_on_equity_pct: float
    debt_to_equity: float
    revenue_cagr_5yr: float
    operating_profit_margin_pct: float
    free_cash_flow_cr: float


class ClusterProfile(BaseModel):
    cluster_id: int
    feature: str
    mean_value: float


class ClusterSectorDistribution(BaseModel):
    cluster_id: int
    broad_sector: str
    company_count: int


class ClusterListResponse(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int
    data: List[Cluster]