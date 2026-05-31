import streamlit as st
import pandas as pd
from datetime import datetime

# ページの設定
st.set_page_config(page_title="イチハブ（配送ルートナビ搭載）デモ", layout="wide")

# --- 1. デモ用の疑似データベース＆チャット履歴の初期化 ---
if "fish_db" not in st.session_state:
    st.session_state.fish_db = pd.DataFrame([
        {
            "id": 1, "seller": "横浜仲卸・魚源", "fish_name": "マグロ中落ち (規格外)", 
            "price": 2000, "scope": "フォロー限定", "group": "横浜中央市場", "distance": 0,
            "processed": "🩸 エラ・内臓除去（水洗血抜き済）", "hitchhike_available": True, "route_id": "ROUTE-A"
        },
        {
            "id": 2, "seller": "豊海丸 (遊漁船)", "fish_name": "大漁アジ (30匹・釣りすぎ)", 
            "price": 3000, "scope": "距離限定 (10km以内)", "group": "江の島漁港", "distance": 5,
            "processed": "🧊 氷締め（水揚げ直後処理）", "hitchhike_available": True, "route_id": "ROUTE-A"
        },
        {
            "id": 3, "seller": "銚子水産", "fish_name": "高級ホウボウ (1匹・一点物)", 
            "price": 1500, "scope": "全体公開", "group": "銚子漁港", "distance": 80,
            "processed": "🩸 神経締め・血抜き済", "hitchhike_available": False, "route_id": None
        }
    ])

if "chat_db" not in st.session_state:
    st.session_state.chat_db = [
        {"room": "横浜仲卸・魚源", "user": "横浜仲卸・魚源", "avatar": "👤", "msg": "今日の中落ち、マジで質がいいよ！大将どう？"},
        {"room": "横浜中央市場 グループ", "user": "市場事務局", "avatar": "📢", "msg": "明日の開市時間は通常通りです。余り物の出品はお早めに。"},
    ]

# 市場カレンダーのモックデータ（2026年6月）
if "market_calendar" not in st.session_state:
    st.session_state.market_calendar = {
        "2026-06-01": {"open": True, "note": "通常開場日"},
        "2026-06-02": {"open": True, "note": "通常開場日"},
        "2026-06-03": {"open": False, "note": "水曜休市日（スマートロッカー直取りのみ対応）"},
        "2026-06-04": {"open": True, "note": "通常開場日"},
    }

# Discord風フォロワーオンラインステータス
if "user_status" not in st.session_state:
    st.session_state.user_status = {
        "横浜仲卸・魚源": {"status": "online", "icon": "🟢"},
        "豊海丸 (遊漁船)": {"status": "away", "icon": "🟡"},
        "銚子水産": {"status": "offline", "icon": "⚫"}
    }

