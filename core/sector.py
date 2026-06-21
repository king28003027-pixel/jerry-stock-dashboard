from __future__ import annotations

import math

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf


SECTOR_ETFS = {
    "Communication Services": "XLC",
    "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP",
    "Energy": "XLE",
    "Financials": "XLF",
    "Health Care": "XLV",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Technology": "XLK",
    "Utilities": "XLU",
}

# This is an editable large-cap research universe, not an exhaustive index constituent list.
SECTOR_UNIVERSE = {
    "Communication Services": ["GOOGL", "META", "TMUS", "VZ", "T", "NFLX"],
    "Consumer Discretionary": ["AMZN", "HD", "MCD", "LOW", "TJX", "BKNG"],
    "Consumer Staples": ["WMT", "COST", "PG", "KO", "PEP", "PM"],
    "Energy": ["XOM", "CVX", "COP", "EOG", "SLB", "MPC"],
    "Financials": ["JPM", "BRK-B", "V", "MA", "BAC", "GS"],
    "Health Care": ["LLY", "JNJ", "ABBV", "MRK", "TMO", "ABT"],
    "Industrials": ["GE", "CAT", "RTX", "HON", "UNP", "ETN"],
    "Materials": ["LIN", "SHW", "ECL", "NEM", "APD", "FCX"],
    "Real Estate": ["PLD", "AMT", "EQIX", "WELL", "O", "SPG"],
    "Technology": ["MSFT", "AAPL", "NVDA", "ORCL", "CSCO", "IBM"],
    "Utilities": ["NEE", "SO", "DUK", "AEP", "SRE", "EXC"],
}

PHASE_PRIORS = {
    "Recovery": {
        "Industrials": 82, "Financials": 78, "Materials": 76,
        "Consumer Discretionary": 72, "Technology": 66, "Real Estate": 64,
        "Communication Services": 60, "Energy": 55, "Health Care": 46,
        "Consumer Staples": 40, "Utilities": 36,
    },
    "Expansion": {
        "Technology": 82, "Consumer Discretionary": 80, "Industrials": 76,
        "Financials": 72, "Communication Services": 70, "Materials": 66,
        "Energy": 60, "Real Estate": 54, "Health Care": 46,
        "Consumer Staples": 38, "Utilities": 34,
    },
    "Late Cycle": {
        "Energy": 82, "Materials": 76, "Health Care": 66,
        "Consumer Staples": 62, "Utilities": 58, "Financials": 50,
        "Industrials": 46, "Communication Services": 44, "Technology": 40,
        "Real Estate": 36, "Consumer Discretionary": 34,
    },
    "Contraction": {
        "Utilities": 82, "Consumer Staples": 80, "Health Care": 76,
        "Real Estate": 62, "Communication Services": 56, "Technology": 50,
        "Financials": 36, "Industrials": 30, "Materials": 26,
        "Energy": 24, "Consumer Discretionary": 24,
    },
    "Neutral": {sector: 50 for sector in SECTOR_ETFS},
}


@st.cache_data(ttl=21600, show_spinner=False)
def download_adjusted_history(tickers: tuple[str, ...], period: str = "3y") -> tuple[pd.DataFrame, pd.DataFrame]:
    data = yf.download(
        list(tickers),
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=True,
        group_by="column",
    )

    if data.empty:
        return pd.DataFrame(), pd.DataFrame()

    close = _extract_field(data, "Close")
    volume = _extract_field(data, "Volume")
    close.index = pd.to_datetime(close.index).tz_localize(None)
    volume.index = pd.to_datetime(volume.index).tz_localize(None)
    return close.sort_index(), volume.sort_index()


def _extract_field(data: pd.DataFrame, field: str) -> pd.DataFrame:
    if isinstance(data.columns, pd.MultiIndex):
        level0 = data.columns.get_level_values(0)
        level1 = data.columns.get_level_values(1)

        if field in level0:
            result = data[field].copy()
        elif field in level1:
            result = data.xs(field, axis=1, level=1).copy()
        else:
            return pd.DataFrame(index=data.index)
    else:
        if field not in data.columns:
            return pd.DataFrame(index=data.index)
        result = data[[field]].copy()

    if isinstance(result, pd.Series):
        result = result.to_frame()
    return result


def build_sector_allocation(phase: str) -> pd.DataFrame:
    tickers = tuple(["SPY", *SECTOR_ETFS.values()])
    close, _ = download_adjusted_history(tickers, period="3y")

    rows = []
    spy = _series(close, "SPY")

    for sector, etf in SECTOR_ETFS.items():
        prices = _series(close, etf)
        prior = PHASE_PRIORS.get(phase, PHASE_PRIORS["Neutral"]).get(sector, 50)

        relative_6m = _relative_return(prices, spy, 126)
        relative_12m = _relative_return(prices, spy, 252)
        momentum_signal = 0.60 * _safe(relative_6m) + 0.40 * _safe(relative_12m)
        momentum_score = 50 + 50 * math.tanh(momentum_signal / 0.15)

        trend_score = _trend_score(prices)
        allocation_score = 0.50 * prior + 0.30 * momentum_score + 0.20 * trend_score

        if allocation_score >= 65:
            status = "Overweight"
        elif allocation_score <= 40:
            status = "Underweight"
        else:
            status = "Neutral"

        rows.append(
            {
                "Sector": sector,
                "ETF": etf,
                "Phase prior": round(prior, 1),
                "6M relative return": relative_6m,
                "12M relative return": relative_12m,
                "Momentum score": round(momentum_score, 1),
                "Trend score": round(trend_score, 1),
                "Allocation score": round(allocation_score, 1),
                "Status": status,
            }
        )

    return pd.DataFrame(rows).sort_values("Allocation score", ascending=False).reset_index(drop=True)


