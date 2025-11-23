import streamlit as st
import openai

# ------------------- Page Setup -------------------
st.set_page_config(page_title="StudyGenie AI", page_icon="✨", layout="centered")

# ------------------- Pastel Background -------------------
pastel_css = """
<style>
body {
    background-color: #f8e8ff; /* pastel lavender */
}
.main {
    background-color: #ffffffbb !important;
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 20px;
}
.chat-bubble-user {
    background: #d8b4f8;
    color: black;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    width: fit-content;
    max-width: 80%;
}
.chat-bubble-bot {
    background: #c9f4ff;
    color: black;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    width: fit-content;
    max-width: 80%;
}
</style>
"""

st.markdown(pastel_css, unsafe_allow_html=True)

# ------------------- API Key -------------------
openai.api_key = "YOUR_OPENAI_API_KEY"

# ------------------- Session State -------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ------------------- Title -------------------
st.markdown("<h1 style='text-align:center;'>✨ StudyGenie AI Chat ✨</h1>", unsafe_allow_html=True)

# ------------------- Chat Display -------------------
for role, msg in st.session_state.history:
    if role == "user":
        st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-bot'><b>Genie:</b> {msg}</div>", unsafe_allow_html=True)

# ------------------- User Input -------------------
user_input = st.text_input("Type your message…", "")

# ------------------- Handle Message -------------------
if st.button("Send") and user_input.strip():
    st.session_state.history.append(("user", user_input))

    # AI response
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are StudyGenie, a helpful AI."},
            ] + [{"role": role, "content": msg} for role, msg in st.session_state.history]
        )

        bot_reply = response.choices[0].message["content"]
        st.session_state.history.append(("assistant", bot_reply))

    except Exception as e:
        bot_reply = f"Error: {str(e)} 😭"
        st.session_state.history.append(("assistant", bot_reply))

    st.experimental_rerun()
