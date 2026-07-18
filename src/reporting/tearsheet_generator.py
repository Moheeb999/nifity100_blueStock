"""
tearsheet_generator.py

Sprint 5 - Professional Company Tearsheet Generator

Generates institutional-style PDF reports for every company in the
Nifty 100 Analytics Platform.

Data Sources
------------
SQLite
    companies
    market_cap
    financial_ratios
    sectors

CSV
    pros_cons_generated.csv
    cashflow_intelligence.csv

Output
------
output/tearsheets/<Company>.pdf
"""

from __future__ import annotations

import argparse
import logging
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

PROS_CONS_CSV = PROJECT_ROOT / "output" / "pros_cons_generated.csv"

CASHFLOW_CSV = PROJECT_ROOT / "output" / "cashflow_intelligence.csv"

OUTPUT_DIR = PROJECT_ROOT / "output" / "tearsheets"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("tearsheet_generator")


# ---------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------

@dataclass
class CompanyTearsheetData:

    company_id: int
    company_name: str

    about_company: Optional[str] = None
    website: Optional[str] = None

    # Company information

    broad_sector: Optional[str] = None
    sub_sector: Optional[str] = None
    market_cap_category: Optional[str] = None

    # Market Metrics

    market_cap_crore: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    dividend_yield_pct: Optional[float] = None

    # Profitability

    roe_percentage: Optional[float] = None
    roce_percentage: Optional[float] = None

    net_profit_margin_pct: Optional[float] = None
    operating_profit_margin_pct: Optional[float] = None

    # Financial Health

    debt_to_equity: Optional[float] = None
    interest_coverage: Optional[float] = None
    asset_turnover: Optional[float] = None

    # Shareholder Metrics

    earnings_per_share: Optional[float] = None
    book_value_per_share: Optional[float] = None

    # Growth

    revenue_cagr_5yr: Optional[float] = None
    pat_cagr_5yr: Optional[float] = None
    eps_cagr_5yr: Optional[float] = None

    # Quality

    composite_quality_score: Optional[float] = None

    # Lists

    pros: list[str] = field(default_factory=list)

    cons: list[str] = field(default_factory=list)

    cashflow_insights: list[tuple[str, str]] = field(default_factory=list)


# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------

def load_companies(
    conn: sqlite3.Connection,
    company_id: Optional[int] = None,
) -> pd.DataFrame:

    query = """
    SELECT

        c.id,
        c.company_name,
        c.about_company,
        c.website,

        c.roe_percentage,
        c.roce_percentage,

        m.market_cap_crore,
        m.pe_ratio,
        m.pb_ratio,
        m.ev_ebitda,
        m.dividend_yield_pct,

        s.broad_sector,
        s.sub_sector,
        s.market_cap_category,

        f.net_profit_margin_pct,
        f.operating_profit_margin_pct,
        f.debt_to_equity,
        f.interest_coverage,
        f.asset_turnover,

        f.earnings_per_share,
        f.book_value_per_share,

        f.revenue_cagr_5yr,
        f.pat_cagr_5yr,
        f.eps_cagr_5yr,

        f.composite_quality_score

    FROM companies c

    LEFT JOIN market_cap m

        ON m.company_id = c.id

       AND m.year = (

            SELECT MAX(year)

            FROM market_cap

            WHERE company_id = c.id

       )

    LEFT JOIN financial_ratios f

        ON f.company_id = c.id

       AND f.year = (

            SELECT MAX(year)

            FROM financial_ratios

            WHERE company_id = c.id

       )

    LEFT JOIN sectors s

        ON s.company_id = c.id
    """

    params = ()

    if company_id is not None:

        query += " WHERE c.id=?"

        params = (company_id,)

    query += " ORDER BY c.id"

    return pd.read_sql_query(query, conn, params=params)


# ---------------------------------------------------------------------
# CSV Loading
# ---------------------------------------------------------------------

def _load_csv_checked(
    path: Path,
    required_cols: list[str],
    label: str,
) -> pd.DataFrame:

    if not path.exists():

        logger.warning("%s not found : %s", label, path)

        return pd.DataFrame(columns=required_cols)

    df = pd.read_csv(path)

    missing = [c for c in required_cols if c not in df.columns]

    if missing:

        logger.error(
            "%s missing columns %s",
            label,
            missing,
        )

        return pd.DataFrame(columns=required_cols)

    return df


