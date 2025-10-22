# app.py

import streamlit as st
import uuid
import requests

# --- モデルID（適宜確認・変更可能） ---
MODEL = "gemini-1.5-flash"  # または "gemini-1.0-pro" など、Googleの提供内容に応じて変更

# --- セッションステート初期化 ---
if "history" not in st.session_state:
    st.session_state.history = []  # チャット履歴
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# --- サイドバー：APIキー入力と取得案内 ---
st.sidebar.title("🔐 Gemini APIキーの設定")

# ユーザーが入力するAPIキー（セッションに保存）
api_key = st.sidebar.text_input("APIキーを入力してください", type="password")
st.sidebar.caption("※ このセッション中のみ保存されます")

# Gemini APIキー取得リンクと手順
st.sidebar.markdown("### 🔑 Gemini APIキーを取得する")
st.sidebar.markdown(
    """
[👉 Google Gemini APIキーを取得する](https://makersuite.google.com/app/apikey)

1. Googleアカウントでログイン  
2. 利用規約に同意  
3. 表示されたAPIキーをコピー  
4. 上の入力欄に貼り付けてください
"""
)

# --- タイトル・気分チェック ---
st.title("🧠 うつ改善カウンセリングチャット")
st.markdown("気持ちや悩みを自由に入力してください。ボットが優しく対話します。")

mood = st.slider("🎭 今日の気分（0=最悪, 10=最高）", 0, 10, 5)

# --- ネガティブワード検出関数（簡易） ---
def check_risk(text):
    risk_keywords = ["死にたい", "自殺", "消えたい", "限界", "苦しい", "つらい", "もうダメ"]
    return any(kw in text for kw in risk_keywords)

# --- Gemini API 呼び出し ---
def call_gemini(prompt, history, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = history + [{"role": "user", "content": prompt}]
    payload = {
        "contents": [
            {
                "role": msg["role"],
                "parts": [{"text": msg["content"]}]
            } for msg in messages
        ]
    }

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

# --- ユーザー入力 ---
user_input = st.text_input("✍️ 今の気持ちを書いてみてください", placeholder="例: 最近、眠れない日が続いています…")

if st.button("送信") and user_input:
    if not api_key:
        st.error("❌ Gemini APIキーを入力してください。サイドバーから取得できます。")
    else:
        # ユーザー発言を履歴に追加
        st.session_state.history.append({"role": "user", "content": user_input})

        try:
            # Gemini にメッセージ送信
            response = call_gemini(user_input, st.session_state.history, api_key)

            # 応答追加
            st.session_state.history.append({"role": "model", "content": response})

            # リスクチェック（入力＋応答）
            if check_risk(user_input + response):
                st.warning("⚠️ 深刻なサインが検出されました。必要に応じて専門機関へご相談ください。")
        
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# --- チャット履歴表示 ---
if st.session_state.history:
    st.write("### 💬 チャット履歴")
    for msg in st.session_state.history:
        speaker = "🧍‍♂️ あなた" if msg["role"] == "user" else "🤖 ボット"
        st.markdown(f"**{speaker}：** {msg['content']}")

# --- フッター警告 ---
st.write("---")
st.info(
    "📌 **このアプリは医療行為を目的としたものではありません。深刻な症状がある場合は、精神科や専門機関にご相談ください。**"
)
