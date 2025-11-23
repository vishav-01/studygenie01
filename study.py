

# app.py — StudyGenie Ultra (All-in-one Streamlit)
# Paste this entire file into your Streamlit app folder as app.py

import streamlit as st
import requests, json, os, time, io, zipfile, html, base64, random
from datetime import datetime

# -----------------------------
# CONFIG + FILE PATHS
# -----------------------------
st.set_page_config(page_title="StudyGenie Ultra", layout="wide")
USER_DB = "users.json"
PROFILE_DB = "profiles.json"
CHAT_DB = "chat_history.json"

# -----------------------------
# HELPERS: JSON load/save
# -----------------------------
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
chat_history = load_json(CHAT_DB, {})  # structure: {username: {tool_name: [ {role,msg,time} ] } }

# -----------------------------
# THEMES
# -----------------------------
THEMES = {
    "Pastel Sky": {"bg": "linear-gradient(170deg,#dff3ff,#f5dfff,#ffe6f2)","#card":"#ffffffaa","accent":"#A7C7E7","text":"#1A1A1A"},
    "Baby Pink": {"bg": "linear-gradient(170deg,#ffeaf4,#fff0f6,#ffdff0)","#card":"#ffffffaa","accent":"#FFB7D5","text":"#1A1A1A"},
    "Lavender Dream": {"bg":"linear-gradient(170deg,#f1e7ff,#efe0ff,#fff0fb)","#card":"#ffffffaa","accent":"#D6B8FF","text":"#1A1A1A"},
    "K-Idol Dark": {"bg":"linear-gradient(170deg,#0d0d0d,#1a1a1a,#111111)","#card":"#1a1a1aaa","accent":"#7A5FFF","text":"#ffffff"},
}

