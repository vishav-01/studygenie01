import streamlit as st
import requests
import json

st.set_page_config(page_title="StudyGenie — K Edition", layout="wide")

# -----------------------------
# THEME SYSTEM (3 Themes)
# -----------------------------
THEMES = {
    "K-Pink": """
        <style>
        body { background-color: #ffe7f3; }
        .main { background-color: #fff0f8; }
        </style>
    """,
    "Sky Pastel": """
        <style>
        body { background-color: #e7f3ff; }
        .main { background-color: #f2f8ff; }
        </style>
    """,
    "Doraemon": """
        <style>
        body { background-color: #d7ecff; }
        .main { background-color: #ffffff; }
        h1, h2, h3, p { color: #005bbb !important; }
        </style>
    """
}

# Load saved theme
if "theme" not in st.session_state:
    st.session_state.theme = "K-Pink"

st.markdown(THEMES[st.session_state.theme], unsafe_allow_html=True)

# -----------------------------
# SIDEBAR UI
# -----------------------------
with st.sidebar:
    st.image("https://i.imgur.com/4QZclRq.png", width=130)  # cute Doraemon / pastel logo

    st.title("StudyGenie — K Edition")

    theme_choice = st.selectbox("Select Theme 💖", ["K-Pink", "Sky Pastel", "Doraemon"])
    st.session_state.theme = theme_choice

    tool = st.radio(
        "Choose a Tool ✨",
        [
            "AI Doubt Solver",
            "Notes Generator",
            "Summary Maker",
            "Timetable Builder",
            "Motivation Booster",
            "Flashcards",
            "Brain-Dump Cleaner",
            "Answer Checker",
            "AI Planner",
            "Mindset Reset",
            "Study Routine Designer",
            "Exam Strategy Maker",
            "Personal Study Coach",
        ]
    )

# -----------------------------
# AI ASK FUNCTION
# -----------------------------
def ask_ai(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}"
    }

    payload = {
        "model": "gpt-4.1-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 350,
        "temperature": 0.65
    }

    try:
        r = requests.post("https://api.openai.com/v1/chat/completions",
                          headers=headers, data=json.dumps(payload), timeout=25)
        data = r.json()

        if "choices" not in data:
            return "⚠️ Bestie, I think the AI fainted for a sec 😭."

        reply = data["choices"][0]["message"]["content"]

        st.session_state.chat_history.append({"you": prompt, "ai": reply})
        return reply

    except Exception as e:
        return "❌ Error: " + str(e)


# -----------------------------
# TOOL ENGINE
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown(f"<h1 style='text-align:center;'>✨ {tool} ✨</h1>", unsafe_allow_html=True)

# Show previous chats
for chat in st.session_state.chat_history:
    st.markdown(f"**You:** {chat['you']}")
    st.markdown(f"**Genie:** {chat['ai']}")

# Input + send
prompt = st.text_area("Type your message 💬")
if st.button("Send"):
    if prompt.strip() != "":
        response = ask_ai(f"{tool}: {prompt}")
        st.markdown(f"**Genie:** {response}")

# Clear chat
if st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()