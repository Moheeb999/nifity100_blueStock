import pandas as pd

# -------------------------------------------------------
# Winsorization (P10 / P90)
# -------------------------------------------------------


def winsorize(series):
    """
    Caps values at the 10th and 90th percentile.
    Prevents outliers from dominating scores.
    """

    s = series.copy()

    s = pd.to_numeric(s, errors="coerce")

    lower = s.quantile(0.10)
    upper = s.quantile(0.90)

    return s.clip(lower, upper)


# -------------------------------------------------------
# Normalization
# -------------------------------------------------------


def normalize(series, reverse=False):
    """
    Converts a metric into a 0-100 score.
    """

    s = winsorize(series)

    s = s.fillna(s.median())

    minimum = s.min()
    maximum = s.max()

    if minimum == maximum:
        return pd.Series(50, index=s.index)

    score = ((s - minimum) / (maximum - minimum)) * 100

    if reverse:
        score = 100 - score

    return score.clip(0, 100)


# -------------------------------------------------------
# Sector Relative Normalization
# -------------------------------------------------------


def sector_normalize(df, column, reverse=False):
    """
    Normalize one metric independently inside each sector.
    """

    result = pd.Series(index=df.index, dtype=float)

    for sector in df["broad_sector"].dropna().unique():

        mask = df["broad_sector"] == sector

        result.loc[mask] = normalize(df.loc[mask, column], reverse=reverse)

    return result


# -------------------------------------------------------
# Composite Score
# -------------------------------------------------------


def compute_composite_score(df):
    """Compute the composite quality score for each company."""

    df = df.copy()

    # -------------------------
    # Profitability (35%)
    # -------------------------

    roe_score = sector_normalize(df, "return_on_equity_pct")

    npm_score = sector_normalize(df, "net_profit_margin_pct")

    opm_score = sector_normalize(df, "operating_profit_margin_pct")

    profitability = roe_score * 0.15 + npm_score * 0.10 + opm_score * 0.10

    # -------------------------
    # Cash Quality (30%)
    # -------------------------

    fcf_score = sector_normalize(df, "free_cash_flow_cr")

    cfo_score = sector_normalize(df, "cash_from_operations_cr")

    positive_fcf = (df["free_cash_flow_cr"] > 0).astype(int) * 100

    cash_quality = fcf_score * 0.15 + cfo_score * 0.10 + positive_fcf * 0.05

    # -------------------------
    # Growth (20%)
    # -------------------------

    revenue_score = sector_normalize(df, "revenue_cagr_5yr")

    pat_score = sector_normalize(df, "pat_cagr_5yr")

    growth = revenue_score * 0.10 + pat_score * 0.10

    # -------------------------
    # Leverage (15%)
    # -------------------------

    debt_score = sector_normalize(df, "debt_to_equity", reverse=True)

    icr_score = sector_normalize(df, "interest_coverage")

    leverage = debt_score * 0.10 + icr_score * 0.05

    # -------------------------
    # Final Composite Score
    # -------------------------

    df["composite_quality_score"] = (
        profitability + cash_quality + growth + leverage
    ).round(2)

    return df
