from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.analytics.portfolio_analytics import PortfolioAnalytics
from src.reporting.portfolio_charts import PortfolioCharts


class PortfolioReport:

    def __init__(self, db_path: str):
        self.analytics = PortfolioAnalytics(db_path)
        self.styles = getSampleStyleSheet()
        self.primary_color = colors.HexColor("#1E3A8A")
        self.success_color = colors.HexColor("#15803D")
        self.warning_color = colors.HexColor("#EA580C")
        self.danger_color = colors.HexColor("#B91C1C")
        self.background_color = colors.whitesmoke
        self.border_color = colors.grey
        self.title_style = ParagraphStyle(
            "CustomTitle",
            parent=self.styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            textColor=self.primary_color,
            alignment=1,
            spaceAfter=18,
        )

        self.heading_style = ParagraphStyle(
            "CustomHeading",
            parent=self.styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=self.primary_color,
            spaceBefore=10,
            spaceAfter=12,
        )

        self.subheading_style = ParagraphStyle(
            "CustomSubHeading",
            parent=self.styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=self.primary_color,
            spaceBefore=8,
            spaceAfter=8,
        )

        self.body_style = ParagraphStyle(
            "CustomBody",
            parent=self.styles["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            spaceAfter=6,
        )

        self.small_style = ParagraphStyle(
            "SmallText",
            parent=self.styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.grey,
        )

        self.standard_table_style = TableStyle(
            [
                # Header
                ("BACKGROUND", (0, 0), (-1, 0), self.primary_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                # Body
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                # Borders
                ("GRID", (0, 0), (-1, -1), 0.4, self.border_color),
                ("BOX", (0, 0), (-1, -1), 1.0, self.primary_color),
                # Alignment
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                # Padding
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )

    def generate(self, portfolio_csv: str, output_pdf: str):

        self.portfolio = self.analytics.load_portfolio(portfolio_csv)

        self.total_cost = self.analytics.calculate_portfolio_cost(self.portfolio)
        self.current_value = self.analytics.calculate_current_value(self.portfolio)
        self.profit_loss = self.analytics.calculate_profit_loss(self.portfolio)
        self.return_pct = self.analytics.calculate_return_percentage(self.portfolio)

        self.quality_score = self.analytics.calculate_weighted_quality_score(
            self.portfolio
        )
        self.health_score = self.analytics.calculate_portfolio_health_score(
            self.portfolio
        )

        self.weighted_pe = self.analytics.calculate_weighted_pe_ratio(self.portfolio)
        self.weighted_pb = self.analytics.calculate_weighted_pb_ratio(self.portfolio)
        self.weighted_roe = self.analytics.calculate_weighted_roe(self.portfolio)

        self.diversification = self.analytics.calculate_diversification_score(
            self.portfolio
        )

        self.concentration = self.analytics.calculate_concentration_risk(self.portfolio)

        self.sectors = self.analytics.calculate_sector_allocation(self.portfolio)
        # -----------------------
        # Generate Charts
        # -----------------------

        self.sector_chart = "output/charts/sector_allocation.png"
        self.valuation_chart = "output/charts/valuation_metrics.png"

        PortfolioCharts.sector_allocation_chart(
            self.sectors,
            self.sector_chart,
        )

        PortfolioCharts.valuation_chart(
            self.weighted_pe,
            self.weighted_pb,
            self.weighted_roe,
            self.valuation_chart,
        )

        Path(output_pdf).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        doc = SimpleDocTemplate(
            output_pdf,
            rightMargin=36,
            leftMargin=36,
            topMargin=50,
            bottomMargin=40,
        )

        story = []

        self.add_cover_page(story)
        self.add_title(story)
        self.add_dashboard(story)
        self.add_top_bottom_performers(story)
        self.add_risk_analysis(story)
        self.add_scorecard(story)
        self.add_summary(story)
        self.add_health(story)
        self.add_valuation(story)
        self.add_sector_table(story)
        self.add_charts(story)
        self.add_holdings_table(story)
        self.add_insights(story)
        self.add_recommendation(story)

        doc.build(
            story,
            onFirstPage=self.add_page_number,
            onLaterPages=self.add_page_number,
        )
        print(f"Generated: {output_pdf}")

    def add_cover_page(self, story):

        story.append(Spacer(1, 80))

        banner = Table(
            [["NIFTY100 PORTFOLIO ANALYTICS"]],
            colWidths=[500],
        )

        banner.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), self.primary_color),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 18),
                    ("TOPPADDING", (0, 0), (-1, -1), 14),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
                ]
            )
        )

        story.append(banner)
        story.append(Spacer(1, 35))

        story.append(
            Paragraph(
                "NIFTY100",
                self.title_style,
            )
        )

        story.append(
            Paragraph(
                "Portfolio Analytics Report",
                self.heading_style,
            )
        )

        story.append(
            Paragraph(
                "Portfolio Performance • Risk Analysis • Investment Insights",
                self.small_style,
            )
        )

        story.append(Spacer(1, 25))

        story.append(Spacer(1, 40))

        story.append(
            Paragraph(
                "<b>Prepared By</b>",
                self.subheading_style,
            )
        )

        story.append(
            Paragraph(
                "Nifty100 Analytics Platform",
                self.body_style,
            )
        )

        story.append(Spacer(1, 25))

        story.append(
            Paragraph(
                f"<b>Generated On:</b> {datetime.now():%d %B %Y}",
                self.body_style,
            )
        )

        story.append(Spacer(1, 30))

        overview = [
            ["Investment", f"₹{self.total_cost:,.2f}"],
            ["Current Value", f"₹{self.current_value:,.2f}"],
            ["Overall Return", f"{self.return_pct:.2f}%"],
        ]

        table = Table(
            overview,
            colWidths=[220, 180],
        )

        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )

        story.append(table)

        story.append(PageBreak())

    # ======================================================
    # SECTOR TABLE
    # ======================================================
    def add_title(self, story):

        story.append(
            Paragraph(
                "Nifty100 Portfolio Analytics Report",
                self.title_style,
            )
        )

        story.append(
            Paragraph(
                f"Generated on : {datetime.now():%d %B %Y %I:%M %p}",
                self.small_style,
            )
        )

        story.append(Spacer(1, 25))

    def add_dashboard(self, story):

        story.append(
            Paragraph(
                "Executive Dashboard",
                self.heading_style,
            )
        )

        card1 = Table(
            [
                ["Portfolio Value"],
                [f"₹{self.current_value:,.2f}"],
            ],
            colWidths=[240],
        )

        card2 = Table(
            [
                ["Investment"],
                [f"₹{self.total_cost:,.2f}"],
            ],
            colWidths=[240],
        )

        card3 = Table(
            [
                ["Profit / Loss"],
                [f"₹{self.profit_loss:,.2f}"],
            ],
            colWidths=[240],
        )

        card4 = Table(
            [
                ["Return"],
                [f"{self.return_pct:.2f}%"],
            ],
            colWidths=[240],
        )
        for card in [card1, card2, card3, card4]:

            card.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), self.primary_color),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("BOX", (0, 0), (-1, -1), 1.5, self.primary_color),
                        ("GRID", (0, 0), (-1, -1), 0.4, self.border_color),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 13),
                        ("FONTSIZE", (0, 1), (-1, -1), 18),
                        ("TOPPADDING", (0, 1), (-1, -1), 20),
                        ("BOTTOMPADDING", (0, 1), (-1, -1), 20),
                    ]
                )
            )
        if self.profit_loss >= 0:
            card3.setStyle(TableStyle([("TEXTCOLOR", (0, 1), (-1, -1), colors.green)]))
        else:
            card3.setStyle(TableStyle([("TEXTCOLOR", (0, 1), (-1, -1), colors.red)]))
        if self.return_pct >= 0:
            card4.setStyle(TableStyle([("TEXTCOLOR", (0, 1), (-1, -1), colors.green)]))
        else:
            card4.setStyle(TableStyle([("TEXTCOLOR", (0, 1), (-1, -1), colors.red)]))
        cards = Table(
            [
                [card1, card2],
                [card3, card4],
            ],
            colWidths=[250, 250],
            rowHeights=[95, 95],
        )

        cards.setStyle(
            TableStyle(
                [
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )

        story.append(cards)
        story.append(Spacer(1, 24))
        story.append(Spacer(1, 15))
        if self.health_score >= 80:
            status = "🟢 Excellent"

        elif self.health_score >= 60:
            status = "🟡 Good"

        else:
            status = "🔴 Needs Improvement"

        story.append(
            Paragraph(
                f"<b>Portfolio Status:</b> {status}",
                self.subheading_style,
            )
        )

        story.append(Spacer(1, 15))

        chart_table = Table(
            [
                [
                    Image(
                        self.sector_chart,
                        width=230,
                        height=230,
                    ),
                    Image(
                        self.valuation_chart,
                        width=230,
                        height=170,
                    ),
                ]
            ],
            colWidths=[245, 245],
        )

        story.append(chart_table)
        story.append(Spacer(1, 20))
        story.append(
            Paragraph(
                "Executive Summary",
                self.subheading_style,
            )
        )

        summary_data = [
            ["Metric", "Value"],
            ["Portfolio Health", f"{self.health_score}/100"],
            ["Expected Return", f"{self.return_pct:.2f}%"],
            ["Diversification", f"{self.diversification}/100"],
            ["Concentration", self.concentration],
        ]

        summary_table = Table(
            summary_data,
            colWidths=[230, 180],
        )

        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), self.primary_color),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.4, self.border_color),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ]
            )
        )

        story.append(summary_table)

        story.append(Spacer(1, 24))

        divider = Table([[""]], colWidths=[500])

        divider.setStyle(
            TableStyle([("LINEBELOW", (0, 0), (-1, -1), 1, self.primary_color)])
        )

        story.append(Spacer(1, 20))
        story.append(divider)
        story.append(Spacer(1, 15))

    def add_top_bottom_performers(self, story):

        holdings = []

        for stock in self.portfolio:

            holding = stock["holding"]
            company = stock["company"]

            investment = holding.shares * holding.buy_price
            value = holding.shares * company["close_price"]

            return_pct = ((value - investment) / investment) * 100 if investment else 0

            holdings.append(
                (
                    holding.ticker,
                    return_pct,
                )
            )

        holdings.sort(
            key=lambda x: x[1],
            reverse=True,
        )

        top = holdings[:3]
        bottom = holdings[-3:]
        top_data = [["Top Performers", "Return %"]]
        for ticker, ret in top:
            top_data.append([ticker, f"{ret:.2f}%"])

        bottom_data = [["Bottom Performers", "Return %"]]
        for ticker, ret in bottom:
            bottom_data.append([ticker, f"{ret:.2f}%"])

        top_table = Table(top_data, colWidths=[150, 90])
        bottom_table = Table(bottom_data, colWidths=[150, 90])
        for table in [top_table, bottom_table]:

            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), self.primary_color),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("GRID", (0, 0), (-1, -1), 0.5, self.border_color),
                        ("BACKGROUND", (0, 1), (-1, -1), self.background_color),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ]
                )
            )
            story.append(
                Table(
                    [[top_table, bottom_table]],
                    colWidths=[250, 250],
                )
            )

            story.append(Spacer(1, 24))

    def add_risk_analysis(self, story):

        story.append(
            Paragraph(
                "Portfolio Risk Analysis",
                self.heading_style,
            )
        )

        data = [
            ["Metric", "Status"],
            ["Concentration Risk", self.concentration],
            ["Diversification Score", f"{self.diversification}/100"],
            ["Portfolio Health", f"{self.health_score}/100"],
            ["Quality Score", f"{self.quality_score}/100"],
        ]

        table = Table(
            data,
            colWidths=[250, 180],
        )

        table.setStyle(self.standard_table_style)
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ]
            )
        )
        for row in range(1, len(data)):
            if row % 2 == 0:
                table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, row),
                                (-1, row),
                                colors.HexColor("#F8FAFC"),
                            )
                        ]
                    )
                )
        story.append(table)
        story.append(Spacer(1, 24))

    def add_scorecard(self, story):

        story.append(
            Paragraph(
                "Portfolio Scorecard",
                self.heading_style,
            )
        )

        def stars(score):

            if score >= 90:
                return "★★★★★"
            elif score >= 80:
                return "★★★★☆"
            elif score >= 70:
                return "★★★☆☆"
            elif score >= 60:
                return "★★☆☆☆"
            else:
                return "★☆☆☆☆"

        valuation_score = max(0, 100 - min(self.weighted_pe, 100))

        data = [
            ["Category", "Rating"],
            ["Portfolio Health", stars(self.health_score)],
            ["Quality", stars(self.quality_score)],
            ["Diversification", stars(self.diversification)],
            ["Valuation", stars(valuation_score)],
        ]

        table = Table(
            data,
            colWidths=[220, 180],
        )

        table.setStyle(self.standard_table_style)
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ]
            )
        )
        for row in range(1, len(data)):
            if row % 2 == 0:
                table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, row),
                                (-1, row),
                                colors.HexColor("#F8FAFC"),
                            )
                        ]
                    )
                )

        story.append(table)
        story.append(Spacer(1, 24))

    def add_summary(self, story):

        story.append(
            Paragraph(
                "Portfolio Summary",
                self.heading_style,
            )
        )

        data = [
            ["Metric", "Value"],
            ["Investment Cost", f"₹{self.total_cost:,.2f}"],
            ["Current Value", f"₹{self.current_value:,.2f}"],
            ["Profit / Loss", f"₹{self.profit_loss:,.2f}"],
            ["Return", f"{self.return_pct:.2f}%"],
        ]

        table = Table(data, colWidths=[250, 180])

        table.setStyle(self.standard_table_style)
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ]
            )
        )
        for row in range(1, len(data)):
            if row % 2 == 0:
                table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, row),
                                (-1, row),
                                colors.HexColor("#F8FAFC"),
                            )
                        ]
                    )
                )

        profit_loss_color = (
            self.success_color if self.profit_loss >= 0 else self.danger_color
        )
        return_color = self.success_color if self.return_pct >= 0 else self.danger_color

        table.setStyle(
            TableStyle(
                [
                    ("TEXTCOLOR", (1, 3), (1, 3), profit_loss_color),
                    ("TEXTCOLOR", (1, 4), (1, 4), return_color),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 24))

    def add_health(self, story):

        story.append(
            Paragraph(
                "Portfolio Health",
                self.heading_style,
            )
        )

        data = [
            ["Metric", "Value"],
            ["Health Score", f"{self.health_score}/100"],
            ["Quality Score", f"{self.quality_score}/100"],
            ["Diversification", f"{self.diversification}/100"],
            ["Concentration", self.concentration],
        ]

        table = Table(data, colWidths=[250, 180])

        table.setStyle(self.standard_table_style)
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ]
            )
        )
        for row in range(1, len(data)):
            if row % 2 == 0:
                table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, row),
                                (-1, row),
                                colors.HexColor("#F8FAFC"),
                            )
                        ]
                    )
                )

        if self.health_score >= 80:
            health_color = self.success_color
        elif self.health_score >= 60:
            health_color = self.warning_color
        else:
            health_color = self.danger_color

        table.setStyle(
            TableStyle(
                [
                    ("TEXTCOLOR", (1, 1), (1, 1), health_color),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 24))

    def add_valuation(self, story):

        story.append(
            Paragraph(
                "Portfolio Valuation",
                self.heading_style,
            )
        )

        data = [
            ["Metric", "Value"],
            ["Weighted PE", f"{self.weighted_pe:.2f}"],
            ["Weighted PB", f"{self.weighted_pb:.2f}"],
            ["Weighted ROE", f"{self.weighted_roe:.2f}%"],
        ]

        table = Table(data, colWidths=[250, 180])

        table.setStyle(self.standard_table_style)
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ]
            )
        )
        for row in range(1, len(data)):
            if row % 2 == 0:
                table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, row),
                                (-1, row),
                                colors.HexColor("#F8FAFC"),
                            )
                        ]
                    )
                )

        pe_color = self.warning_color if self.weighted_pe > 35 else self.success_color

        table.setStyle(
            TableStyle(
                [
                    ("TEXTCOLOR", (1, 1), (1, 1), pe_color),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 24))

    def add_sector_table(self, story):

        story.append(
            Paragraph(
                "Sector Allocation",
                self.heading_style,
            )
        )

        data = [["Sector", "Allocation", "Exposure"]]

        for sector, allocation in self.sectors.items():

            if allocation >= 30:
                exposure = "High"

            elif allocation >= 15:
                exposure = "Moderate"

            else:
                exposure = "Low"

            data.append(
                [
                    sector,
                    f"{allocation:.2f}%",
                    exposure,
                ]
            )

        table = Table(
            data,
            colWidths=[220, 120, 120],
        )

        table.setStyle(self.standard_table_style)
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ]
            )
        )

        for row in range(1, len(data)):

            exposure = data[row][2]

            if exposure == "High":
                color = colors.red

            elif exposure == "Moderate":
                color = colors.orange

            else:
                color = colors.green

            table.setStyle(
                TableStyle(
                    [
                        ("TEXTCOLOR", (2, row), (2, row), color),
                        ("FONTNAME", (2, row), (2, row), "Helvetica-Bold"),
                    ]
                )
            )
        for row in range(1, len(data)):
            if row % 2 == 0:
                table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, row),
                                (-1, row),
                                colors.HexColor("#F8FAFC"),
                            )
                        ]
                    )
                )

        story.append(table)
        story.append(Spacer(1, 24))

    # ======================================================
    # CHARTS
    # ======================================================

    def add_charts(self, story):

        story.append(
            Paragraph(
                "Sector Allocation Chart",
                self.heading_style,
            )
        )

        story.append(
            Image(
                self.sector_chart,
                width=300,
                height=300,
            )
        )

        story.append(Spacer(1, 20))

        story.append(
            Paragraph(
                "Portfolio Valuation Chart",
                self.heading_style,
            )
        )

        story.append(
            Image(
                self.valuation_chart,
                width=380,
                height=250,
            )
        )

        story.append(Spacer(1, 24))

    # ======================================================
    # HOLDINGS TABLE
    # ======================================================

    def add_holdings_table(self, story):

        story.append(
            Paragraph(
                "Portfolio Holdings",
                self.heading_style,
            )
        )

        data = [
            [
                "Ticker",
                "Company",
                "Sector",
                "Shares",
                "Buy",
                "Current",
                "Investment",
                "Value",
                "P/L",
                "Return %",
            ]
        ]

        for stock in self.portfolio:

            holding = stock["holding"]
            company = stock["company"]

            investment = holding.shares * holding.buy_price
            value = holding.shares * company["close_price"]
            profit_loss = value - investment
            return_pct = (profit_loss / investment) * 100 if investment else 0

            data.append(
                [
                    holding.ticker,
                    company["company_name"],
                    company["broad_sector"],
                    holding.shares,
                    f"₹{holding.buy_price:.2f}",
                    f"₹{company['close_price']:.2f}",
                    f"₹{investment:,.2f}",
                    f"₹{value:,.2f}",
                    f"₹{profit_loss:,.2f}",
                    f"{return_pct:.2f}%",
                ]
            )

        table = Table(
            data,
            colWidths=[
                45,  # Ticker
                110,  # Company
                75,  # Sector
                40,  # Shares
                55,  # Buy
                55,  # Current
                70,  # Investment
                70,  # Value
                65,  # P/L
                55,  # Return %
            ],
            repeatRows=1,
        )

        table.setStyle(self.standard_table_style)
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (1, 1), (2, -1), "LEFT"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 1), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ]
            )
        )

        # Zebra striping
        for row_num in range(1, len(data)):

            if row_num % 2 == 0:
                table.setStyle(
                    TableStyle(
                        [("BACKGROUND", (0, row_num), (-1, row_num), colors.whitesmoke)]
                    )
                )
        # Color Profit/Loss and Return % columns
        for row_num in range(1, len(data)):

            profit_loss = float(data[row_num][8].replace("₹", "").replace(",", ""))

            color = colors.green if profit_loss >= 0 else colors.red

            table.setStyle(
                TableStyle(
                    [
                        ("TEXTCOLOR", (8, row_num), (8, row_num), color),
                        ("TEXTCOLOR", (9, row_num), (9, row_num), color),
                    ]
                )
            )

        story.append(table)
        story.append(Spacer(1, 24))

    # ======================================================
    # INSIGHTS
    # ======================================================

    def add_insights(self, story):

        story.append(
            Paragraph(
                "Investment Insights",
                self.heading_style,
            )
        )

        insights = []

        if self.health_score >= 80:
            insights.append("✓ Portfolio health is excellent.")
        elif self.health_score >= 60:
            insights.append("• Portfolio health is good.")
        else:
            insights.append("⚠ Portfolio health needs improvement.")

        if self.concentration == "High":
            insights.append(
                "⚠ High sector concentration. Consider Healthcare, Industrials and Automobile stocks."
            )

        elif self.concentration == "Medium":
            insights.append("• Moderate concentration risk.")

        else:
            insights.append("✓ Portfolio is well diversified.")

        if self.weighted_roe >= 20:
            insights.append("✓ Portfolio companies have excellent profitability.")

        if self.weighted_pe > 35:
            insights.append("⚠ Portfolio valuation appears expensive.")

        for text in insights:

            story.append(
                Paragraph(
                    text,
                    self.body_style,
                )
            )

        story.append(Spacer(1, 24))

    # ======================================================
    # RECOMMENDATION
    # ======================================================

    def add_recommendation(self, story):

        story.append(
            Paragraph(
                "Portfolio Conclusion",
                self.heading_style,
            )
        )

        # --------------------------------------------------
        # Step 4.1 — Rating Badges
        # --------------------------------------------------

        health_badge = (
            "🟢 Excellent"
            if self.health_score >= 80
            else ("🟡 Good" if self.health_score >= 60 else "🔴 Poor")
        )

        quality_badge = (
            "🟢 Excellent"
            if self.quality_score >= 80
            else ("🟡 Good" if self.quality_score >= 60 else "🔴 Poor")
        )

        diversification_badge = (
            "🟢 Good"
            if self.diversification >= 70
            else ("🟡 Average" if self.diversification >= 50 else "🔴 Weak")
        )

        risk_badge = {"Low": "🟢 Low", "Medium": "🟡 Medium", "High": "🔴 High"}.get(
            self.concentration, self.concentration
        )

        # --------------------------------------------------
        # Step 4.2 — Portfolio Rating Card
        # --------------------------------------------------

        rating_data = [
            ["Metric", "Status"],
            ["Portfolio Health", health_badge],
            ["Quality", quality_badge],
            ["Diversification", diversification_badge],
            ["Risk", risk_badge],
        ]

        rating_table = Table(rating_data, colWidths=[240, 180])

        rating_table.setStyle(self.standard_table_style)

        story.append(rating_table)
        story.append(Spacer(1, 20))

        # --------------------------------------------------
        # Step 4.3 — Strengths Panel
        # --------------------------------------------------

        story.append(
            Paragraph(
                "<b>✔ Strengths</b>",
                self.subheading_style,
            )
        )

        strengths = []

        if self.health_score >= 80:
            strengths.append("Excellent portfolio health.")

        if self.quality_score >= 80:
            strengths.append("High-quality fundamentally strong companies.")

        if self.weighted_roe >= 20:
            strengths.append("Strong profitability.")

        if self.diversification >= 70:
            strengths.append("Good diversification.")

        if not strengths:
            strengths.append("Portfolio has room for improvement.")

        for item in strengths:
            story.append(Paragraph(f"✓ {item}", self.body_style))
            story.append(Spacer(1, 8))

        story.append(Spacer(1, 10))

        # --------------------------------------------------
        # Step 4.4 — Weaknesses Panel
        # --------------------------------------------------

        story.append(
            Paragraph(
                "<b>⚠ Weaknesses</b>",
                self.subheading_style,
            )
        )

        weaknesses = []

        if self.concentration == "High":
            weaknesses.append("High sector concentration.")

        if self.weighted_pe > 35:
            weaknesses.append("Portfolio valuation appears expensive.")

        if self.diversification < 60:
            weaknesses.append("Diversification can be improved.")

        if not weaknesses:
            weaknesses.append("No significant weaknesses identified.")

        for item in weaknesses:
            story.append(Paragraph(f"⚠ {item}", self.body_style))
            story.append(Spacer(1, 8))

        story.append(Spacer(1, 10))

        # --------------------------------------------------
        # Step 4.5 — Recommended Actions Panel
        # --------------------------------------------------

        story.append(
            Paragraph(
                "<b>Recommended Actions</b>",
                self.subheading_style,
            )
        )

        actions = []

        if self.concentration == "High":
            actions.append("Increase Healthcare allocation.")
            actions.append("Add Industrials or Capital Goods.")

        if self.weighted_pe > 35:
            actions.append("Avoid adding highly overvalued stocks.")

        actions.append("Review portfolio quarterly.")
        actions.append("Continue long-term investing.")

        for item in actions:
            story.append(Paragraph(f"➡ {item}", self.body_style))

        story.append(Spacer(1, 15))

        # --------------------------------------------------
        # Step 4.6 — Recommendation Card
        # --------------------------------------------------

        story.append(
            Paragraph(
                "<b>Overall Recommendation</b>",
                self.subheading_style,
            )
        )

        overall = (self.health_score + self.quality_score + self.diversification) / 3

        if overall >= 90:
            verdict = "★★★★★ Outstanding"

        elif overall >= 80:
            verdict = "★★★★☆ Very Good"

        elif overall >= 70:
            verdict = "★★★☆☆ Good"

        elif overall >= 60:
            verdict = "★★☆☆☆ Average"

        else:
            verdict = "★☆☆☆☆ Needs Improvement"

        recommendation = [
            ["Overall Rating", verdict],
            [
                "Recommendation",
                "Continue Holding" if overall >= 80 else "Review Portfolio",
            ],
        ]

        recommendation_table = Table(recommendation, colWidths=[200, 250])

        recommendation_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), self.primary_color),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, self.border_color),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ]
            )
        )

        story.append(recommendation_table)

        # --------------------------------------------------
        # Step 4.7 — Executive Comment
        # --------------------------------------------------

        if overall >= 90:
            comment = (
                "The portfolio demonstrates outstanding "
                "fundamental quality with excellent "
                "long-term investment potential."
            )

        elif overall >= 80:
            comment = (
                "The portfolio is fundamentally strong "
                "with good diversification and healthy "
                "growth characteristics."
            )

        elif overall >= 70:
            comment = (
                "The portfolio is reasonably balanced "
                "but there are opportunities for "
                "improvement."
            )

        else:
            comment = (
                "The portfolio requires significant "
                "rebalancing to improve quality and "
                "risk profile."
            )

        story.append(Spacer(1, 12))

        story.append(Paragraph(comment, self.body_style))

        story.append(Spacer(1, 20))

        # --------------------------------------------------
        # Step 4.8 — Bottom Divider
        # --------------------------------------------------

        divider = Table([[""]], colWidths=[500])

        divider.setStyle(
            TableStyle([("LINEABOVE", (0, 0), (-1, -1), 1, self.primary_color)])
        )

        story.append(Spacer(1, 20))
        story.append(divider)

    # ======================================================
    # FOOTER
    # ======================================================

    def add_footer(self, story):

        story.append(
            Paragraph(
                "<font size='9' color='grey'>Generated by Nifty100 Analytics Platform</font>",
                self.small_style,
            )
        )

    def add_page_number(self, canvas, doc):

        canvas.saveState()

        # Header
        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(self.primary_color)
        canvas.drawString(
            40,
            820,
            "Nifty100 Portfolio Analytics Report",
        )

        canvas.setStrokeColor(self.border_color)
        canvas.setLineWidth(0.5)
        canvas.line(40, 815, 555, 815)

        # Footer
        canvas.setStrokeColor(self.border_color)
        canvas.setLineWidth(0.5)
        canvas.line(40, 32, 555, 32)

        canvas.setFillColor(colors.grey)
        canvas.setFont("Helvetica", 9)

        canvas.drawString(
            40,
            18,
            "Generated by Nifty100 Analytics Platform",
        )

        canvas.drawRightString(
            555,
            18,
            f"Page {doc.page}",
        )

        canvas.restoreState()


if __name__ == "__main__":

    report = PortfolioReport("db/nifty100.db")

    report.generate(
        "data/raw/sample_portfolio.csv",
        "output/portfolio_report.pdf",
    )
