import streamlit as st import requests import json

----------------------

💖 K‑POP THEMED AI STUDYGENIE — FULLY WORKING

----------------------

st.set_page_config(page_title="StudyGenie K‑POP Edition", layout="centered")

💎 TITLE

st.markdown( """ <h1 style='text-align: center; color:#ff66cc; font-family: "Poppins", sans-serif;'>✨ StudyGenie — K‑POP Edition ✨</h1> <p style='text-align: center; color:#ff99dd;'>Your ultimate study idol — serving looks, brains, and A+ vibes 🎤📚💘</p> """, unsafe_allow_html=True, )

----------------------

🔐 AI CALL FUNCTION

----------------------

def ask_ai(prompt): headers = { "Content-Type": "application/json", "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}" }

payload = {
    "model": "gpt-4.1-mini",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 350,
    "temperature": 0.7
}

try:
    req = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(payload))
    res = req.json()

    if "choices" not in res:
        return "⚠️ Oppa the AI fainted from too much beauty. Try again! 💞"

    return res["choices"][0]["message"]["content"]

except Exception as e:
    return "❌ Error: " + str(e)

----------------------

💖 FEATURES (K‑POP STYLE)

----------------------

features = [ "AI Doubt Solver", "Notes Generator", "Summary Maker", "Timetable Builder", "Motivation Booster", "Flashcards", "Brain‑Dump Cleaner", "Answer Checker", "AI Planner", "Mindset Reset", "Study Routine Designer", "Exam Strategy Maker", "Personal Study Coach" ]

selected = st.selectbox("Choose your feature, trainee 💗:", features)

st.write("---")

----------------------

💫 FEATURE LOGIC

----------------------

if selected: user_input = st.text_area(f"💬 Enter your request for {selected}:")

if st.button("✨ Generate — K‑POP Style ✨"):
    if user_input.strip() == "":
        st.error("Write something babe 💗🥺✨")
    else:
        prompt = f"You are a K‑POP idol AI helper with cute, stylish energy. Feature: {selected}. User request: {user_input}. Respond in a helpful, aesthetic, slightly sparkly idol tone."
        reply = ask_ai(prompt)
        st.markdown(f"<div style='background:#ffe6f7; padding:15px; border-radius:15px; color:#cc0088;'>{reply}</div>", unsafe_allow_html=True)