import streamlit as st

st.set_page_config(
    page_title="Macro Cycle Dashboard",
    page_icon="📈",
    layout="wide"
)

TEXT = {
    "繁體中文": {
        "title": "📈 景氣循環儀表板",
        "language": "語言",
        "cycle": "景氣循環判斷",
        "no_data": "目前尚未連接真實數據",
        "rotation": "產業輪動建議",
        "watchlist": "觀察名單",
        "sectors": ["工業", "礦業", "金融", "能源"],
    },
    "English": {
        "title": "📈 Macro Cycle Dashboard",
        "language": "Language",
        "cycle": "Cycle Regime",
        "no_data": "Real-time data is not connected yet.",
        "rotation": "Sector Rotation View",
        "watchlist": "Watchlist",
        "sectors": ["Industrials", "Miners", "Financials", "Energy"],
    },
    "日本語": {
        "title": "📈 景気循環ダッシュボード",
        "language": "言語",
        "cycle": "景気循環の判断",
        "no_data": "現在、実データにはまだ接続されていません。",
        "rotation": "セクターローテーション",
        "watchlist": "ウォッチリスト",
        "sectors": ["工業", "鉱業", "金融", "エネルギー"],
    }
}

LANG_OPTIONS = {
    "🇹🇼 繁體中文": "繁體中文",
    "🇺🇸 English": "English",
    "🇯🇵 日本語": "日本語"
}

st.sidebar.markdown("## 🌐 Language")

selected = st.sidebar.selectbox(
    "",
    list(LANG_OPTIONS.keys())
)

lang = LANG_OPTIONS[selected]
t = TEXT[lang]
)

t = TEXT[lang]

st.title(t["title"])

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("PMI", "50.0", "0.0")

with col2:
    st.metric("DXY", "100.0", "0.0")

with col3:
    st.metric("VIX", "20.0", "0.0")

with col4:
    st.metric("Copper", "4.50", "0.0")

st.markdown("---")

st.subheader(t["cycle"])
st.info(t["no_data"])

st.subheader(t["rotation"])

for sector in t["sectors"]:
    st.write(f"- {sector}")

st.subheader(t["watchlist"])

watchlist = [
    "CAT - Caterpillar",
    "FCX - Freeport-McMoRan",
    "JPM - JPMorgan",
    "XOM - Exxon Mobil"
]

st.table(watchlist)
