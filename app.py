import streamlit as st

# =========================
# Page Config
# =========================

st.set_page_config(
    page_title="Macro Cycle Dashboard | 景氣循環儀表板",
    page_icon="📈",
    layout="wide"
)

# =========================
# Language Pack
# =========================

TEXT = {
    "繁體中文": {
        "title": "📈 景氣循環儀表板",
        "language": "語言",
        "cycle": "景氣循環判斷",
        "cycle_msg": "目前尚未連接真實數據",
        "rotation": "產業輪動建議",
        "watchlist": "觀察名單",
        "sectors": ["工業", "礦業", "金融", "能源"],
    },

    "English": {
        "title": "📈 Macro Cycle Dashboard",
        "language": "Language",
        "cycle": "Cycle Regime",
        "cycle_msg": "Real-time data not connected yet.",
        "rotation": "Sector Rotation",
        "watchlist": "Watchlist",
        "sectors": ["Industrials", "Mining", "Financials", "Energy"],
    },

    "日本語": {
        "title": "📈 景気循環ダッシュボード",
        "language": "言語",
        "cycle": "景気循環判定",
        "cycle_msg": "現在リアルタイムデータ未接続",
        "rotation": "セクターローテーション",
        "watchlist": "ウォッチリスト",
        "sectors": ["工業", "鉱業", "金融", "エネルギー"],
    }
}

# =========================
# Language Selector
# =========================

LANG_OPTIONS = {
    "🇹🇼 繁體中文": "繁體中文",
    "🇺🇸 English": "English",
    "🇯🇵 日本語": "日本語"
}

st.sidebar.markdown("## 🌐 Language")

selected = st.sidebar.selectbox(
    label="Language",
    options=list(LANG_OPTIONS.keys()),
    label_visibility="collapsed"
)

lang = LANG_OPTIONS[selected]

t = TEXT[lang]

# =========================
# Title
# =========================

st.title(t["title"])

st.divider()

# =========================
# KPI Area
# =========================

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
        label="Copper",
        value="4.50",
        delta="0.0"
    )

st.divider()

# =========================
# Cycle
# =========================

st.subheader(t["cycle"])

st.info(t["cycle_msg"])

# =========================
# Rotation
# =========================

st.subheader(t["rotation"])

for sector in t["sectors"]:
    st.write(f"• {sector}")

# =========================
# Watchlist
# =========================

st.subheader(t["watchlist"])

watchlist = [
    {"Ticker": "CAT", "Company": "Caterpillar"},
    {"Ticker": "FCX", "Company": "Freeport-McMoRan"},
    {"Ticker": "JPM", "Company": "JPMorgan"},
    {"Ticker": "XOM", "Company": "Exxon Mobil"},
]

st.dataframe(
    watchlist,
    use_container_width=True,
    hide_index=True
)
