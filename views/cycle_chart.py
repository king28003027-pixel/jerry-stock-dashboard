import streamlit as st

from core.charts import build_sector_cycle_chart
from core.data import get_market_history
from core.i18n import get_text
from core.model import build_cycle_model


language = st.session_state.get("language", "繁體中文")
t = get_text(language)

SECTOR_ETFS = {
    "XLI — Industrials": "XLI",
    "XLF — Financials": "XLF",
    "XLE — Energy": "XLE",
    "XLB — Materials": "XLB",
    "XLY — Consumer Discretionary": "XLY",
    "XLK — Technology": "XLK",
    "XLU — Utilities": "XLU",
    "XLP — Consumer Staples": "XLP",
    "XLV — Health Care": "XLV",
}

PERIODS = {
    "5Y": "5y",
    "10Y": "10y",
    "20Y": "20y",
    "MAX": "max",
}

st.title(t["chart_title"])

control_left, control_right = st.columns(2)

with control_left:
    sector_label = st.selectbox(t["sector_etf"], list(SECTOR_ETFS.keys()))

with control_right:
    period_label = st.selectbox(t["period"], list(PERIODS.keys()), index=1)

ticker = SECTOR_ETFS[sector_label]
price = get_market_history(ticker, PERIODS[period_label])
model = build_cycle_model()

if price.empty or model.empty:
    st.warning(t["no_data"])
else:
    visible_model = model.loc[model.index >= price.index.min()]
    figure = build_sector_cycle_chart(
        price=price,
        model=visible_model,
        ticker=ticker,
        title=f"{ticker} — {t['chart_title']}",
    )
    st.plotly_chart(figure, use_container_width=True)

    legend_cols = st.columns(4)
    labels = [
        ("Recovery", t["phase_recovery"]),
        ("Expansion", t["phase_expansion"]),
        ("Late Cycle", t["phase_late"]),
        ("Contraction", t["phase_contraction"]),
    ]
    for col, (_, localized) in zip(legend_cols, labels):
        with col:
            st.caption(localized)

st.caption(t["method_warning"])
st.caption(t["disclaimer"])
