
import streamlit as st
import pandas as pd
from pathlib import Path


# ---------- CSV 路徑 ----------
FOOD_PATH = Path("data/Food.csv")


# ---------- 日期設定 ----------
DAY_TITLES = {
    "2/15": "Day 1｜抵達大阪",
    "2/16": "Day 2｜奈良一日遊",
    "2/17": "Day 3｜神戶一日遊",
    "2/18": "Day 4｜大阪市區",
    "2/19": "Day 5｜返回台灣"
}

DAY_LIST = list(DAY_TITLES.keys())


# ---------- 餐食名稱與排序 ----------
MEAL_LABELS = {
    "早": "🌅 早餐",
    "午": "☀️ 午餐",
    "晚": "🌙 晚餐",
    "點心": "🍡 點心",
    "宵夜": "🍢 宵夜",
    "晚餐備案": "🍖 晚餐備案"
}

MEAL_ORDER = {
    "早": 1,
    "午": 2,
    "點心": 3,
    "晚": 4,
    "晚餐備案": 5,
    "宵夜": 6
}


# ---------- 讀取 Food.csv ----------
def load_food():

    required_cols = ["日期", "餐食", "內容"]

    if not FOOD_PATH.exists():
        st.error(f"找不到餐食資料：{FOOD_PATH}")
        return pd.DataFrame(columns=required_cols)

    try:
        df = pd.read_csv(
            FOOD_PATH,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig"
        )

        df.columns = df.columns.str.strip()

        missing = [
            col for col in required_cols
            if col not in df.columns
        ]

        if missing:
            st.error(
                "Food.csv 缺少欄位："
                + "、".join(missing)
            )
            return pd.DataFrame(columns=required_cols)

        for col in required_cols:
            df[col] = (
                df[col]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        df = df[
            (df["日期"] != "") &
            (df["內容"] != "")
        ].copy()

        # 依早餐、午餐、點心、晚餐等順序排列
        df["meal_order"] = (
            df["餐食"]
            .map(MEAL_ORDER)
            .fillna(99)
        )

        return df.reset_index(drop=True)

    except Exception as e:
        st.error(f"讀取餐食資料失敗：{e}")
        return pd.DataFrame(columns=required_cols)


# ---------- 顯示餐食卡片 ----------
def render_food_card(row):

    meal = row["餐食"]
    content = row["內容"]

    meal_label = MEAL_LABELS.get(
        meal,
        f"🍽️ {meal}"
    )

    with st.container(border=True):

        st.subheader(meal_label)

        st.write(content)


# ---------- 餐食主頁面 ----------
def show_food_page():

    st.title("🍽️ 關西五日餐食規劃")
    st.caption("2027/02/15 ～ 02/19｜大阪・奈良・神戶")

    # ---------- 返回首頁 ----------
    if st.button("🏠 回首頁"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown("---")

    # ---------- 讀取餐食資料 ----------
    df = load_food()

    # ---------- 日期選擇 ----------
    st.subheader("📅 請選擇日期")

    if (
        "selected_food_day" not in st.session_state
        or st.session_state.selected_food_day not in DAY_LIST
    ):
        st.session_state.selected_food_day = DAY_LIST[0]

    cols = st.columns(len(DAY_LIST))

    for i, day in enumerate(DAY_LIST):

        with cols[i]:

            if st.button(
                day,
                key=f"food_day_{day}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.selected_food_day == day
                    else "secondary"
                )
            ):
                st.session_state.selected_food_day = day
                st.rerun()

    selected_day = st.session_state.selected_food_day

    st.markdown("---")

    # ---------- 當日標題 ----------
    st.header(
        DAY_TITLES.get(
            selected_day,
            f"{selected_day} 餐食"
        )
    )

    # ---------- 篩選當日餐食 ----------
    day_df = df[
        df["日期"] == selected_day
    ].copy()

    if day_df.empty:
        st.info(f"{selected_day} 目前沒有餐食安排")
        return

    # ---------- 依餐食順序排序 ----------
    day_df = day_df.sort_values(
        by="meal_order",
        kind="stable"
    )

    st.caption(
        f"🍴 本日共有 {len(day_df)} 筆餐食安排"
    )

    # ---------- 直接顯示所有餐食 ----------
    for _, row in day_df.iterrows():
        render_food_card(row)

    st.markdown("---")

    st.caption(
        "🇯🇵 Kansai Trip 2027｜"
        "餐食安排可能依實際情況調整"
    )
