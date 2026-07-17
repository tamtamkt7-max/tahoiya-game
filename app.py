import streamlit as st
import sqlite3
import random
import time

# ページ設定
st.set_page_config(page_title="たほいや", layout="centered", initial_sidebar_state="collapsed")

# データベースからランダムにお題を取得
def get_random_question():
    conn = sqlite3.connect('tahoiya.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row

# 全サーバーで共有する多重ルーム管理システム
@st.cache_resource
def get_global_rooms():
    return {}

global_rooms = get_global_rooms()

# スタイリング（スマホでの視認性とファーストビューの密度を極限まで高めたUI）
st.markdown("""
    <style>
    /* タイトルとヘッダー */
    .main-title { font-size: 2.2rem; font-weight: 800; text-align: center; color: #FF4B4B; margin-bottom: 1rem; letter-spacing: 0.15rem; }
    .room-tag { font-size: 0.9rem; padding: 0.4rem 0.8rem; border-radius: 8px; border: 1px solid #e0e0e0; text-align: center; margin-bottom: 1rem; color: #555555; }
    
    /* お題表示 */
    .word-display { font-size: 1.8rem; font-weight: bold; text-align: center; padding: 1rem; border-radius: 12px; border: 2px solid #FF4B4B; margin: 0.8rem 0; }
    .timer-display { font-size: 1.3rem; font-weight: bold; text-align: center; color: #FF4B4B; margin: 0.5rem 0; }
    
    /* スマホ向け：横並びコンパクトサマリー */
    .summary-container { display: flex; justify-content: space-between; border: 1px solid #e0e0e0; border-radius: 10px; padding: 0.7rem; margin-bottom: 1rem; background-color: transparent; }
    .summary-item { flex: 1; text-align: center; border-right: 1px solid #e0e0e0; }
    .summary-item:last-child { border-right: none; }
    .summary-label { font-size: 0.75rem; color: #777777; margin-bottom: 0.2rem; }
    .summary-value { font-size: 1.1rem; font-weight: bold; color: #333333; }
    .summary-value-highlight { font-size: 1.1rem; font-weight: bold; color: #FF4B4B; }
    
    /* 選択肢カード（タイト設計） */
    .stat-box { padding: 0.8rem 1rem; border-radius: 10px; margin-bottom: 0.5rem; border: 1px solid #e0e0e0; font-size: 0.95rem; line-height: 1.4; }
    .stat-box-correct { padding: 0.8rem 1rem; border-radius: 10px; margin-bottom: 0.5rem; border: 2px solid #2e7d32; font-size: 0.95rem; line-height: 1.4; }
    
    /* グループ分け結果表示 */
    .result-group { border: 1px solid #e0e0e0; border-radius: 8px; padding: 0.6rem 0.8rem; margin-bottom: 0.5rem; font-size: 0.9rem; }
    
    /* 各種微調整 */
    .stTextArea textarea { padding: 0.5rem; }
    div.stButton > button { margin-top: 0.2rem; margin-bottom: 0.2rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">たほいや</div>', unsafe_allow_html=True)

# セッション状態の初期化
if "room_id" not in st.session_state: st.session_state.room_id = None
if "role" not in st.session_state: st.session_state.role = None
if "my_name" not in st.session_state: st.session_state.my_name = ""

# --- ルーム入室・作成画面 ---
if st.session_state.room_id is None:
    tab1, tab2 = st.tabs(["ルームに参加する", "新しくルームを作る"])
    
    with tab1:
        st.write("共有された4桁のルームIDを入力してください。")
        input_room = st.text_input("ルームID (4桁)", max_chars=4).upper()
        input_name = st.text_input("あなたのプレイヤー名", key="join_name")
        
        if st.button("参加する", use_container_width=True):
            if input_room in global_rooms and input_name.strip():
                st.session_state.room_id = input_room
                st.session_state.role = "子（解答者）"
                st.session_state.my_name = input_name.strip()
                if st.session_state.my_name not in global_rooms[input_room]["players"]:
                    global_rooms[input_room]["players"].append(st.session_state.my_name)
                st.rerun()
            elif input_room not in global_rooms:
                st.error("指定されたルームが見つかりません。")
            else:
                st.error("プレイヤー名を入力してください。")
                
    with tab2:
        st.write("あなたが親（出題者）となってゲームを開始します。")
        parent_name = st.text_input("あなたの親（出題者）名", key="create_name")
        
        if st.button("ルームを新規作成する", use_container_width=True):
            if parent_name.strip():
                while True:
                    new_room_id = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=4))
                    if new_room_id not in global_rooms:
                        break
                
                global_rooms[new_room_id] = {
                    "status": "waiting",
                    "parent_name": parent_name.strip(),
                    "players": [],
                    "word": "",
                    "choices": [],
                    "correct": "",
                    "votes": {},
                    "fake_pool": [],
                    "used_pool_count": 0,
                    "time_limit": 60,
                    "start_time": 0,
                    "f1_text": "",
                    "f2_text": "",
                    "f3_text": "",
                    "scores": {},       
                    "score_updated": False
                }
                st.session_state.room_id = new_room_id
                st.session_state.role = "親（出題者）"
                st.session_state.my_name = parent_name.strip()
                st.rerun()
            else:
                st.error("親の名前を入力してください。")

# --- ゲーム本編画面 ---
else:
    room_id = st.session_state.room_id
    role = st.session_state.role
    room = global_rooms[room_id]
    total_players = len(room["players"])
    
    parent_display = f"{room['parent_name']}（親）" if role == "子（解答者）" else room['parent_name']
    st.markdown(f'<div class="room-tag">ROOM: <b>{room_id}</b> ｜ 親: <b>{parent_display}</b> ｜ 子: <b>{total_players}人</b></div>', unsafe_allow_html=True)
    
    if st.sidebar.button("ルームを退室"):
        if role == "親（出題者）":
            global_rooms.pop(room_id, None)
        else:
            if st.session_state.my_name in room["players"]:
                room["players"].remove(st.session_state.my_name)
        st.session_state.room_id = None
        st.session_state.role = None
        st.rerun()

    # ⏰ タイマー及び自動締め切り監視（投票中のみ）
    if room["status"] == "voting":
        elapsed = time.time() - room["start_time"]
        remaining = int(room["time_limit"] - elapsed)
        
        if (total_players > 0 and len(room["votes"]) >= total_players) or remaining <= 0:
            room["status"] = "result"
            st.rerun()

    # 📈 結果画面になった瞬間に1度だけ通算スコアを計算
    if room["status"] == "result" and not room["score_updated"]:
        for name in room["players"]:
            if name not in room["scores"]:
                room["scores"][name] = {"correct": 0, "total": 0}
            
            room["scores"][name]["total"] += 1
            if room["votes"].get(name) == room["correct"]:
                room["scores"][name]["correct"] += 1
        room["score_updated"] = True

    # ==================== 📊 共通リザルト画面関数 ====================
    def render_result_view():
        st.markdown(f'<div class="word-display">結果発表：【 {room["word"]} 】</div>', unsafe_allow_html=True)
        
        # 1. 横並び1行サマリー
        total_votes = len(room["votes"])
        correct_list = [name for name, vote in room["votes"].items() if vote == room["correct"]]
        incorrect_list = [name for name, vote in room["votes"].items() if vote != room["correct"]]
        
        correct_count = len(correct_list)
        incorrect_count = len(incorrect_list)
        accuracy_rate = (correct_count / total_votes * 100) if total_votes > 0 else 0
        
        st.markdown(f"""
        <div class="summary-container">
            <div class="summary-item">
                <div class="summary-label">正解</div>
                <div class="summary-value" style="color: #2e7d32;">{correct_count} 人</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">誤答</div>
                <div class="summary-value">{incorrect_count} 人</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">正答率</div>
                <div class="summary-value-highlight">{accuracy_rate:.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.success(f"🟩 **正しい意味（正解）**\n\n{room['correct']}")
        
        # 2. 各解答の投票率（コンパクト設計）
        st.write("---")
        st.subheader("📈 選択肢ごとの得票状況")
        for choice in room["choices"]:
            choice_votes = sum(1 for v in room["votes"].values() if v == choice)
            percentage = (choice_votes / total_votes * 100) if total_votes > 0 else 0
            
            if choice == room["correct"]:
                st.markdown(f"""
                <div class="stat-box-correct">
                    <strong style="color: #2e7d32;">【正解】 {choice}</strong><br>
                    <span style="font-size: 0.8rem; color: #666;">得票: {choice_votes}人 ({percentage:.1f}%)</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="stat-box">
                    <strong>{choice}</strong><br>
                    <span style="font-size: 0.8rem; color: #666;">得票: {choice_votes}人 ({percentage:.1f}%)</span>
                </div>
                """, unsafe_allow_html=True)
            
        # 3. 大人数でも縦伸びしないユーザー別の回答（完全グループ集約型）
        st.write("---")
        st.subheader("👤 プレイヤーの回答グループ")
        
        if room["votes"]:
            correct_names = "、".join(correct_list) if correct_list else "なし"
            incorrect_names = "、".join(incorrect_list) if incorrect_list else "なし"
            
            st.markdown(f"""
            <div class="result-group">
                <span style="color: #2e7d32; font-weight: bold;">🟢 正解したプレイヤー ({correct_count}人):</span><br>
                <span style="color: #333;">{correct_names}</span>
            </div>
            <div class="result-group">
                <span style="color: #FF4B4B; font-weight: bold;">❌ 騙されたプレイヤー ({incorrect_count}人):</span><br>
                <span style="color: #555;">{incorrect_names}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.write("投票したプレイヤーはいませんでした。")
            
        # 4. 連続プレイ時の通算成績（タイトなランキング形式）
        st.write("---")
        st.subheader("🏆 通算成績ランキング")
        if room["scores"]:
            sorted_scores = sorted(
                room["scores"].items(), 
                key=lambda x: (x[1]["correct"] / x[1]["total"] if x[1]["total"] > 0 else 0), 
                reverse=True
            )
            for idx, (name, data) in enumerate(sorted_scores, start=1):
                rate = (data["correct"] / data["total"] * 100) if data["total"] > 0 else 0
                st.markdown(f"**{idx}位** : {name} （{data['correct']}/{data['total']}問正解 ・ **{rate:.1f}%**）")
        else:
            st.write("まだ通算記録はありません。")

    # ---------------- 👑 親のゲーム進行 ----------------
    if role == "親（出題者）":
        button_label = "お題を更新"
        if st.button(button_label, use_container_width=True):
            q = get_random_question()
            if q:
                room["word"] = q[1]
                room["correct"] = q[2]
                room["fake_pool"] = [q[3], q[4], q[5]]
                room["used_pool_count"] = 0
                room["status"] = "playing"
                room["votes"] = {}
                room["f1_text"] = ""
                room["f2_text"] = ""
                room["f3_text"] = ""
                room["score_updated"] = False
                st.rerun()
                
        if room["status"] == "waiting":
            st.info("上の「お題を更新」ボタンを押してお題を引いてください。子は待機画面で待っています。")
            if room["players"]:
                st.write("現在の参加者:", ", ".join(room["players"]))
            
        elif room["status"] == "playing":
            st.markdown(f'<div class="word-display">【 {room["word"]} 】</div>', unsafe_allow_html=True)
            st.markdown(f"**正しい意味（正解）**\n> {room['correct']}\n")
            
            st.write("---")
            st.subheader("嘘の選択肢を作成")
            room["time_limit"] = st.number_input("制限時間（秒）", min_value=10, max_value=300, value=60, step=10)
            
            if st.button("嘘の選択肢をストックから1つ補給", use_container_width=True):
                if room["used_pool_count"] < len(room["fake_pool"]):
                    next_fake = room["fake_pool"][room["used_pool_count"]]
                    if not room["f1_text"].strip(): room["f1_text"] = next_fake; room["used_pool_count"] += 1
                    elif not room["f2_text"].strip(): room["f2_text"] = next_fake; room["used_pool_count"] += 1
                    elif not room["f3_text"].strip(): room["f3_text"] = next_fake; room["used_pool_count"] += 1
                    else: st.warning("すべての入力欄が埋まっています。")
                    st.rerun()
                else:
                    st.warning("これ以上ストックされている嘘はありません。")

            room["f1_text"] = st.text_area("嘘の意味 1", value=room["f1_text"])
            room["f2_text"] = st.text_area("嘘の意味 2", value=room["f2_text"])
            room["f3_text"] = st.text_area("嘘の意味 3", value=room["f3_text"])
            
            if st.button("この4択で出題を開始！", use_container_width=True, type="primary"):
                if room["f1_text"].strip() and room["f2_text"].strip() and room["f3_text"].strip():
                    choices = [room["correct"], room["f1_text"], room["f2_text"], room["f3_text"]]
                    random.shuffle(choices)
                    room["choices"] = choices
                    room["start_time"] = time.time()
                    room["status"] = "voting"
                    st.rerun()
                else:
                    st.error("嘘の選択肢を3つすべて埋めてください。")
                    
        elif room["status"] == "voting":
            st.markdown(f'<div class="word-display">出題中：【 {room["word"]} 】</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="timer-display">⏱ 締め切りまで あと {remaining} 秒</div>', unsafe_allow_html=True)
            
            st.write("---")
            st.subheader("現在の投票状況")
            st.write(f"投票済み: {len(room['votes'])} / {total_players} 人")
            for p in room["players"]:
                status = "✅ 完了" if p in room["votes"] else "⏳ 思考中..."
                st.write(f"- {p} : {status}")
                
            if st.button("今すぐ投票を締め切る", use_container_width=True, type="primary"):
                room["status"] = "result"
                st.rerun()
                
            time.sleep(2)
            st.rerun()

        elif room["status"] == "result":
            render_result_view()
            st.write("---")
            if st.button("待機室に戻る（次のゲームへ）", use_container_width=True, type="primary"):
                room["status"] = "waiting"
                st.rerun()

    # ---------------- 👥 子のゲーム進行 ----------------
    else:
        if room["status"] == "waiting":
            st.warning("⏳ 親がお題を選択中です。お待ちください。")
            time.sleep(2)
            st.rerun()
            
        elif room["status"] == "playing":
            st.warning("⏳ 親が4択問題を作成しています。お待ちください。")
            time.sleep(2)
            st.rerun()
            
        elif room["status"] == "voting":
            st.markdown(f'<div class="word-display">お題：【 {room["word"]} 】</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="timer-display">⏱ 残り時間: {remaining} 秒</div>', unsafe_allow_html=True)
            
            if st.session_state.my_name in room["votes"]:
                st.info(f"あなたの投票は受領されました。待機中... ({len(room['votes'])}/{total_players}人完了)")
                time.sleep(2)
                st.rerun()
            else:
                st.write("どれが本当の辞書の意味？")
                chosen = st.radio("選択肢", room["choices"], index=None, label_visibility="collapsed")
                
                if st.button("投票を確定する", use_container_width=True, type="primary"):
                    if chosen:
                        room["votes"][st.session_state.my_name] = chosen
                        st.success("投票しました！")
                        st.rerun()
                    else:
                        st.error("選択肢を選んでください。")
                
                time.sleep(2)
                st.rerun()
                    
        elif room["status"] == "result":
            render_result_view()
            st.info("親が次のゲームを開始するまでこのままお待ちください。")
            time.sleep(3)
            st.rerun()