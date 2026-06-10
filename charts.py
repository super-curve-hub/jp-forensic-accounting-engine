import pandas as pd
import numpy as np


# =====================================================
# Required columns for non-financial companies
# =====================================================

REQUIRED_COLUMNS = [
    "ticker",
    "company",
    "sector",
    "date",
    "revenue",
    "operating_income",
    "pretax_income",
    "income_tax",
    "net_income",
    "cfo",
    "capex",
    "assets",
    "liabilities",
    "equity",
    "cash",
    "receivables",
    "inventory",
    "dividend",
    "buyback",
    "market_cap",
    "pbr",
]


# =====================================================
# Utilities
# =====================================================

def safe_div(a, b):
    out = a / b

    if isinstance(out, pd.Series):
        return out.replace(
            [np.inf, -np.inf],
            np.nan
        )

    try:
        return np.nan if np.isinf(out) else out
    except Exception:
        return out


def load_financial_data(path):
    df = pd.read_csv(path)

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan

    df["ticker"] = df["ticker"].astype(str)

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    numeric_cols = [
        c
        for c in df.columns
        if c not in [
            "ticker",
            "company",
            "sector",
            "date",
        ]
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        subset=[
            "ticker",
            "date",
        ]
    )

    df = (
        df
        .sort_values(
            [
                "ticker",
                "date",
            ]
        )
        .reset_index(drop=True)
    )

    return df


def forensic_grade(score):
    if pd.isna(score):
        return "NA"

    if score <= 20:
        return "A"

    if score <= 40:
        return "B"

    if score <= 60:
        return "C"

    if score <= 80:
        return "D"

    return "F"


# =====================================================
# Regime
# =====================================================

def corporate_regime_label(latest):
    spread = latest.get(
        "ROIC_WACC_Spread",
        np.nan
    )

    accrual = latest.get(
        "AccrualRatio",
        np.nan
    )

    cfo = latest.get(
        "CFO_to_NI",
        np.nan
    )

    risk = latest.get(
        "ForensicRiskScore",
        np.nan
    )

    roic = latest.get(
        "ROIC_TTM",
        np.nan
    )

    pbr = latest.get(
        "pbr",
        np.nan
    )

    if (
        pd.notna(spread)
        and pd.notna(accrual)
        and pd.notna(cfo)
        and pd.notna(risk)
        and spread > 0
        and accrual < 0
        and cfo > 1
        and risk <= 20
    ):
        return "Quality Compounder"

    if pd.notna(spread) and spread < 0:
        return "Value Destruction"

    if (
        pd.notna(roic)
        and roic > 0.15
        and pd.notna(pbr)
        and pbr < 1
    ):
        return "TSE Reform Candidate"

    if (
        pd.notna(roic)
        and roic > 0.15
        and pd.notna(risk)
        and risk <= 40
    ):
        return "High ROIC / Monitor"

    return "Neutral / Inconclusive"


# =====================================================
# Forensic Risk Score
# =====================================================

