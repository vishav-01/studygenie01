# app.py — StudyGenie Ultra (Tiles + Dropdown, all tools, per-tool history)
import streamlit as st
import requests, json, os, time, io, zipfile, html, random
from datetime import datetime

# -------------------------
# Config + files
# -------------------------
st.set_page_config(page_title="StudyGenie Ultra", layout="wide", initial_sidebar_state="expanded")
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
chat_history = load_json(CHAT_DB, {})  # {username: {tool: [ {role, message, time} ] } }

# -------------------------
# Basic UI CSS (pastel tiles + card)
# -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] { font-family: 'Poppins', sans-serif; }
.page { background: linear-gradient(135deg,#dff3ff 0%,#f3e8ff 50%,#ffe6f2 100%); padding:20px; }
.tile {
  background: rgba(255,255,255,0.7);
  padding:18px; border-radius:16px; box-shadow: 0 6px 18px rgba(0,0,0,0.06);
  text-align:center; transition: transform .15s ease; cursor:pointer;
}
.tile:hover { transform: translateY(-6px) scale(1.01); }
.tile h3 { margin:6px 0 4px 0; font-weight:700; }
.tile p { margin:0; opacity:0.85; }
.tools-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:14px; }
.chat-box { padding:12px; border-radius:12px; margin:8px 0; background: rgba(255,255,255,0.9); }
.user { background: rgba(255,230,240,0.95); padding:10px; border-radius:10px; text-align:right; }
.assistant { background: rgba(225,245,255,0.95); padding:10px; border-radius:10px; text-align:left; }
.small { font-size:12px; opacity:0.7; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Session init
# -------------------------
if "username" not in st.session_state:
    st.session_state.username = "Guest"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_tool" not in st.session_state:
    st.session_state.current_tool = "AI Doubt Solver"
if "ui_theme" not in st.session_state:
    st.session_state.ui_theme = "Pastel"
if "ai_cache" not in st.session_state:
    st.session_state.ai_cache = {}

# -------------------------
# Tools list
# -------------------------
TOOLS = [
    "AI Doubt Solver","Notes Generator","Summary Maker","Timetable Builder","Motivation Booster",
    "Flashcards","Brain-Dump Cleaner","Answer Checker","AI Planner","Mindset Reset",
    "Study Routine Designer","Exam Strategy Maker","Personal Study Coach"
]

# -------------------------
# Utilities: per-user per-tool history
# -------------------------
def get_user_tool_history(user, tool):
    return chat_history.get(user, {}).get(tool, [])

def add_user_tool_history(user, tool, role, message):
    if user not in chat_history:
        chat_history[user] = {}
    if tool not in chat_history[user]:
        chat_history[user][tool] = []
    chat_history[user][tool].append({"role": role, "message": message, "time": str(datetime.now())})
    save_json(CHAT_DB, chat_history)

# -------------------------
# Simple robust AI call with graceful fallback
# -------------------------
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
    key = st.secrets.get("OPENAI_API_KEY", "")
    # check cache
    if prompt in st.session_state.ai_cache:
        return st.session_state.ai_cache[prompt]
    if not key:
        demo = "(Demo) No API key. Add OPENAI_API_KEY to Secrets to enable AI."
        st.session_state.ai_cache[prompt] = demo
        return demo

    if preferred_models is None:
        preferred_models = ["gpt-4.1-mini","gpt-4o-mini","gpt-3.5-turbo"]
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
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
    # if all fails
    wiki = wiki_fallback_summary(prompt)
    ans = "(Fallback) " + (wiki or "AI is unavailable right now. Try again later.")
    st.session_state.ai_cache[prompt] = ans
    return ans

# -------------------------
# Helper: tool-specific prompt routing (keeps answers crisp)
# -------------------------
def route_prompt_for_tool(toolname, user_text):
    mapping = {
        "AI Doubt Solver": f"Explain concisely in bullet points: {user_text}",
        "Notes Generator": f"Create crisp revision notes for: {user_text}",
        "Summary Maker": f"Summarize in 3-6 bullets: {user_text}",
        "Timetable Builder": f"Create a daily timetable given: {user_text}",
        "Motivation Booster": f"Write a 2-3 line encouraging motivational message about: {user_text}",
        "Flashcards": f"Create 6 short Q/A flashcards for: {user_text}",
        "Brain-Dump Cleaner": f"Organize the following messy notes into clean bullets: {user_text}",
        "Answer Checker": f"Grade and correct this student's answer: {user_text}",
        "AI Planner": f"Make a simple plan to achieve: {user_text}",
        "Mindset Reset": f"Write a short mindset reset to re-energize: {user_text}",
        "Study Routine Designer": f"Design a realistic daily study routine for: {user_text}",
        "Exam Strategy Maker": f"Create a high-impact exam strategy for: {user_text}",
        "Personal Study Coach": f"You are a study coach. Respond kindly with practical steps: {user_text}"
    }
    return mapping.get(toolname, user_text)

# -------------------------
# UI: sidebar login & dropdown
# -------------------------
with st.sidebar:
    st.title("StudyGenie ✨")
    st.markdown("**Sign in** (name only — local)")
    if not st.session_state.logged_in:
        name = st.text_input("Enter name", value="")
        if st.button("Login / Continue"):
            nm = name.strip() or "Guest"
            st.session_state.username = nm
            st.session_state.logged_in = True
            if nm not in users:
                users[nm] = {"created": str(datetime.now())}
                profiles[nm] = {"notes": [], "flashcards": [], "motivations": []}
                save_json(USER_DB, users); save_json(PROFILE_DB, profiles)
            st.experimental_rerun()
    else:
        st.markdown(f"**Signed in as:** {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = "Guest"
            st.experimental_rerun()

    st.markdown("---")
    # Dropdown quick tool
    st.subheader("Quick tool")
    sel_tool = st.selectbox("Choose a tool", TOOLS, index=TOOLS.index(st.session_state.current_tool) if st.session_state.current_tool in TOOLS else 0)
    if st.button("Go"):
        st.session_state.current_tool = sel_tool
        st.experimental_rerun()

    st.markdown("---")
    # Export profile data
    if st.button("Export my data"):
        mem = io.BytesIO()
        with zipfile.ZipFile(mem, "w") as z:
            z.writestr(f"{st.session_state.username}_profile.json", json.dumps(profiles.get(st.session_state.username, {}), indent=2))
            z.writestr(f"{st.session_state.username}_chats.json", json.dumps(chat_history.get(st.session_state.username, {}), indent=2))
        mem.seek(0)
        st.download_button("Download ZIP", data=mem, file_name=f"{st.session_state.username}_studygenie.zip")

# -------------------------
# Home: show tiles (B) and a header
# -------------------------
st.markdown("<div class='page'>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;'>✨ StudyGenie Ultra — Your AI Study Bestie ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;opacity:0.85;'>Tap a tool tile below or use the dropdown in the sidebar. Each tool keeps its own chat history.</p>", unsafe_allow_html=True)

st.markdown("<div class='tools-grid'>", unsafe_allow_html=True)
# tile info
TILE_DESCS = {
    "AI Doubt Solver":"Ask a doubt and get crisp explanation.",
    "Notes Generator":"Generate short revision notes.",
    "Summary Maker":"Summarize long text into bullets.",
    "Timetable Builder":"Make a study timetable.",
    "Motivation Booster":"Get multi-line motivation.",
    "Flashcards":"Auto-generate Q/A flashcards.",
    "Brain-Dump Cleaner":"Organize messy thoughts.",
    "Answer Checker":"Compare and correct answers.",
    "AI Planner":"Make a simple plan for your goal.",
    "Mindset Reset":"Short mental reset script.",
    "Study Routine Designer":"Design a daily routine.",
    "Exam Strategy Maker":"Create an exam strategy.",
    "Personal Study Coach":"Friendly personalized advice."
}
for t in TOOLS:
    # clicking a tile sets current tool and reruns
    if st.button(f"{t}", key=f"tile_{t}"):
        st.session_state.current_tool = t
        st.rerun()
    # small description under each button (use columns to make grid but simple)
    st.markdown(f"<div style='text-align:center;font-size:12px;margin-bottom:8px;color:#333;'>{TILE_DESCS.get(t,'')}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Tool runner UI (single function handles all tools)
# -------------------------
st.markdown("---")
st.markdown(f"### 🔹 Active tool: **{st.session_state.current_tool}**")

def render_tool_ui(tool):
    # show per-tool history
    hist = get_user_tool_history(st.session_state.username, tool)
    if hist:
        st.markdown("**Conversation (this tool)**")
        for m in hist[-200:]:
            if m["role"] == "user":
                st.markdown(f"<div class='chat-box user'><b>You</b><div>{html.escape(m['message'])}</div><div class='small'>{m['time']}</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-box assistant'><b>Genie</b><div>{m['message']}</div><div class='small'>{m['time']}</div></div>", unsafe_allow_html=True)
    else:
        st.info("No conversation for this tool yet — say hi!")

    st.markdown("---")
    col1, col2 = st.columns([4,1])
    with col1:
        user_text = st.text_area("Type your input here", key=f"input_{tool}", height=150)
    with col2:
        uploaded = st.file_uploader("Upload audio (optional)", type=["mp3","wav","m4a"], key=f"up_{tool}")
        if uploaded:
            st.audio(uploaded)
            st.success("Audio uploaded (transcription requires OpenAI key).")

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
                    # simple browser TTS
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

    # Tool-specific extra UI sections
    if tool == "Motivation Booster":
        if st.button("New Motivation"):
            mot = random.choice([
                "Your effort today builds the life you want tomorrow.",
                "One focused hour counts more than a scattered day.",
                "You are allowed to rest — rest and return stronger."
            ])
            st.markdown(f"<div class='chat-box assistant'>{mot}</div>", unsafe_allow_html=True)

    if tool == "Flashcards":
        if st.button("Generate 6 flashcards (from last input)"):
            txt = st.session_state.get(f"input_{tool}", "").strip()
            if not txt:
                st.warning("Provide a topic or paste notes.")
            else:
                prompt = f"Create 6 concise Q/A flashcards for: {txt}"
                out = ask_ai_with_fallback(prompt)
                # store as simple flashcards
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
                st.markdown(f"<div class='chat-box assistant'>{out}</div>", unsafe_allow_html=True)
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
                st.markdown(f"<div class='chat-box assistant'>{out}</div>", unsafe_allow_html=True)

# render active tool
render_tool_ui(st.session_state.current_tool)

# footer: quick profile view and small autosaves
st.markdown("---")
col1, col2 = st.columns([3,1])
with col1:
    st.markdown(f"**User:** {st.session_state.username}  •  **Tool:** {st.session_state.current_tool}")
    prof = profiles.get(st.session_state.username, {})
    st.markdown(f"Notes: {len(prof.get('notes',[]))} • Flashcards: {len(prof.get('flashcards',[]))} • Motivations: {len(prof.get('motivations',[]))}")
with col2:
    if st.button("Save snapshot of tool"):
        mem = io.BytesIO()
        z = zipfile.ZipFile(mem, mode="w")
        z.writestr(f"{st.session_state.username}_{st.session_state.current_tool}.json", json.dumps(get_user_tool_history(st.session_state.username, st.session_state.current_tool), indent=2))
        z.close()
        mem.seek(0)
        st.download_button("Download Snapshot", data=mem, file_name=f"{st.session_state.username}_{st.session_state.current_tool}_snapshot.zip")

# persist DBs
save_json(USER_DB, users)
save_json(PROFILE_DB, profiles)
save_json(CHAT_DB, chat_history)

st.markdown("</div>", unsafe_allow_html=True)