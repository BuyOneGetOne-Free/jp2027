
import streamlit as st
import pandas as pd
import os
import urllib.parse


# ---------- CSV 路徑 ----------
DATA_PATH = "data/activities.csv"


# ---------- 時段名稱 ----------
SEGMENT_LABELS = {
    "morning": "早上",
    "noon": "中午",
    "afternoon": "下午",
    "night": "晚上"
}


# ---------- 日期與行程標題 ----------
DAY_TITLES = {
    "2/15": "Day 1｜抵達大阪",
    "2/16": "Day 2｜奈良＋大阪夜景",
    "2/17": "Day 3｜神戶一日遊",
    "2/18": "Day 4｜大阪市區（A/B 分隊）",
    "2/19": "Day 5｜返回台灣"
}

DAY_LIST = list(DAY_TITLES.keys())


# ---------- 讀取行程 CSV ----------
def load_activities():

    required_cols = [
        "date",
        "segment",
        "order",
        "team",
        "title",
        "detail",
        "start_time",
        "end_time",
        "link",
        "map_query"
    ]

    if not os.path.exists(DATA_PATH):
        st.error(f"找不到行程資料：{DATA_PATH}")
        return pd.DataFrame(columns=required_cols)

    try:
        # 使用字串讀取，避免時間與日期格式被自動轉換
        df = pd.read_csv(
            DATA_PATH,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig"
        )

        # 移除欄位名稱前後空白
        df.columns = df.columns.str.strip()

        # 缺少欄位時自動補上
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""

        # 清理文字欄位
        for col in required_cols:
            df[col] = df[col].fillna("").astype(str).str.strip()

        # 舊版 CSV 若沒有 team，預設為所有人
        df.loc[df["team"] == "", "team"] = "ALL"
        df["team"] = df["team"].str.upper()

        # 排序用數值
        df["order_num"] = pd.to_numeric(
            df["order"],
            errors="coerce"
        )

        return df

    except Exception as e:
        st.error(f"讀取行程資料失敗：{e}")
        return pd.DataFrame(columns=required_cols)


# ---------- Google Maps 連結 ----------
def build_google_maps_url(row):

    link = row.get("link", "").strip()
    map_query = row.get("map_query", "").strip()
    title = row.get("title", "").strip()

    if link:
        return link

    if map_query.startswith(("https://", "http://")):
        return map_query

    keyword = map_query if map_query else title

    if keyword:
        return (
            "https://www.google.com/maps/search/"
            "?api=1&query="
            + urllib.parse.quote(keyword)
        )

    return ""


# ---------- 判斷是否顯示地圖 ----------
def has_map_location(row):

    # 只有明確提供 link 或 map_query 才顯示地圖
    # 避免早餐自理、飯店休息等活動產生無意義的搜尋
    return bool(
        row.get("link", "") or row.get("map_query", "")
    )


# ---------- 顯示行程卡片 ----------
def render_activity_card(row):

    title = row.get("title", "")
    detail = row.get("detail", "")
    start_time = row.get("start_time", "")
    end_time = row.get("end_time", "")
    team = row.get("team", "ALL")

    with st.container(border=True):

        # A/B 分隊標示
        if team == "A":
            st.caption("🔵 A 隊")

        elif team == "B":
            st.caption("🟠 B 隊")

        st.subheader(title if title else "未命名行程")

        # ---------- 時間 ----------
        if start_time and end_time:
            st.write(
                f"🕒 **時間：** {start_time} ～ {end_time}"
            )

        elif start_time:
            st.write(
                f"🕒 **開始時間：** {start_time}"
            )

        elif end_time:
            st.write(
                f"🕒 **結束時間：** {end_time}"
            )

        else:
            st.caption("🕒 時間尚未確定")

        # ---------- 行程內容 ----------
        if detail:
            st.write(f"📝 **內容：** {detail}")

        # ---------- Google Maps ----------
        if has_map_location(row):

            map_url = build_google_maps_url(row)

            if map_url:
                st.link_button(
                    "📍 開啟 Google Maps",
                    map_url,
                    use_container_width=True
                )


