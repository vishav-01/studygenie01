# ---------------------------------------------------
# NEW: IQ TEST GAME (Fun + Smart)
# ---------------------------------------------------

elif tool == "IQ Test Game":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🧠 IQ Test Game")

    # Questions (You can add more)
    questions = [
        {
            "q": "If 5 cats catch 5 mice in 5 minutes, how long for 1 cat to catch 1 mouse?",
            "options": ["5 minutes", "1 minute", "25 minutes", "10 minutes"],
            "answer": "5 minutes"
        },
        {
            "q": "What comes next in the pattern? 2, 4, 8, 16, __",
            "options": ["18", "20", "24", "32"],
            "answer": "32"
        },
        {
            "q": "Which one is different?",
            "options": ["Apple", "Banana", "Car", "Orange"],
            "answer": "Car"
        },
        {
            "q": "A cube has how many faces?",
            "options": ["4", "6", "8", "10"],
            "answer": "6"
        },
        {
            "q": "Find the odd number: 3, 9, 27, 81, 45",
            "options": ["3", "9", "27", "45"],
            "answer": "45"
        }
    ]

    # Save game state
    if "iq_q_index" not in st.session_state:
        st.session_state.iq_q_index = 0
        st.session_state.iq_score = 0
        st.session_state.iq_finished = False

    if st.session_state.iq_q_index < len(questions):
        qdata = questions[st.session_state.iq_q_index]

        st.write(f"**Q{st.session_state.iq_q_index + 1}: {qdata['q']}**")

        user_ans = st.radio("Choose your answer:", qdata["options"])

        if st.button("Submit"):
            if user_ans == qdata["answer"]:
                st.success("Correct bestie 💖😎")
                st.session_state.iq_score += 1
            else:
                st.error(f"Wrong babe 😭 The right answer is **{qdata['answer']}**")

            st.session_state.iq_q_index += 1
            st.rerun()

    else:
        st.session_state.iq_finished = True

    # Final Score
    if st.session_state.iq_finished:
        st.subheader("🎉 Test Complete!")

        st.write(f"✨ **Your IQ Game Score:** {st.session_state.iq_score} / {len(questions)}")

        if st.session_state.iq_score == len(questions):
            st.success("BRAIN OF THE YEAR AWARD GOES TO YOU 🧠🏆😍")
        elif st.session_state.iq_score >= len(questions) - 2:
            st.info("Smart + cute = you 😭💗")
        else:
            st.warning("Bestie… we need to study together tonight 😭😂💞")

        if st.button("Play Again"):
            st.session_state.iq_q_index = 0
            st.session_state.iq_score = 0
            st.session_state.iq_finished = False
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)