import pandas as pd
import numpy as np


# =====================================================
# Required Columns
# Non-financial corporate version only
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
# Helpers
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
# Regime Label
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
# Corporate Forensic Engine
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
        if col not in df.columns:
            df[col] = np.nan
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
        if col not in df.columns:
            df[col] = np.nan

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

    scores = []
    flags = []

    for _, r in df.iterrows():
        score = 0
        f = []

        if pd.notna(r["AccrualRatio"]):
            if r["AccrualRatio"] > 0.10:
                score += 25
                f.append(
                    "Accrual distortion severe"
                )
            elif r["AccrualRatio"] > 0.05:
                score += 15
                f.append(
                    "Accrual distortion moderate"
                )

        if (
            pd.notna(r["CFO_to_NI"])
            and pd.notna(r["net_income_TTM"])
            and r["net_income_TTM"] > 0
        ):
            if r["CFO_to_NI"] < 0.80:
                score += 20
                f.append(
                    "Weak CFO conversion"
                )
            elif r["CFO_to_NI"] < 1.00:
                score += 10
                f.append(
                    "CFO below NI"
                )

        if pd.notna(r["DSO"]):
            if r["DSO"] > 90:
                score += 15
                f.append(
                    "High DSO"
                )
            elif r["DSO"] > 60:
                score += 10
                f.append(
                    "Moderate DSO"
                )

        if pd.notna(r["InventoryDays"]):
            if r["InventoryDays"] > 120:
                score += 15
                f.append(
                    "Inventory buildup"
                )
            elif r["InventoryDays"] > 90:
                score += 10
                f.append(
                    "Moderate inventory buildup"
                )

        if (
            pd.notna(r["ROIC_WACC_Spread"])
            and r["ROIC_WACC_Spread"] < 0
        ):
            score += 15
            f.append(
                "ROIC below WACC"
            )

        if (
            pd.notna(r["pbr"])
            and r["pbr"] < 1
        ):
            f.append(
                "PBR below 1x"
            )

        scores.append(
            min(score, 100)
        )

        flags.append(
            "; ".join(f)
            if f
            else "No major red flags"
        )

    df["ForensicRiskScore"] = scores
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
