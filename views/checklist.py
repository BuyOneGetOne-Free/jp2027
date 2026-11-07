
import streamlit as st
import pandas as pd
from pathlib import Path


# ---------- 資料設定 ----------
DATA_DIR = Path("data")
CHECKLIST_PATH = DATA_DIR / "checklist.csv"
USERS_PATH = DATA_DIR / "users.csv"

CATEGORIES = [
    "證件與文件",
    "機票與住宿",
    "交通與金錢",
    "行李與衣物",
    "電子用品",
    "其他"
]


# ---------- 讀取旅伴名單 ----------
def load_users():

    try:
        df = pd.read_csv(
            USERS_PATH,
            dtype=str,
            encoding="utf-8-sig"
        )

        df.columns = df.columns.str.strip()

        if not {"user_id", "name"}.issubset(df.columns):
            st.error("users.csv 必須包含 user_id 和 name 欄位")
            return pd.DataFrame(columns=["user_id", "name"])

        df = df[["user_id", "name"]].fillna("")

        return df[
            (df["user_id"] != "") &
            (df["name"] != "")
        ].reset_index(drop=True)

    except FileNotFoundError:
        st.error("找不到 data/users.csv")
        return pd.DataFrame(columns=["user_id", "name"])

    except Exception as e:
        st.error(f"讀取旅伴名單失敗：{e}")
        return pd.DataFrame(columns=["user_id", "name"])


# ---------- 讀取行前準備清單 ----------
def load_checklist():

    if not CHECKLIST_PATH.exists():
        st.error("找不到 data/checklist.csv")
        return pd.DataFrame(
            columns=["category", "item"]
        )

    try:
        df = pd.read_csv(
            CHECKLIST_PATH,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig"
        )

        df.columns = df.columns.str.strip()

        if "item" not in df.columns:
            st.error("checklist.csv 必須包含 item 欄位")
            return pd.DataFrame(
                columns=["category", "item"]
            )

        # 相容舊版只有 item 欄位的 CSV
        if "category" not in df.columns:
            df["category"] = "其他"

        df["item"] = df["item"].astype(str).str.strip()
        df["category"] = (
            df["category"]
            .astype(str)
            .str.strip()
        )

        df.loc[
            df["category"] == "",
            "category"
        ] = "其他"

        df = df[df["item"] != ""].copy()

        # 移除完全重複的項目
        df = df.drop_duplicates(
            subset=["category", "item"]
        )

        return df.reset_index(drop=True)

    except Exception as e:
        st.error(f"讀取行前準備清單失敗：{e}")
        return pd.DataFrame(
            columns=["category", "item"]
        )


# ---------- 個人進度檔案 ----------
def get_progress_path(user_id):

    safe_id = "".join(
        c for c in str(user_id)
        if c.isascii() and (
            c.isalnum() or c in ("_", "-")
        )
    )

    if not safe_id:
        raise ValueError("無效的使用者代號")

    return DATA_DIR / f"{safe_id}_checklist.csv"


# ---------- 讀取個人進度 ----------
def load_progress(user_id):

    path = get_progress_path(user_id)

    if not path.exists():
        return set()

    try:
        df = pd.read_csv(
            path,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig"
        )

        if not {"category", "item", "checked"}.issubset(df.columns):
            return set()

        completed = df[
            df["checked"].str.lower() == "true"
        ]

        return set(
            zip(
                completed["category"],
                completed["item"]
            )
        )

    except Exception as e:
        st.warning(f"讀取進度失敗：{e}")
        return set()


# ---------- 儲存個人進度 ----------
def save_progress(user_id, checklist_df, completed_items):

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    records = []

    for _, row in checklist_df.iterrows():

        category = row["category"]
        item = row["item"]

        records.append({
            "category": category,
            "item": item,
            "checked": (
                (category, item) in completed_items
            )
        })

    progress_df = pd.DataFrame(
        records,
        columns=["category", "item", "checked"]
    )

    progress_df.to_csv(
        get_progress_path(user_id),
        index=False,
        encoding="utf-8-sig"
    )


# ---------- 主頁面 ----------
def show_checklist_page():

    st.title("🧳 關西旅遊行前準備")
    st.caption("2027/02/15 ～ 02/19｜出發前確認清單")

    # ---------- 返回首頁 ----------
    if st.button("🏠 回首頁"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown("---")

    # ---------- 選擇旅伴 ----------
    st.subheader("👤 選擇你的身分")

    users_df = load_users()

    if users_df.empty:
        st.warning("目前沒有可選擇的旅伴")
        return

    user_options = {
        str(row["user_id"]): str(row["name"])
        for _, row in users_df.iterrows()
    }

    user_ids = list(user_options.keys())

    selected_user = st.selectbox(
        "選擇要查看的準備清單",
        options=user_ids,
        format_func=lambda x: user_options[x],
        key="checklist_selected_user"
    )

    st.markdown("---")

    # ---------- 讀取清單 ----------
    checklist_df = load_checklist()

    if checklist_df.empty:
        st.info("目前沒有行前準備項目")
        return

    # ---------- 載入個人進度 ----------
    progress_key = f"checklist_progress_{selected_user}"

    if progress_key not in st.session_state:
        st.session_state[progress_key] = load_progress(
            selected_user
        )

    completed_items = st.session_state[progress_key]

    # ---------- 清單標題 ----------
    st.subheader(
        f"📋 {user_options[selected_user]} 的準備清單"
    )

    st.caption(
        "勾選完成後，請記得按下最下方的「儲存進度」。"
    )

    # ---------- 分類顯示 ----------
    available_categories = (
        CATEGORIES
        + [
            c for c in checklist_df["category"].unique()
            if c not in CATEGORIES
        ]
    )

    for category in available_categories:

        category_df = checklist_df[
            checklist_df["category"] == category
        ]

        if category_df.empty:
            continue

        st.markdown(f"### 📌 {category}")

        for _, row in category_df.iterrows():

            item = row["item"]
            item_key = (category, item)

            checked = st.checkbox(
                item,
                value=item_key in completed_items,
                key=(
                    f"check_{selected_user}_"
                    f"{category}_{item}"
                )
            )

            if checked:
                completed_items.add(item_key)
            else:
                completed_items.discard(item_key)

    # ---------- 完成進度 ----------
    st.markdown("---")
    st.subheader("📊 準備進度")

    total_items = len(checklist_df)
    checked_count = len(completed_items)

    progress = (
        checked_count / total_items
        if total_items > 0
        else 0
    )

    st.progress(progress)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "已完成",
            f"{checked_count} / {total_items}"
        )

    with col2:
        st.metric(
            "完成率",
            f"{progress * 100:.1f}%"
        )

    # ---------- 儲存進度 ----------
    if st.button(
        "💾 儲存準備進度",
        use_container_width=True,
        type="primary"
    ):

        try:
            save_progress(
                selected_user,
                checklist_df,
                completed_items
            )

            st.success("準備進度已儲存！")

        except Exception as e:
            st.error(f"儲存進度失敗：{e}")

    # ---------- 全部完成 ----------
    if total_items > 0 and checked_count == total_items:

        st.success(
            "🎉 所有準備事項都完成了！"
            "可以準備出發去日本囉！"
        )

        celebration_key = (
            f"checklist_celebrated_{selected_user}"
        )

        if not st.session_state.get(celebration_key, False):
            st.balloons()
            st.session_state[celebration_key] = True

    st.markdown("---")

    st.caption(
        "⚠️ 使用 Streamlit Community Cloud 時，"
        "CSV 儲存資料可能因伺服器重啟或重新部署而遺失。"
    )
