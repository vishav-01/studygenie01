import streamlit as st
import requests
import json
import random

st.set_page_config(page_title="StudyGenie — K Edition", layout="wide")

# -----------------------------
# THEME SELECTOR
# -----------------------------
theme = st.sidebar.selectbox(
    "🌈 Choose Theme",
    ["Pink Pastel", "Sky Blue", "Lavender", "Doraemon"]
)

theme_colors = {
    "Pink Pastel": "#ffd1dc",
    "Sky Blue": "#cfe8ff",
    "Lavender": "#e6d7ff",
    "Doraemon": "#44a8ff"
}

bg_color = theme_colors[theme]

# -----------------------------
# APPLY CSS
# -----------------------------
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {bg_color} !important;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {bg_color}20 !important;
        }}
        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# SIDEBAR UI
# -----------------------------
with st.sidebar:
    st.title("StudyGenie — K Edition 💖")

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
            "Mini IQ Test Game 🧠",
            "Mini Snake Game 🐍"
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
        "max_tokens": 1500,
        "temperature": 0.65
    }

    try:
        r = requests.post("https://api.openai.com/v1/chat/completions",
                          headers=headers, data=json.dumps(payload), timeout=20)
        data = r.json()

        if "choices" not in data:
            return "⚠️ Bestie, I think the AI fainted 😭."

        reply = data["choices"][0]["message"]["content"]
        st.session_state.chat_history.append({"you": prompt, "ai": reply})
        return reply

    except Exception as e:
        return "❌ Error: " + str(e)


# -----------------------------
# CHAT SYSTEM
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Normal tools output
if tool not in ["Mini IQ Test Game 🧠", "Mini Snake Game 🐍"]:
    st.markdown(f"<h1 style='text-align:center;'>✨ {tool} ✨</h1>", unsafe_allow_html=True)

    for chat in st.session_state.chat_history:
        st.markdown(f"**You:** {chat['you']}")
        st.markdown(f"**Genie:** {chat['ai']}")

    prompt = st.text_area("Type your message 💬")
    if st.button("Send"):
        if prompt.strip() != "":
            response = ask_ai(f"{tool}: {prompt}")
            st.markdown(f"**Genie:** {response}")

    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()


# ============================
# 🧠 MINI IQ TEST GAME
# ============================
if tool == "Mini IQ Test Game 🧠":
    st.markdown("<h1 style='text-align:center;'>🧠 Mini IQ Test Game</h1>", unsafe_allow_html=True)

    if "iq_answer" not in st.session_state:
        num1 = random.randint(10, 99)
        num2 = random.randint(10, 99)
        st.session_state.iq_question = f"{num1} + {num2}"
        st.session_state.iq_answer = num1 + num2

    st.subheader(f"Solve this bestie 👉 {st.session_state.iq_question}")

    user_ans = st.number_input("Your answer:", step=1)

    if st.button("Submit Answer"):
        if user_ans == st.session_state.iq_answer:
            st.success("💖 Yesss bestieee! You’re a genius 😭🔥")
        else:
            st.error("😭 Wrong babe… try again, I believe in you 💕")

    if st.button("New Question"):
        st.session_state.pop("iq_answer")
        st.rerun()


# ============================
# 🐍 MINI SNAKE GAME
# ============================
if tool == "Mini Snake Game 🐍":
    st.markdown("<h1 style='text-align:center;'>🐍 Mini Snake Game</h1>", unsafe_allow_html=True)

    st.info("Bestie full premium Snake Game needs HTML canvas & JS.  
            But Streamlit cannot run JS directly 😭  
            So I added a simple clickable Snake-like game.")

    if "snake_score" not in st.session_state:
        st.session_state.snake_score = 0

    if st.button("Eat Fruit 🍎"):
        st.session_state.snake_score += 1

    st.write(f"Score: **{st.session_state.snake_score}**")

    if st.button("Reset Game"):
        st.session_state.snake_score = 0
        st.rerun()