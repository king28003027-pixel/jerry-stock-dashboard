import pandas as pd
import streamlit as st

from core.i18n import get_text
from core.model import build_cycle_model, latest_model_state
from core.sector import build_sector_allocation, rank_sector_candidates


language = st.session_state.get("language", "繁體中文")
t = get_text(language)

model = build_cycle_model()
state = latest_model_state(model)
allocation = build_sector_allocation(state["phase"])

st.title(t["sector_page_title"])

overweight = allocation[allocation["Status"] == "Overweight"]
underweight = allocation[allocation["Status"] == "Underweight"]
neutral = allocation[allocation["Status"] == "Neutral"]

left, right = st.columns(2)

with left:
    st.subheader(t["overweight"])
    if overweight.empty:
        st.write("—")
    else:
        st.dataframe(
            overweight[["Sector", "ETF", "Allocation score"]].head(5),
            hide_index=True,
            use_container_width=True,
        )

with right:
    st.subheader(t["underweight"])
    if underweight.empty:
        st.write("—")
    else:
        st.dataframe(
            underweight[["Sector", "ETF", "Allocation score"]]
            .sort_values("Allocation score")
            .head(5),
            hide_index=True,
            use_container_width=True,
        )

with st.expander(t["neutral"]):
    if neutral.empty:
        st.write("—")
    else:
        st.dataframe(
            neutral[
                [
                    "Sector",
                    "ETF",
                    "Allocation score",
                    "6M relative return",
                    "12M relative return",
                    "Trend score",
                ]
            ],
            hide_index=True,
            use_container_width=True,
            column_config={
                "6M relative return": st.column_config.NumberColumn(format="%.2f%%"),
                "12M relative return": st.column_config.NumberColumn(format="%.2f%%"),
            },
        )

st.divider()
st.subheader(t["research_candidates"])

selected_sector = st.selectbox(
    "Sector",
    options=allocation["Sector"].tolist(),
    index=0,
)

candidates = rank_sector_candidates(selected_sector).head(3).copy()

if candidates.empty:
    st.warning(t["no_data"])
else:
    percent_columns = [
        "Annual volatility",
        "Max drawdown",
        "6M return",
        "6M vs sector",
    ]
    for column in percent_columns:
        candidates[column] = candidates[column] * 100.0

    st.dataframe(
        candidates,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Candidate score": st.column_config.NumberColumn(format="%.1f"),
            "Stability score": st.column_config.NumberColumn(format="%.1f"),
            "Cycle fit": st.column_config.NumberColumn(format="%.1f"),
            "Annual volatility": st.column_config.NumberColumn(format="%.1f%%"),
            "Max drawdown": st.column_config.NumberColumn(format="%.1f%%"),
            "6M return": st.column_config.NumberColumn(format="%.1f%%"),
            "6M vs sector": st.column_config.NumberColumn(format="%.1f%%"),
            "Avg dollar volume": st.column_config.NumberColumn(format="$%.0f"),
        },
    )

st.info(t["ranking_note"])
st.caption(t["universe_note"])
st.caption(t["disclaimer"])