def load_pros_cons(path: Path):

    return _load_csv_checked(
        path,
        ["company_id", "type", "text"],
        "Pros / Cons",
    )


def load_cashflow_intelligence(path: Path):

    return _load_csv_checked(
        path,
        ["company_id", "category", "insight"],
        "Cashflow",
    )


# ---------------------------------------------------------------------
# Build Company Object
# ---------------------------------------------------------------------

def build_company_data(

    companies_df: pd.DataFrame,

    pros_cons_df: pd.DataFrame,

    cashflow_df: pd.DataFrame,

) -> list[CompanyTearsheetData]:

    records = []

    for row in companies_df.itertuples(index=False):

        company = CompanyTearsheetData(

            company_id=row.id,

            company_name=row.company_name,

            about_company=row.about_company,

            website=row.website,

            broad_sector=row.broad_sector,

            sub_sector=row.sub_sector,

            market_cap_category=row.market_cap_category,

            market_cap_crore=row.market_cap_crore,

            pe_ratio=row.pe_ratio,

            pb_ratio=row.pb_ratio,

            ev_ebitda=row.ev_ebitda,

            dividend_yield_pct=row.dividend_yield_pct,

            roe_percentage=row.roe_percentage,

            roce_percentage=row.roce_percentage,

            net_profit_margin_pct=row.net_profit_margin_pct,

            operating_profit_margin_pct=row.operating_profit_margin_pct,

            debt_to_equity=row.debt_to_equity,

            interest_coverage=row.interest_coverage,

            asset_turnover=row.asset_turnover,

            earnings_per_share=row.earnings_per_share,

            book_value_per_share=row.book_value_per_share,

            revenue_cagr_5yr=row.revenue_cagr_5yr,

            pat_cagr_5yr=row.pat_cagr_5yr,

            eps_cagr_5yr=row.eps_cagr_5yr,

            composite_quality_score=row.composite_quality_score,

        )

        if not pros_cons_df.empty:

            pc = pros_cons_df[pros_cons_df.company_id == row.id]

            company.pros = (
                pc[pc.type.str.lower() == "pro"]["text"].tolist()
            )

            company.cons = (
                pc[pc.type.str.lower() == "con"]["text"].tolist()
            )

        if not cashflow_df.empty:

            cf = cashflow_df[cashflow_df.company_id == row.id]

            company.cashflow_insights = list(
                zip(
                    cf["category"],
                    cf["insight"],
                )
            )

        records.append(company)

    return records

# ============================
# END OF PART 1
# ============================

# ---------------------------------------------------------------------
# Formatting Helpers
# ---------------------------------------------------------------------

def fmt_pct(value) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:.1f}%"


def fmt_num(value, decimals: int = 2) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def fmt_crore(value) -> str:
    if pd.isna(value):
        return "N/A"
    return f"₹{value:,.0f} Cr"


def fmt_currency(value) -> str:
    if pd.isna(value):
        return "N/A"
    return f"₹{value:,.2f}"


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._ -]+", "", name).strip()
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned or "company"


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

def draw_footer(canvas, doc):
    canvas.saveState()

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)

    canvas.drawString(
        doc.leftMargin,
        10 * mm,
        "Generated by Nifty 100 Analytics Platform"
    )

    canvas.drawRightString(
        A4[0] - doc.rightMargin,
        10 * mm,
        f"Page {canvas.getPageNumber()}"
    )

    canvas.restoreState()


# ---------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------

def _build_styles():

    base = getSampleStyleSheet()

    return {

        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontSize=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=4,
        ),

        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=12,
        ),

        "section": ParagraphStyle(
            "Section",
            parent=base["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#1E3A8A"),
            spaceBefore=14,
            spaceAfter=8,
        ),

        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=10,
            leading=15,
        ),

        "metric_label": ParagraphStyle(
            "MetricLabel",
            parent=base["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#475569"),
        ),

        "metric_value": ParagraphStyle(
            "MetricValue",
            parent=base["Normal"],
            fontSize=10,
            textColor=colors.black,
        ),

        "pro": ParagraphStyle(
            "Pro",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#15803D"),
        ),

        "con": ParagraphStyle(
            "Con",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#B91C1C"),
        ),

        "cashflow": ParagraphStyle(
            "Cashflow",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#1D4ED8"),
        ),

        "empty": ParagraphStyle(
            "Empty",
            parent=base["Italic"],
            textColor=colors.grey,
        ),
    }


