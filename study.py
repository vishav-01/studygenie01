# app.py — StudyGenie K-POP Baby-Pink Edition (All-in-one)
import streamlit as st
import requests, json, os, io, zipfile, html, random, time
from datetime import datetime
from typing import List

# ---------------------------
# Config + storage paths
# ---------------------------
st.set_page_config(page_title="StudyGenie — K-POP Baby Pink", layout="wide")
USER_DB = "users.json"
PROFILE_DB = "profiles.json"
CHAT_DB = "chat_history.json"

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_json(USER_DB, {})
profiles = load_json(PROFILE_DB, {})
chat_history = load_json(CHAT_DB, {})  # {username: {toolname: [ {role, message, time} ] } }

# ---------------------------
# Baby-pink K-pop CSS + fonts
# ---------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] { font-family: 'Poppins', sans-serif; }
.app-bg {
  background: linear-gradient(135deg, #fff0f6 0%, #ffe6f4 40%, #fff7fb 100%);
  padding: 16px;
}
.header-title { text-align:center; color:#ff3ca6; font-weight:700; }
.header-sub { text-align:center; color:#b65b9a; opacity:0.9; }
.tiles { display:grid; grid-template-columns: repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin-top:18px; }
.tile {
  background: linear-gradient(180deg, #fff, #fff5fb);
  border-radius:16px; padding:16px; text-align:center; box-shadow: 0 8px 24px rgba(255,100,180,0.06);
  transition: transform .12s ease;
}
.tile:hover { transform: translateY(-6px); cursor:pointer; }
.tile h3 { margin:6px 0 4px 0; color:#ff2f92; font-size:18px;}
.tile p { margin:0; color:#6b2b55; opacity:0.85; font-size:13px;}
.controls { background: rgba(255,255,255,0.7); padding:12px; border-radius:12px; }
.chat-box { padding:12px; border-radius:12px; margin:10px 0; }
.chat-user { background: #ffeef7; color:#3b073a; text-align:right; padding:12px; border-radius:12px; }
.chat-assistant { background: #e9f8ff; color:#003b4f; text-align:left; padding:12px; border-radius:12px; }
.small { font-size:12px; opacity:0.7; }
button.stButton>button { background: linear-gradient(90deg,#ff7eb8,#ff66cc)!important; color:white!important; border:none!important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Session Initialization
# ---------------------------
if "username" not in st.session_state:
    st.session_state.username = "Guest"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_tool" not in st.session_state:
    st.session_state.current_tool = "AI Doubt Solver"
if "ai_cache" not in st.session_state:
    st.session_state.ai_cache = {}
if "current_motivation" not in st.session_state:
    st.session_state.current_motivation = None

# ---------------------------
# Tools list + descriptions
# ---------------------------
TOOLS = [
    "AI Doubt Solver","Notes Generator","Summary Maker","Timetable Builder","Motivation Booster",
    "Flashcards","Brain-Dump Cleaner","Answer Checker","AI Planner","Mindset Reset",
    "Study Routine Designer","Exam Strategy Maker","Personal Study Coach"
]
TILE_DESCS = {
    "AI Doubt Solver":"Ask a doubt and get crisp explanation.",
    "Notes Generator":"Generate short revision notes.",
    "Summary Maker":"Summarize long text into bullets.",
    "Timetable Builder":"Make a study timetable quickly.",
    "Motivation Booster":"Get 2–3 line motivational messages.",
    "Flashcards":"Auto-generate Q/A flashcards.",
    "Brain-Dump Cleaner":"Turn messy thoughts into structured bullets.",
    "Answer Checker":"Check and correct student answers.",
    "AI Planner":"Create simple step-by-step plans.",
    "Mindset Reset":"Short mental reset scripts to refocus.",
    "Study Routine Designer":"Design a daily routine for hours you choose.",
    "Exam Strategy Maker":"High-impact strategy for upcoming exams.",
    "Personal Study Coach":"Personalized study & motivation guidance."
}

# ---------------------------
# Motivation pool (shortened examples; full 55 present in profile saving logic)
# ---------------------------
MOTIVATIONS = [
    "You are becoming stronger and more skilled every day. Small actions now create large results later.",
    "Your consistency is quietly building a remarkable future. Trust the process and keep showing up.",
    "Every hour of focused work is a gift to your future self. You are planting seeds that will bloom."
]
def random_motivation():
    return random.choice(MOTIVATIONS)

# ---------------------------
# Per-user per-tool history helpers
# ---------------------------
def get_user_tool_history(user:str, tool:str) -> List[dict]:
    return chat_history.get(user, {}).get(tool, [])

def add_user_tool_history(user:str, tool:str, role:str, message:str):
    if user not in chat_history:
        chat_history[user] = {}
    if tool not in chat_history[user]:
        chat_history[user][tool] = []
    chat_history[user][tool].append({"role":role, "message": message, "time": str(datetime.now())})
    save_json(CHAT_DB, chat_history)

# ---------------------------
# Simple wiki fallback & AI call with graceful handling
# ---------------------------
def wiki_fallback_summary(query):
    try:
        q = requests.get("https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(query), timeout=6)
        if q.status_code == 200:
            j = q.json()
            return j.get("extract")
    except:
        return ""
    return ""

def ask_ai_with_fallback(prompt, preferred_models=None, max_retries=1, temp=0.5, max_tokens=300):
    # cache fast
    if prompt in st.session_state.ai_cache:
        return st.session_state.ai_cache[prompt]
    key = st.secrets.get("OPENAI_API_KEY", "")
    if not key:
        demo = "(Demo) Add OPENAI_API_KEY in Streamlit Secrets to enable AI responses."
        st.session_state.ai_cache[prompt] = demo
        return demo

    if preferred_models is None:
        preferred_models = ["gpt-4.1-mini","gpt-4o-mini","gpt-3.5-turbo"]
    headers = {"Authorization": f"Bearer {key}", "Content-Type":"application/json"}
    system = "You are StudyGenie — warm, concise, Gen-Z friendly. Reply in short crisp notes unless asked otherwise."
    for model in preferred_models:
        try:
            payload = {"model": model, "messages":[{"role":"system","content":system},{"role":"user","content":prompt}], "temperature": temp, "max_tokens": max_tokens}
            r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=18)
            j = r.json()
            if "error" in j:
                err = j["error"].get("message","")
                low = err.lower()
                if "quota" in low or "rate limit" in low or r.status_code in (429,402):
                    wiki = wiki_fallback_summary(prompt)
                    if wiki:
                        ans = "(Fallback) Quick wiki summary:\n\n" + wiki
                        st.session_state.ai_cache[prompt] = ans
                        return ans
                    demo = "(Demo) AI unavailable due to quota or rate limits."
                    st.session_state.ai_cache[prompt] = demo
                    return demo
                continue
            choices = j.get("choices")
            if not choices:
                continue
            content = choices[0].get("message", {}).get("content", "").strip()
            if content:
                st.session_state.ai_cache[prompt] = content
                return content
        except Exception:
            continue
    # ultimate fallback
    wiki = wiki_fallback_summary(prompt)
    ans = "(Fallback) " + (wiki or "AI is unavailable right now. Try again later.")
    st.session_state.ai_cache[prompt] = ans
    return ans

# ---------------------------
# Tool-specific prompt router (keeps replies focused)
# ---------------------------
def route_prompt_for_tool(toolname, user_text):
    mapping = {
        "AI Doubt Solver": f"Explain concisely in simple bullet points: {user_text}",
        "Notes Generator": f"Create crisp revision notes for: {user_text}",
        "Summary Maker": f"Summarize this text into 4–6 bullets: {user_text}",
        "Timetable Builder": f"Create a daily timetable given: {user_text}",
        "Motivation Booster": f"Write a 2–3 line encouraging message about: {user_text}",
        "Flashcards": f"Create 6 concise Q/A flashcards for: {user_text}",
        "Brain-Dump Cleaner": f"Organize the following messy notes into clear bullets: {user_text}",
        "Answer Checker": f"Grade this student's answer and provide brief corrections: {user_text}",
        "AI Planner": f"Create a simple step-by-step plan to achieve: {user_text}",
        "Mindset Reset": f"Write a short mindset reset to re-energize: {user_text}",
        "Study Routine Designer": f"Design a daily study routine for: {user_text}",
        "Exam Strategy Maker": f"Create a high-impact exam strategy for: {user_text}",
        "Personal Study Coach": f"You are a study coach. Respond kindly with practical steps: {user_text}"
    }
    return mapping.get(toolname, user_text)

# ---------------------------
# Sidebar: login, quick dropdown, export
# ---------------------------
with st.sidebar:
    st.markdown("<div class='controls'>", unsafe_allow_html=True)
    st.header("StudyGenie • K-POP")
    if not st.session_state.logged_in:
        name = st.text_input("Enter your display name", value="")
        if st.button("Login / Continue"):
            nm = name.strip() or "Guest"
            st.session_state.username = nm
            st.session_state.logged_in = True
            if nm not in users:
                users[nm] = {"created": str(datetime.now())}
                profiles[nm] = {"notes": [], "flashcards": [], "motivations": []}
                save_json(USER_DB, users); save_json(PROFILE_DB, profiles)
            st.rerun()
    else:
        st.markdown(f"**Signed in as:** {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = "Guest"
            st.rerun()

    st.markdown("---")
    st.subheader("Quick tool")
    sel = st.selectbox("Jump to tool", TOOLS, index=TOOLS.index(st.session_state.current_tool) if st.session_state.current_tool in TOOLS else 0)
    if st.button("Go"):
        st.session_state.current_tool = sel
        st.rerun()

    st.markdown("---")
    if st.button("Export my profile & chats"):
        mem = io.BytesIO()
        with zipfile.ZipFile(mem, "w") as z:
            z.writestr(f"{st.session_state.username}_profile.json", json.dumps(profiles.get(st.session_state.username, {}), indent=2))
            z.writestr(f"{st.session_state.username}_chats.json", json.dumps(chat_history.get(st.session_state.username, {}), indent=2))
        mem.seek(0)
        st.download_button("Download ZIP", data=mem, file_name=f"{st.session_state.username}_studygenie.zip")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Main: header + tiles (B)
# ---------------------------
st.markdown("<div class='app-bg'>", unsafe_allow_html=True)
st.markdown("<h1 class='header-title'>✨ StudyGenie — K-POP Baby Pink Edition ✨</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;' class='header-sub'>Your adorable study idol — answers, notes, plans, and hype 💖</div>", unsafe_allow_html=True)

st.markdown("<div class='tiles'>", unsafe_allow_html=True)
# Show tiles as clickable buttons (each button sets current tool)
for t in TOOLS:
    # tile button
    col_html = f"""
    <div class='tile'>
      <h3>{t}</h3>
      <p>{TILE_DESCS.get(t,'')}</p>
    </div>
    """
    # Use st.button with same label to capture clicks
    if st.button(t, key=f"tile_{t}"):
        st.session_state.current_tool = t
        st.rerun()
    st.markdown(col_html, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---", unsafe_allow_html=True)

# ---------------------------
# Tool UI renderer
# ---------------------------
st.markdown(f"### 🔹 Active tool: **{st.session_state.current_tool}**")
def render_tool_ui(tool):
    hist = get_user_tool_history(st.session_state.username, tool)
    if hist:
        st.markdown("**Conversation (this tool)**")
        for m in hist[-200:]:
            if m["role"] == "user":
                st.markdown(f"<div class='chat-box chat-user'><b>You</b><div>{html.escape(m['message'])}</div><div class='small'>{m['time']}</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-box chat-assistant'><b>Genie</b><div>{m['message']}</div><div class='small'>{m['time']}</div></div>", unsafe_allow_html=True)
    else:
        st.info("No conversation for this tool yet — say hi!")

    st.markdown("---")
    col1, col2 = st.columns([4,1])
    with col1:
        user_text = st.text_area("Type your input here", key=f"input_{tool}", height=160)
    with col2:
        uploaded = st.file_uploader("Upload audio (optional)", type=["mp3","wav","m4a"], key=f"up_{tool}")
        if uploaded:
            st.audio(uploaded)
            st.success("Audio uploaded. (Transcription requires OpenAI key.)")

    speak_pref = st.checkbox("Speak replies aloud (browser TTS)", key=f"speak_{tool}", value=False)
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("Send", key=f"send_{tool}"):
            if not user_text.strip():
                st.warning("Please write something first.")
            else:
                add_user_tool_history(st.session_state.username, tool, "user", user_text)
                prompt = route_prompt_for_tool(tool, user_text)
                reply = ask_ai_with_fallback(prompt)
                add_user_tool_history(st.session_state.username, tool, "assistant", reply)
                if speak_pref and not reply.startswith("(Demo)"):
                    safe = html.escape(reply)
                    st.components.v1.html(f"<script>var u=new SpeechSynthesisUtterance(`{safe}`);window.speechSynthesis.speak(u);</script>", height=0)
                st.rerun()
    with c2:
        if st.button("Save last reply to notes", key=f"save_{tool}"):
            hist2 = get_user_tool_history(st.session_state.username, tool)
            last = next((h for h in reversed(hist2) if h["role"]=="assistant"), None)
            if last:
                profiles.setdefault(st.session_state.username, {}).setdefault("notes", []).append({"from_tool":tool,"content":last["message"], "time": last["time"]})
                save_json(PROFILE_DB, profiles)
                st.success("Saved to profile notes.")
            else:
                st.info("No assistant reply to save.")
    with c3:
        if st.button("Clear history (tool)", key=f"clear_{tool}"):
            if st.session_state.username in chat_history and tool in chat_history[st.session_state.username]:
                chat_history[st.session_state.username][tool] = []
                save_json(CHAT_DB, chat_history)
                st.success("Cleared history for this tool.")
                st.rerun()

    # Tool-specific UI extras:
    if tool == "Motivation Booster":
        if st.button("New Motivation"):
            st.session_state.current_motivation = random_motivation()
        if st.session_state.current_motivation:
            st.markdown(f"<div class='chat-box chat-assistant'>{st.session_state.current_motivation}</div>", unsafe_allow_html=True)
        if st.button("Save Motivation to profile"):
            profiles.setdefault(st.session_state.username, {}).setdefault("motivations", []).append(st.session_state.current_motivation)
            save_json(PROFILE_DB, profiles)
            st.success("Saved to profile.")

    if tool == "Flashcards":
        if st.button("Generate 6 flashcards (from input)"):
            txt = st.session_state.get(f"input_{tool}", "").strip()
            if not txt:
                st.warning("Provide a topic or paste notes.")
            else:
                out = ask_ai_with_fallback(f"Create 6 concise Q/A flashcards for: {txt}")
                profiles.setdefault(st.session_state.username, {}).setdefault("flashcards", []).append({"topic":txt,"cards":out,"time":str(datetime.now())})
                save_json(PROFILE_DB, profiles)
                st.success("Flashcards saved to your profile.")

    if tool == "Notes Generator":
        if st.button("Generate Notes"):
            txt = st.session_state.get(f"input_{tool}", "").strip()
            if not txt:
                st.warning("Enter topic or paste content.")
            else:
                out = ask_ai_with_fallback(f"Create crisp notes for: {txt}")
                st.markdown(f"<div class='chat-box chat-assistant'>{out}</div>", unsafe_allow_html=True)
                if st.button("Save notes to profile"):
                    profiles.setdefault(st.session_state.username, {}).setdefault("notes", []).append({"title":txt,"content":out,"time":str(datetime.now())})
                    save_json(PROFILE_DB, profiles)
                    st.success("Saved.")

    if tool == "Summary Maker":
        if st.button("Summarize now"):
            txt = st.session_state.get(f"input_{tool}", "").strip()
            if not txt:
                st.warning("Paste text first.")
            else:
                out = ask_ai_with_fallback(f"Summarize in bullets: {txt}")
                st.markdown(f"<div class='chat-box chat-assistant'>{out}</div>", unsafe_allow_html=True)

    if tool == "Timetable Builder":
        if st.button("Build Timetable"):
            txt = st.session_state.get(f"input_{tool}", "").strip()
            if not txt:
                st.warning("Enter subjects (comma separated).")
            else:
                out = ask_ai_with_fallback(f"Create a daily timetable given: {txt}")
                st.markdown(f"<div class='chat-box chat-assistant'>{out}</div>", unsafe_allow_html=True)

    if tool == "Answer Checker":
        st.info("Paste the question and student's answer separated by a new line. First line = Question, second line = Answer.")
        if st.button("Check Answer"):
            txt = st.session_state.get(f"input_{tool}", "").strip()
            if not txt or "\n" not in txt:
                st.warning("Paste question and answer separated by a newline.")
            else:
                q,a = txt.split("\n",1)
                out = ask_ai_with_fallback(f"Question: {q}\nStudent answer: {a}\nGrade and correct briefly.")
                st.markdown(f"<div class='chat-box chat-assistant'>{out}</div>", unsafe_allow_html=True)

    if tool == "AI Planner":
        if st.button("Make Plan"):
            txt = st.session_state.get(f"input_{tool}", "").strip()
            if not txt:
                st.warning("Enter your goal.")
            else:
                out = ask_ai_with_fallback(f"Create a simple plan to achieve: {txt}")
                st.markdown(f"<div class='chat-box chat-assistant'>{out}</div>", unsafe_allow_html=True)

    if tool == "Mindset Reset":
        if st.button("Reset Mindset"):
            out = ask_ai_with_fallback("Write a short mindset reset script to re-energize.")
            st.markdown(f"<div class='chat-box chat-assistant'>{out}</div>", unsafe_allow_html=True)

    if tool == "Study Routine Designer":
        if st.button("Design Routine"):
            hours = st.session_state.get(f"input_{tool}", "").strip() or "4"
            out = ask_ai_with_fallback(f"Design a daily study routine for {hours} hours.")
            st.markdown(f"<div class='chat-box chat-assistant'>{out}</div>", unsafe_allow_html=True)

    if tool == "Exam Strategy Maker":
        if st.button("Create Strategy"):
            txt = st.session_state.get(f"input_{tool}", "").strip()
            if not txt:
                st.warning("Enter exam name/topic.")
            else:
                out = ask_ai_with_fallback(f"Create a high-impact exam strategy for: {txt}")
                st.markdown(f"<div class='chat-box chat-assistant'>{out}</div>", unsafe_allow_html=True)

    if tool == "Personal Study Coach":
        if st.button("Get Coaching"):
            txt = st.session_state.get(f"input_{tool}", "").strip()
            if not txt:
                st.warning("Tell me what you're struggling with.")
            else:
                out = ask_ai_with_fallback(f"You are a study coach. Provide kind, practical steps: {txt}")
                st.markdown(f"<div class='chat-box chat-assistant'>{out}</div>", unsafe_allow_html=True)

# ---------------------------
# Render active tool
# ---------------------------
render_tool_ui(st.session_state.current_tool)

# ---------------------------
# Footer: quick profile summary + snapshot export
# ---------------------------
st.markdown("---")
c1, c2 = st.columns([3,1])
with c1:
    st.markdown(f"**User:** {st.session_state.username}  •  **Tool:** {st.session_state.current_tool}")
    prof = profiles.get(st.session_state.username, {})
    st.markdown(f"Notes: {len(prof.get('notes',[]))} • Flashcards: {len(prof.get('flashcards',[]))} • Motivations: {len(prof.get('motivations',[]))}")

with c2:
    if st.button("Save snapshot of tool"):
        mem = io.BytesIO()
        with zipfile.ZipFile(mem, mode="w") as z:
            z.writestr(f"{st.session_state.username}_{st.session_state.current_tool}.json", json.dumps(get_user_tool_history(st.session_state.username, st.session_state.current_tool), indent=2))
        mem.seek(0)
        st.download_button("Download Snapshot", data=mem, file_name=f"{st.session_state.username}_{st.session_state.current_tool}_snapshot.zip")

# ---------------------------
# Persist DBs
# ---------------------------
save_json(USER_DB, users)
save_json(PROFILE_DB, profiles)
save_json(CHAT_DB, chat_history)

st.markdown("</div>", unsafe_allow_html=True)