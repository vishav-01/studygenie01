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
            "Mini IQ Test Game 🧠"
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

if tool != "Mini IQ Test Game 🧠":
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


# =====================================================
# 🧠 MULTI-LEVEL IQ TEST GAME (EASY / MEDIUM / HARD)
# =====================================================
if tool == "Mini IQ Test Game 🧠":
    st.markdown("<h1 style='text-align:center;'>🧠 Multi-Level IQ Test</h1>", unsafe_allow_html=True)

    # Level Selector
    level = st.selectbox(
        "Choose Difficulty 🎯",
        ["Easy", "Medium", "Hard"]
    )

    # IQ Question Generator
    def generate_question(level):
        if level == "Easy":
            a = random.randint(5, 20)
            b = random.randint(5, 20)
            return f"{a} + {b}", a + b

        elif level == "Medium":
            a = random.randint(10, 40)
            b = random.randint(10, 40)
            return f"{a} × {b}", a * b

        elif level == "Hard":
            a = random.randint(50, 150)
            b = random.randint(2, 12)
            c = random.randint(10, 50)
            expr = f"({a} ÷ {b}) + {c}"
            return expr, (a / b) + c

    # Store Question
    if "iq_question" not in st.session_state:
        q, ans = generate_question(level)
        st.session_state.iq_question = q
        st.session_state.iq_answer = ans
        st.session_state.iq_level = level

    # New question when level changes
    if level != st.session_state.iq_level:
        q, ans = generate_question(level)
        st.session_state.iq_question = q
        st.session_state.iq_answer = ans
        st.session_state.iq_level = level

    # Display Question
    st.subheader(f"Solve this bestie 👉 {st.session_state.iq_question}")

    user_ans = st.text_input("Your answer:")

    if st.button("Submit Answer"):
        try:
            if float(user_ans) == float(st.session_state.iq_answer):
                st.success("💖 AYYYYE you got it right bestie!! Smartest alive 😭🔥")
            else:
                st.error("😭 Wrong babe… but I still love you, try again 💗")
        except:
            st.warning("Enter a valid number babe 😭💗")

    if st.button("New Question"):
        q, ans = generate_question(level)
        st.session_state.iq_question = q
        st.session_state.iq_answer = ans
        st.session_state.iq_level = level
        st.rerun()