import streamlit as st

from core.data import last_update_utc, latest_market_snapshot
from core.i18n import get_text
from core.model import build_cycle_model, latest_model_state


language = st.session_state.get("language", "繁體中文")
t = get_text(language)

PHASE_KEY = {
    "Recovery": "recovery",
    "Expansion": "expansion",
    "Late Cycle": "late",
    "Contraction": "contraction",
    "Neutral": "neutral",
}

model = build_cycle_model()
state = latest_model_state(model)
phase_suffix = PHASE_KEY.get(state["phase"], "neutral")

st.title(t["dashboard_title"])

left, right = st.columns([1.15, 1])

with left:
    phase_col, strength_col = st.columns(2)

    with phase_col:
        st.metric(
            t["current_phase"],
            t[f"phase_{phase_suffix}"],
        )

    with strength_col:
        strength = state["signal_strength"]
        st.metric(
            t["signal_strength"],
            "N/A" if strength is None else f"{strength:.0f}/100",
        )

    if strength is not None:
        st.progress(strength / 100.0)

    st.markdown(f"**{t['allocation_action']}**")
    st.info(t[f"action_{phase_suffix}"])

    st.markdown(f"**{t['preferred_sectors']}**")
    st.write(" · ".join(t[f"sector_{phase_suffix}"]))

with right:
    a, b = st.columns(2)
    c, d = st.columns(2)

    with a:
        value = state["growth_score"]
        st.metric(t["growth_score"], "N/A" if value is None else f"{value:.1f}")

    with b:
        value = state["yield_curve"]
        st.metric(t["yield_curve"], "N/A" if value is None else f"{value:.2f}%")

    with c:
        value = state["unemployment_change"]
        st.metric(
            t["unemployment_trend"],
            "N/A" if value is None else f"{value:+.2f} pp",
        )

    with d:
        value = state["credit_spread"]
        st.metric(t["credit_spread"], "N/A" if value is None else f"{value:.2f}%")

@st.dialog(t["details_title"], width="large")
def show_more_indicators():
    st.subheader(t["market_data"])
    market_cols = st.columns(4)
    market_items = [
        ("S&P 500", "^GSPC"),
        ("VIX", "^VIX"),
        ("Copper", "HG=F"),
        ("DXY", "DX-Y.NYB"),
    ]

    for col, (label, ticker) in zip(market_cols, market_items):
        value, change = latest_market_snapshot(ticker)
        with col:
            st.metric(
                label,
                "N/A" if value is None else f"{value:,.2f}",
                "N/A" if change is None else f"{change:+.2f}%",
            )

    st.subheader(t["macro_data"])
    macro_cols = st.columns(4)
    macro_items = [
        ("Fed funds", state["fed_funds"], "%"),
        ("CPI YoY", state["inflation_yoy"], "%"),
        ("Sahm rule", state["sahm"], " pp"),
        ("Model date", state["date"].strftime("%Y-%m") if state["date"] is not None else None, ""),
    ]

    for col, (label, value, unit) in zip(macro_cols, macro_items):
        with col:
            if isinstance(value, str):
                display = value
            else:
                display = "N/A" if value is None else f"{value:.2f}{unit}"
            st.metric(label, display)

if st.button(t["more_indicators"], icon=":material/open_in_new:"):
    show_more_indicators()

st.caption(f"{t['data_updated']}: {last_update_utc()}")
st.caption(t["disclaimer"])
