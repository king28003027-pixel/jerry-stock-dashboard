import streamlit as st

st.set_page_config(
    page_title="景氣循環儀表板",
    page_icon="📈",
    layout="wide"
)

st.title("📈 景氣循環儀表板")

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="PMI",
        value="50.0",
        delta="0.0"
    )

with col2:
    st.metric(
        label="DXY",
        value="100.0",
        delta="0.0"
    )

with col3:
    st.metric(
        label="VIX",
        value="20.0",
        delta="0.0"
    )

with col4:
    st.metric(
        label="銅價",
        value="4.50",
        delta="0.0"
    )

st.markdown("---")

st.subheader("景氣循環判斷")

st.info("目前尚未連接真實數據")

st.subheader("產業輪動建議")

st.write("""
- 工業
- 礦業
- 金融
- 能源
""")

st.subheader("觀察名單")

watchlist = [
    "CAT - Caterpillar",
    "FCX - Freeport-McMoRan",
    "JPM - JPMorgan",
    "XOM - Exxon Mobil"
]

st.table(watchlist)
