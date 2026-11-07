
import streamlit as st
import pandas as pd
import random
from datetime import date


# ---------- 旅遊基本資料 ----------
TRIP_START = date(2027, 2, 15)
TRIP_END = date(2027, 2, 19)

HOTEL_NAME = "APA Hotel & Resort Osaka Namba Ekimae Tower"


# ---------- 讀取日本小知識 ----------
def load_japan_facts(csv_path="data/japan_facts.csv"):
    try:
        df = pd.read_csv(csv_path)

        if "fact" not in df.columns:
            st.warning("日本小知識 CSV 缺少 fact 欄位")
            return []

        return df["fact"].dropna().astype(str).tolist()

    except FileNotFoundError:
        st.warning("找不到 data/japan_facts.csv")
        return []

    except Exception as e:
        st.error(f"讀取日本小知識失敗：{e}")
        return []


# ---------- 首頁 ----------
def show_home():

    st.title("🇯🇵 2027 關西五日自由行")
    st.caption("大阪・奈良・神戶｜2027/02/15 ～ 02/19")
    st.caption("本網站操作時應以回首頁為主，避免使用瀏覽器的返回鍵。")
    st.caption("若瀏覽器為深色主題，請切換為淺色主題以獲得最佳瀏覽體驗。")
    st.markdown("---")

    # ---------- 旅遊倒數 ----------
    st.subheader("⏳ 旅遊倒數")

    today = date.today()
    days_left = (TRIP_START - today).days

    if days_left > 0:
        st.metric("距離出發還有", f"{days_left} 天")

    elif TRIP_START <= today <= TRIP_END:
        trip_day = (today - TRIP_START).days + 1
        st.success(f"🎉 旅遊進行中！今天是 Day {trip_day}")

    else:
        st.success("🎉 2027 關西之旅已經結束！")

    st.markdown("---")

    # ---------- 旅遊基本資訊 ----------
    st.subheader("✈️ 旅遊基本資訊")

    col1, col2 = st.columns(2)

    with col1:
        st.info(
            "📅 **旅遊日期**\n\n"
            "2027/02/15 ～ 02/19\n\n"
            "5 天 4 夜"
        )

    with col2:
        st.info(
            "📍 **旅遊地點**\n\n"
            "大阪・奈良・神戶\n\n"
            "日本關西地區"
        )

    # ---------- 航班資訊 ----------
    st.subheader("🛫 航班資訊")

    with st.container(border=True):
        st.markdown("**去程｜CX564**")
        st.write("2027/02/15（一）")
        st.write("TPE 桃園國際機場 → KIX 關西國際機場")
        st.write("11:15 起飛 → 14:45 抵達")
        st.caption("以上時間皆為當地時間，請以機票資訊為準。")

    with st.container(border=True):
        st.markdown("**回程｜CX565**")
        st.write("2027/02/19（五）")
        st.write("KIX 關西國際機場 → TPE 桃園國際機場")
        st.write("16:15 起飛 → 18:30 抵達")
        st.caption("以上時間皆為當地時間，請以機票資訊為準。")

    # ---------- 住宿資訊 ----------
    st.subheader("🏨 住宿資訊")

    with st.container(border=True):
        st.markdown("**APA 度假酒店大阪難波站前塔樓**")
        st.write(HOTEL_NAME)
        st.write("入住：2027/02/15")
        st.write("退房：2027/02/19")
        st.write("共 4 晚，全程入住同一間飯店。")

        st.link_button(
            "📍 查看飯店 Google Maps",
            "https://www.google.com/maps/search/?api=1&query=APA+Hotel+Resort+Osaka+Namba+Ekimae+Tower",
            use_container_width=True
        )

    st.markdown("---")

    # ---------- 網站功能 ----------
    st.subheader("📱 網站功能")

    st.write("請選擇你想使用的功能：")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "🗓️ 行程",
            use_container_width=True
        ):
            st.session_state.page = "trip"
            st.rerun()

    with col2:
        if st.button(
            "🍽️ 餐食",
            use_container_width=True
        ):
            st.session_state.page = "food"
            st.rerun()

    with col3:
        if st.button(
            "🧳 行前準備",
            use_container_width=True
        ):
            st.session_state.page = "checklist"
            st.rerun()

    # ---------- 網站使用說明 ----------
    st.markdown("### 📘 網站使用說明")

    usage_text = """
1. 【行程】
   查看 2027/02/15～02/19 的每日行程。
   包含時間、交通方式及 Google Maps。
   2/18 可以切換 A 隊或 B 隊的行程。

2. 【食物】
    查看每日餐食規劃。

3. 【行前準備】
   確認護照、行李、交通卡及其他準備事項。
   可以勾選已完成的項目。

4. 【日本小知識】
   每次按下 Reroll 可以抽取新的日本小知識。
"""

    st.text_area(
        "使用說明",
        usage_text.strip(),
        height=250,
        disabled=True
    )

    st.markdown("---")

    # ---------- 日本小知識 ----------
    st.subheader("🎌 抽一個日本小知識")

    facts = load_japan_facts()

    if "current_fact" not in st.session_state:
        st.session_state.current_fact = (
            random.choice(facts)
            if facts
            else "目前沒有可顯示的小知識。"
        )

    col_fact, col_btn = st.columns([4, 1])

    with col_fact:
        st.text_area(
            "日本小知識",
            st.session_state.current_fact,
            height=120,
            disabled=True
        )

    with col_btn:
        if st.button(
            "🎲 Reroll",
            use_container_width=True
        ):
            if facts:
                st.session_state.current_fact = random.choice(facts)
            else:
                st.session_state.current_fact = "目前沒有可顯示的小知識。"

            st.rerun()

    st.markdown("---")
    st.caption("🇯🇵 Kansai Trip 2027｜Powered by Streamlit")
