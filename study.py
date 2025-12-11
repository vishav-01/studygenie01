# =====================================================
# 🧠 NEW IQ TEST GAME (MCQ VERSION) — Doraemon Blue Default
# =====================================================
if tool == "Mini IQ Test Game 🧠":

    st.markdown("<h1 style='text-align:center;'>🧠 Mini IQ Test (K-Edition)</h1>", unsafe_allow_html=True)

    # Default background override for IQ test
    st.markdown("""
        <style>
            .stApp {
                background-color: #44a8ff !important;
            }
        </style>
    """, unsafe_allow_html=True)

    level = st.selectbox("Choose Difficulty 🎯", ["Easy", "Medium", "Hard"])

    # -----------------------------
    # MCQ QUESTION BANK
    # -----------------------------
    iq_mcq = [
        {
            "q": "What number comes next? 2, 6, 12, 20, 30, __",
            "options": ["A) 36", "B) 40", "C) 42", "D) 48"],
            "answer": "C"
        },
        {
            "q": "Which one is different?",
            "options": ["A) Dog", "B) Lion", "C) Wolf", "D) Cat"],
            "answer": "D"
        },
        {
            "q": "If ALL roses are flowers, which is true?",
            "options": [
                "A) Some roses are not flowers",
                "B) All roses are flowers",
                "C) No roses are flowers",
                "D) Flowers aren't roses"
            ],
            "answer": "B"
        },
        {
            "q": "Missing letter? A, D, G, J, M, __",
            "options": ["A) O", "B) P", "C) R", "D) S"],
            "answer": "B"
        },
        {
            "q": "Find the odd number:",
            "options": ["A) 27", "B) 64", "C) 125", "D) 144"],
            "answer": "D"
        },
        {
            "q": "Angle at 3:15?",
            "options": ["A) 0°", "B) 7.5°", "C) 15°", "D) 22.5°"],
            "answer": "B"
        },
        {
            "q": "Which fraction is bigger?",
            "options": ["A) 3/7", "B) 4/9", "C) Both equal", "D) None"],
            "answer": "B"
        },
        {
            "q": "Sun : Day :: Moon : __",
            "options": ["A) Light", "B) Night", "C) Sky", "D) Cloud"],
            "answer": "B"
        },
        {
            "q": "BB, DDD, FFFF, HHHHH, __",
            "options": ["A) JJJJJJ", "B) KKKKKK", "C) LLLLLL", "D) MMMMMM"],
            "answer": "A"
        },
        {
            "q": "Which weighs more?",
            "options": [
                "A) 1kg iron", 
                "B) 1kg cotton", 
                "C) Both same", 
                "D) Can't say"
            ],
            "answer": "C"
        }
    ]

    # -----------------------------
    # LOAD RANDOM QUESTION
    # -----------------------------
    if "current_mcq" not in st.session_state:
        st.session_state.current_mcq = random.choice(iq_mcq)

    qdata = st.session_state.current_mcq

    st.subheader("👉 " + qdata["q"])

    user_choice = st.radio("Choose your answer:", qdata["options"])

    if st.button("Submit Answer"):
        chosen = user_choice[0]  # Extract A/B/C/D

        if chosen == qdata["answer"]:
            st.success("🔥 Correct bestie!! You’re literally Einstein 2.0 😭💙")
        else:
            st.error(f"😭 Wrong babe… the right answer was **{qdata['answer']}** 💗")

    if st.button("New Question"):
        st.session_state.current_mcq = random.choice(iq_mcq)
        st.rerun()