# -----------------------------
# AESTHETIC CSS
# -----------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] { font-family: 'Poppins', sans-serif; }
.header { text-align:center; }
.section { background: rgba(255,255,255,0.45); padding:18px; border-radius:14px; margin:12px 0; backdrop-filter: blur(6px); }
.genie { background: rgba(255,255,255,0.8); padding:12px; border-radius:12px; margin:10px 0; }
.user { background: rgba(210,235,255,0.95); padding:10px; border-radius:12px; margin:8px 0; text-align:right; }
.small { font-size:13px; opacity:0.7; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# SESSION STATE init
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = "Guest"
if "current_tool" not in st.session_state:
    st.session_state.current_tool = "AI Doubt Solver"
if "ui_theme" not in st.session_state:
    st.session_state.ui_theme = "Pastel Sky"
if "chat_session" not in st.session_state:
    # chat_session stores messages for current tool in-memory while user is active
    st.session_state.chat_session = []

# -----------------------------
# MOTIVATIONS (55 multi-line)
# -----------------------------
MOTIVATIONS = [
"""You are becoming stronger and more skilled every day. Small actions now create large results later.""",
"""Your consistency is quietly building a remarkable future. Trust the process and keep showing up.""",
"""Every hour of focused work is a gift to your future self. You are planting seeds that will bloom.""",
"""You deserve calm confidence and peaceful success. Your effort is shaping a life you will be proud of.""",
"""You are learning and improving even when progress feels slow. Growth is happening, and it is real.""",
"""Your discipline today becomes your freedom tomorrow. Keep building the habits that serve you.""",
"""You are not defined by one moment or one result. Your journey is long and full of beautiful beginnings.""",
"""Every small win adds up to a meaningful life. Celebrate the tiny victories and keep moving forward.""",
"""You are becoming someone who solves problems with grace. Your mind is getting sharper and more confident.""",
"""The future you are creating is soft, abundant, and steady. Continue to take kind, purposeful steps.""",
"""You are allowed to rest and continue at your own pace. Balance is a part of long term success.""",
"""Each chapter you complete teaches you something new. Your knowledge is stacking in the best possible way.""",
"""You are developing focus and clarity each week. Those qualities will open doors you have not seen yet.""",
"""Your persistence will outlast every short lived challenge. Keep steady and trust your path.""",
"""You are crafting a life that feels intentional and beautiful. Your effort is not wasted.""",
"""You are becoming someone who inspires even by simple actions. Your small routines make a big difference.""",
"""You are learning to manage your energy and protect your time. That skill is more valuable than you think.""",
"""Your dedication is shaping opportunities that will feel effortless later. Keep investing in yourself.""",
"""You are learning the art of consistent improvement. That is the real secret of lasting success.""",
"""Your future self is thankful for the choices you are making today. Continue to invest in your growth.""",
"""You are stronger than the doubts that appear in your mind. Your actions prove your capability.""",
"""Every page you study adds depth to your thinking. Your knowledge will become your advantage.""",
"""You are building routines that become your identity. Small habits make big outcomes over time.""",
"""You are allowed to be imperfect and still progress. Perfection is unnecessary, progress is essential.""",
"""Your vision is clearer because you keep working at it. Clarity grows from steady attention.""",
"""You are learning to trust your own rhythm. There is power in moving at your natural pace.""",
"""You are becoming resilient in a kind and steady way. Challenges are shaping constructive strength.""",
"""Your curiosity is a compass guiding you to better knowledge. Keep asking, exploring, and practicing.""",
"""You are designing a future that aligns with your values. That alignment makes success sweeter and calmer.""",
"""You are learning how to turn effort into results. Skill is built by repetition and thoughtful practice.""",
"""You are allowed to change direction and still win. Flexibility is part of a smart strategy.""",
"""Your consistency is like a quiet engine moving everything forward. Trust it even when you cannot see immediate reward.""",
"""You are slowly constructing a life you admiration. Small choices made daily produce meaningful change.""",
"""You are becoming someone who completes their promises to themselves. That trust is the foundation of growth.""",
"""You are building a life with intention and care. That life will feel stable, joyful, and meaningful.""",
"""You are learning how to stay focused under pressure. That ability will serve you for years to come.""",
"""You are creating a future that honors your effort. Every hour counts and every effort matters.""",
"""You are moving toward opportunities that match your work ethic. The world rewards steady, persistent effort.""",
"""You are allowed to be patient while you build something great. Patience compounds with consistent practice.""",
"""You are becoming more capable than you imagine. Keep practicing the fundamentals and trust the progress.""",
"""You are developing patterns that support your ambitions. Habit is the architecture of success.""",
"""You are allowed to rest without guilt and return refreshed. Rest is part of sustainable growth.""",
"""You are learning to set boundaries that protect your focus. That discipline is an act of self love.""",
"""You are steadily improving in ways that become obvious over time. Keep going; the change is real.""",
"""You are a builder of your future life, one small choice at a time. That reality is powerful and true.""",
"""You are cultivating calm confidence every day. Confidence grows from repeated, successful effort.""",
"""You are turning your goals into daily practices. That is how dreams become reliable realities.""",
"""You are learning to make consistent progress, not dramatic leaps. Small progress is still powerful progress.""",
"""You are growing a skill set that will support your independence. Your work is building long term freedom.""",
"""You are prepared for good things by how you spend your time now. Your future will reflect your current choices.""",
"""You are becoming disciplined and kind to yourself. Both qualities together create meaningful success.""",
"""You are learning the graceful art of finishing tasks. Completion is a skill that brings confidence and momentum.""",
"""You are building momentum through repeated small wins. Momentum makes difficult days easier.""",
"""You are capable of more than you currently believe. Keep challenging yourself with kind persistence.""",
]

def random_motivation():
    return random.choice(MOTIVATIONS)

# -----------------------------
# UTILS: per-user & per-tool history
# -----------------------------
def get_user_tool_history(username, tool):
    user_hist = chat_history.get(username, {})
    return user_hist.get(tool, [])

def add_user_tool_history(username, tool, role, message):
    if username not in chat_history:
        chat_history[username] = {}
    if tool not in chat_history[username]:
        chat_history[username][tool] = []
    chat_history[username][tool].append({"role": role, "message": message, "time": str(datetime.now())})
    save_json(CHAT_DB, chat_history)

# -----------------------------
# ROBUST OPENAI CALL (fallbacks + retries)
# -----------------------------
def ask_ai_robust(prompt, preferred_models=None, max_retries=2, temperature=0.45, max_tokens=350):
    key = st.secrets.get("OPENAI_API_KEY", "")
    if not key:
        return "❌ Please add OPENAI_API_KEY to Streamlit Secrets."

    if preferred_models is None:
        preferred_models = ["gpt-5-mini", "gpt-4o-mini", "gpt-4.1-mini", "gpt-3.5-turbo"]

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    system_prompt = ("You are StudyGenie — warm, encouraging, concise and Gen-Z friendly. "
                     "Always reply in short crisp notes (2–4 bullets) unless user asks for long.")
    payload_base = {"messages": [{"role":"system","content":system_prompt}, {"role":"user","content":prompt}],
                    "temperature": temperature, "max_tokens": max_tokens}

    for model in preferred_models:
        attempt = 0
        while attempt <= max_retries:
            attempt += 1
            payload = dict(payload_base)
            payload["model"] = model
            try:
                resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            except Exception as e:
                if attempt > max_retries:
                    return f"❌ Network error: {e}"
                time.sleep(0.8 * attempt)
                continue

            try:
                rj = resp.json()
            except Exception as e:
                if attempt > max_retries:
                    return f"❌ Invalid JSON: {e}"
                time.sleep(0.5)
                continue

            if "error" in rj:
                err = rj["error"].get("message", str(rj["error"]))
                # retry on server/rate-limit
                if attempt <= max_retries and (resp.status_code >= 500 or "rate limit" in err.lower()):
                    time.sleep(1.0 * attempt)
                    continue
                return f"❌ AI error: {err}"

            choices = rj.get("choices")
            if not choices:
                if attempt <= max_retries:
                    time.sleep(0.5)
                    continue
                break
            msg = choices[0].get("message") or {}
            content = msg.get("content") or msg.get("text") or ""
            if not content:
                if attempt <= max_retries:
                    time.sleep(0.4)
                    continue
                break
            return content.strip()

    return "❌ AI did not return a valid response after multiple attempts. Try again later."

# -----------------------------
# BROWSER TTS (client-side) — cute tone
# -----------------------------
def speak_in_browser(text, pitch=1.05, rate=0.95, volume=0.98):
    safe = html.escape(text)
    js = f"""
    <script>
    const u = new SpeechSynthesisUtterance(`{safe}`);
    u.pitch = {pitch}; u.rate = {rate}; u.volume = {volume};
    const voices = window.speechSynthesis.getVoices();
    let found = voices.find(v => /female|korean|noto/i.test(v.name)) || voices.find(v => v.lang.startsWith('en')) || voices[0];
    if(found) u.voice = found;
    window.speechSynthesis.speak(u);
    </script>
    """
    st.components.v1.html(js, height=0)

# -----------------------------
# VOICE TRANSCRIPTION via upload (Whisper endpoints if available)
# -----------------------------
def transcribe_audio_file(uploaded):
    key = st.secrets.get("OPENAI_API_KEY", "")
    if not key:
        return ""
    try:
        files = {"file": (uploaded.name, uploaded.getvalue())}
        data = {"model": "gpt-4o-transcribe"}  # best effort
        headers = {"Authorization": f"Bearer {key}"}
        resp = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data, timeout=90)
        rj = resp.json()
        return rj.get("text", "")
    except Exception:
        return ""