def rank_sector_candidates(sector: str) -> pd.DataFrame:
    tickers = tuple([*SECTOR_UNIVERSE[sector], SECTOR_ETFS[sector]])
    close, volume = download_adjusted_history(tickers, period="3y")
    etf_prices = _series(close, SECTOR_ETFS[sector])
    rows = []

    for ticker in SECTOR_UNIVERSE[sector]:
        prices = _series(close, ticker)
        vols = _series(volume, ticker)

        if prices.dropna().shape[0] < 252:
            continue

        prices = prices.dropna()
        returns = prices.pct_change().dropna()
        if returns.empty:
            continue

        annual_vol = float(returns.std() * np.sqrt(252))
        downside = returns[returns < 0]
        downside_vol = float(downside.std() * np.sqrt(252)) if not downside.empty else 0.0
        drawdown = prices / prices.cummax() - 1.0
        max_drawdown = float(drawdown.min())

        aligned_volume = vols.reindex(prices.index).fillna(0)
        dollar_liquidity = float((prices * aligned_volume).tail(60).mean())

        stock_6m = _period_return(prices, 126)
        etf_6m = _period_return(etf_prices, 126)
        relative_to_sector = _safe(stock_6m) - _safe(etf_6m)
        cycle_fit = 50 + 50 * math.tanh(relative_to_sector / 0.20)

        rows.append(
            {
                "Ticker": ticker,
                "Annual volatility": annual_vol,
                "Max drawdown": max_drawdown,
                "Downside volatility": downside_vol,
                "Avg dollar volume": dollar_liquidity,
                "6M return": stock_6m,
                "6M vs sector": relative_to_sector,
                "Cycle fit": cycle_fit,
            }
        )

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame

    frame["Volatility score"] = _higher_is_better(-frame["Annual volatility"])
    frame["Drawdown score"] = _higher_is_better(frame["Max drawdown"])
    frame["Downside score"] = _higher_is_better(-frame["Downside volatility"])
    frame["Liquidity score"] = _higher_is_better(np.log1p(frame["Avg dollar volume"]))

    frame["Stability score"] = (
        0.30 * frame["Volatility score"]
        + 0.30 * frame["Drawdown score"]
        + 0.20 * frame["Downside score"]
        + 0.20 * frame["Liquidity score"]
    )
    frame["Candidate score"] = 0.60 * frame["Stability score"] + 0.40 * frame["Cycle fit"]

    columns = [
        "Ticker",
        "Candidate score",
        "Stability score",
        "Cycle fit",
        "Annual volatility",
        "Max drawdown",
        "6M return",
        "6M vs sector",
        "Avg dollar volume",
    ]
    return frame[columns].sort_values("Candidate score", ascending=False).reset_index(drop=True)


def _series(frame: pd.DataFrame, ticker: str) -> pd.Series:
    if frame.empty:
        return pd.Series(dtype="float64")
    if ticker in frame.columns:
        return frame[ticker].dropna()
    if len(frame.columns) == 1:
        return frame.iloc[:, 0].dropna()
    return pd.Series(dtype="float64")


def _period_return(series: pd.Series, periods: int) -> float | None:
    series = series.dropna()
    if len(series) <= periods:
        return None
    start = float(series.iloc[-periods - 1])
    end = float(series.iloc[-1])
    if start == 0:
        return None
    return end / start - 1.0


def _relative_return(asset: pd.Series, benchmark: pd.Series, periods: int) -> float | None:
    asset_return = _period_return(asset, periods)
    benchmark_return = _period_return(benchmark, periods)
    if asset_return is None or benchmark_return is None:
        return None
    return asset_return - benchmark_return


def _trend_score(prices: pd.Series) -> float:
    prices = prices.dropna()
    if len(prices) < 200:
        return 50.0

    latest = float(prices.iloc[-1])
    ma50 = float(prices.tail(50).mean())
    ma200 = float(prices.tail(200).mean())

    if latest > ma50 > ma200:
        return 80.0
    if latest > ma200:
        return 65.0
    if latest > ma50:
        return 50.0
    if ma50 > ma200:
        return 45.0
    return 30.0


def _higher_is_better(values: pd.Series) -> pd.Series:
    if values.nunique(dropna=True) <= 1:
        return pd.Series(50.0, index=values.index)
    return values.rank(pct=True, method="average") * 100.0


def _safe(value: float | None) -> float:
    return 0.0 if value is None or pd.isna(value) else float(value)
