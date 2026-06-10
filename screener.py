import pandas as pd


# =====================================================
# Compare Presets
# =====================================================

JP_COMPARE_PRESETS = {
    "JP Semiconductor": [
        "8035",  # 東京エレクトロン
        "6857",  # アドバンテスト
        "6146",  # ディスコ
        "6920",  # レーザーテック
        "6526",  # ソシオネクスト
    ],
    "JP Trading": [
        "8058",  # 三菱商事
        "8001",  # 伊藤忠
        "8031",  # 三井物産
        "8053",  # 住友商事
        "8002",  # 丸紅
    ],
    "JP Shipping": [
        "9101",
        "9104",
        "9107",
    ],
    "JP Large Cap": [
        "7203",
        "6758",
        "6861",
        "9984",
        "9432",
        "6098",
    ],
}


# =====================================================
# Latest Row
# =====================================================

def latest_row_for_table(result):

    latest = result["latest"]

    return {

        "Ticker": latest.get("Ticker"),

        "Company": latest.get("Company"),

        "Sector": latest.get(
            "Sector",
            latest.get("sector")
        ),

        "Grade": latest.get("Grade"),

        "Regime": latest.get("Regime"),

        "ROIC": latest.get(
            "ROIC_TTM"
        ),

        "ROIC-WACC": latest.get(
            "ROIC_WACC_Spread"
        ),

        "EconomicEarnings": latest.get(
            "EconomicEarnings_TTM"
        ),

        "Accrual": latest.get(
            "AccrualRatio"
        ),

        "CFO/NI": latest.get(
            "CFO_to_NI"
        ),

        "FCF/NI": latest.get(
            "FCF_to_NI"
        ),

        "FCFMargin": latest.get(
            "FCFMargin"
        ),

        "BuybackYield": latest.get(
            "BuybackYield"
        ),

        "DividendYieldProxy": latest.get(
            "DividendYieldProxy"
        ),

        "PBR": latest.get(
            "pbr"
        ),

        "Risk": latest.get(
            "ForensicRiskScore"
        ),

        "Quality": latest.get(
            "QualityScore"
        ),

        "Flags": latest.get(
            "Flags"
        ),
    }


# =====================================================
# Ranking Engine
# =====================================================

def rank_companies(rows):

    if isinstance(
        rows,
        pd.DataFrame
    ):
        df = rows.copy()

    else:
        df = pd.DataFrame(rows)

    if df.empty:
        return df

    required_cols = {

        "ROIC": 0,

        "ROIC-WACC": 0,

        "FCFMargin": 0,

        "CFO/NI": 0,

        "BuybackYield": 0,

        "DividendYieldProxy": 0,

        "Risk": 50,

        "Quality": 50,

        "PBR": 999,
    }

    for col, default in required_cols.items():

        if col not in df.columns:
            df[col] = default

    # ==========================================
    # Capital Allocation
    # ==========================================

    df["CapitalPolicyScore"] = (

        df["BuybackYield"]
        .fillna(0)
        * 200

        +

        df["DividendYieldProxy"]
        .fillna(0)
        * 100
    )

    # ==========================================
    # TSE Reform
    # ==========================================

    df["TSEReformScore"] = 0

    df.loc[
        df["PBR"].fillna(999) < 1,
        "TSEReformScore"
    ] = 10

    # ==========================================
    # Economic Score
    # ==========================================

    df["EconomicScore"] = (

        df["ROIC-WACC"]
        .fillna(0)
        * 100

        +

        df["ROIC"]
        .fillna(0)
        * 100

        +

        df["FCFMargin"]
        .fillna(0)
        * 50

        +

        df["CFO/NI"]
        .fillna(0)
        .clip(upper=3)
        * 10

        +

        df["CapitalPolicyScore"]
        .fillna(0)

        +

        df["TSEReformScore"]
        .fillna(0)

        +

        df["Quality"]
        .fillna(0)

        -

        df["Risk"]
        .fillna(0)
    )

    df = df.sort_values(
        "EconomicScore",
        ascending=False
    )

    return (
        df
        .reset_index(drop=True)
    )


# =====================================================
# Screening
# =====================================================

def apply_screen(
    df,
    roic_min_pct,
    spread_min_pct,
    risk_max,
    accrual_max_pct,
):

    if df.empty:
        return df

    screen = df.copy()

    # ==========================================
    # ROIC Filter
    # ==========================================

    screen = screen[
        screen["ROIC"]
        .fillna(-999)
        >= roic_min_pct / 100
    ]

    # ==========================================
    # Spread Filter
    # ==========================================

    screen = screen[
        screen["ROIC-WACC"]
        .fillna(-999)
        >= spread_min_pct / 100
    ]

    # ==========================================
    # Risk Filter
    # ==========================================

    screen = screen[
        screen["Risk"]
        .fillna(999)
        <= risk_max
    ]

    # ==========================================
    # Accrual Filter
    # ==========================================

    screen = screen[
        screen["Accrual"]
        .fillna(999)
        <= accrual_max_pct / 100
    ]

    return (
        screen
        .reset_index(drop=True)
    )


print("SCREENER LOADED")
