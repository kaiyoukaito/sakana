import streamlit as st
import pandas as pd
from datetime import datetime

# ページの設定
st.set_page_config(page_title="イチゴイチエ・フィッシュ デモ", layout="wide")
st.title("🐟 水産物マッチング「イチゴイチエ・フィッシュ」プロトタイプ")

# --- 1. デモ用の疑似データベース＆チャット履歴の初期化 ---
if "fish_db" not in st.session_state:
    st.session_state.fish_db = pd.DataFrame([
        {
            "id": 1, "seller": "横浜仲卸・魚源", "fish_name": "マグロ中落ち (規格外)", 
            "price": 2000, "scope": "フォロー限定", "group": "横浜中央市場", "distance": 0
        },
        {
            "id": 2, "seller": "豊海丸 (遊漁船)", "fish_name": "大漁アジ (30匹・釣りすぎ)", 
            "price": 3000, "scope": "距離限定 (10km以内)", "group": "江の島漁港", "distance": 5
        },
        {
            "id": 3, "seller": "銚子水産", "fish_name": "高級ホウボウ (1匹・一点物)", 
            "price": 1500, "scope": "全体公開", "group": "銚子漁港", "distance": 80
        }
    ])

# チャットの履歴を保存する構造
if "chat_db" not in st.session_state:
    st.session_state.chat_db = [
        {"room": "横浜仲卸・魚源", "user": "横浜仲卸・魚源", "msg": "今日の中落ち、マジで質がいいよ！", "time": "15:30"},
        {"room": "横浜中央市場 グループ", "user": "市場事務局", "msg": "明日の開市時間は通常通りです。", "time": "10:00"},
    ]

# 現在開いているチャットルームの管理
if "current_room" not in st.session_state:
    st.session_state.current_room = None

# --- 2. サイドバーでユーザー切り替え（デモ用） ---
st.sidebar.header("👥 役割・画面切り替え")
user_type = st.sidebar.radio("役割を選択:", ["出品者 (仲卸・船長)", "買い手 (飲食店)"])

# チャットへのショートカットボタン（フォロワー・グループ）
st.sidebar.write("---")
st.sidebar.subheader("💬 チャット連絡網")

# 常時繋がっているグループチャット
if st.sidebar.button("🌐 横浜中央市場 グループ"):
    st.session_state.current_room = "横浜中央市場 グループ"

# フォロワーとの常時チャット窓口
st.sidebar.caption("↓フォロー中の出品者 (いつでも連絡可)")
if st.sidebar.button("👤 横浜仲卸・魚源 (フォロー中)"):
    st.session_state.current_room = "横浜仲卸・魚源"
if st.sidebar.button("👤 豊海丸 (遊漁船)"):
    st.session_state.current_room = "豊海丸 (遊漁船)"

if st.session_state.current_room:
    if st.sidebar.button("❌ チャットを閉じる"):
        st.session_state.current_room = None
        st.rerun()

# 画面レイアウトの分割（チャットが開いている時は右側に表示する）
if st.session_state.current_room:
    main_col, chat_col = st.columns([2, 1.2])
else:
    main_col = st.container()

# --- 3. メインコンテンツエリア ---
with main_col:
    # --- 【出品者画面】 ---
    if user_type == "出品者 (仲卸・船長)":
        st.header("🛒 出品管理パネル")
        
        with st.form("clearance_form"):
            st.subheader("浮いた魚を登録する")
            fish_name = st.text_input("魚種名・商品名", placeholder="例：アジ詰め合わせ、マグロ中落ち")
            price = st.number_input("価格 (円)", min_value=0, step=500, value=2000)
            scope = st.selectbox("初期の公開範囲", ["グループ限定", "フォロー限定", "距離限定 (10km以内)", "全体公開"])
            submit = st.form_submit_button("出品する")
            
            if submit and fish_name:
                new_data = {
                    "id": len(st.session_state.fish_db) + 1, "seller": "テスト出品者 (あなた)",
                    "fish_name": fish_name, "price": price, "scope": scope,
                    "group": "横浜中央市場", "distance": 3
                }
                st.session_state.fish_db = pd.concat([st.session_state.fish_db, pd.DataFrame([new_data])], ignore_index=True)
                st.success(f"「{fish_name}」を出品しました！")

        st.subheader("📦 在庫一覧")
        st.dataframe(st.session_state.fish_db)

    # --- 【買い手（飲食店）画面】 ---
    else:
        st.header("🍽️ 飲食店仕入れパネル")
        
        st.subheader("🔍 あなた（飲食店）のステータス設定")
        col1, col2 = st.columns(2)
        with col1:
            is_following = st.checkbox("「横浜仲卸・魚源」をフォローしている", value=True)
        with col2:
            my_group = st.selectbox("所属コミュニティ", ["横浜中央市場", "江の島漁港", "その他"])

        st.write("---")
        st.subheader("🔔 あなたが購入可能な「一期一会」の魚たち")

        # フィルタリング
        available_fish = []