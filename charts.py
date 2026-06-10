import pandas as pd
import plotly.express as px
import streamlit as st


# =====================================================
# Trend Charts
# =====================================================

def render_trend_charts(result):

    df = result["df"].copy()

    # ==========================================
    # ROIC
    # ==========================================

    if (
        "ROIC_TTM" in df.columns
        and
        df["ROIC_TTM"].notna().any()
    ):

        tmp = df.copy()

        tmp["ROIC_pct"] = (
            tmp["ROIC_TTM"] * 100
        )

        fig = px.line(
            tmp,
            x="date",
            y="ROIC_pct",
            title="ROIC Trend"
        )

        fig.update_layout(
            height=450
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # ==========================================
    # Accrual Ratio
    # ==========================================

    if (
        "AccrualRatio" in df.columns
        and
        df["AccrualRatio"].notna().any()
    ):

        tmp = df.copy()

        tmp["Accrual_pct"] = (
            tmp["AccrualRatio"] * 100
        )

        fig = px.line(
            tmp,
            x="date",
            y="Accrual_pct",
            title="Accrual Ratio Trend"
        )

        fig.update_layout(
            height=450
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # ==========================================
    # Forensic Risk
    # ==========================================

    if (
        "ForensicRiskScore" in df.columns
        and
        df["ForensicRiskScore"].notna().any()
    ):

        fig = px.bar(
            df,
            x="date",
            y="ForensicRiskScore",
            title="Forensic Risk Trend"
        )

        fig.update_layout(
            height=450
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # ==========================================
    # FCF Margin
    # ==========================================

    if (
        "FCFMargin" in df.columns
        and
        df["FCFMargin"].notna().any()
    ):

        tmp = df.copy()

        tmp["FCFMargin_pct"] = (
            tmp["FCFMargin"] * 100
        )

        fig = px.line(
            tmp,
            x="date",
            y="FCFMargin_pct",
            title="FCF Margin Trend"
        )

        fig.update_layout(
            height=450
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )


# =====================================================
# Bubble Size
# =====================================================

def _bubble_size(plot_df):

    if (
        "EconomicScore" in plot_df.columns
        and
        plot_df["EconomicScore"].notna().any()
    ):

        return (
            plot_df["EconomicScore"]
            .fillna(1)
            .clip(lower=1)
            ** 0.5
        )

    if (
        "Quality" in plot_df.columns
        and
        plot_df["Quality"].notna().any()
    ):

        return (
            plot_df["Quality"]
            .fillna(1)
            .clip(lower=1)
            ** 0.5
        )

    return pd.Series(
        [10] * len(plot_df),
        index=plot_df.index
    )


# =====================================================
# Hover Columns
# =====================================================

def _build_hover_cols(plot_df):

    hover_cols = {}

    percent_cols = [

        "ROIC",

        "ROIC-WACC",

        "FCFMargin",

        "BuybackYield",

        "DividendYieldProxy",
    ]

    number_cols = [

        "Risk",

        "EconomicScore",

        "Quality",

        "PBR",

        "CFO/NI",
    ]

    for col in percent_cols:

        if col in plot_df.columns:
            hover_cols[col] = ":.1%"

    for col in number_cols:

        if col in plot_df.columns:
            hover_cols[col] = ":.1f"

    return hover_cols


# =====================================================
# Compare Scatter
# =====================================================

def compare_scatter(compare_df):

    if compare_df.empty:
        return px.scatter()

    plot_df = compare_df.copy()

    if "Risk" not in plot_df.columns:
        plot_df["Risk"] = 50

    if "EconomicScore" not in plot_df.columns:
        plot_df["EconomicScore"] = 50

    plot_df["EconomicScore"] = (
        pd.to_numeric(
            plot_df["EconomicScore"],
            errors="coerce"
        )
        .fillna(50)
    )

    plot_df["Risk"] = (
        pd.to_numeric(
            plot_df["Risk"],
            errors="coerce"
        )
        .fillna(50)
    )

    plot_df["BubbleSize"] = (
        _bubble_size(plot_df)
    )

    hover_cols = (
        _build_hover_cols(plot_df)
    )

    fig = px.scatter(
        plot_df,
        x="Risk",
        y="EconomicScore",
        size="BubbleSize",
        size_max=50,
        color="EconomicScore",
        color_continuous_scale="RdYlGn",
        hover_name="Ticker",
        hover_data=hover_cols,
        title="Economic Score vs Risk"
    )

    fig.update_layout(
        height=750,
        showlegend=False,
        hovermode="closest",
        xaxis_title="Forensic Risk",
        yaxis_title="Economic Score"
    )

    return fig


# =====================================================
# Screening Scatter
# =====================================================

def screen_scatter(screen_df):

    if screen_df.empty:
        return px.scatter()

    plot_df = screen_df.copy()

    if "Risk" not in plot_df.columns:
        plot_df["Risk"] = 50

    if "EconomicScore" not in plot_df.columns:
        plot_df["EconomicScore"] = 50

    plot_df["EconomicScore"] = (
        pd.to_numeric(
            plot_df["EconomicScore"],
            errors="coerce"
        )
        .fillna(50)
    )

    plot_df["Risk"] = (
        pd.to_numeric(
            plot_df["Risk"],
            errors="coerce"
        )
        .fillna(50)
    )

    plot_df["BubbleSize"] = (
        _bubble_size(plot_df)
    )

    hover_cols = (
        _build_hover_cols(plot_df)
    )

    fig = px.scatter(
        plot_df,
        x="Risk",
        y="EconomicScore",
        size="BubbleSize",
        size_max=45,
        color="EconomicScore",
        color_continuous_scale="RdYlGn",
        hover_name="Ticker",
        hover_data=hover_cols,
        title="Screened Candidates"
    )

    fig.update_layout(
        height=700,
        showlegend=False,
        hovermode="closest",
        xaxis_title="Forensic Risk",
        yaxis_title="Economic Score"
    )

    return fig


print("CHARTS LOADED")
