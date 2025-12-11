import streamlit as st
import random

# -------------------- APP SETTINGS --------------------
st.set_page_config(
    page_title="StudyGenie — K•Apple Fusion",
    page_icon="🧠",
    layout="wide",
)

# -------------------- COLORS --------------------
COLOR_THEMES = {
    "Sky Blue (Doraemon)": ("#6EC9F5", "#0096D1"),
    "Rose Red": ("#FF6B81", "#FF4757"),
    "Lime Green": ("#A4E56D", "#4CD137"),
    "Purple Dream": ("#B197FC", "#6F42C1"),
    "Orange Burst": ("#FFD166", "#F77F00"),
}

# -------------------- SIDEBAR --------------------
st.sidebar.title("🎨 Theme Settings")
theme_name = st.sidebar.selectbox("Choose Theme", COLOR_THEMES.keys(), index=0)
gradient_start, gradient_end = COLOR_THEMES[theme_name]

# Background gradient
st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(to bottom right, {gradient_start}, {gradient_end});
        color: white !important;
    }}
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}
    [data-testid="stToolbar"] {{
        display: none;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- IQ QUESTIONS --------------------
QUESTIONS = [
    {
        "question": "1️⃣ What number comes next?\n2, 6, 12, 20, 30, ____",
        "options": ["40", "42", "45", "50"],
        "answer": "42"
    },
    {
        "question": "2️⃣ Which one is different?\nCat — Dog — Lion — Wolf",
        "options": ["Cat", "Dog", "Lion", "Wolf"],
        "answer": "Cat"
    },
    {
        "question": "3️⃣ If ALL roses are flowers, and SOME flowers fade quickly, what can you conclude?",
        "options": [
            "All roses fade quickly",
            "Some roses may fade quickly",
            "No roses fade quickly",
            "All flowers fade quickly"
        ],
        "answer": "Some roses may fade quickly"
    },
    {
        "question": "4️⃣ What is the missing letter?\nA, D, G, J, M, ____",
        "options": ["O", "N", "P", "Q"],
        "answer": "P"
    },
    {
        "question": "5️⃣ Find the odd number:\n27 — 64 — 125 — 144 — 216",
        "options": ["27", "64", "125", "144"],
        "answer": "144"
    },
    {
        "question": "6️⃣ A clock shows 3:15. What is the angle between hour & minute hand?",
        "options": ["0°", "7.5°", "15°", "30°"],
        "answer": "7.5°"
    },
    {
        "question": "7️⃣ What’s next?\nBB, DDD, FFFF, HHHHH, ____",
        "options": ["JJJJJJ", "IIIIII", "JJJJJ", "KKKKK"],
        "answer": "JJJJJJ"
    },
    {
        "question": "8️⃣ Solve: (3 × 4)² ÷ 6 = ?",
        "options": ["12", "24", "36", "144"],
        "answer": "24"
    },
    {
        "question": "9️⃣ Which shape has the most sides?",
        "options": ["Pentagon", "Hexagon", "Octagon", "Heptagon"],
        "answer": "Octagon"
    },
    {
        "question": "🔟 Complete the analogy:\nSun : Day :: Moon : ____",
        "options": ["Light", "Star", "Night", "Sky"],
        "answer": "Night"
    },
]

# -------------------- APP BODY --------------------
st.title("🧠 StudyGenie — K•Apple Fusion IQ Test")
st.markdown("Welcome, Genius! Let's test your IQ 💡 Choose the correct answer for each question.")

# Shuffle questions (optional)
random.shuffle(QUESTIONS)

score = 0

for q in QUESTIONS:
    st.markdown(f"### {q['question']}")
    answer = st.radio("Choose your answer:", q["options"], key=q["question"])
    if st.button(f"Submit for Q: {q['question']}", key=f"btn_{q['question']}"):
        if answer == q["answer"]:
            st.success(f"✅ Correct! The answer is **{q['answer']}**")
            score += 1
        else:
            st.error(f"❌ Wrong! The correct answer is **{q['answer']}**")

st.markdown("---")
st.subheader(f"🎯 Your Total Score: {score} / {len(QUESTIONS)}")