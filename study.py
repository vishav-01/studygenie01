import streamlit as st
import requests
import json
import random
import time

st.set_page_config(page_title="StudyGenie AI Bestie", layout="wide")

# -----------------------------
# THEME SELECTOR
# -----------------------------
theme = st.sidebar.selectbox(
    "🌈 Choose Theme",
    ["Pink Pastel", "Sky Blue", "Lavender", "Doraemon"]
)

theme_colors = {
    "Sky Blue": "#cfe8ff",
    "Lavender": "#e6d7ff",
    "Doraemon": "#44a8ff",
    "Pink Pastel": "#ffd1dc"
}

bg_color = theme_colors[theme]

# Apply CSS aesthetic
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
# SIDEBAR
# -----------------------------
with st.sidebar:

    st.title("StudyGenie AI Study Bestie 💕")

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
            "Snake Game 🎮"   # ADDED NEW GAME OPTION
        ]
    )

# -----------------------------
# AI CHAT FUNCTION
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
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=25
        )
        data = r.json()

        if "choices" not in data:
            return "⚠️ Bestie, I think the AI fainted 😭."

        reply = data["choices"][0]["message"]["content"]

        st.session_state.chat_history.append({"you": prompt, "ai": reply})
        return reply

    except Exception as e:
        return "❌ Error: " + str(e)


# -----------------------------
# CHAT HISTORY
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown(f"<h1 style='text-align:center;'>✨ {tool} ✨</h1>", unsafe_allow_html=True)

for chat in st.session_state.chat_history:
    st.markdown(f"**You:** {chat['you']}")
    st.markdown(f"**Genie:** {chat['ai']}")

prompt = st.text_area("Type your message 💬")
if st.button("Send"):
    if prompt.strip():
        response = ask_ai(f"{tool}: {prompt}")
        st.markdown(f"**Genie:** {response}")

if st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()


# ---------------------------------------------------
# (ALL YOUR OLD TOOLS ARE SAME — SKIPPING TO NEW ONE)
# ---------------------------------------------------

# ---------------------------------------------------
# NEW TOOL — SNAKE GAME 🎮
# ---------------------------------------------------
if tool == "Snake Game 🎮":

    st.subheader("🐍 Welcome to Snack King — Snake Game!")

    GRID = 20

    if "snake" not in st.session_state:
        st.session_state.snake = [(5, 11), (5, 12), (5, 13)]
        st.session_state.food = (10, 10)
        st.session_state.direction = "RIGHT"
        st.session_state.score = 0
        st.session_state.game_over = False

    def move():
        if st.session_state.game_over:
            return
        
        x, y = st.session_state.snake[-1]

        if st.session_state.direction == "UP":
            y -= 1
        elif st.session_state.direction == "DOWN":
            y += 1
        elif st.session_state.direction == "LEFT":
            x -= 1
        else:
            x += 1

        head = (x, y)

        # collision
        if x < 0 or x >= GRID or y < 0 or y >= GRID or head in st.session_state.snake:
            st.session_state.game_over = True
            return

        st.session_state.snake.append(head)

        # food
        if head == st.session_state.food:
            st.session_state.score += 1
            st.session_state.food = (random.randint(0, GRID-1), random.randint(0, GRID-1))
        else:
            st.session_state.snake.pop(0)

    def draw():
        board = ""
        for yy in range(GRID):
            for xx in range(GRID):
                if (xx, yy) in st.session_state.snake:
                    board += "🟩"
                elif (xx, yy) == st.session_state.food:
                    board += "🍎"
                else:
                    board += "⬛"
            board += "\n"
        st.text(board)

    st.markdown("### 🎮 Controls")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⬅️ Left"):
            st.session_state.direction = "LEFT"
    with c2:
        if st.button("⬆️ Up"):
            st.session_state.direction = "UP"
        if st.button("⬇️ Down"):
            st.session_state.direction = "DOWN"
    with c3:
        if st.button("➡️ Right"):
            st.session_state.direction = "RIGHT"

    if not st.session_state.game_over:
        move()

    draw()

    st.markdown(f"### ⭐ Score: **{st.session_state.score}**")

    if st.session_state.game_over:
        st.error("💀 Game Over Bestie!")


# END OF CODE