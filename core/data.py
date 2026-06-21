from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import streamlit as st
import yfinance as yf


FRED_GRAPH_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"


@st.cache_data(ttl=3600, show_spinner=False)
def get_fred_series(series_id: str) -> pd.Series:
    """Download one FRED series through the public CSV graph endpoint."""
    url = FRED_GRAPH_URL.format(series_id=series_id)
    frame = pd.read_csv(url)

    if frame.empty or len(frame.columns) < 2:
        return pd.Series(dtype="float64", name=series_id)

    date_col, value_col = frame.columns[0], frame.columns[1]
    frame[date_col] = pd.to_datetime(frame[date_col], errors="coerce")
    frame[value_col] = pd.to_numeric(frame[value_col], errors="coerce")
    frame = frame.dropna(subset=[date_col, value_col]).set_index(date_col)

    series = frame[value_col].sort_index()
    series.name = series_id
    return series


@st.cache_data(ttl=1800, show_spinner=False)
def get_market_history(ticker: str, period: str = "10y") -> pd.DataFrame:
    """Download OHLCV data and normalize yfinance's possible MultiIndex output."""
    frame = yf.download(
        ticker,
        period=period,
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    if frame.empty:
        return pd.DataFrame()

    if isinstance(frame.columns, pd.MultiIndex):
        last_level = frame.columns.get_level_values(-1)
        if ticker in last_level:
            frame = frame.xs(ticker, axis=1, level=-1)
        else:
            frame.columns = frame.columns.get_level_values(0)

    wanted = [col for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if col in frame.columns]
    frame = frame[wanted].copy()
    frame.index = pd.to_datetime(frame.index).tz_localize(None)
    return frame.dropna(how="all")


def latest_market_snapshot(ticker: str) -> tuple[float | None, float | None]:
    frame = get_market_history(ticker, period="1mo")
    close_col = "Adj Close" if "Adj Close" in frame.columns else "Close"

    if frame.empty or close_col not in frame.columns:
        return None, None

    close = frame[close_col].dropna()
    if close.empty:
        return None, None

    latest = float(close.iloc[-1])
    if len(close) < 2 or float(close.iloc[-2]) == 0:
        return latest, 0.0

    previous = float(close.iloc[-2])
    return latest, (latest / previous - 1.0) * 100.0


def last_update_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
