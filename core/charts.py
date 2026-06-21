from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


PHASE_COLORS = {
    "Recovery": "rgba(46, 204, 113, 0.14)",
    "Expansion": "rgba(52, 152, 219, 0.12)",
    "Late Cycle": "rgba(241, 196, 15, 0.15)",
    "Contraction": "rgba(231, 76, 60, 0.13)",
    "Neutral": "rgba(127, 140, 141, 0.08)",
}


def build_sector_cycle_chart(
    price: pd.DataFrame,
    model: pd.DataFrame,
    ticker: str,
    title: str,
) -> go.Figure:
    if price.empty:
        return go.Figure()

    close_col = "Adj Close" if "Adj Close" in price.columns else "Close"
    monthly_score = model[["growth_score", "phase"]].copy()

    figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.72, 0.28],
    )

    if all(col in price.columns for col in ["Open", "High", "Low", "Close"]):
        figure.add_trace(
            go.Candlestick(
                x=price.index,
                open=price["Open"],
                high=price["High"],
                low=price["Low"],
                close=price["Close"],
                name=ticker,
            ),
            row=1,
            col=1,
        )
    else:
        figure.add_trace(
            go.Scatter(
                x=price.index,
                y=price[close_col],
                mode="lines",
                name=ticker,
            ),
            row=1,
            col=1,
        )

    figure.add_trace(
        go.Scatter(
            x=monthly_score.index,
            y=monthly_score["growth_score"],
            mode="lines",
            name="Growth score",
        ),
        row=2,
        col=1,
    )

    figure.add_hline(y=50, line_dash="dot", row=2, col=1)

    for start, end, phase in _phase_segments(monthly_score["phase"]):
        figure.add_vrect(
            x0=start,
            x1=end,
            fillcolor=PHASE_COLORS.get(phase, PHASE_COLORS["Neutral"]),
            opacity=1,
            line_width=0,
            layer="below",
        )

    figure.update_layout(
        title=title,
        height=720,
        margin=dict(l=20, r=20, t=55, b=20),
        xaxis_rangeslider_visible=False,
        legend_orientation="h",
        legend_y=1.02,
        hovermode="x unified",
    )
    figure.update_yaxes(title_text="Price", row=1, col=1)
    figure.update_yaxes(title_text="Score", range=[0, 100], row=2, col=1)
    return figure


def _phase_segments(phases: pd.Series):
    clean = phases.dropna()
    if clean.empty:
        return []

    segments = []
    start = clean.index[0]
    current = clean.iloc[0]

    for date, value in clean.iloc[1:].items():
        if value != current:
            segments.append((start, date, current))
            start = date
            current = value

    final_end = clean.index[-1] + pd.offsets.MonthEnd(1)
    segments.append((start, final_end, current))
    return segments