# ---------------------------------------------------------------------
# KPI Table
# ---------------------------------------------------------------------

def _kpi_table(data: CompanyTearsheetData, styles):

    rows = [

        [
            "Market Cap",
            fmt_crore(data.market_cap_crore),

            "ROE",
            fmt_pct(data.roe_percentage),

            "Revenue CAGR",
            fmt_pct(data.revenue_cagr_5yr),
        ],

        [
            "P/E",
            fmt_num(data.pe_ratio),

            "ROCE",
            fmt_pct(data.roce_percentage),

            "PAT CAGR",
            fmt_pct(data.pat_cagr_5yr),
        ],

        [
            "P/B",
            fmt_num(data.pb_ratio),

            "Net Margin",
            fmt_pct(data.net_profit_margin_pct),

            "EPS CAGR",
            fmt_pct(data.eps_cagr_5yr),
        ],

        [
            "EV/EBITDA",
            fmt_num(data.ev_ebitda),

            "Operating Margin",
            fmt_pct(data.operating_profit_margin_pct),

            "Quality Score",
            fmt_num(data.composite_quality_score),
        ],

        [
            "Dividend Yield",
            fmt_pct(data.dividend_yield_pct),

            "Debt / Equity",
            fmt_num(data.debt_to_equity),

            "Interest Coverage",
            fmt_num(data.interest_coverage),
        ],

        [
            "Asset Turnover",
            fmt_num(data.asset_turnover),

            "EPS",
            fmt_currency(data.earnings_per_share),

            "Book Value",
            fmt_currency(data.book_value_per_share),
        ],
    ]

    table = Table(
        rows,
        colWidths=[
            32 * mm,
            28 * mm,
            32 * mm,
            28 * mm,
            36 * mm,
            28 * mm,
        ],
    )

    table.setStyle(

        TableStyle(

            [

                ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),

                ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),

                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2FF")),
                ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#EEF2FF")),
                ("BACKGROUND", (4, 0), (4, -1), colors.HexColor("#EEF2FF")),

                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),

                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("FONTNAME", (4, 0), (4, -1), "Helvetica-Bold"),

                ("FONTSIZE", (0, 0), (-1, -1), 9),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),

                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

            ]

        )

    )

    return table


# ---------------------------------------------------------------------
# Bullet Lists
# ---------------------------------------------------------------------

def _bullet_list(items, style, empty_style, empty_text):

    if not items:
        return Paragraph(empty_text, empty_style)

    return ListFlowable(

        [

            ListItem(
                Paragraph(item, style),
                leftIndent=8,
            )

            for item in items

        ],

        bulletType="bullet",

        leftIndent=15,

    )

# =========================
# END OF PART 2
# =========================

# ---------------------------------------------------------------------
# PDF Generation
# ---------------------------------------------------------------------

