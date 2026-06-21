# Macro Cycle Dashboard V3

A Streamlit research dashboard with:

- Top navigation
- Traditional Chinese, English, and Japanese UI
- FRED macroeconomic data
- A transparent monthly business-cycle model
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
    ├── cycle_chart.py
    └── methodology.py
```

## Deploy

1. Upload all files and folders to the GitHub repository.
2. In Streamlit Community Cloud, set the main file path to `app.py`.
3. Reboot the app after dependencies finish installing.

## Important limitation

The current historical model uses latest revised FRED data. It is not yet a point-in-time, look-ahead-free backtest. A production validation version should use ALFRED vintages and release-date alignment.
