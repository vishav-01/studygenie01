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
# 🧠 CUSTOM IQ TEST GAME — YOUR QUESTIONS ADDED
# =====================================================
if tool == "Mini IQ Test Game 🧠":
    st.markdown("<h1 style='text-align:center;'>🧠 Multi-Level IQ Test</h1>", unsafe_allow_html=True)

    # -----------------------------
    # QUESTION BANK (YOUR QUESTIONS)
    # -----------------------------

    EASY_QUESTIONS = [
        ("Which one is different? Cat — Dog — Lion — Wolf", "Cat"),
        ("What is the missing letter? A, D, G, J, M, ____", "P"),
        ("Rearrange the letters to make a word: A P L E P", "APPLE"),
        ("Which shape has the most sides? Pentagon — Hexagon — Octagon — Heptagon", "Octagon"),
        ("Sun : Day :: Moon : ____", "Night"),
        ("Which weighs more? 1 kg iron or 1 kg cotton?", "Same"),
        ("What comes next? ⬛⬜⬛⬜ → ⬜⬛⬜⬛ → ⬛⬜⬛⬜ → ?", "⬜⬛⬜⬛")
    ]

    MEDIUM_QUESTIONS = [
        ("What number comes next? 2, 6, 12, 20, 30, ____", "42"),
        ("What is the missing letter? B, E, H, K, N, ____", "Q"),
        ("Find the odd number: 27 — 64 — 125 — 144 — 216", "144"),
        ("Which number completes the series? 5, 9, 17, 33, ____", "65"),
        ("A clock shows 3:15. What is the angle between hour & minute hand?", "7.5"),
        ("Solve: (3 × 4)² ÷ 6 = ?", "8"),
        ("What fraction is bigger? 3/7 or 4/9?", "4/9")
    ]

    HARD_QUESTIONS = [
        ("If TRAP becomes WSDS (+3 letters), what does COLD become?", "FROG"),
        ("What comes next? 11, 13, 17, 19, 23, ____", "29"),
        ("Solve: 45% of 200 = ?", "90"),
        ("If 1 = 3, 2 = 3, 3 = 5, 4 = 4, then 5 = ?", "4"),
        ("Complete the analogy: BB, DDD, FFFF, HHHHH, ____", "JJJJJJ"),
        ("Complete: AZ, BY, CX, DW, ____", "EV"),
        ("Find the odd one: Blue — Red — Circle — Green — Yellow", "Circle")
    ]

    # Level selector
    level = st.selectbox(
        "Choose Difficulty 🎯",
        ["Easy", "Medium", "Hard"]
    )

    # Select question set based on level
    if level == "Easy":
        qset = EASY_QUESTIONS
    elif level == "Medium":
        qset = MEDIUM_QUESTIONS
    else:
        qset = HARD_QUESTIONS

    # Create new question if needed
    if "iq_q" not in st.session_state:
        st.session_state.iq_q, st.session_state.iq_a = random.choice(qset)

    # Display question
    st.subheader(f"Bestie solve this 👉 {st.session_state.iq_q}")

    user_ans = st.text_input("Your answer:")

    if st.button("Submit Answer"):
        if user_ans.strip().lower() == str(st.session_state.iq_a).lower():
            st.success("💖 YESS BABE YOU’RE A GENIUS OMG 😭🔥")
        else:
            st.error(f"😭 Wrong babe… correct is: {st.session_state.iq_a}")

    if st.button("New Question"):
        st.session_state.iq_q, st.session_state.iq_a = random.choice(qset)
        st.rerun()