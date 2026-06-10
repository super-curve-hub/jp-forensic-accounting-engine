import streamlit as st
import pandas as pd


def pct_fmt(x, digits=1):
    return "NA" if pd.isna(x) else f"{x * 100:.{digits}f}%"


def ratio_fmt(x, digits=2):
    return "NA" if pd.isna(x) else f"{x:.{digits}f}"


def inject_css():

    st.markdown(
        """
        <style>

        .main-title{
            font-size:2.2rem;
            font-weight:800;
            margin-bottom:0.2rem;
        }

        .sub-title{
            color:#666;
            margin-bottom:1rem;
        }

        .metric-card{
            border:1px solid rgba(0,0,0,0.08);
            border-radius:18px;
            padding:18px;
            margin-bottom:12px;
            background:white;
        }

        .metric-label{
            font-size:0.8rem;
            color:#666;
        }

        .metric-value{
            font-size:1.6rem;
            font-weight:700;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def page_title():

    st.markdown(
        '<div class="main-title">JP Forensic Accounting Engine</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sub-title">ROIC / Economic Profit / Forensic Quality Dashboard</div>',
        unsafe_allow_html=True,
    )


def metric_card(
    label,
    value,
    note=""
):

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div style="font-size:0.8rem;color:#777;">
                {note}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero_card(
    latest,
    wacc_pct
):

    company = latest.get(
        "Company",
        "NA"
    )

    ticker = latest.get(
        "Ticker",
        "NA"
    )

    grade = latest.get(
        "Grade",
        "NA"
    )

    regime = latest.get(
        "Regime",
        "NA"
    )

    roic = pct_fmt(
        latest.get(
            "ROIC_TTM"
        )
    )

    spread = pct_fmt(
        latest.get(
            "ROIC_WACC_Spread"
        )
    )

    risk = ratio_fmt(
        latest.get(
            "ForensicRiskScore"
        ),
        0
    )

    st.subheader(
        company
    )

    st.caption(
        f"{ticker} | WACC {wacc_pct:.1f}%"
    )

    st.markdown(
        f"## Grade {grade} — {regime}"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "ROIC",
            roic
        )

    with c2:

        st.metric(
            "ROIC-WACC",
            spread
        )

    with c3:

        st.metric(
            "Risk",
            risk
        )


def metric_cards(
    latest
):

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
                latest.get(
                    "pbr"
                )
            ),
            "TSE reform pressure"
        )


def render_ranking_table(
    df
):

    display_cols = [
        c
        for c in [
            "Ticker",
            "Company",
            "Sector",
            "EconomicScore",
            "ROIC",
            "ROIC-WACC",
            "PBR",
            "FCFMargin",
            "CFO/NI",
            "Risk",
            "Quality",
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
            width="stretch"
        )


print(
    "UI COMPONENTS LOADED"
)
