import streamlit as st

from engine import load_financial_data, run_jp_forensic_engine
from charts import (
    render_trend_charts,
    compare_scatter,
    screen_scatter,
)
from screener import (
    JP_COMPARE_PRESETS,
    apply_screen,
    rank_companies,
    latest_row_for_table,
)
from ui_components import (
    inject_css,
    page_title,
    hero_card,
    metric_cards,
    render_ranking_table,
)


st.set_page_config(
    page_title="JP Forensic Accounting Engine",
    layout="wide"
)

inject_css()
page_title()

with st.sidebar:
    st.subheader("Settings")

    data_path = st.text_input(
        "Financial CSV path",
        "data/jp_financials_sample.csv"
    )

    wacc_pct = st.number_input(
        "WACC (%)",
        min_value=0.0,
        max_value=30.0,
        value=8.0,
        step=0.5
    )

    wacc = wacc_pct / 100

    st.caption("日本株の初期値は 6〜10% 程度を想定。")


@st.cache_data(show_spinner=False)
def get_data(path):
    return load_financial_data(path)


try:
    financial_df = get_data(data_path)
except Exception as e:
    st.error("Financial CSV could not be loaded.")
    st.exception(e)
    st.stop()


tab_analysis, tab_compare, tab_screening = st.tabs(
    [
        "Analysis",
        "Compare",
        "Screening",
    ]
)


with tab_analysis:

    st.subheader("Analysis")

    search = st.text_input(
        "銘柄コードまたは会社名で検索",
        "",
        key="analysis_search"
    )

    companies = (
        financial_df[["ticker", "company"]]
        .drop_duplicates()
        .sort_values("ticker")
    )

    if search.strip():
        s = search.strip().lower()
        companies = companies[
            companies["ticker"].astype(str).str.lower().str.contains(s)
            |
            companies["company"].astype(str).str.lower().str.contains(s)
        ]

    if companies.empty:
        st.warning("該当銘柄がありません。")
    else:
        labels = [
            f"{row.ticker} | {row.company}"
            for _, row in companies.iterrows()
        ]

        selected_label = st.selectbox(
            "Company",
            labels,
            index=0
        )

        ticker = selected_label.split("|")[0].strip()

        if st.button(
    "Analyze",
    width="stretch"
):
            try:
                result = run_jp_forensic_engine(
                    financial_df,
                    ticker=ticker,
                    wacc=wacc
                )

                latest = result["latest"]

                hero_card(
                    latest,
                    wacc_pct=wacc_pct
                )

                metric_cards(latest)

                render_trend_charts(result)

                with st.expander("Raw Data"):
                    st.dataframe(
                        result["df"],
                        use_container_width=True
                    )

            except Exception as e:
                st.error("Analysis failed.")
                st.exception(e)


with tab_compare:

    st.subheader("Compare")

    preset = st.selectbox(
        "Compare Preset",
        list(JP_COMPARE_PRESETS.keys())
    )

    tickers = JP_COMPARE_PRESETS[preset]

    st.caption(
        ", ".join(tickers)
    )

    if st.button(
        "Run Compare",
        key="compare_button"
    ):
        rows = []
        errors = []

        for ticker in tickers:
            try:
                result = run_jp_forensic_engine(
                    financial_df,
                    ticker=ticker,
                    wacc=wacc
                )
                rows.append(
                    latest_row_for_table(result)
                )
            except Exception as e:
                errors.append(
                    {
                        "Ticker": ticker,
                        "Error": str(e)
                    }
                )

        if rows:
            ranked = rank_companies(rows)

            st.markdown(
                f"### Comparing {len(ranked)} Companies"
            )

            st.plotly_chart(
    compare_scatter(ranked),
    width="stretch"
)
            render_ranking_table(ranked)

        if errors:
            with st.expander("Errors"):
                st.dataframe(errors, use_container_width=True)


with tab_screening:

    st.subheader("Screening")

    universe = (
        financial_df["ticker"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        roic_min_pct = st.slider(
            "ROIC minimum (%)",
            -100.0,
            100.0,
            10.0,
            1.0
        )

    with c2:
        spread_min_pct = st.slider(
            "ROIC-WACC minimum (%)",
            -50.0,
            50.0,
            0.0,
            1.0
        )

    with c3:
        risk_max = st.slider(
            "Risk maximum",
            0,
            100,
            40,
            5
        )

    with c4:
        accrual_max_pct = st.slider(
            "Accrual maximum (%)",
            -100.0,
            100.0,
            10.0,
            1.0
        )

    if st.button(
        "Run Screen",
        key="screen_button"
    ):
        rows = []
        errors = []

        for ticker in universe:
            try:
                result = run_jp_forensic_engine(
                    financial_df,
                    ticker=ticker,
                    wacc=wacc
                )
                rows.append(
                    latest_row_for_table(result)
                )
            except Exception as e:
                errors.append(
                    {
                        "Ticker": ticker,
                        "Error": str(e)
                    }
                )

        ranked = rank_companies(rows)

        screen_df = apply_screen(
            ranked,
            roic_min_pct=roic_min_pct,
            spread_min_pct=spread_min_pct,
            risk_max=risk_max,
            accrual_max_pct=accrual_max_pct,
        )

        st.markdown(
            f"### Results: {len(screen_df)}"
        )

        if not screen_df.empty:
            st.plotly_chart(
    screen_scatter(screen_df),
    width="stretch"
)

            render_ranking_table(screen_df)

        if errors:
            with st.expander("Errors"):
                st.dataframe(errors, use_container_width=True)
