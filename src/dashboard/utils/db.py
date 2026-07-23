import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "db/nifty100.db"


@st.cache_data(ttl=600)
def get_companies():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            id,
            company_name
        FROM companies
        ORDER BY company_name
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):

    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
    """

    params = [ticker]

    if year is not None:
        query += " AND year = ?"
        params.append(year)

    query += " ORDER BY year"

    df = pd.read_sql(
        query,
        conn,
        params=params
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_pl(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[ticker]
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_bs(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[ticker]
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_cf(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[ticker]
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_sectors():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM sectors
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_peers(group_name):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM peer_groups
        WHERE peer_group_name = ?
        """,
        conn,
        params=[group_name]
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_valuation(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM market_cap
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[ticker]
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_home_kpis(year):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            fr.company_id,
            fr.return_on_equity_pct,
            fr.debt_to_equity,
            fr.revenue_cagr_5yr,
            mc.pe_ratio
        FROM financial_ratios fr
        LEFT JOIN market_cap mc
            ON fr.company_id = mc.company_id
           AND fr.year = mc.year
        WHERE fr.year = ?
        """,
        conn,
        params=[year]
    )

    conn.close()

    return {
        "avg_roe": round(df["return_on_equity_pct"].mean(), 2),
        "median_pe": round(df["pe_ratio"].median(), 2),
        "median_de": round(df["debt_to_equity"].median(), 2),
        "total_companies": int(df["company_id"].nunique()),
        "median_revenue_cagr": round(
            df["revenue_cagr_5yr"].median(),
            2
        ),
        "debt_free_companies": int(
            (df["debt_to_equity"] <= 0.10).sum()
        )
    }


@st.cache_data(ttl=600)
def get_sector_breakdown():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            broad_sector,
            COUNT(*) AS companies
        FROM sectors
        GROUP BY broad_sector
        ORDER BY companies DESC
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_top_quality_companies(year):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            fr.company_id,
            c.company_name,
            s.broad_sector,
            fr.composite_quality_score
        FROM financial_ratios fr
        JOIN companies c
            ON fr.company_id = c.id
        LEFT JOIN sectors s
            ON fr.company_id = s.company_id
        WHERE fr.year = ?
        ORDER BY fr.composite_quality_score DESC
        LIMIT 5
        """,
        conn,
        params=[year]
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def search_companies():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            id,
            company_name
        FROM companies
        ORDER BY company_name
        """,
        conn
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_company_profile(ticker):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
    c.id,
    c.company_name,
    c.about_company,
    s.broad_sector,
    s.sub_sector,
    c.website,
    c.nse_profile,
    c.bse_profile
    FROM companies c
    LEFT JOIN sectors s
    ON c.id = s.company_id
    WHERE c.id = ?
    """

    df = pd.read_sql(
        query,
        conn,
        params=[ticker]
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_latest_ratios(ticker):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        fr.return_on_equity_pct,
        fr.return_on_capital_employed_pct,
        fr.net_profit_margin_pct,
        fr.debt_to_equity,
        fr.revenue_cagr_5yr,
        fr.free_cash_flow_cr,
        fr.year
    FROM financial_ratios fr
    WHERE fr.company_id = ?
    ORDER BY fr.year DESC
    LIMIT 1
    """

    df = pd.read_sql(
        query,
        conn,
        params=[ticker]
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_pros_cons(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            pros,
            cons
        FROM prosandcons
        WHERE company_id=?
        """,
        conn,
        params=[ticker]
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_profit_loss_history(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            year,
            sales,
            net_profit
        FROM profitandloss
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=[ticker]
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_ratio_history(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            year,
            return_on_equity_pct,
            return_on_capital_employed_pct
        FROM financial_ratios
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=[ticker]
    )

    conn.close()

    return df
@st.cache_data(ttl=600)
def get_screener_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        fr.company_id,
        c.company_name,
        s.broad_sector,
        fr.return_on_equity_pct,
        fr.return_on_capital_employed_pct,
        fr.net_profit_margin_pct,
        fr.operating_profit_margin_pct,
        fr.debt_to_equity,
        fr.free_cash_flow_cr,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.interest_coverage,
        fr.composite_quality_score,
        mc.pe_ratio,
        mc.pb_ratio,
        mc.ev_ebitda,
        mc.dividend_yield_pct
    FROM financial_ratios fr

    LEFT JOIN companies c
        ON fr.company_id = c.id

    LEFT JOIN sectors s
        ON fr.company_id = s.company_id

    LEFT JOIN market_cap mc
        ON fr.company_id = mc.company_id
       AND fr.year = mc.year

    WHERE fr.year = (
        SELECT MAX(year)
        FROM financial_ratios
    )

    ORDER BY fr.company_id
    """

    df = pd.read_sql(
        query,
        conn
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_peer_groups():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT DISTINCT peer_group_name
        FROM peer_groups
        ORDER BY peer_group_name
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_peer_companies(group_name):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            pg.company_id,
            c.company_name
        FROM peer_groups pg
        JOIN companies c
            ON pg.company_id = c.id
        WHERE pg.peer_group_name = ?
        ORDER BY c.company_name
        """,
        conn,
        params=[group_name]
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_peer_metrics(group_name):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        pg.company_id,
        c.company_name,
        fr.return_on_equity_pct,
        fr.return_on_capital_employed_pct,
        fr.net_profit_margin_pct,
        fr.operating_profit_margin_pct,
        fr.debt_to_equity,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.composite_quality_score
    FROM peer_groups pg

    JOIN financial_ratios fr
        ON pg.company_id = fr.company_id

    JOIN companies c
        ON pg.company_id = c.id

    WHERE pg.peer_group_name = ?
      AND fr.year = (
          SELECT MAX(year)
          FROM financial_ratios
      )
    """

    df = pd.read_sql(
        query,
        conn,
        params=[group_name]
    )

    conn.close()
    
    return df

@st.cache_data(ttl=600)
def get_trend_data(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            year,
            revenue_cagr_5yr,
            pat_cagr_5yr,
            return_on_equity_pct,
            return_on_capital_employed_pct,
            net_profit_margin_pct,
            operating_profit_margin_pct,
            debt_to_equity,
            interest_coverage,
            free_cash_flow_cr
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[ticker]
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_sector_analysis():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            mc.market_cap_crore,
            pl.sales,
            fr.return_on_equity_pct
        FROM companies c

        JOIN sectors s
            ON c.id = s.company_id

        JOIN market_cap mc
            ON c.id = mc.company_id

        JOIN financial_ratios fr
            ON c.id = fr.company_id
           AND fr.year = mc.year

        JOIN profitandloss pl
            ON c.id = pl.company_id
           AND pl.year = mc.year

        WHERE mc.year = (
            SELECT MAX(year)
            FROM market_cap
        )
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_capital_map():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM capital_allocation
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_reports():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM annual_reports
        ORDER BY company_id, year DESC
        """,
        conn
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_capital_allocation_data():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            fr.company_id,
            c.company_name,
            s.broad_sector,
            fr.return_on_equity_pct,
            fr.debt_to_equity,
            fr.free_cash_flow_cr,
            fr.revenue_cagr_5yr
        FROM financial_ratios fr
        JOIN companies c
            ON fr.company_id = c.id
        LEFT JOIN sectors s
            ON fr.company_id = s.company_id
        WHERE fr.year = (
            SELECT MAX(year)
            FROM financial_ratios
        )
        """,
        conn
    )

    conn.close()

    return df