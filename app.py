
import streamlit as st
from router import show_page

# ---------- 網站基本設定 ----------
st.set_page_config(
    page_title="2027 關西五日自由行",
    page_icon="🇯🇵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- 網站主程式 ----------
show_page()
