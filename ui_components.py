def hero_card(latest, wacc_pct):

    company = latest.get("Company", "NA")
    ticker = latest.get("Ticker", "NA")
    grade = latest.get("Grade", "NA")
    regime = latest.get("Regime", "NA")

    sector = str(
        latest.get(
            "Sector",
            ""
        )
    ).lower()

    is_financial = (
        "bank" in sector
        or "financial" in sector
        or "insurance" in sector
        or "capital markets" in sector
    )

    risk = ratio_fmt(
        latest.get(
            "ForensicRiskScore"
        ),
        0
    )

    if is_financial:

        metric1_name = "ROE"
        metric1_value = pct_fmt(
            latest.get("roe")
        )

        metric2_name = "ROE-CoE"
        metric2_value = pct_fmt(
            latest.get(
                "ROE_EconomicSpread"
            )
        )

    else:

        metric1_name = "ROIC"
        metric1_value = pct_fmt(
            latest.get(
                "ROIC_TTM"
            )
        )

        metric2_name = "ROIC-WACC"
        metric2_value = pct_fmt(
            latest.get(
                "ROIC_WACC_Spread"
            )
        )

    st.markdown(
        f"""
        <div class="hero-card">

            <div style="font-size:1.75rem;
                        font-weight:800;
                        margin-bottom:6px;">
                {company}
            </div>

            <div style="
                color:rgba(255,255,255,0.72);
                font-size:0.95rem;
                margin-bottom:14px;
            ">
                {ticker}
            </div>

            <div style="
                font-size:1.2rem;
                font-weight:800;
            ">
                Grade {grade} — {regime}
            </div>

            <div style="
                margin-top:14px;
                display:flex;
                gap:22px;
                flex-wrap:wrap;
            ">

                <div>
                    {metric1_name}<br>
                    <b style="font-size:1.35rem;">
                        {metric1_value}
                    </b>
                </div>

                <div>
                    {metric2_name}<br>
                    <b style="font-size:1.35rem;">
                        {metric2_value}
                    </b>
                </div>

                <div>
                    Risk<br>
                    <b style="font-size:1.35rem;">
                        {risk}
                    </b>
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def metric_cards(latest):

    sector = str(
        latest.get(
            "Sector",
            ""
        )
    ).lower()

    is_financial = (
        "bank" in sector
        or "financial" in sector
        or "insurance" in sector
        or "capital markets" in sector
    )

    # =====================================
    # Financial Sector
    # =====================================

    if is_financial:

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(
                "ROE",
                pct_fmt(
                    latest.get("roe")
                ),
                "Return on equity"
            )

        with c2:
            metric_card(
                "ROE-CoE",
                pct_fmt(
                    latest.get(
                        "ROE_EconomicSpread"
                    )
                ),
                "Economic spread"
            )

        with c3:
            metric_card(
                "Risk",
                ratio_fmt(
                    latest.get(
                        "ForensicRiskScore"
                    ),
                    0
                ),
                "Lower is better"
            )

        c4, c5, c6 = st.columns(3)

        with c4:
            metric_card(
                "PBR",
                ratio_fmt(
                    latest.get("pbr")
                ),
                "Valuation"
            )

        with c5:
            metric_card(
                "Total Yield",
                pct_fmt(
                    latest.get(
                        "TotalYield"
                    )
                ),
                "Dividend + Buyback"
            )

        with c6:
            metric_card(
                "Economic Score",
                ratio_fmt(
                    latest.get(
                        "EconomicScore"
                    ),
                    0
                ),
                "Bank quality score"
            )

        return

    # =====================================
    # Non-Financial Sector
    # =====================================

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "ROIC",
            pct_fmt(
                latest.get(
                    "ROIC_TTM"
                )
            ),
            "Return on invested capital"
        )

    with c2:
        metric_card(
            "ROIC-WACC",
            pct_fmt(
                latest.get(
                    "ROIC_WACC_Spread"
                )
            ),
            "Economic spread"
        )

    with c3:
        metric_card(
            "Risk",
            ratio_fmt(
                latest.get(
                    "ForensicRiskScore"
                ),
                0
            ),
            "Lower is better"
        )

    c4, c5, c6 = st.columns(3)

    with c4:
        metric_card(
            "CFO / NI",
            ratio_fmt(
                latest.get(
                    "CFO_to_NI"
                )
            ),
            "Cash conversion"
        )

    with c5:
        metric_card(
            "FCF Margin",
            pct_fmt(
                latest.get(
                    "FCFMargin"
                )
            ),
            "Free cash flow margin"
        )

    with c6:
        metric_card(
            "PBR",
            ratio_fmt(
                latest.get("pbr")
            ),
            "TSE reform pressure"
        )
