import streamlit as st
import pandas as pd
from datetime import datetime

# ページの設定
st.set_page_config(page_title="イチハブ（旧イチゴイチエ・フィッシュ）デモ", layout="wide")

# --- 1. デモ用の疑似データベース＆チャット履歴の初期化 ---
if "fish_db" not in st.session_state:
    st.session_state.fish_db = pd.DataFrame([
        {
            "id": 1, "seller": "横浜仲卸・魚源", "fish_name": "マグロ中落ち (規格外)", 
            "price": 2000, "scope": "フォロー限定", "group": "横浜中央市場", "distance": 0,
            "processed": "🩸 エラ・内臓除去（水洗血抜き済）"
        },
        {
            "id": 2, "seller": "豊海丸 (遊漁船)", "fish_name": "大漁アジ (30匹・釣りすぎ)", 
            "price": 3000, "scope": "距離限定 (10km以内)", "group": "江の島漁港", "distance": 5,
            "processed": "🧊 氷締め（水揚げ直後処理）"
        },
        {
            "id": 3, "seller": "銚子水産", "fish_name": "高級ホウボウ (1匹・一点物)", 
            "price": 1500, "scope": "全体公開", "group": "銚子漁港", "distance": 80,
            "processed": "🩸 神経締め・血抜き済"
        }
    ])

if "chat_db" not in st.session_state:
    st.session_state.chat_db = [
        {"room": "横浜仲卸・魚源", "user": "横浜仲卸・魚源", "avatar": "👤", "msg": "今日の中落ち、マジで質がいいよ！大将どう？"},
        {"room": "横浜中央市場 グループ", "user": "市場事務局", "avatar": "📢", "msg": "明日の開市時間は通常通りです。余り物の出品はお早めに。"},
    ]

# 💡 新機能用：市場カレンダーのモックデータ（2026年6月）
# True: 通常開場（当日配送あり）, False: 休市（ロッカー直取りのみ）
if "market_calendar" not in st.session_state:
    st.session_state.market_calendar = {
        "2026-06-01": {"open": True, "note": "通常開場日"},
        "2026-06-02": {"open": True, "note": "通常開場日"},
        "2026-06-03": {"open": False, "note": "水曜休市日（スマートロッカー直取りのみ対応）"},
        "2026-06-04": {"open": True, "note": "通常開場日"},
    }

# 💡 新機能用：Discord風フォロワーオンラインステータス
if "user_status" not in st.session_state:
    st.session_state.user_status = {
        "横浜仲卸・魚源": {"status": "online", "icon": "🟢"},
        "豊海丸 (遊漁船)": {"status": "away", "icon": "🟡"},
        "銚子水産": {"status": "offline", "icon": "⚫"}
    }

# 画面遷移フラグ
if "current_room" not in st.session_state:
    st.session_state.current_room = None


# --- 2. 【全画面チャットモード】 ---
if st.session_state.current_room:
    col_back, col_title = st.columns([1, 10])
    with col_back:
        if st.button("⬅️ 戻る"):
            st.session_state.current_room = None
            st.rerun()
            
    with col_title:
        st.header(f"💬 {st.session_state.current_room}")
        st.caption("顔見知り同士の専用・安全な連絡網")
    
    st.write("---")
    
    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.chat_db:
            if chat["room"] == st.session_state.current_room:
                role = "user" if chat["user"] == "あなた" else "assistant"
                avatar = "🍳" if chat["user"] == "あなた" else chat["avatar"]
                
                with st.chat_message(role, avatar=avatar):
                    st.markdown(f"**{chat['user']}**")
                    st.write(chat["msg"])
    
    if user_msg := st.chat_input("メッセージを入力...（Enterで送信）"):
        st.session_state.chat_db.append({
            "room": st.session_state.current_room,
            "user": "あなた",
            "avatar": "🍳",
            "msg": user_msg
        })
        st.rerun()


# --- 3. 【通常画面モード】 ---
else:
    st.title("🏛️ 卸売市場直結ネットワーク「イチハブ」")
    st.caption("〜 倉庫なし・トラックなし。すでにある市場と定期便をデータで繋ぐ 〜")
    
    # --- サイドバー：コントロールパネル ---
    st.sidebar.header("👥 役割・画面切り替え")
    user_type = st.sidebar.radio("役割を選択:", ["出品者 (仲卸・船長)", "買い手 (飲食店)"])
    
    # 💡 新機能：デモ用カレンダーシミュレーター
    st.sidebar.write("---")
    st.sidebar.subheader("📅 デモ用カレンダー設定")
    selected_date_obj = st.sidebar.date_input(
        "シミュレートする日付:",
        value=datetime.strptime("2026-06-01", "%Y-%m-%d")
    )
    selected_date = selected_date_obj.strftime("%Y-%m-%d")
    st.sidebar.caption("※『2026-06-03』を選ぶと水曜休市日（ロッカーモード）を実演できます")
    
    # 連絡網一覧（Discord風ステータス統合）
    st.sidebar.write("---")
    st.sidebar.subheader("📩 DM・連絡網一覧")
    
    if st.sidebar.button("🌐 横浜中央市場 グループ"):
        st.session_state.current_room = "横浜中央市場 グループ"
        st.rerun()
        
    st.sidebar.caption("↓フォロワーステータス（Discord風）")
    
    # 魚源のステータス取得
    yugen_status = st.session_state.user_status["横浜仲卸・魚源"]["icon"]
    if st.sidebar.button(f"{yugen_status} 横浜仲卸・魚源 (2)"):
        st.session_state.current_room = "横浜仲卸・魚源"
        st.rerun()
        
    # 豊海丸のステータス取得
    toyomi_status = st.session_state.user_status["豊海丸 (遊漁船)"]["icon"]
    if st.sidebar.button(f"{toyomi_status} 豊海丸 (遊漁船)"):
        st.session_state.current_room = "豊海丸 (遊漁船)"
        st.rerun()

    # --- 💡 新機能：カレンダー連動バナーの表示 ---
    if selected_date in st.session_state.market_calendar:
        day_info = st.session_state.market_calendar[selected_date]
        if day_info["open"]:
            st.success(f"🟢 **【当日配送モード稼働中】** 本日（{selected_date}）は