def calculate_forensic_risk_row(df, idx):
    r = df.iloc[idx]

    risk = 0
    flags = []

    # -----------------------------
    # 1. Accrual risk
    # -----------------------------
    accrual = r.get(
        "AccrualRatio",
        np.nan
    )

    if pd.notna(accrual):
        if accrual > 0.10:
            risk += 25
            flags.append("Accrual distortion severe")
        elif accrual > 0.05:
            risk += 15
            flags.append("Accrual distortion moderate")
        elif accrual > 0.02:
            risk += 5
            flags.append("Accrual positive")

    # -----------------------------
    # 2. CFO conversion risk
    # -----------------------------
    cfo_ni = r.get(
        "CFO_to_NI",
        np.nan
    )

    net_income_ttm = r.get(
        "net_income_TTM",
        np.nan
    )

    if (
        pd.notna(cfo_ni)
        and pd.notna(net_income_ttm)
        and net_income_ttm > 0
    ):
        if cfo_ni < 0.50:
            risk += 20
            flags.append("Very weak CFO conversion")
        elif cfo_ni < 0.80:
            risk += 10
            flags.append("Weak CFO conversion")
        elif cfo_ni < 1.00:
            risk += 5
            flags.append("CFO below NI")

    # -----------------------------
    # 3. FCF conversion risk
    # -----------------------------
    fcf_ni = r.get(
        "FCF_to_NI",
        np.nan
    )

    if (
        pd.notna(fcf_ni)
        and pd.notna(net_income_ttm)
        and net_income_ttm > 0
    ):
        if fcf_ni < 0:
            risk += 20
            flags.append("Negative FCF despite profit")
        elif fcf_ni < 0.50:
            risk += 10
            flags.append("Weak FCF conversion")
        elif fcf_ni < 0.80:
            risk += 5
            flags.append("FCF below NI")

    # -----------------------------
    # 4. Leverage deterioration
    # -----------------------------
    if idx >= 4:
        prev = df.iloc[idx - 4]

        dte_now = safe_div(
            r.get("liabilities", np.nan),
            r.get("equity", np.nan)
        )

        dte_prev = safe_div(
            prev.get("liabilities", np.nan),
            prev.get("equity", np.nan)
        )

        if (
            pd.notna(dte_now)
            and pd.notna(dte_prev)
            and dte_prev > 0
        ):
            if dte_now > dte_prev * 1.30:
                risk += 15
                flags.append("Leverage rising sharply")
            elif dte_now > dte_prev * 1.15:
                risk += 8
                flags.append("Leverage rising")

    # -----------------------------
    # 5. Operating margin deterioration
    # -----------------------------
    if idx >= 4:
        prev = df.iloc[idx - 4]

        margin_now = safe_div(
            r.get("operating_income_TTM", np.nan),
            r.get("revenue_TTM", np.nan)
        )

        margin_prev = safe_div(
            prev.get("operating_income_TTM", np.nan),
            prev.get("revenue_TTM", np.nan)
        )

        if (
            pd.notna(margin_now)
            and pd.notna(margin_prev)
            and margin_prev > 0
        ):
            decline = margin_prev - margin_now

            if decline > 0:
                penalty = min(
                    20,
                    decline * 200
                )

                risk += penalty
                flags.append("Operating margin deteriorating")

    # -----------------------------
    # 6. Working capital stress
    # -----------------------------
    dso = r.get(
        "DSO",
        np.nan
    )

    inv_days = r.get(
        "InventoryDays",
        np.nan
    )

    if pd.notna(dso):
        if dso > 90:
            risk += 10
            flags.append("High DSO")
        elif dso > 60:
            risk += 5
            flags.append("Moderate DSO")

    if pd.notna(inv_days):
        if inv_days > 120:
            risk += 10
            flags.append("Inventory buildup")
        elif inv_days > 90:
            risk += 5
            flags.append("Moderate inventory buildup")

    # -----------------------------
    # 7. Economic spread risk
    # -----------------------------
    spread = r.get(
        "ROIC_WACC_Spread",
        np.nan
    )

    if pd.notna(spread) and spread < 0:
        risk += 10
        flags.append("ROIC below WACC")

    risk = max(
        0,
        min(
            100,
            risk
        )
    )

    if not flags:
        flags = [
            "No major red flags"
        ]

    return risk, "; ".join(flags)


# =====================================================
# Corporate Engine
# =====================================================

