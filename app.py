import streamlit as st

from engine import (
    load_financial_data,
    run_jp_forensic_engine,
)

from charts import (
    render_trend_charts,
    compare_scatter,
    screen_scatter,
)

from screener import (
    JP_COMPARE_PRESETS,
    latest_row_for_table,
    rank_companies,
    apply_screen,
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
    layout="wide",
)

inject_css()
page_title()


# ==========================================
# Sidebar
# ==========================================

with st.sidebar:

    st.subheader("Settings")

    data_path = st.text_input(
        "Financial CSV",
        "data/jp_financials_sample.csv"
    )

    wacc_pct = st.slider(
        "WACC (%)",
        0.0,
        20.0,
        8.0,
        0.5
    )

    wacc = wacc_pct / 100


# ==========================================
# Load Data
# ==========================================

@st.cache_data(show_spinner=False)
def get_data(path):
    return load_financial_data(path)


try:

    financial_df = get_data(data_path)

except Exception as e:

    st.error(str(e))
    st.stop()


# ==========================================
# Remove Financials
# ==========================================

non_financial_df = financial_df[
    ~financial_df["sector"]
    .astype(str)
    .str.contains(
        "銀行|金融|保険|証券|bank|financial|insurance|securities",
        case=False,
        na=False
    )
].copy()


# ==========================================
# Tabs
# ==========================================

tab_analysis, tab_compare, tab_screen = st.tabs(
    [
        "Analysis",
        "Compare",
        "Screening",
    ]
)


# ==========================================
# Analysis
# ==========================================

with tab_analysis:

    st.subheader("Analysis")

    companies = (
        non_financial_df[
            ["ticker", "company"]
        ]
        .drop_duplicates()
        .sort_values("ticker")
    )

    labels = [
        f"{r.ticker} | {r.company}"
        for _, r in companies.iterrows()
    ]

    selected = st.selectbox(
        "Company",
        labels
    )

    ticker = selected.split("|")[0].strip()

    if st.button(
        "Analyze",
        width="stretch"
    ):

        result = run_jp_forensic_engine(
            non_financial_df,
            ticker=ticker,
            wacc=wacc
        )

        latest = result["latest"]

        hero_card(
            latest,
            wacc_pct
        )

        metric_cards(
            latest
        )

        render_trend_charts(
            result
        )

        with st.expander(
            "Raw Data"
        ):
            st.dataframe(
                result["df"],
                width="stretch"
            )


# ==========================================
# Compare
# ==========================================

with tab_compare:

    st.subheader("Compare")

    preset = st.selectbox(
        "Preset",
        list(
            JP_COMPARE_PRESETS.keys()
        )
    )

    if st.button(
        "Run Compare"
    ):

        rows = []

        for ticker in JP_COMPARE_PRESETS[preset]:

            try:

                result = run_jp_forensic_engine(
                    non_financial_df,
                    ticker=ticker,
                    wacc=wacc
                )

                rows.append(
                    latest_row_for_table(
                        result
                    )
                )

            except:
                pass

        ranked = rank_companies(
            rows
        )

        st.plotly_chart(
            compare_scatter(
                ranked
            ),
            width="stretch"
        )

        render_ranking_table(
            ranked
        )


# ==========================================
# Screening
# ==========================================

with tab_screen:

    st.subheader("Screening")

    roic_min_pct = st.slider(
        "ROIC minimum (%)",
        -100.0,
        100.0,
        10.0,
    )

    spread_min_pct = st.slider(
        "ROIC-WACC minimum (%)",
        -50.0,
        50.0,
        0.0,
    )

    risk_max = st.slider(
        "Risk maximum",
        0,
        100,
        40,
    )

    accrual_max_pct = st.slider(
        "Accrual maximum (%)",
        -100.0,
        100.0,
        10.0,
    )

    if st.button(
        "Run Screen"
    ):

        rows = []

        for ticker in (
            non_financial_df["ticker"]
            .astype(str)
            .unique()
        ):

            try:

                result = run_jp_forensic_engine(
                    non_financial_df,
                    ticker=ticker,
                    wacc=wacc
                )

                rows.append(
                    latest_row_for_table(
                        result
                    )
                )

            except:
                pass

        ranked = rank_companies(
            rows
        )

        screened = apply_screen(
            ranked,
            roic_min_pct,
            spread_min_pct,
            risk_max,
            accrual_max_pct,
        )

        st.plotly_chart(
            screen_scatter(
                screened
            ),
            width="stretch"
        )

        render_ranking_table(
            screened
        )
