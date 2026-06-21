import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="Macro Cycle Dashboard | 景氣循環儀表板",
    page_icon="📈",
    layout="wide"
)

TEXT = {
    "繁體中文": {
        "title": "📈 景氣循環儀表板",
        "cycle": "景氣循環判斷",
        "cycle_msg": "目前已接入市場價格資料，總經資料尚未接入。",
        "rotation": "產業輪動建議",
        "watchlist": "觀察名單",
        "sectors": ["工業", "礦業", "金融", "能源"],
    },
    "English": {
        "title": "📈 Macro Cycle Dashboard",
        "cycle": "Cycle Regime",
        "cycle_msg": "Market price data connected. Macro data is not connected yet.",
        "rotation": "Sector Rotation",
        "watchlist": "Watchlist",
        "sectors": ["Industrials", "Mining", "Financials", "Energy"],
    },
    "日本語": {
        "title": "📈 景気循環ダッシュボード",
        "cycle": "景気循環判定",
        "cycle_msg": "市場価格データは接続済み。マクロデータは未接続です。",
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

SYMBOLS = {
    "DXY": "DX-Y.NYB",
    "VIX": "^VIX",
    "S&P 500": "^GSPC",
    "Copper": "HG=F"
}

@st.cache_data(ttl=1800)
def get_price(symbol):
    @st.cache_data(ttl=1800)
def get_price(symbol):
    try:
        data = yf.download(
            symbol,
            period="7d",
            interval="1d",
            progress=False,
            auto_adjust=False
        )

        if data.empty or "Close" not in data:
            return None, None

        close = data["Close"]

        # yfinance 有時候會回傳 DataFrame，多 ticker 結構要壓成 Series
        if hasattr(close, "columns"):
            close = close.iloc[:, 0]

        close = close.dropna()

        if len(close) == 0:
            return None, None

        latest = close.iloc[-1].item()

        if len(close) < 2:
            return latest, 0.0

        previous = close.iloc[-2].item()

        if previous == 0:
            return latest, 0.0

        change_pct = (latest - previous) / previous * 100

        return latest, change_pct

    except Exception:
        return None, None
)

lang = LANG_OPTIONS[selected]
t = TEXT[lang]

st.title(t["title"])
st.divider()

col1, col2, col3, col4 = st.columns(4)

metrics = [
    ("DXY", SYMBOLS["DXY"], col1),
    ("VIX", SYMBOLS["VIX"], col2),
    ("S&P 500", SYMBOLS["S&P 500"], col3),
    ("Copper", SYMBOLS["Copper"], col4),
]

for name, symbol, col in metrics:
    value, change = get_price(symbol)

    with col:
        if value is None:
            st.metric(name, "N/A", "N/A")
        else:
            st.metric(
                label=name,
                value=f"{value:,.2f}",
                delta=f"{change:.2f}%"
            )

st.divider()

st.subheader(t["cycle"])
st.info(t["cycle_msg"])

st.subheader(t["rotation"])

for sector in t["sectors"]:
    st.write(f"• {sector}")

st.subheader(t["watchlist"])

watchlist = [
    {"Ticker": "CAT", "Company": "Caterpillar", "Theme": "Industrials"},
    {"Ticker": "FCX", "Company": "Freeport-McMoRan", "Theme": "Copper / Mining"},
    {"Ticker": "JPM", "Company": "JPMorgan", "Theme": "Financials"},
    {"Ticker": "XOM", "Company": "Exxon Mobil", "Theme": "Energy"},
]

st.dataframe(
    watchlist,
    use_container_width=True,
    hide_index=True
)