def build_pdf(data: CompanyTearsheetData, output_dir: Path) -> Path:

    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = output_dir / f"{safe_filename(data.company_name)}.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        topMargin=15 * mm,
        bottomMargin=18 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        title=f"{data.company_name} Tearsheet",
    )

    styles = _build_styles()

    story = []

    # -------------------------------------------------------
    # HEADER
    # -------------------------------------------------------

    story.append(
        Paragraph(data.company_name, styles["title"])
    )

    subtitle = []

    for value in [
        data.broad_sector,
        data.sub_sector,
        data.market_cap_category,
        data.website,
    ]:
        if pd.notna(value) and str(value).strip():
            subtitle.append(str(value))

    story.append(
    Paragraph(
        " | ".join(subtitle),
        styles["subtitle"],
    )
)

    story.append(Spacer(1, 5))

    # -------------------------------------------------------
    # OVERVIEW
    # -------------------------------------------------------

    story.append(
        Paragraph(
            "Company Overview",
            styles["section"],
        )
    )

    story.append(
        Paragraph(
            data.about_company
            if data.about_company
            else "No company description available.",
            styles["body"],
        )
    )

    story.append(Spacer(1, 10))

    # -------------------------------------------------------
    # KPI
    # -------------------------------------------------------

    story.append(
        Paragraph(
            "Financial Snapshot",
            styles["section"],
        )
    )

    story.append(
        _kpi_table(
            data,
            styles,
        )
    )

    story.append(Spacer(1, 12))

    # -------------------------------------------------------
    # PROS
    # -------------------------------------------------------

    story.append(
        Paragraph(
            "Investment Strengths",
            styles["section"],
        )
    )

    story.append(

        _bullet_list(

            data.pros,

            styles["pro"],

            styles["empty"],

            "No strengths available."

        )

    )

    story.append(Spacer(1, 10))

    # -------------------------------------------------------
    # CONS
    # -------------------------------------------------------

    story.append(

        Paragraph(

            "Investment Risks",

            styles["section"],

        )

    )

    story.append(

        _bullet_list(

            data.cons,

            styles["con"],

            styles["empty"],

            "No risks available."

        )

    )

    story.append(Spacer(1, 10))

    # -------------------------------------------------------
    # CASHFLOW
    # -------------------------------------------------------

    story.append(

        Paragraph(

            "Cash Flow Intelligence",

            styles["section"],

        )

    )

    if data.cashflow_insights:

        cf = []

        for category, insight in data.cashflow_insights:

            cf.append(

                Paragraph(

                    f"<b>{category}</b>",

                    styles["cashflow"],

                )

            )

            cf.append(

                Paragraph(

                    insight,

                    styles["body"],

                )

            )

            cf.append(

                Spacer(1, 5)

            )

        story.append(

            KeepTogether(cf)

        )

    else:

        story.append(

            Paragraph(

                "No cash flow intelligence available.",

                styles["empty"],

            )

        )

    # -------------------------------------------------------
    # BUILD PDF
    # -------------------------------------------------------

    doc.build(

        story,

        onFirstPage=draw_footer,

        onLaterPages=draw_footer,

    )

    return pdf_path

# ---------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------

def generate_tearsheets(
    db_path: Path = DB_PATH,
    pros_cons_path: Path = PROS_CONS_CSV,
    cashflow_path: Path = CASHFLOW_CSV,
    output_dir: Path = OUTPUT_DIR,
    company_id: Optional[int] = None,
    limit: Optional[int] = None,
) -> list[Path]:

    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found: {db_path}"
        )

    logger.info("Connecting to database: %s", db_path)

    conn = sqlite3.connect(str(db_path))

    try:

        companies_df = load_companies(
            conn,
            company_id=company_id,
        )

    finally:

        conn.close()

    if companies_df.empty:

        logger.warning("No companies found.")

        return []

    if limit is not None:

        companies_df = companies_df.head(limit)

    pros_cons_df = load_pros_cons(
        pros_cons_path
    )

    cashflow_df = load_cashflow_intelligence(
        cashflow_path
    )

    company_records = build_company_data(
        companies_df,
        pros_cons_df,
        cashflow_df,
    )

    generated = []

    for company in company_records:

        try:

            pdf = build_pdf(
                company,
                output_dir,
            )

            generated.append(pdf)

            logger.info(
                "Generated: %s",
                pdf.name,
            )

        except Exception:

            logger.exception(
                "Failed for %s (%s)",
                company.company_name,
                company.company_id,
            )

    logger.info(
        "Done. %d/%d tearsheets generated.",
        len(generated),
        len(company_records),
    )

    return generated


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def parse_args():

    parser = argparse.ArgumentParser(
        description="Generate Company Tearsheets"
    )

    parser.add_argument(
        "--company-id",
        type=int,
        default=None,
        help="Generate one company only.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Generate first N companies.",
    )

    parser.add_argument(
        "--db-path",
        default=str(DB_PATH),
    )

    parser.add_argument(
        "--pros-cons-csv",
        default=str(PROS_CONS_CSV),
    )

    parser.add_argument(
        "--cashflow-csv",
        default=str(CASHFLOW_CSV),
    )

    parser.add_argument(
        "--output-dir",
        default=str(OUTPUT_DIR),
    )

    return parser.parse_args()


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():

    args = parse_args()

    generate_tearsheets(

        db_path=Path(args.db_path),

        pros_cons_path=Path(
            args.pros_cons_csv
        ),

        cashflow_path=Path(
            args.cashflow_csv
        ),

        output_dir=Path(
            args.output_dir
        ),

        company_id=args.company_id,

        limit=args.limit,

    )


if __name__ == "__main__":
    main()