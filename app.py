import streamlit as st

st.set_page_config(
    page_title="景氣循環儀表板",
    layout="wide"
)

st.title("景氣循環儀表板")

st.metric("PMI", "50.0")
st.metric("DXY", "100.0")
st.metric("VIX", "20.0")

st.success("系統建置中")
