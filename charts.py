import plotly.express as px
import streamlit as st


def render_trend_charts(result):
    df = result["df"].copy()

    if "ROIC_TTM" in df.columns:
        tmp = df.copy()
        tmp["ROIC_pct"] = tmp["ROIC_TTM"] * 100

        fig = px.line(
            tmp,
            x="date",
            y="ROIC_pct",
            title="ROIC Trend"
        )
        fig.update_layout(height=450)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if "AccrualRatio" in df.columns:
        tmp = df.copy()
        tmp["Accrual_pct"] = tmp["AccrualRatio"] * 100

        fig = px.line(
            tmp,
            x="date",
            y="Accrual_pct",
            title="Accrual Trend"
        )
        fig.update_layout(height=450)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if "ForensicRiskScore" in df.columns:
        fig = px.bar(
            df,
            x="date",
            y="ForensicRiskScore",
            title="Forensic Risk Trend"
        )
        fig.update_layout(height=450)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if "FCFMargin" in df.columns:
        tmp = df.copy()
        tmp["FCFMargin_pct"] = tmp["FCFMargin"] * 100

        fig = px.line(
            tmp,
            x="date",
            y="FCFMargin_pct",
            title="FCF Margin Trend"
        )
        fig.update_layout(height=450)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


def _bubble_size(plot_df):
    if "EconomicScore" in plot_df.columns:
        return (
            plot_df["EconomicScore"]
            .fillna(1)
            .clip(lower=1)
            ** 0.5
        )

    return (
        plot_df["Quality"]
        .fillna(1)
        .clip(lower=1)
        ** 0.5
    )


def compare_scatter(compare_df):
    if compare_df.empty:
        return px.scatter()

    plot_df = compare_df.copy()
    plot_df["BubbleSize"] = _bubble_size(plot_df)

    fig = px.scatter(
        plot_df,
        x="Risk",
        y="EconomicScore",
        size="BubbleSize",
        size_max=50,
        color="EconomicScore",
        color_continuous_scale="RdYlGn",
        hover_name="Ticker",
        hover_data={
            "ROIC": ":.1%",
            "ROIC-WACC": ":.1%",
            "Risk": ":.1f",
            "EconomicScore": ":.1f",
            "Quality": ":.0f",
            "PBR": ":.2f",
            "ROE": ":.1%",
        },
        title="Economic Profit vs Risk"
    )

    fig.update_layout(
        height=750,
        xaxis_title="Forensic Risk",
        yaxis_title="Economic Score",
        coloraxis_colorbar_title="Economic Score",
        showlegend=False,
        hovermode="closest"
    )

    fig.update_xaxes(
        zeroline=True,
        zerolinewidth=1
    )

    fig.update_yaxes(
        zeroline=True,
        zerolinewidth=1
    )

    return fig


def screen_scatter(screen_df):
    if screen_df.empty:
        return px.scatter()

    plot_df = screen_df.copy()
    plot_df["BubbleSize"] = _bubble_size(plot_df)

    fig = px.scatter(
        plot_df,
        x="Risk",
        y="EconomicScore",
        size="BubbleSize",
        size_max=45,
        color="EconomicScore",
        color_continuous_scale="RdYlGn",
        hover_name="Ticker",
        hover_data={
            "ROIC": ":.1%",
            "ROIC-WACC": ":.1%",
            "Risk": ":.1f",
            "EconomicScore": ":.1f",
            "Quality": ":.0f",
            "PBR": ":.2f",
            "ROE": ":.1%",
        },
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

    fig.update_xaxes(
        zeroline=True,
        zerolinewidth=1
    )

    fig.update_yaxes(
        zeroline=True,
        zerolinewidth=1
    )

    return fig
