# JP Forensic Accounting Engine

日本株向けの会計品質・資本効率スクリーニング用 Streamlit アプリです。

## 目的

東証上場銘柄を対象に、以下を統合して企業の質を比較します。

- ROIC
- ROIC-WACC
- Economic Score
- Accrual Ratio
- CFO / NI
- FCF Margin
- Forensic Risk
- Quality Score

## 画面構成

- Analysis  
  全銘柄から銘柄コードまたは会社名で検索し、個別企業を分析します。

- Compare  
  業種プリセットごとに Economic Profit vs Risk を比較します。

- Screening  
  ROIC、ROIC-WACC、Risk、Accrual などの条件で候補銘柄を抽出します。

Watchlist と Portfolio は削除済みです。

## 起動方法

```bash
pip install -r requirements.txt
streamlit run app.py
```

## データ入力

初期状態では `data/jp_financials_sample.csv` を読み込みます。

本番運用では同じ形式で EDINET 等から作成した財務データ CSV を差し替えてください。

必要カラムは以下です。

```text
ticker,company,sector,date,revenue,operating_income,pretax_income,income_tax,net_income,cfo,capex,assets,liabilities,equity,cash,receivables,inventory,dividend,buyback,market_cap,pbr,roe
```

## 推奨ワークフロー

1. Screening で候補銘柄を抽出
2. Compare で業種内順位を確認
3. Analysis で個別深掘り
