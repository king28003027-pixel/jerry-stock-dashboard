import streamlit as st

from core.i18n import LANG_OPTIONS

st.set_page_config(
    page_title="Macro Cycle Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "language" not in st.session_state:
    st.session_state.language = "繁體中文"

header_left, header_right = st.columns([8, 2])

with header_left:
    st.markdown("### Macro Cycle Dashboard")

with header_right:
    selected_label = st.selectbox(
        "Language",
        options=list(LANG_OPTIONS.keys()),
        index=list(LANG_OPTIONS.values()).index(st.session_state.language),
        label_visibility="collapsed",
        key="global_language_selector",
    )
    st.session_state.language = LANG_OPTIONS[selected_label]

pages = [
    st.Page(
        "views/dashboard.py",
        title="Dashboard",
        icon=":material/dashboard:",
        default=True,
    ),
    st.Page(
        "views/sector_allocation.py",
        title="Sector Allocation",
        icon=":material/finance_mode:",
    ),
    st.Page(
        "views/cycle_chart.py",
        title="Cycle Chart",
        icon=":material/candlestick_chart:",
    ),
    st.Page(
        "views/methodology.py",
        title="Methodology",
        icon=":material/science:",
    ),
]

navigation = st.navigation(pages, position="top")
navigation.run()
