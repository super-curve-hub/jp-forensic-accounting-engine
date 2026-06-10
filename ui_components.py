import streamlit as st
import pandas as pd


def pct_fmt(x, digits=1):
    return "NA" if pd.isna(x) else f"{x * 100:.{digits}f}%"


def ratio_fmt(x, digits=2):
    return "NA" if pd.isna(x) else f"{x:.{digits}f}"


def num_fmt(x, digits=1):
    return "NA" if pd.isna(x) else f"{x:.{digits}f}"


def inject_css():
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 0.1rem;
        }
        .sub-title {
            color: #666;
            font-size: 0.95rem;
            margin-bottom: 1.2rem;
        }
        .hero-card {
            border-radius: 24px;
            padding: 24px;
            margin: 12px 0 20px 0;
            background: linear-gradient(135deg, rgba(40,40,52,0.95), rgba(15,15,22,0.95));
            color: white;
            border: 1px solid rgba(255,255,255,0.10);
        }
        .metric-card {
            border: 1px solid rgba(49, 51, 63, 0.15);
            border-radius: 18px;
            padding: 18px 18px;
            background: rgba(255,255,255,0.65);
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            margin-bottom: 12px;
        }
        .metric-label {
            font-size: 0.78rem;
            color: #666;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 1.55rem;
            font-weight: 800;
            color: #111;
        }
        .small-note {
            font-size: 0.78rem;
            color: #777;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def page_title():
    st.markdown(
        '<div class="main-title">JP Forensic Accounting Engine</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">Japanese equity quality, ROIC, cash conversion and governance-aware screening dashboard</div>',
        unsafe_allow_html=True
    )


def hero_card(latest, wacc_pct):
    company = latest.get("Company", "NA")
    ticker = latest.get("Ticker", "NA")
    grade = latest.get("Grade", "NA")
    regime = latest.get("Regime", "NA")
    risk = ratio_fmt(latest.get("ForensicRiskScore"), 0)
    roic = pct_fmt(latest.get("ROIC_TTM"))
    spread = pct_fmt(latest.get("ROIC_WACC_Spread"))

    st.markdown(
        f"""
        <div class="hero-card">
            <div style="font-size:1.75rem;font-weight:800;margin-bottom:6px;">{company}</div>
            <div style="color:rgba(255,255,255,0.72);font-size:0.95rem;margin-bottom:14px;">
                {ticker} | WACC {wacc_pct:.1f}%
            </div>
            <div style="font-size:1.2rem;font-weight:800;">Grade {grade} — {regime}</div>
            <div style="margin-top:14px;display:flex;gap:22px;flex-wrap:wrap;">
                <div>ROIC<br><b style="font-size:1.35rem;">{roic}</b></div>
                <div>ROIC-WACC<br><b style="font-size:1.35rem;">{spread}</b></div>
                <div>Risk<br><b style="font-size:1.35rem;">{risk}</b></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def metric_card(label, value, note=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="small-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def metric_cards(latest):
    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "ROIC",
            pct_fmt(latest.get("ROIC_TTM")),
            "Return on invested capital"
        )

    with c2:
        metric_card(
            "ROIC-WACC",
            pct_fmt(latest.get("ROIC_WACC_Spread")),
            "Economic spread"
        )

    with c3:
        metric_card(
            "Risk",
            ratio_fmt(latest.get("ForensicRiskScore"), 0),
            "Lower is better"
        )

    c4, c5, c6 = st.columns(3)

    with c4:
        metric_card(
            "CFO / NI",
            ratio_fmt(latest.get("CFO_to_NI")),
            "Cash conversion"
        )

    with c5:
        metric_card(
            "FCF Margin",
            pct_fmt(latest.get("FCFMargin")),
            "Free cash flow margin"
        )

    with c6:
        metric_card(
            "PBR",
            ratio_fmt(latest.get("pbr")),
            "TSE reform pressure"
        )


def render_ranking_table(df):
    display_cols = [
        c
        for c in [
            "Ticker",
            "Company",
            "Sector",
            "EconomicScore",
            "ROIC",
            "ROIC-WACC",
            "FCFMargin",
            "CFO/NI",
            "Risk",
            "Quality",
            "PBR",
            "ROE",
            "Grade",
            "Regime",
            "Flags",
        ]
        if c in df.columns
    ]

    with st.expander(
        "Ranking Data",
        expanded=True
    ):
        st.dataframe(
            df[display_cols],
            use_container_width=True
        )
