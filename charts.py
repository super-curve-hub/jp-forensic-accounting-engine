import plotly.express as px
import streamlit as st
import pandas as pd


def render_trend_charts(result):

    df = result["df"].copy()

    # =====================================
    # ROIC / ROE
    # =====================================

    if "ROIC_TTM" in df.columns:

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

    elif "roe" in df.columns:

        tmp = df.copy()

        tmp["ROE_pct"] = (
            tmp["roe"] * 100
        )

        fig = px.line(
            tmp,
            x="date",
            y="ROE_pct",
            title="ROE Trend"
        )

        fig.update_layout(
            height=450
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # =====================================
    # Accrual
    # =====================================

    if "AccrualRatio" in df.columns:

        tmp = df.copy()

        tmp["Accrual_pct"] = (
            tmp["AccrualRatio"] * 100
        )

        fig = px.line(
            tmp,
            x="date",
            y="Accrual_pct",
            title="Accrual Trend"
        )

        fig.update_layout(
            height=450
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # =====================================
    # Risk
    # =====================================

    if "ForensicRiskScore" in df.columns:

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

    # =====================================
    # FCF Margin
    # =====================================

    if "FCFMargin" in df.columns:

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


def _build_hover_cols(plot_df):

    hover_cols = {}

    pct_cols = [
        "ROIC",
        "ROIC-WACC",
        "ROE",
        "ROE-CoE",
        "TotalYield",
        "FCFMargin",
    ]

    num_cols = [
        "Risk",
        "EconomicScore",
        "Quality",
        "PBR",
    ]

    for col in pct_cols:

        if col in plot_df.columns:
            hover_cols[col] = ":.1%"

    for col in num_cols:

        if col in plot_df.columns:
            hover_cols[col] = ":.1f"

    return hover_cols


def compare_scatter(compare_df):

    if compare_df.empty:
        return px.scatter()

    plot_df = compare_df.copy()

    if "Risk" not in plot_df.columns:
        plot_df["Risk"] = 50

    if "EconomicScore" not in plot_df.columns:

        if "Quality" in plot_df.columns:
            plot_df["EconomicScore"] = (
                plot_df["Quality"]
            )
        else:
            plot_df["EconomicScore"] = 50

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
        xaxis_title="Forensic Risk",
        yaxis_title="Economic Score",
        coloraxis_colorbar_title="Economic Score",
        showlegend=False,
        hovermode="closest"
    )

    return fig


def screen_scatter(screen_df):

    if screen_df.empty:
        return px.scatter()

    plot_df = screen_df.copy()

    if "Risk" not in plot_df.columns:
        plot_df["Risk"] = 50

    if "EconomicScore" not in plot_df.columns:

        if "Quality" in plot_df.columns:
            plot_df["EconomicScore"] = (
                plot_df["Quality"]
            )
        else:
            plot_df["EconomicScore"] = 50

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
        xaxis_title="Forensic Risk",
        yaxis_title="Economic Score",
        coloraxis_colorbar_title="Economic Score",
        showlegend=False,
        hovermode="closest"
    )

    return fig