# ---------- 顯示指定時段 ----------
def render_segment_schedule(day_df, segment_key):

    segment_df = day_df[
        day_df["segment"] == segment_key
    ].copy()

    if segment_df.empty:
        st.info(
            f"目前沒有{SEGMENT_LABELS[segment_key]}行程"
        )
        return

    # 按照 CSV 的 order 排序
    segment_df = segment_df.sort_values(
        by="order_num",
        na_position="last",
        kind="stable"
    )

    for _, row in segment_df.iterrows():
        render_activity_card(row)


# ---------- A/B 分隊篩選 ----------
def filter_team_activities(day_df, selected_team):

    if selected_team == "全部":
        return day_df

    if selected_team == "A 隊":
        allowed_teams = ["ALL", "A"]

    elif selected_team == "B 隊":
        allowed_teams = ["ALL", "B"]

    else:
        allowed_teams = ["ALL"]

    return day_df[
        day_df["team"].isin(allowed_teams)
    ].copy()


# ---------- 行程主頁面 ----------
def show_trip_page():

    st.title("🗓️ 關西五日行程")
    st.caption("2027/02/15 ～ 02/19｜大阪・奈良・神戶")

    # ---------- 返回首頁 ----------
    if st.button("🏠 回首頁"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown("---")

    # ---------- 讀取 CSV ----------
    df = load_activities()

    # ---------- 日期選擇 ----------
    st.subheader("📅 請選擇日期")

    if (
        "selected_trip_day" not in st.session_state
        or st.session_state.selected_trip_day not in DAY_LIST
    ):
        st.session_state.selected_trip_day = DAY_LIST[0]

    cols = st.columns(len(DAY_LIST))

    for i, day in enumerate(DAY_LIST):

        with cols[i]:

            if st.button(
                day,
                key=f"trip_day_{day}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.selected_trip_day == day
                    else "secondary"
                )
            ):
                st.session_state.selected_trip_day = day
                st.rerun()

    selected_day = st.session_state.selected_trip_day

    st.markdown("---")

    # ---------- 當日標題 ----------
    st.header(
        DAY_TITLES.get(
            selected_day,
            f"{selected_day} 行程"
        )
    )

    # ---------- 篩選日期 ----------
    day_df = df[
        df["date"] == selected_day
    ].copy()

    if day_df.empty:
        st.warning(
            f"{selected_day} 目前沒有行程資料"
        )
        return

    # ---------- 2/18 分隊選擇 ----------
    if selected_day == "2/18":

        st.subheader("👥 選擇行程隊伍")

        selected_team = st.radio(
            "查看哪一隊的行程？",
            options=["全部", "A 隊", "B 隊"],
            horizontal=True,
            key="selected_trip_team"
        )

        day_df = filter_team_activities(
            day_df,
            selected_team
        )

        if selected_team == "全部":
            st.info("目前顯示 A 隊、B 隊及共同活動。")

        elif selected_team == "A 隊":
            st.info("目前顯示 A 隊及共同活動。")

        else:
            st.info("目前顯示 B 隊及共同活動。")

    # ---------- 當日行程數量 ----------
    st.caption(f"📌 本日共有 {len(day_df)} 項行程")

    # ---------- 四個時段分頁 ----------
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🌅 早上", "☀️ 中午", "🌇 下午", "🌙 晚上"]
    )

    with tab1:
        render_segment_schedule(
            day_df,
            "morning"
        )

    with tab2:
        render_segment_schedule(
            day_df,
            "noon"
        )

    with tab3:
        render_segment_schedule(
            day_df,
            "afternoon"
        )

    with tab4:
        render_segment_schedule(
            day_df,
            "night"
        )

    st.markdown("---")
    st.caption("🇯🇵 Kansai Trip 2027｜行程可能依實際情況調整")