# -----------------------------
# THE UI: Header + Sidebar login + theme
# -----------------------------
st.markdown("<div class='header'><h1>✨ StudyGenie Ultra — Your AI Study Bestie 💕</h1></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#5f569b;'>Ask questions, take notes, build timetables, and glow up ✨</p>", unsafe_allow_html=True)

# Sidebar: login / profile / theme / export
st.sidebar.title("StudyGenie Menu")
if not st.session_state.logged_in:
    st.sidebar.subheader("Login")
    name = st.sidebar.text_input("Enter a display name", value="")
    if st.sidebar.button("Login / Continue"):
        if name.strip():
            if name not in users:
                users[name] = {"created": str(datetime.now())}
                profiles[name] = {"theme":"Pastel Sky", "avatar_color":"#FFB7D5"}
                save_json(USER_DB, users); save_json(PROFILE_DB, profiles)
            st.session_state.logged_in = True
            st.session_state.username = name
            st.success(f"Welcome, {name}!")
else:
    st.sidebar.markdown(f"**Signed in as:** {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = "Guest"
        st.session_state.chat_session = []
        st.experimental_rerun()

# Theme picker
theme_choice = st.sidebar.selectbox("Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.ui_theme))
st.session_state.ui_theme = theme_choice

# small profile quick edit
st.sidebar.subheader("Profile")
if st.session_state.logged_in:
    prof = profiles.get(st.session_state.username, {})
    name_val = st.sidebar.text_input("Display name", value=st.session_state.username)
    avatar = st.sidebar.color_picker("Avatar color", value=prof.get("avatar_color","#FFB7D5"))
    if st.sidebar.button("Save Profile"):
        profiles[st.session_state.username] = prof
        profiles[st.session_state.username]["avatar_color"] = avatar
        profiles[st.session_state.username]["display_name"] = name_val
        save_json(PROFILE_DB, profiles)
        st.success("Profile saved!")

# Export / download
st.sidebar.markdown("---")
if st.sidebar.button("Export My Data (ZIP)"):
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{st.session_state.username}_profile.json", json.dumps(profiles.get(st.session_state.username, {}), indent=2))
        z.writestr(f"{st.session_state.username}_chats.json", json.dumps(chat_history.get(st.session_state.username, {}), indent=2))
    mem.seek(0)
    st.sidebar.download_button("Download ZIP", data=mem, file_name=f"{st.session_state.username}_studygenie.zip")

# -----------------------------
# TOOL SELECTION
# -----------------------------
tool = st.sidebar.radio("Choose tool", [
    "AI Doubt Solver","Notes Generator","Summary Maker","Timetable Builder","Motivation Booster",
    "Flashcards","Brain-Dump Cleaner","Answer Checker","AI Planner","Mindset Reset",
    "Study Routine Designer","Exam Strategy Maker","Personal Study Coach"
])
st.session_state.current_tool = tool

# Sidebar: show per-tool recent history (last 10 messages)
st.sidebar.markdown("### Recent (this tool)")
recent = get_user_tool_history(st.session_state.username, tool)[-12:]
if not recent:
    st.sidebar.write("No recent chat for this tool.")
else:
    for entry in recent[-12:]:
        who = entry["role"]
        msg = entry["message"]
        tm = entry["time"].split(" ")[0]
        st.sidebar.markdown(f"<div style='padding:6px;border-radius:8px;background:rgba(255,255,255,0.6);'><b class='small'>{who}</b>: {html.escape(msg)[:60]}<br><small class='small'>{tm}</small></div>", unsafe_allow_html=True)

# -----------------------------
# TOOL: helper to render chat UI for this tool
# -----------------------------
def tool_chat_ui():
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader(f"🔹 {tool}")
    # Show previous messages for this tool (full)
    hist = get_user_tool_history(st.session_state.username, tool)
    if hist:
        for m in hist[-200:]:
            if m["role"] == "user":
                st.markdown(f"<div class='user'>{html.escape(m['message'])}<br><small class='small'>{m['time']}</small></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='genie'><b>Genie</b><br>{m['message']}<br><small class='small'>{m['time']}</small></div>", unsafe_allow_html=True)
    else:
        st.info("No messages yet. Ask anything related to this tool!")

    st.markdown("---")
    # input + voice upload
    col1, col2 = st.columns([4,1])
    with col1:
        user_text = st.text_area("Type your message", key=f"input_{tool}", height=120)
    with col2:
        uploaded = st.file_uploader("Upload audio (mp3/wav)", type=["mp3","wav","m4a"], key=f"up_{tool}")
        if uploaded:
            st.audio(uploaded)
            trans = transcribe_audio_file(uploaded)
            if trans:
                st.success("Transcription: " + trans)
                # append transcription to input
                user_text = (st.session_state.get(f"input_{tool}", "") + " " + trans).strip()
                st.session_state[f"input_{tool}"] = user_text

    # send / clear / speak toggle
    speak_pref = st.checkbox("Speak replies aloud", key=f"speak_{tool}", value=False)
    colA, colB, colC = st.columns([1,1,1])
    with colA:
        if st.button("Send", key=f"send_{tool}"):
            if not user_text.strip():
                st.warning("Write something first!")
            else:
                # save user msg and call AI (or local generator)
                add_user_tool_history(st.session_state.username, tool, "user", user_text)
                # route tool-specific prompts for concise outputs
                prompt = route_prompt_for_tool(tool, user_text)
                reply = ask_ai_robust(prompt)
                # save reply
                add_user_tool_history(st.session_state.username, tool, "assistant", reply)
                if speak_pref and not reply.startswith("❌"):
                    speak_in_browser(reply)
                st.experimental_rerun()
    with colB:
        if st.button("Clear history (tool)", key=f"clear_{tool}"):
            if st.session_state.username in chat_history and tool in chat_history[st.session_state.username]:
                chat_history[st.session_state.username][tool] = []
                save_json(CHAT_DB, chat_history)
                st.success("Cleared history for this tool.")
                st.experimental_rerun()
    with colC:
        if st.button("Save to notes", key=f"save_note_{tool}"):
            # quick save last assistant reply to user profile notes
            hist = get_user_tool_history(st.session_state.username, tool)
            last_assist = next((h for h in reversed(hist) if h["role"]=="assistant"), None)
            if last_assist:
                profiles.setdefault(st.session_state.username, {}).setdefault("notes", []).append({"from_tool":tool, "content": last_assist["message"], "time": str(datetime.now())})
                save_json(PROFILE_DB, profiles)
                st.success("Saved last reply to your notes.")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Helper: route prompts specific to tool
# -----------------------------
def route_prompt_for_tool(toolname, user_text):
    # create short, tool-specific prompts so AI answer is concise and relevant
    mapping = {
        "AI Doubt Solver": f"Explain concisely and in simple bullet points: {user_text}",
        "Notes Generator": f"Create short crisp revision notes for: {user_text}",
        "Summary Maker": f"Summarize in 3-6 bullets: {user_text}",
        "Timetable Builder": f"Create a daily timetable based on: {user_text}",
        "Motivation Booster": f"Give a 2-3 line motivational message related to: {user_text}",
        "Flashcards": f"Make 6 Q/A flashcards for: {user_text}",
        "Brain-Dump Cleaner": f"Organize these messy notes into clean bullet points: {user_text}",
        "Answer Checker": f"Compare student's answer and give corrections: {user_text}",
        "AI Planner": f"Create a simple plan to achieve: {user_text}",
        "Mindset Reset": f"Write an encouraging mindset reset: {user_text}",
        "Study Routine Designer": f"Design a study routine for: {user_text}",
        "Exam Strategy Maker": f"Create a high-impact exam strategy for: {user_text}",
        "Personal Study Coach": f"You are a study coach. Respond kindly and give practical steps: {user_text}"
    }
    return mapping.get(toolname, user_text)

# -----------------------------
# Tools UI routing + extra UIs (notes, flashcards, summary etc.)
# -----------------------------
def tools_main_router():
    if tool == "Motivation Booster":
        st.markdown("<div class='section'><h3>🔥 Motivation Booster</h3>", unsafe_allow_html=True)
        if st.button("New Motivation"):
            st.session_state.current_motivation = random_motivation()
        if "current_motivation" not in st.session_state:
            st.session_state.current_motivation = random_motivation()
        st.markdown(f"<div class='genie'>{st.session_state.current_motivation}</div>", unsafe_allow_html=True)
        if st.button("Save Motivation to profile"):
            profiles.setdefault(st.session_state.username, {}).setdefault("motivations", []).append(st.session_state.current_motivation)
            save_json(PROFILE_DB, profiles)
            st.success("Saved to your profile.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # for all other tools: show chat UI
        tool_chat_ui()
        # additional small sections for Notes Generator & Summary Maker
        if tool == "Notes Generator":
            st.markdown("### Saved Notes")
            saved = profiles.get(st.session_state.username, {}).get("notes", [])
            for n in reversed(saved[-8:]):
                st.markdown(f"<div class='genie'><b>{n.get('title','Note')}</b><br>{n.get('content')[:500]}<br><small class='small'>{n.get('time')}</small></div>", unsafe_allow_html=True)
        if tool == "Summary Maker":
            st.markdown("### Saved Summaries")
            saved = profiles.get(st.session_state.username, {}).get("summaries", [])
            for s in reversed(saved[-8:]):
                st.markdown(f"<div class='genie'><b>{s.get('title')}</b><br>{s.get('content')[:500]}</div>", unsafe_allow_html=True)

# -----------------------------
# MAIN: show router
# -----------------------------
tools_main_router()

# -----------------------------
# FOOTER: quick profile display & save chat snapshot
# -----------------------------
st.markdown("<hr>")
col1, col2 = st.columns([2,1])
with col1:
    st.markdown(f"**User:** {st.session_state.username} • **Tool:** {tool}")
    prof = profiles.get(st.session_state.username, {})
    st.markdown(f"**Theme:** {st.session_state.ui_theme} • **Notes:** {len(prof.get('notes',[]))} • **Flashcards:** {len(prof.get('flashcards',[])) if prof else 0}")
with col2:
    if st.button("Save snapshot of this tool (export)"):
        mem = io.BytesIO()
        with zipfile.ZipFile(mem, mode="w") as z:
            z.writestr(f"{st.session_state.username}_{tool}_snapshot.json", json.dumps(get_user_tool_history(st.session_state.username, tool), indent=2))
        mem.seek(0)
        st.download_button("Download Snapshot", data=mem, file_name=f"{st.session_state.username}_{tool}_snapshot.zip")

# -----------------------------
# Persist small autosaves on exit / periodically
# -----------------------------
save_json(USER_DB, users)
save_json(PROFILE_DB, profiles)
save_json(CHAT_DB, chat_history)