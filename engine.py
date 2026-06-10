import pandas as pd
import numpy as np


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
    "roe",
    "cet1",
    "npl_ratio",
]


    return any(
        keyword in sector
        for keyword in keywords
    )

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


def bank_regime_label(economic_score):

    if pd.isna(economic_score):
        return "Financial Institution"

    if economic_score >= 80:
        return "Capital Compounder"

    if economic_score >= 65:
        return "Quality Bank"

    if economic_score >= 50:
        return "Neutral Bank"

    return "Capital Destroyer"


def score_roe(roe):

    if pd.isna(roe):
        return 0

    if roe >= 0.15:
        return 100

    if roe >= 0.12:
        return 80

    if roe >= 0.10:
        return 60

    if roe >= 0.08:
        return 40

    return 20


def score_spread(spread):

    if pd.isna(spread):
        return 0

    if spread >= 0.05:
        return 100

    if spread >= 0.03:
        return 80

    if spread >= 0:
        return 60

    return 20


def score_cet1(cet1):

    if pd.isna(cet1):
        return 50

    if cet1 >= 0.13:
        return 100

    if cet1 >= 0.11:
        return 80

    if cet1 >= 0.09:
        return 60

    return 20


def score_pbr(pbr):

    if pd.isna(pbr):
        return 50

    return max(
        0,
        min(
            100,
            100 - (pbr - 1) * 50
        )
    )


def score_yield(total_yield):

    if pd.isna(total_yield):
        return 0

    if total_yield >= 0.08:
        return 100

    if total_yield >= 0.06:
        return 80

    if total_yield >= 0.04:
        return 60

    return 30


def score_npl(npl_ratio):

    if pd.isna(npl_ratio):
        return 50

    if npl_ratio <= 0.01:
        return 100

    if npl_ratio <= 0.02:
        return 80

    if npl_ratio <= 0.03:
        return 60

    return 20


def run_bank_engine(
    financial_df,
    ticker,
    coe=0.09
):

    ticker = str(ticker).strip()

    df = financial_df[
        financial_df["ticker"].astype(str)
        == ticker
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
        "dividend",
        "buyback",
        "market_cap",
        "roe",
        "pbr",
        "cet1",
        "npl_ratio",
    ]:
        if col not in df.columns:
            df[col] = np.nan

    for col in [
        "dividend",
        "buyback",
    ]:
        df[col] = df[col].fillna(0)

    for col in [
        "dividend",
        "buyback",
    ]:
        df[f"{col}_TTM"] = (
            df[col]
            .rolling(
                4,
                min_periods=4
            )
            .sum()
        )

    df["DividendYield"] = safe_div(
        df["dividend_TTM"],
        df["market_cap"]
    )

    df["BuybackYield"] = safe_div(
        df["buyback_TTM"],
        df["market_cap"]
    )

    df["TotalYield"] = (
        df["DividendYield"].fillna(0)
        +
        df["BuybackYield"].fillna(0)
    )

    df["CoE"] = coe

    df["ROE_EconomicSpread"] = (
        df["roe"]
        -
        df["CoE"]
    )

    economic_scores = []
    risk_scores = []
    quality_scores = []
    regimes = []
    flags = []

    roe_scores = []
    spread_scores = []
    cet1_scores = []
    pbr_scores = []
    yield_scores = []
    npl_scores = []

    for _, r in df.iterrows():

        roe = r.get(
            "roe",
            np.nan
        )

        spread = r.get(
            "ROE_EconomicSpread",
            np.nan
        )

        pbr = r.get(
            "pbr",
            np.nan
        )

        cet1 = r.get(
            "cet1",
            np.nan
        )

        npl = r.get(
            "npl_ratio",
            np.nan
        )

        total_yield = r.get(
            "TotalYield",
            np.nan
        )

        roe_score = score_roe(roe)
        spread_score = score_spread(spread)
        cet1_score = score_cet1(cet1)
        pbr_score = score_pbr(pbr)
        yield_score = score_yield(total_yield)
        npl_score = score_npl(npl)

        economic_score = (
            0.25 * roe_score
            +
            0.25 * spread_score
            +
            0.15 * cet1_score
            +
            0.15 * pbr_score
            +
            0.10 * yield_score
            +
            0.10 * npl_score
        )

        risk = 100 - economic_score
        quality = economic_score

        f = []

        if pd.notna(spread) and spread < 0:
            f.append("ROE below CoE")

        if pd.notna(pbr) and pbr < 1:
            f.append("PBR below 1x")

        if pd.notna(cet1) and cet1 < 0.09:
            f.append("Low CET1")

        if pd.notna(npl) and npl > 0.03:
            f.append("High NPL ratio")

        economic_scores.append(economic_score)
        risk_scores.append(risk)
        quality_scores.append(quality)
        regimes.append(
            bank_regime_label(economic_score)
        )
        flags.append(
            "; ".join(f)
            if f
            else "No major red flags"
        )

        roe_scores.append(roe_score)
        spread_scores.append(spread_score)
        cet1_scores.append(cet1_score)
        pbr_scores.append(pbr_score)
        yield_scores.append(yield_score)
        npl_scores.append(npl_score)

    df["EconomicScore"] = economic_scores
    df["ForensicRiskScore"] = risk_scores
    df["QualityScore"] = quality_scores
    df["Regime"] = regimes
    df["Flags"] = flags

    df["ROE_Score"] = roe_scores
    df["Spread_Score"] = spread_scores
    df["CET1_Score"] = cet1_scores
    df["PBR_Score"] = pbr_scores
    df["Yield_Score"] = yield_scores
    df["NPL_Score"] = npl_scores

    # Compatibility columns for existing UI / charts
    df["ROIC_TTM"] = df["roe"]
    df["ROIC_WACC_Spread"] = df["ROE_EconomicSpread"]
    df["FCFMargin"] = np.nan
    df["AccrualRatio"] = np.nan
    df["CFO_to_NI"] = np.nan
    df["FCF_to_NI"] = np.nan
    df["DSO"] = np.nan
    df["InventoryDays"] = np.nan
    df["EconomicEarnings_TTM"] = (
        df["equity"]
        *
        df["ROE_EconomicSpread"]
    )

    latest = (
        df.iloc[-1]
        .to_dict()
    )

    latest.update(
        {
            "Ticker": ticker,
            "Company": latest.get(
                "company",
                ticker
            ),
            "Sector": latest.get(
                "sector",
                ""
            ),
            "Grade": forensic_grade(
                latest.get(
                    "ForensicRiskScore",
                    np.nan
                )
            ),
            "Regime": latest.get(
                "Regime",
                "Financial Institution"
            ),
        }
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


def run_corporate_engine(
    financial_df,
    ticker,
    wacc=0.08
):

    ticker = str(ticker).strip()

    df = financial_df[
        financial_df["ticker"].astype(str)
        == ticker
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


def run_jp_forensic_engine(
    financial_df,
    ticker,
    wacc=0.08,
    coe=0.09
):

    ticker = str(ticker).strip()

    df = financial_df[
        financial_df["ticker"].astype(str)
        == ticker
    ].copy()

    if df.empty:
        raise ValueError(
            f"Ticker not found: {ticker}"
        )

    # =====================================
    # Bank Engine is temporarily disabled
    # All tickers are processed by Corporate Engine
    # =====================================

    return run_corporate_engine(
        financial_df=financial_df,
        ticker=ticker,
        wacc=wacc
    )
