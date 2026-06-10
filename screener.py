import pandas as pd


JP_COMPARE_PRESETS = {
    "JP Semiconductor": [
        "8035",
        "6857",
        "6146",
        "6920",
        "6526",
    ],
    "JP Bank": [
        "8306",
        "8316",
        "8411",
        "7182",
    ],
    "JP Trading": [
        "8058",
        "8001",
        "8031",
        "8053",
        "8002",
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


def _is_financial(latest):

    sector = str(
        latest.get(
            "Sector",
            latest.get(
                "sector",
                ""
            )
        )
    ).lower()

    return (
        "bank" in sector
        or "financial" in sector
        or "insurance" in sector
        or "capital markets" in sector
        or "securities" in sector
        or "銀行" in sector
        or "証券" in sector
        or "保険" in sector
    )


def latest_row_for_table(result):

    latest = result["latest"]

    if _is_financial(latest):

        return {
            "Ticker": latest.get("Ticker"),
            "Company": latest.get("Company"),
            "Sector": latest.get("Sector"),
            "Grade": latest.get("Grade"),
            "Regime": latest.get("Regime"),

            "ROE": latest.get("roe"),

            "ROE-CoE": latest.get(
                "ROE_EconomicSpread"
            ),

            "EconomicScore": latest.get(
                "EconomicScore"
            ),

            "TotalYield": latest.get(
                "TotalYield"
            ),

            "PBR": latest.get("pbr"),

            "Risk": latest.get(
                "ForensicRiskScore"
            ),

            "Quality": latest.get(
                "QualityScore"
            ),

            "Flags": latest.get("Flags"),
        }

    return {
        "Ticker": latest.get("Ticker"),
        "Company": latest.get("Company"),
        "Sector": latest.get("Sector"),
        "Grade": latest.get("Grade"),
        "Regime": latest.get("Regime"),

        "ROIC": latest.get("ROIC_TTM"),

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

        "PBR": latest.get("pbr"),

        "ROE": latest.get("roe"),

        "DSO": latest.get("DSO"),

        "InventoryDays": latest.get(
            "InventoryDays"
        ),

        "Risk": latest.get(
            "ForensicRiskScore"
        ),

        "Quality": latest.get(
            "QualityScore"
        ),

        "Flags": latest.get("Flags"),
    }


def rank_companies(rows):

    if isinstance(rows, pd.DataFrame):
        df = rows.copy()
    else:
        df = pd.DataFrame(rows)

    if df.empty:
        return df

    # ==========================
    # Bank Engine Output
    # ==========================

    if (
        "EconomicScore" in df.columns
        and
        df["EconomicScore"].notna().any()
    ):

        return (
            df
            .sort_values(
                "EconomicScore",
                ascending=False
            )
            .reset_index(drop=True)
        )

    # ==========================
    # Corporate Engine Output
    # ==========================

    if "BuybackYield" not in df.columns:
        df["BuybackYield"] = 0

    if "DividendYieldProxy" not in df.columns:
        df["DividendYieldProxy"] = 0

    if "ROIC" not in df.columns:
        df["ROIC"] = 0

    if "ROIC-WACC" not in df.columns:
        df["ROIC-WACC"] = 0

    if "FCFMargin" not in df.columns:
        df["FCFMargin"] = 0

    if "CFO/NI" not in df.columns:
        df["CFO/NI"] = 0

    if "Risk" not in df.columns:
        df["Risk"] = 50

    if "Quality" not in df.columns:
        df["Quality"] = 50

    df["CapitalPolicyScore"] = (
        df["BuybackYield"]
        .fillna(0)
        * 200
        +
        df["DividendYieldProxy"]
        .fillna(0)
        * 100
    )

    df["TSEReformScore"] = 0

    if "PBR" in df.columns:

        df.loc[
            df["PBR"].fillna(999) < 1,
            "TSEReformScore"
        ] = 10

    df["EconomicScore"] = (
        df["ROIC-WACC"]
        .fillna(0)
        * 150
        +
        df["ROIC"]
        .fillna(0)
        * 100
        +
        df["FCFMargin"]
        .fillna(0)
        * 75
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

    return df.reset_index(drop=True)


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

    # ==========================
    # Bank Mode
    # ==========================

    if (
        "ROE-CoE" in screen.columns
        and
        screen["ROE-CoE"].notna().any()
    ):

        screen = screen[
            screen["Risk"]
            .fillna(999)
            <= risk_max
        ]

        return (
            screen
            .reset_index(drop=True)
        )

    # ==========================
    # Corporate Mode
    # ==========================

    screen = screen[
        screen["ROIC"]
        .fillna(-999)
        >= roic_min_pct / 100
    ]

    screen = screen[
        screen["ROIC-WACC"]
        .fillna(-999)
        >= spread_min_pct / 100
    ]

    screen = screen[
        screen["Risk"]
        .fillna(999)
        <= risk_max
    ]

    screen = screen[
        screen["Accrual"]
        .fillna(999)
        <= accrual_max_pct / 100
    ]

    return (
        screen
        .reset_index(drop=True)
    )
