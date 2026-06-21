# Macro Cycle Dashboard V3

A Streamlit research dashboard with:

- Top navigation
- Traditional Chinese, English, and Japanese UI
- FRED macroeconomic data
- A transparent monthly business-cycle model
- Sector overweight / neutral / underweight scores
- Top 3 price-stability research candidates by sector
- Sector ETF candlestick charts
- Cycle-phase background overlays
- A real modal dialog for secondary indicators

## Repository structure

```text
.
├── app.py
├── requirements.txt
├── core/
│   ├── data.py
│   ├── model.py
│   ├── charts.py
│   └── i18n.py
└── views/
    ├── dashboard.py
    ├── sector_allocation.py
    ├── cycle_chart.py
    └── methodology.py
```

## Deploy

1. Upload all files and folders to the GitHub repository.
2. In Streamlit Community Cloud, set the main file path to `app.py`.
3. Reboot the app after dependencies finish installing.

## Important limitation

The current historical model uses latest revised FRED data. It is not yet a point-in-time, look-ahead-free backtest. A production validation version should use ALFRED vintages and release-date alignment.


## Sector allocation model

Sector allocation combines:

- 50% phase prior
- 30% six- and twelve-month relative momentum versus SPY
- 20% price trend

Candidate ranking combines:

- 60% market-price stability
- 40% relative six-month performance versus the sector ETF

The initial stock universe is editable and is not an exhaustive index-constituent list.
