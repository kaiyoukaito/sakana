import streamlit as st
import pandas as pd

# ページの設定
st.set_page_config(page_title="イチゴイチエ・フィッシュ デモ", layout="wide")

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

if "chat_db" not in st.session_state:
    st.session_state.chat_db = [
        {"room": "横浜仲卸・魚源", "user": "横浜仲卸・魚源", "avatar": "👤", "msg": "今日の中落ち、マジで質がいいよ！大将どう？"},
        {"room": "横浜中央市場 グループ", "user": "市場事務局", "avatar": "📢", "msg": "明日の開市時間は通常通りです。余り物の出品はお早めに。"},
    ]

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
    st.title("🐟 水産物マッチング「イチゴイチエ・フィッシュ」")
    
    st.sidebar.header("👥 役割・画面切り替え")
    user_type = st.sidebar.radio("役割を選択:", ["出品者 (仲卸・船長)", "買い手 (飲食店)"])
    
    st.sidebar.write("---")
    st.sidebar.subheader("📩 DM・連絡網一覧")
    
    if st.sidebar.button("🌐 横浜中央市場 グループ"):
        st.session_state.current_room = "横浜中央市場 グループ"
        st.rerun()
        
    st.sidebar.caption("↓メッセージスレッド")
    if st.sidebar.button("👤 横浜仲卸・魚源 (2)"):
        st.session_state.current_room = "横浜仲卸・魚源"
        st.rerun()
    if st.sidebar.button("👤 豊海丸 (遊漁船)"):
        st.session_state.current_room = "豊海丸 (遊漁船)"
        st.rerun()

    # --- 【通常：出品者画面】 ---
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

    # --- 【通常：買い手（飲食店）画面】 ---
    else:
        st.header("🍽️ 飲食店仕入れパネル")
        
        st.subheader("🔍 あなた（飲食店）のステータス設定")
        col1, col2 = st.columns(2)
        with col1:
            is_following = st.checkbox("「横浜仲卸・魚源」をフォローしている", value=True)
        with col2:
            my_group = st.selectbox("所属コミュニティ", ["横浜中央市場", "江の島漁港", "その他"])

        # 新機能：飲食店の意思でかける絞り込みフィルター
        st.write("---")
        st.subheader("🎛️ 表示フィルター（大将のカスタム検索）")
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            only_following = st.toggle("👤 フォローしている出品者のみ表示", value=False)
        with filter_col2:
            only_nearby = st.toggle("📍 10km以内の近隣のみ表示 (直取り用)", value=False)

        st.write("---")
        st.subheader("🔔 あなたが購入可能な「一期一会」の魚たち")

        # フィルタリングロジック
        available_fish = []
        for _, fish in st.session_state.fish_db.iterrows():
            # 基本的な公開範囲のチェック（前ステップまでのロジック）
            can_see = False
            if fish["scope"] == "全体公開": can_see = True
            elif fish["scope"] == "グループ限定" and fish["group"] == my_group: can_see = True
            elif fish["scope"] == "フォロー限定" and fish["seller"] == "横浜仲卸・魚源" and is_following: can_see = True
            elif fish["scope"] == "距離限定 (10km以内)" and fish["distance"] <= 10: can_see = True
            
            # 追加ロジック：「フォローのみ」フィルターがONの場合の絞り込み
            if only_following and fish["seller"] != "横浜仲卸・魚源":
                can_see = False
                
            # 追加ロジック：「10km以内のみ」フィルターがONの場合の絞り込み
            if only_nearby and fish["distance"] > 10:
                can_see = False
                
            if can_see: 
                available_fish.append(fish)

        if available_fish:
            for _, row in pd.DataFrame(available_fish).iterrows():
                with st.container():
                    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                    c1.markdown(f"### **{row['fish_name']}**")
                    c1.caption(f"出品者: {row['seller']} | 所属: {row['group']} | 距離: {row['distance']}km")
                    
                    c2.markdown(f"#### **{row['price']} 円**")
                    c3.write(f"🔒 {row['scope']}")
                    
                    if c4.button(f"💬 交渉", key=f"chat_{row['id']}"):
                        st.session_state.current_room = row['seller']
                        st.rerun()
                        
                    if c4.button("📥 購入", key=f"buy_{row['id']}"):
                        st.balloons()
                        st.success("購入確定！左メニューのDMか、交渉ボタンからメッセージを送ってください。")
                    st.write("---")
        else:
            st.info("条件にマッチする魚はありません。フィルターを緩めてみてください。")