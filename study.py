import streamlit as st
import requests
import json

# -----------------------------
# BASIC PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="StudyGenie ✨",
    page_icon="✨",
    layout="wide"
)

# -----------------------------
# PASTEL BACKGROUND + CSS
# -----------------------------
st.markdown("""
<style>
body {
    background-color: #f6f0ff !important;
}
.chat-box {
    padding: 15px;
    background: white;
    border-radius: 12px;
    margin-bottom: 10px;
    box-shadow: 0 0 8px rgba(150,150,150,0.15);
}
.user-msg {
    background: #ffe9f3;
    border-left: 4px solid #ff7eb8;
}
.ai-msg {
    background: #e8f7ff;
    border-left: 4px solid #5abaff;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# INIT SESSION STATE
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# -----------------------------
# OPENAI REQUEST FUNCTION
# -----------------------------
def ask_ai(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}"
    }

    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": "You are StudyGenie, a helpful, cute, fun AI assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }

    try:
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=25
        )

        result = res.json()

        if "choices" not in result:
            return "⚠️ Bestie, AI got shy for a sec."

        reply = result["choices"][0]["message"]["content"]

        # save history
        st.session_state.chat_history.append({"you": prompt, "ai": reply})

        return reply

    except Exception as e:
        return f"❌ Error: {e}"


# -----------------------------
# SIDEBAR — Menu
# -----------------------------
with st.sidebar:
    st.title("✨ StudyGenie Menu")
    tool = st.radio("Choose Mode", ["Chat", "Saved Chats"])


# -----------------------------
# MAIN UI — CHAT MODE
# -----------------------------
if tool == "Chat":

    st.markdown("## 💬 Chat with StudyGenie")

    # show chat history
    for chat in st.session_state.chat_history:
        st.markdown(f"""
        <div class="chat-box user-msg"><b>You:</b> {chat['you']}</div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="chat-box ai-msg"><b>Genie:</b> {chat['ai']}</div>
        """, unsafe_allow_html=True)

    # input box
    user_msg = st.text_input("Type your message…")

    if st.button("Send 💫"):
        if user_msg.strip() != "":
            reply = ask_ai(user_msg)
            st.rerun()


# -----------------------------
# SAVED CHATS PAGE
# -----------------------------
if tool == "Saved Chats":
    st.markdown("## 📁 Saved Chats")

    if len(st.session_state.chat_history) == 0:
        st.info("No saved chats yet, bestie 💗")
    else:
        for i, chat in enumerate(st.session_state.chat_history):
            st.markdown(f"""
            <div class="chat-box"><b>Chat {i+1}</b><br><br>
            <b>You:</b> {chat['you']}<br>
            <b>Genie:</b> {chat['ai']}
            </div>
            """, unsafe_allow_html=True)

    if st.button("Clear All Chats 🚮"):
        st.session_state.chat_history = []
        st.rerun()