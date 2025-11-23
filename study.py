import streamlit as st
import requests
import json

st.set_page_config(page_title="StudyGenie — K Edition", layout="wide")

# -----------------------------
# THEME SYSTEM (3 Themes)
# -----------------------------
THEMES = {
    "Pink K-Pop Glow": {
        # Baby Pink Background & K-Pink Text
        "page_bg": "#f9e7f7", 
        "tile_border": "#ff69b4", # Bright Pink Border
        "css_extras": """
            /* Text Color adjustment for better visibility on light pink */
            html, body, [data-testid="stAppViewContainer"] {
                color: #ff1493; /* Deep K-Pink text color */
            }
        """,
    },
    "Sky Pastel Dream": {
        # Lavender Background & Dark Blue Text
        "page_bg": "#e6e6fa", # Lavender background
        "tile_border": "#00008b", # Dark Blue Border
        "css_extras": """
            /* Dark Blue Text color */
            html, body, [data-testid="stAppViewContainer"], 
            h1, h2, h3, p, .stMarkdown {
                color: #00008b !important; 
            }
        """,
    },
    "Doraemon Playroom": {
        # Sky Blue Background & Doraemon Blue Text
        "page_bg": "#87ceeb", # Sky Blue background
        "tile_border": "#005bbb", # Doraemon Blue Border
        "css_extras": """
            /* Doraemon Blue Text color */
            html, body, [data-testid="stAppViewContainer"],
            h1, h2, h3, p, .stMarkdown {
                color: #005bbb !important; 
            }
        """,
    }
}

# Load saved theme
if "theme" not in st.session_state:
    st.session_state.theme = "K-Pink"

st.markdown(THEMES[st.session_state.theme], unsafe_allow_html=True)

# -----------------------------
# SIDEBAR UI
# -----------------------------
with st.sidebar:

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
