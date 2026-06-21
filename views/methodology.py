import streamlit as st

from core.i18n import get_text


language = st.session_state.get("language", "繁體中文")
t = get_text(language)

st.title(t["method_title"])

if language == "繁體中文":
    st.markdown(
        """
### 模型分成兩層

**第一層：經濟成長分數**

每月將下列訊號轉成 0–100 分，再依權重合成：

| 指標 | 轉換 | 權重 |
|---|---|---:|
| 工業生產 | 6 個月變化率 | 25% |
| 非農就業 | 3 個月變化率 | 20% |
| 失業率 | 3 個月下降幅度 | 20% |
| 房屋開工 | 6 個月變化率 | 15% |
| 10Y–2Y 利差 | 當月平均水準 | 10% |
| Baa 信用利差 | 3 個月收斂幅度 | 10% |

**第二層：階段分類**

- **復甦**：分數仍低於中線，但動能轉強。
- **擴張**：分數位於中線以上，動能未明顯惡化。
- **景氣後期**：分數仍高，但動能轉弱，或通膨偏高且再加速。
- **收縮**：分數低於中線且動能沒有改善；Sahm 指標觸發時會提高收縮判定。
- **資料不足**：關鍵資料尚未齊全。

### 目前限制

1. 目前採用最新修訂後的 FRED 資料。
2. 歷史圖可能受到資料修訂造成的前視偏誤。
3. ETF 價格來自 Yahoo Finance 的非官方資料介面。
4. 階段與配置動作是研究規則，不是保證報酬的交易訊號。

正式回測版應改用 ALFRED 歷史版本資料，並以當時已公布的資料日期重建每一期判斷。
"""
    )
elif language == "日本語":
    st.markdown(
        """
### モデルは二層構造です

**第1層：経済成長スコア**

鉱工業生産、雇用、失業率、住宅着工、イールドカーブ、信用スプレッドを月次で0–100に変換し、加重平均します。

**第2層：局面分類**

- **回復**：スコアは低いがモメンタムが改善。
- **拡大**：スコアが中立以上で、モメンタムが維持。
- **景気後期**：スコアは高いがモメンタムが悪化、またはインフレが再加速。
- **収縮**：スコアが低く、改善が見られない。
- **データ不足**：必要データが不十分。

正式なバックテストには、ALFREDの当時利用可能だったヴィンテージデータが必要です。
"""
    )
else:
    st.markdown(
        """
### The model has two layers

**Layer 1: Economic growth score**

Industrial production, payrolls, unemployment, housing starts, the yield curve, and credit spreads are transformed to monthly 0–100 component scores and combined using fixed weights.

**Layer 2: Phase classification**

- **Recovery**: The score remains below neutral, but momentum is improving.
- **Expansion**: The score is above neutral and momentum has not materially weakened.
- **Late cycle**: The score remains high, but momentum deteriorates or inflation reaccelerates.
- **Contraction**: The score is below neutral without improvement.
- **Insufficient data**: Key observations are missing.

A formal backtest should use ALFRED point-in-time vintages and publication-date alignment to avoid look-ahead bias.
"""
    )

st.warning(t["method_warning"])
st.caption(t["disclaimer"])
