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
    st.title("😘 StudyGenie AI Study Bestie 💖")

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

        # auto-clear input box
        st.session_state["clear_input"] = True

        return reply

    except Exception as e:
        return "❌ Error: " + str(e)

# -----------------------------
# CHAT SYSTEM
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

if tool != "Mini IQ Test Game 🧠":
    st.markdown(f"<h1 style='text-align:center;'>✨ {tool} ✨</h1>", unsafe_allow_html=True)

    for chat in st.session_state.chat_history:
        st.markdown(f"**You:** {chat['you']}")
        st.markdown(f"**Genie:** {chat['ai']}")

    # auto-clear after send
    default_text = "" if st.session_state.clear_input else st.session_state.get("last_prompt", "")
    prompt = st.text_area("Type your message 💬", value=default_text)
    st.session_state.last_prompt = prompt

    if st.button("Send"):
        if prompt.strip() != "":
            st.session_state.clear_input = True
            response = ask_ai(f"{tool}: {prompt}")
            st.markdown(f"**Genie:** {response}")
            st.session_state.last_prompt = ""

    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.last_prompt = ""
        st.session_state.clear_input = True
        st.rerun()


# =====================================================
# 🧠 NEW IQ TEST GAME WITH 25 REAL QUESTIONS
# =====================================================
if tool == "Mini IQ Test Game 🧠":
    st.markdown("<h1 style='text-align:center;'>🧠 Mini IQ Test (K-Edition)</h1>", unsafe_allow_html=True)

    level = st.selectbox("Choose Difficulty 🎯", ["Easy", "Medium", "Hard"])

    iq_questions = [
        ("What number comes next? 2,6,12,20,30,__", "42"),
        ("Which one is different? Cat — Dog — Lion — Wolf", "Cat"),
        ("If ALL roses are flowers... conclusion?", "B"),
        ("Which figure completes pattern?⬜⬜⬛⬜ / ⬛⬜⬛⬜ / ⬜⬛⬜⬛", "⬛⬜⬛⬜"),
        ("Missing letter? A, D, G, J, M, __", "P"),
        ("If TRAP→WSDS (+3), COLD becomes?", "FROG"),
        ("Find odd number: 27,64,125,144,216", "144"),
        ("Angle at 3:15?", "7.5"),
        ("Series: 5,9,17,33,__", "65"),
        ("If 1=3,2=3,3=5,4=4 then 5=?", "4"),
        ("Rearrange: A P L E P", "APPLE"),
        ("Most sides? Pentagon, Hexagon, Octagon, Heptagon", "Octagon"),
        ("Solve: (3×4)² ÷ 6", "24"),
        ("Add to 25 & multiply to 126", "9 and 14"),
        ("If TODAY = 23, HAPPY = ?", "50"),
        ("Cube has 3 faces painted red, how many not painted?", "3"),
        ("Which word doesn't belong? Blue Red Circle Green Yellow", "Circle"),
        ("Which fraction bigger? 3/7 or 4/9", "4/9"),
        ("Analogy: Sun:Day :: Moon:__", "Night"),
        ("Train 6:45 → 9:15 duration?", "2.5 hours"),
        ("Next: BB, DDD, FFFF, HHHHH,__", "JJJJJJ"),
        ("Perimeter 30, length 9, width?", "6"),
        ("Which weighs more? 1kg iron or 1kg cotton", "Same"),
        ("45% of 200", "90"),
        ("12 edges + 8 vertices = which 3D shape?", "Cube")
    ]

    if "current_q" not in st.session_state:
        st.session_state.current_q = random.choice(iq_questions)

    question, answer = st.session_state.current_q

    st.subheader(f"👉 {question}")

    user_input = st.text_input("Your answer:")

    if st.button("Submit Answer"):
        if user_input.strip().lower() == str(answer).lower():
            st.success("🔥 Correct bestie!! Genius mode unlocked 💖")
        else:
            st.error(f"😭 Wrong babe… correct answer was **{answer}** 💗")

    if st.button("New Question"):
        st.session_state.current_q = random.choice(iq_questions)
        st.rerun()