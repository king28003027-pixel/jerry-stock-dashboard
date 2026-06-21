import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(
    page_title="Macro Cycle Dashboard | 景氣循環儀表板",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

TEXT = {
    "繁體中文": {
        "title": "📈 景氣循環儀表板",
        "market": "市場指標",
        "macro": "總經指標",
        "cycle": "景氣循環判斷",
        "score": "景氣信心分數",
        "regime": "目前階段",
        "rotation": "產業輪動建議",
        "watchlist": "觀察名單",
        "regimes": {
            "Recovery": "復甦期",
            "Expansion": "成長期",
            "Late Cycle": "景氣後期",
            "Risk-Off": "風險收縮",
            "Neutral": "中性 / 資料不足"
        },
        "sector_map": {
            "Recovery": ["工業", "礦業", "金融"],
            "Expansion": ["工業", "能源", "金融"],
            "Late Cycle": ["能源", "原物料", "防禦型"],
            "Risk-Off": ["現金", "公債", "防禦型"],
            "Neutral": ["分散配置", "降低槓桿", "等待確認"]
        }
    },
    "English": {
        "title": "📈 Macro Cycle Dashboard",
        "market": "Market Indicators",
        "macro": "Macro Indicators",
        "cycle": "Cycle Regime",
        "score": "Cycle Confidence Score",
        "regime": "Current Regime",
        "rotation": "Sector Rotation",
        "watchlist": "Watchlist",
        "regimes": {
            "Recovery": "Recovery",
            "Expansion": "Expansion",
            "Late Cycle": "Late Cycle",
            "Risk-Off": "Risk-Off",
            "Neutral": "Neutral / Insufficient Data"
        },
        "sector_map": {
            "Recovery": ["Industrials", "Mining", "Financials"],
            "Expansion": ["Industrials", "Energy", "Financials"],
            "Late Cycle": ["Energy", "Materials", "Defensive"],
            "Risk-Off": ["Cash", "Treasuries", "Defensive"],
            "Neutral": ["Diversified", "Lower leverage", "Wait for confirmation"]
        }
    },
    "日本語": {
        "title": "📈 景気循環ダッシュボード",
        "market": "市場指標",
        "macro": "マクロ指標",
        "cycle": "景気循環判定",
        "score": "景気信頼スコア",
        "regime": "現在の局面",
        "rotation": "セクターローテーション",
        "watchlist": "ウォッチリスト",
        "regimes": {
            "Recovery": "回復期",
            "Expansion": "拡大期",
            "Late Cycle": "景気後期",
            "Risk-Off": "リスクオフ",
            "Neutral": "中立 / データ不足"
        },
        "sector_map": {
            "Recovery": ["工業", "鉱業", "金融"],
            "Expansion": ["工業", "エネルギー", "金融"],
            "Late Cycle": ["エネルギー", "素材", "防御型"],
            "Risk-Off": ["現金", "国債", "防御型"],
            "Neutral": ["分散投資", "レバレッジ低下", "確認待ち"]
        }
    }
}

LANG_OPTIONS = {
    "🇹🇼 繁體中文": "繁體中文",
    "🇺🇸 English": "English",
    "🇯🇵 日本語": "日本語"
}

MARKET_SYMBOLS = {
    "DXY": "DX-Y.NYB",
    "VIX": "^VIX",
    "S&P 500": "^GSPC",
    "Copper": "HG=F"
}

FRED_SERIES = {
    "Unemployment Rate": "UNRATE",
    "Fed Funds Rate": "FEDFUNDS",
    "10Y-2Y Spread": "T10Y2Y",
    "CPI": "CPIAUCSL"
}


@st.cache_data(ttl=1800)
def get_market_price(symbol):
    try:
        data = yf.download(symbol, period="7d", interval="1d", progress=False, auto_adjust=False)
        if data.empty or "Close" not in data:
            return None, None

        close = data["Close"]
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


@st.cache_data(ttl=3600)
def get_fred_value(series_id):
    try:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        data = pd.read_csv(url)

        if data.empty:
            return None, None

        data.columns = ["Date", "Value"]
        data["Value"] = pd.to_numeric(data["Value"], errors="coerce")
        data = data.dropna()

        if len(data) == 0:
            return None, None

        latest = data["Value"].iloc[-1]

        if len(data) < 2:
            return latest, 0.0

        previous = data["Value"].iloc[-2]
        change = latest - previous

        return latest, change

    except Exception:
        return None, None


def calculate_cycle_regime(market_data, macro_data):
    score = 50

    vix = market_data.get("VIX", {}).get("value")
    vix_chg = market_data.get("VIX", {}).get("change")

    spx_chg = market_data.get("S&P 500", {}).get("change")
    copper_chg = market_data.get("Copper", {}).get("change")
    dxy_chg = market_data.get("DXY", {}).get("change")

    unemployment_chg = macro_data.get("Unemployment Rate", {}).get("change")
    fed_chg = macro_data.get("Fed Funds Rate", {}).get("change")
    spread = macro_data.get("10Y-2Y Spread", {}).get("value")

    if vix is not None:
        if vix < 18:
            score += 10
        elif vix > 25:
            score -= 15

    if vix_chg is not None:
        if vix_chg < 0:
            score += 5
        elif vix_chg > 5:
            score -= 5

    if spx_chg is not None:
        if spx_chg > 0:
            score += 5
        else:
            score -= 5

    if copper_chg is not None:
        if copper_chg > 0:
            score += 10
        else:
            score -= 5

    if dxy_chg is not None:
        if dxy_chg < 0:
            score += 5
        else:
            score -= 3

    if unemployment_chg is not None:
        if unemployment_chg < 0:
            score += 10
        elif unemployment_chg > 0:
            score -= 10

    if fed_chg is not None:
        if fed_chg < 0:
            score += 5
        elif fed_chg > 0:
            score -= 5

    if spread is not None:
        if spread > 0:
            score += 10
        elif spread < -0.5:
            score -= 10

    score = max(0, min(100, score))

    if score >= 70 and copper_chg is not None and copper_chg > 0:
        regime = "Expansion"
    elif score >= 60:
        regime = "Recovery"
    elif score <= 40:
        regime = "Risk-Off"
    elif vix is not None and vix > 22:
        regime = "Late Cycle"
    else:
        regime = "Neutral"

    return regime, score


header_left, header_right = st.columns([8, 2])

with header_right:
    selected = st.selectbox(
        label="Language",
        options=list(LANG_OPTIONS.keys()),
        label_visibility="collapsed"
    )

lang = LANG_OPTIONS[selected]
t = TEXT[lang]

with header_left:
    st.title(t["title"])

st.divider()

market_data = {}
macro_data = {}

st.subheader(t["market"])
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

market_metrics = [
    ("DXY", MARKET_SYMBOLS["DXY"], m_col1),
    ("VIX", MARKET_SYMBOLS["VIX"], m_col2),
    ("S&P 500", MARKET_SYMBOLS["S&P 500"], m_col3),
    ("Copper", MARKET_SYMBOLS["Copper"], m_col4),
]

for name, symbol, col in market_metrics:
    value, change = get_market_price(symbol)
    market_data[name] = {"value": value, "change": change}

    with col:
        if value is None:
            st.metric(name, "N/A", "N/A")
        else:
            st.metric(name, f"{value:,.2f}", f"{change:.2f}%")

st.divider()

st.subheader(t["macro"])
f_col1, f_col2, f_col3, f_col4 = st.columns(4)

fred_metrics = [
    ("Unemployment Rate", FRED_SERIES["Unemployment Rate"], f_col1, "%"),
    ("Fed Funds Rate", FRED_SERIES["Fed Funds Rate"], f_col2, "%"),
    ("10Y-2Y Spread", FRED_SERIES["10Y-2Y Spread"], f_col3, "%"),
    ("CPI", FRED_SERIES["CPI"], f_col4, ""),
]

for name, series_id, col, unit in fred_metrics:
    value, change = get_fred_value(series_id)
    macro_data[name] = {"value": value, "change": change}

    with col:
        if value is None:
            st.metric(name, "N/A", "N/A")
        else:
            st.metric(name, f"{value:,.2f}{unit}", f"{change:+.2f}")

st.divider()

regime, score = calculate_cycle_regime(market_data, macro_data)

st.subheader(t["cycle"])

c1, c2 = st.columns(2)

with c1:
    st.metric(t["regime"], t["regimes"][regime])

with c2:
    st.metric(t["score"], f"{score}/100")

st.progress(score / 100)

st.subheader(t["rotation"])

for sector in t["sector_map"][regime]:
    st.write(f"• {sector}")

st.subheader(t["watchlist"])

watchlist = [
    {"Ticker": "CAT", "Company": "Caterpillar", "Theme": "Industrials"},
    {"Ticker": "FCX", "Company": "Freeport-McMoRan", "Theme": "Copper / Mining"},
    {"Ticker": "JPM", "Company": "JPMorgan", "Theme": "Financials"},
    {"Ticker": "XOM", "Company": "Exxon Mobil", "Theme": "Energy"},
]

st.dataframe(watchlist, use_container_width=True, hide_index=True)