# 💡 新機能：ヤフー乗換案内風の配送ルートマスターデータ
if "route_master" not in st.session_state:
    st.session_state.route_master = {
        "ROUTE-A": {
            "name": "🚚 湘南・関内大口循環便（ルートA）",
            "timeline": [
                {"time": "09:30", "station": "🏛️ 横浜中央卸売市場（ハブ出発・積込締切）"},
                {"time": "10:15", "station": "📍 みなとみらい交差点（通過）"},
                {"time": "10:40", "station": "✨ 【ハック地点】関内・馬車道エリア（あなたのお店前）"},
                {"time": "11:30", "station": "🏁 最終目的地：湘南業務用スーパー（運行終了）"}
            ],
            "buffer": "🟢 タイムバッファ十分（遅延リスク 0%）"
        }
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
    st.caption("〜 ラストワンマイルを固定し、流動的な中間サプライチェーンをハックする 〜")
    
    # --- サイドバー：コントロールパネル ---
    st.sidebar.header("👥 役割・画面切り替え")
    user_type = st.sidebar.radio("役割を選択:", ["出品者 (仲卸・船長)", "買い手 (飲食店)"])
    
    # デモ用カレンダーシミュレーター
    st.sidebar.write("---")
    st.sidebar.subheader("📅 デモ用カレンダー設定")
    selected_date_obj = st.sidebar.date_input(
        "シミュレートする日付:",
        value=datetime.strptime("2026-06-01", "%Y-%m-%d")
    )
    selected_date = selected_date_obj.strftime("%Y-%m-%d")
    
    # 連絡網一覧（Discord風ステータス統合）
    st.sidebar.write("---")
    st.sidebar.subheader("📩 DM・連絡網一覧")
    
    if st.sidebar.button("🌐 横浜中央市場 グループ"):
        st.session_state.current_room = "横浜中央市場 グループ"
        st.rerun()
        
    st.sidebar.caption("↓フォロワーステータス（Discord風）")
    yugen_status = st.session_state.user_status["横浜仲卸・魚源"]["icon"]
    if st.sidebar.button(f"{yugen_status} 横浜仲卸・魚源 (2)"):
        st.session_state.current_room = "横浜仲卸・魚源"
        st.rerun()
        
    toyomi_status = st.session_state.user_status["豊海丸 (遊漁船)"]["icon"]
    if st.sidebar.button(f"{toyomi_status} 豊海丸 (遊漁船)"):
        st.session_state.current_room = "豊海丸 (遊漁船)"
        st.rerun()

    # --- カレンダー連動バナーの表示 ---
    is_market_open = True
    if selected_date in st.session_state.market_calendar:
        day_info = st.session_state.market_calendar[selected_date]
        is_market_open = day_info["open"]
        if is_market_open:
            st.success(f"🟢 **【当日配送・相乗りモード稼働中】** 本日（{selected_date}）は通常開場日。午前9:30発の定期便の固定ルートをハック可能です。")
            delivery_mode_text = "🚚 既存ルート便へのヒッチハイク相乗り"
        else:
            st.warning(f"🟡 **【スマートロッカー直取り限定モード】** 本日（{selected_date}）は「{day_info['note']}」です。市場の冷蔵ロッカー（大将の動ける最大距離内）への保管に切り替わります。")
            delivery_mode_text = "📥 市場内 0℃高鮮度スマートロッカー引き取り"
    else:
        st.info("ℹ️ 通常運行枠")
        delivery_mode_text = "🚚 既存の市場ルート定期便"

    # --- 【通常：出品者画面】 ---
    if user_type == "出品者 (仲卸・船長)":
        st.header("🛒 出品管理パネル")
        with st.form("clearance_form"):
            st.subheader("浮いた魚を登録する")
            fish_name = st.text_input("魚種名・商品名", placeholder="例：マグロ中落ち")
            price = min_value=0, step=500, value=2000
            price = st.number_input("価格 (円)", min_value=0, step=500, value=2000)
            scope = st.selectbox("初期の公開範囲", ["グループ限定", "フォロー限定", "距離限定 (10km以内)", "全体公開"])
            processed_tag = st.selectbox("鮮度保持の処理（仕立て）", ["🩸 エラ・内臓除去（水洗血抜き済）", "🧊 氷締め（水揚げ直後処理）", "🩸 神経締め・血抜き済"])
            submit = st.form_submit_button("出品する")
            
            if submit and fish_name:
                new_data = {
                    "id": len(st.session_state.fish_db) + 1, "seller": "テスト出品者 (あなた)",
                    "fish_name": fish_name, "price": price, "scope": scope,
                    "group": "横浜中央市場", "distance": 3, "processed": processed_tag, "hitchhike_available": True, "route_id": "ROUTE-A"
                }
                st.session_state.fish_db = pd.concat([st.session_state.fish_db, pd.DataFrame([new_data])], ignore_index=True)
                st.success(f"「{fish_name}」を出品しました！")

        st.subheader("📦 在庫一覧")
        st.dataframe(st.session_state.fish_db)

    # --- 【通常：買い手（飲食店）画面】 ---
    else:
        st.header("🍽️ 飲食店仕入れパネル")
        
        # 💡 ネットの乗換案内風：固定された配送ルートのナビゲーション表示
        with st.expander("🗺️ ヤフー乗換案内風：あなたのお店を通過する定期便ルートナビ", expanded=True):
            if is_market_open:
                route = st.session_state.route_master["ROUTE-A"]
                st.markdown(f"### **{route['name']}**")
                st.caption(f"状況: {route['buffer']} | 他の顧客のルート変更：不要")
                
                # 乗換案内風タイムラインの描画
                for step in route["timeline"]:
                    # あなたの店を通る部分だけ強調表示
                    if "ハック地点" in step["station"]:
                        st.markdown(f"**⏱️ {step['time']}** ➔ <span style='color:#ff4b4b; font-weight:bold;'>{step['station']}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"⏱️ {step['time']} ➔ {step['station']}")
            else:
                st.markdown("### 📴 本日はルート便の運行はありません（市場休市日）")
                st.markdown("➔ 市場内の**0℃冷蔵スマートロッカー（24時間いつでも受取可能）**にルートが自動固定されています。")

        st.write("---")
        st.subheader("🔔 あなたが購入可能な「一期一会」の魚たち")

        # フィルタリングされた魚の表示
        for _, row in st.session_state.fish_db.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                
                # 魚情報＆品質仕立てタグ
                c1.markdown(f"### **{row['fish_name']}**")
                c1.markdown(f"**仕立て:** `{row['processed']}`")
                c1.caption(f"出品者: {row['seller']} | 所属: {row['group']} | 距離: {row['distance']}km")
                
                c2.markdown(f"#### **{row['price']} 円**")
                c2.caption(f"運搬: {delivery_mode_text}")
                
                # ヒッチハイク相乗り可能タグの動的出し分け
                if is_market_open and row['hitchhike_available']:
                    c3.markdown("⛽ **ヒッチハイク対象便**")
                    c3.markdown("<span style='color:#1fcb64; font-weight:bold; font-size:12px;'>相乗り送料: ¥100 (通常¥350)</span>", unsafe_allow_html=True)
                    buy_btn_label = "📥 ヒッチハイク注文"
                else:
                    c3.markdown(f"🔒 {row['scope']}")
                    buy_btn_label = "📥 ロッカー直取り購入" if not is_market_open else "📥 購入する"
                
                # 交渉ボタン
                seller_name = row['seller']
                status_icon = st.session_state.user_status.get(seller_name, {}).get("icon", "👤")
                if c4.button(f"💬 交渉 ({status_icon})", key=f"chat_{row['id']}"):
                    st.session_state.current_room = row['seller']
                    st.rerun()
                    
                # 購入ボタンのアクション
                if c4.button(buy_btn_label, key=f"buy_{row['id']}", type="primary"):
                    st.balloons()
                    if not is_market_open:
                        st.success("【ロッカー直取り確定】大将が動ける最大距離内（市場A-3冷蔵ロッカー）への格納指示を出しました。解錠QRを発行します。")
                    elif row['hitchhike_available']:
                        route_name = st.session_state.route_master["ROUTE-A"]["name"]
                        st.success(f"【ヒッチハイク相乗り成立！】「{route_name}」の10:40通過のタイミングでお店前にてドロップイン手配が完了しました（送料100円）。")
                    else:
                        st.success("購入確定！通常配送の手配が完了しました。")