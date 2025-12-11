import streamlit as st
import requests
import json
import random

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="StudyGenie", layout="wide")

# =====================================================
# SOFT GRADIENT THEMES (DEFAULT = Doraemon)
# =====================================================

theme = st.sidebar.selectbox(
    "🌈 Choose Theme",
    ["Doraemon", "Sky Blue", "Pink Pastel", "Lavender"],
    index=0
)

gradient_themes = {
    "Doraemon": ("#a6e3ff", "#44a8ff"),
    "Sky Blue": ("#d8edff", "#a9d4ff"),
    "Pink Pastel": ("#ffd6e9", "#ffb3d1"),
    "Lavender": ("#efdbff", "#d2b6ff")
}

grad_start, grad_end = gradient_themes[theme]

# =====================================================
# APPLY GRADIENT CSS (35 DEGREE BABYYY 😭💙)
# =====================================================
st.markdown(
    f"""
    <style>

        /* MAIN APP BACKGROUND */
        .stApp {{
            background: linear-gradient(35deg, {grad_start}, {grad_end}) !important;
            color: #000000;
        }}

        /* SIDEBAR GLASS EFFECT */
        section[data-testid="stSidebar"] {{
            background: rgba(255,255,255,0.35) !important;
            border-right: 1px solid rgba(255,255,255,0.4);
            backdrop-filter: blur(6px);
        }}

        /* FONT FAMILY */
        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif !important;
        }}

        /* QUESTION BOX */
        .question-box {{
            padding: 20px;
            background: white;
            border-radius: 16px;
            font-size: 18px;
            border: 2px solid #ffffff55;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# SIDEBAR UI
# =====================================================
with st.sidebar:
    st.title("📘 StudyGenie")

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

# =====================================================
# AI API FUNCTION
# =====================================================
def ask_ai(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}"
    }

    payload = {
        "model": "gpt-4.1-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.7
    }

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers, 
            data=json.dumps(payload), 
            timeout=20
        )
        data = r.json()

        if "choices" not in data:
            return "⚠️ AI error."

        reply = data["choices"][0]["message"]["content"]

        st.session_state.chat_history.append({"you": prompt, "ai": reply})
        st.session_state["clear_input"] = True

        return reply

    except Exception as e:
        return "❌ Error: " + str(e)

# =====================================================
# INIT CHAT VARIABLES
# =====================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

# =====================================================
# NON-IQ TOOLS
# =====================================================
if tool != "Mini IQ Test Game 🧠":

    st.markdown(f"<h1 style='text-align:center;'>✨ {tool} ✨</h1>", unsafe_allow_html=True)

    for chat in st.session_state.chat_history:
        st.markdown(f"**You:** {chat['you']}")
        st.markdown(f"**Genie:** {chat['ai']}")

    default_text = "" if st.session_state.clear_input else st.session_state.get("last_prompt", "")
    prompt = st.text_area("Type your message 💬", value=default_text)
    st.session_state.last_prompt = prompt

    if st.button("Send"):
        if prompt.strip():
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
# IQ TEST (MCQ)
# =====================================================
if tool == "Mini IQ Test Game 🧠":
    
    st.markdown("<h1 style='text-align:center;'>🧠 Mini IQ Test (MCQ)</h1>", unsafe_allow_html=True)

    iq_mcq = [
        ("What number comes next? 2,6,12,20,30,__",
         ["36", "40", "42", "44"], "42"),

        ("Which one is different?",
         ["Cat", "Dog", "Lion", "Wolf"], "Cat"),

        ("Conclusion? If ALL roses are flowers…",
         ["All roses fade", "Some roses may fade", "No roses fade"], "Some roses may fade"),

        ("Missing letter? A, D, G, J, M, __",
         ["O", "P", "N", "Q"], "P"),

        ("Odd number: 27, 64, 125, 144, 216",
         ["27", "144", "125", "216"], "144"),

        ("Which is bigger?",
         ["3/7", "4/9"], "4/9"),

        ("Solve: (3×4)² ÷ 6",
         ["12", "24", "36", "48"], "24"),

        ("Sun : Day :: Moon : __",
         ["Light", "Night", "Sky", "Dark"], "Night"),

        ("Which weighs more?",
         ["1kg Iron", "1kg Cotton", "Same"], "Same"),

        ("45% of 200",
         ["70", "80", "90", "100"], "90")
    ]

    if "current_q" not in st.session_state:
        st.session_state.current_q = random.choice(iq_mcq)

    q, options, correct = st.session_state.current_q

    st.markdown(f"<div class='question-box'>{q}</div>", unsafe_allow_html=True)

    user_choice = st.radio("Choose option:", options)

    if st.button("Submit Answer"):
        if user_choice == correct:
            st.success("🔥 Correct!!")
        else:
            st.error(f"❌ Wrong! Correct answer: **{correct}**")

    if st.button("New Question"):
        st.session_state.current_q = random.choice(iq_mcq)
        st.rerun()