def run_corporate_engine(
    financial_df,
    ticker,
    wacc=0.08
):
    ticker = str(ticker).strip()

    df = financial_df[
        financial_df["ticker"].astype(str) == ticker
    ].copy()

    if df.empty:
        raise ValueError(
            f"Ticker not found: {ticker}"
        )

    df = (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )

    for col in [
        "cash",
        "receivables",
        "inventory",
        "dividend",
        "buyback",
    ]:
        df[col] = df[col].fillna(0)

    flows = [
        "revenue",
        "operating_income",
        "pretax_income",
        "income_tax",
        "net_income",
        "cfo",
        "capex",
        "dividend",
        "buyback",
    ]

    for col in flows:
        df[f"{col}_TTM"] = (
            df[col]
            .rolling(
                4,
                min_periods=4
            )
            .sum()
        )

    df["TaxRate"] = (
        safe_div(
            df["income_tax_TTM"],
            df["pretax_income_TTM"]
        )
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .clip(0, 0.35)
        .fillna(0.30)
    )

    df["NOPAT_TTM"] = (
        df["operating_income_TTM"]
        *
        (1 - df["TaxRate"])
    )

    df["InvestedCapital"] = (
        df["equity"].fillna(0)
        +
        df["liabilities"].fillna(0)
        -
        df["cash"].fillna(0)
    )

    df["InvestedCapital"] = (
        df["InvestedCapital"]
        .replace(0, np.nan)
    )

    df["AvgIC"] = (
        df["InvestedCapital"]
        .rolling(
            2,
            min_periods=2
        )
        .mean()
    )

    df["ROIC_TTM"] = safe_div(
        df["NOPAT_TTM"],
        df["AvgIC"]
    )

    df["ROIC_WACC_Spread"] = (
        df["ROIC_TTM"]
        -
        wacc
    )

    df["EconomicEarnings_TTM"] = (
        df["NOPAT_TTM"]
        -
        wacc * df["AvgIC"]
    )

    df["Accruals_TTM"] = (
        df["net_income_TTM"]
        -
        df["cfo_TTM"]
    )

    df["AvgAssets"] = (
        df["assets"]
        .rolling(
            2,
            min_periods=2
        )
        .mean()
    )

    df["AccrualRatio"] = safe_div(
        df["Accruals_TTM"],
        df["AvgAssets"]
    )

    df["CFO_to_NI"] = safe_div(
        df["cfo_TTM"],
        df["net_income_TTM"]
    )

    df["FCF_TTM"] = (
        df["cfo_TTM"]
        -
        df["capex_TTM"].abs()
    )

    df["FCF_to_NI"] = safe_div(
        df["FCF_TTM"],
        df["net_income_TTM"]
    )

    df["FCFMargin"] = safe_div(
        df["FCF_TTM"],
        df["revenue_TTM"]
    )

    df["GrossMargin"] = np.nan

    df["DSO"] = safe_div(
        df["receivables"],
        df["revenue_TTM"] / 365
    )

    df["InventoryDays"] = safe_div(
        df["inventory"],
        df["revenue_TTM"] / 365
    )

    df["BuybackYield"] = safe_div(
        df["buyback_TTM"],
        df["market_cap"]
    )

    df["DividendYieldProxy"] = safe_div(
        df["dividend_TTM"],
        df["market_cap"]
    )

    risk_scores = []
    flags = []

    for i in range(len(df)):
        risk, flag = calculate_forensic_risk_row(
            df,
            i
        )

        risk_scores.append(risk)
        flags.append(flag)

    df["ForensicRiskScore"] = risk_scores

    df["QualityScore"] = (
        100
        -
        df["ForensicRiskScore"]
    )

    df["Flags"] = flags

    valid = df.dropna(
        subset=[
            "ROIC_TTM",
            "AccrualRatio",
            "FCFMargin",
        ],
        how="all"
    )

    latest = (
        df.iloc[-1]
        if valid.empty
        else valid.iloc[-1]
    ).to_dict()

    latest.update(
        {
            "Ticker": ticker,
            "Company": latest.get(
                "company",
                ticker
            ),
            "Sector": latest.get(
                "sector",
                "NA"
            ),
            "Grade": forensic_grade(
                latest.get(
                    "ForensicRiskScore",
                    np.nan
                )
            ),
        }
    )

    latest["Regime"] = corporate_regime_label(
        latest
    )

    return {
        "ticker": ticker,
        "company": latest.get(
            "Company",
            ticker
        ),
        "df": df,
        "latest": latest,
    }


# =====================================================
# Public Entry Point
# =====================================================

def run_jp_forensic_engine(
    financial_df,
    ticker,
    wacc=0.08,
    coe=0.09
):
    return run_corporate_engine(
        financial_df=financial_df,
        ticker=str(ticker).strip(),
        wacc=wacc
    )
