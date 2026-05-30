import streamlit as st
import pandas as pd

# ページの設定
st.set_page_config(page_title="イチゴイチエ・フィッシュ デモ", layout="wide")
st.title("🐟 水産物マッチング「イチゴイチエ・フィッシュ」プロトタイプ")

# --- 1. デモ用の疑似データベース（セッション状態の初期化） ---
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

# --- 2. サイドバーでユーザー切り替え（デモ用） ---
st.sidebar.header("👥 ユーザー切り替え (デモ用)")
user_type = st.sidebar.radio("役割を選択してください:", ["出品者 (仲卸・船長)", "買い手 (飲食店)"])

# --- 3. 【出品者画面】 ---
if user_type == "出品者 (仲卸・船長)":
    st.header("🛒 出品管理パネル")
    
    with st.form("clearance_form"):
        st.subheader("浮いた魚を登録する")
        fish_name = st.text_input("魚種名・商品名", placeholder="例：アジ詰め合わせ、マグロ中落ち")
        price = st.number_input("価格 (円)", min_value=0, step=500, value=2000)
        
        # ここがコア！公開範囲の設定
        scope = st.selectbox(
            "初期の公開範囲", 
            ["グループ限定", "フォロー限定", "距離限定 (10km以内)", "全体公開"]
        )
        
        submit = st.form_submit_button("出品する")
        
        if submit and fish_name:
            # 新しい出品データを追加
            new_data = {
                "id": len(st.session_state.fish_db) + 1,
                "seller": "テスト出品者 (あなた)",
                "fish_name": fish_name,
                "price": price,
                "scope": scope,
                "group": "横浜中央市場",  # デモ用固定
                "distance": 3             # デモ用固定 (近隣設定)
            }
            st.session_state.fish_db = pd.concat([st.session_state.fish_db, pd.DataFrame([new_data])], ignore_index=True)
            st.success(f"「{fish_name}」を【{scope}】で出品しました！")

    # 現在の全在庫を表示
    st.subheader("📦 現在の市場の「浮いている魚」一覧（全データ）")
    st.dataframe(st.session_state.fish_db)

# --- 4. 【買い手（飲食店）画面】 ---
else:
    st.header("🍽️ 飲食店仕入れパネル")
    
    # 飲食店の属性を設定（デモ用に可変にする）
    st.subheader("🔍 あなた（飲食店）のステータス設定")
    col1, col2, col3 = st.columns(3)
    with col1:
        is_following = st.checkbox("「横浜仲卸・魚源」をフォローしている", value=True)
    with col2:
        my_group = st.selectbox("所属コミュニティ", ["横浜中央市場", "江の島漁港", "その他"])
    with col3:
        target_distance = 10 # 10km圏内をローカル物流範囲とする
        st.write(f"ローカル物流範囲: 港から {target_distance} km 以内")

    st.write("---")
    st.subheader("🔔 あなたが購入可能な「一期一会」の魚たち")

    # フィルタリングロジックの構築
    available_fish = []
    
    for _, fish in st.session_state.fish_db.iterrows():
        show_flag = False
        
        # ロジック1: 全体公開なら誰でも見れる
        if fish["scope"] == "全体公開":
            show_flag = True
            
        # ロジック2: グループ限定（同じ市場コミュニティなら見れる）
        elif fish["scope"] == "グループ限定" and fish["group"] == my_group:
            show_flag = True
            
        # ロジック3: フォロー限定（フォロー関係があれば見れる）
        elif fish["scope"] == "フォロー限定" and fish["seller"] == "横浜仲卸・魚源" and is_following:
            show_flag = True
            
        # ロジック4: 距離限定（指定km以内なら見れる＝配送コストがかからない）
        elif fish["scope"] == "距離限定 (10km以内)" and fish["distance"] <= target_distance:
            show_flag = True
            
        if show_flag:
            available_fish.append(fish)

    # フィルター結果の表示
    if available_fish:
        df_display = pd.DataFrame(available_fish)
        
        # 見やすいカード形式（グリッド）で表示
        for _, row in df_display.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                c1.markdown(f"### **{row['fish_name']}**")
                c1.caption(f"出品者: {row['seller']} | 所属: {row['group']}")
                c2.markdown(f"#### **{row['price']} 円**")
                c3.badge(row['scope'], variant="outline") if hasattr(st, "badge") else c3.write(f"🔒 {row['scope']}")
                
                if c4.button("購入する", key=row['id']):
                    st.balloons()
                    st.success(f"【{row['fish_name']}】の購入が確定しました！拠点（{row['group']}）での引き取り、またはいつものルートで配送されます。")
                st.write("---")
    else:
        st.info("現在、あなたの条件にマッチする「浮いた魚」はありません。公開範囲が広がるのを待つか、条件を変更してください。")