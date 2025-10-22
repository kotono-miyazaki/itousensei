# app.py

import streamlit as st
import uuid
import requests

# ------------------------
# モデルID（必要に応じて変更）
# ------------------------
MODEL = "gemini-2.0-flash"

# ------------------------
# セッション初期化
# ------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# ------------------------
# 画面タイトル・説明
# ------------------------
st.title("🧠 うつ改善カウンセリングチャット")
st.markdown("あなたの気持ちにやさしく寄り添うチャットボットです。")

# ------------------------
# APIキー入力欄（画面中央）
# ------------------------
st.subheader("🔐 Gemini APIキーの入力")
api_key = st.text_input(
    "APIキー（[取得はこちら](https://makersuite.google.com/app/apikey)）",
    type="password",
    placeholder="ここに貼り付けてください",
)

if not api_key:
    st.warning("まずは上にAPIキーを入力してください。")
    st.stop()

# ------------------------
# 気分スライダー
# ------------------------
mood = st.slider("🎭 今日の気分（0=最悪, 10=最高）", 0, 10, 5)

# ------------------------
# ネガティブワード検出
# ------------------------
def check_risk(text):
    risk_keywords = ["死にたい", "自殺", "消えたい", "限界", "苦しい", "つらい", "もうダメ"]
    return any(kw in text for kw in risk_keywords)

# ------------------------
# Gemini API 呼び出し関数
# ------------------------
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

# ------------------------
# チャット入力欄
# ------------------------
user_input = st.text_input("✍️ 今の気持ちを書いてみてください", placeholder="例: 最近、眠れない日が続いています…")

if st.button("送信") and user_input:
    # ユーザーの発言を履歴に追加
    st.session_state.history.append({"role": "user", "content": user_input})

    try:
        # Gemini に送信して応答取得
        response = call_gemini(user_input, st.session_state.history, api_key)

        # 応答を履歴に追加
        st.session_state.history.append({"role": "model", "content": response})

        # ネガティブワード検出（ユーザー + 応答）
        if check_risk(user_input + response):
            st.warning("⚠️ 深刻なサインが検出されました。必要に応じて専門機関へご相談ください。")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

# ------------------------
# チャット履歴表示
# ------------------------
if st.session_state.history:
    st.write("### 💬 チャット履歴")
    for msg in st.session_state.history:
        speaker = "🧍‍♂️ あなた" if msg["role"] == "user" else "🤖 ボット"
        st.markdown(f"**{speaker}：** {msg['content']}")

# ------------------------
# フッター注意喚起
# ------------------------
st.write("---")
st.info(
    "📌 このアプリは医療行為を目的としたものではありません。深刻な症状がある場合は、精神科や専門機関にご相談ください。"
)

# ------------------------
# APIキー取得リンク（再掲）
# ------------------------
st.markdown(
    """
---  
🔑 **[Gemini APIキーを取得するにはこちらをクリック](https://makersuite.google.com/app/apikey)**  
1. Googleアカウントでログイン  
2. 利用規約に同意  
3. 表示されたAPIキーをコピー  
4. 上の入力欄に貼り付けてください
"""
)
