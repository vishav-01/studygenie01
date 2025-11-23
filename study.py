# app.py — StudyGenie K-Edition (Sidebar-only tools + 3 themes) - Final
import streamlit as st
import requests
import json
import os
import io
import zipfile
import html
import random
import time
from datetime import datetime
from typing import List, Dict

# ---------------------------
# Config + storage paths
# ---------------------------
st.set_page_config(page_title="StudyGenie — K-Edition", layout="wide")
USER_DB = "users.json"
PROFILE_DB = "profiles.json"
CHAT_DB = "chat_history.json"

# ---------------------------
# Helpers: load / save JSON
# ---------------------------
def load_json(path: str, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path: str, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

users: Dict = load_json(USER_DB, {})
profiles: Dict = load_json(PROFILE_DB, {})
chat_history: Dict = load_json(CHAT_DB, {})  # {username: {tool: [{role, message, time}] } }

# ---------------------------
# Base CSS and Themes
# ---------------------------
BASE_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] { font-family: 'Poppins', sans-serif; }
.app-shell { padding:18px; }
.tile { background: rgba(255,255,255,0.78); padding:14px; border-radius:14px; text-align:center; box-shadow: 0 8px 20px rgba(0,0,0,0.05); transition: transform .12s ease; }
.tile:hover { transform: translateY(-6px); cursor:pointer; }
.tools-grid { display:grid; grid-template-columns: repeat(auto-fit,minmax(180px,1fr)); gap:12px; }
.controls { background: rgba(255,255,255,0.6); padding:10px; border-radius:12px; }
.chat-box { padding:12px; border-radius:12px; margin:8px 0; }
.chat-user { background: rgba(255,235,245,0.95); padding:10px; border-radius:10px; text-align:right; }
.chat-assistant { background: rgba(230,250,255,0.95); padding:10px; border-radius:10px; text-align:left; }
.small { font-size:12px; opacity:0.75; }
.stButton>button { border:none; }
"""

THEMES = {
    "Pink K-Pop Glow": {
        "page_bg": "linear-gradient(135deg,#fff0f6 0%,#ffe6f4 40%,#fff7fb 100%)",
        "title_color": "#ff2f92",
    },
    "Sky Pastel Dream": {
        "page_bg": "linear-gradient(135deg,#e6f8ff 0%,#eef6ff 40%,#f7faff 100%)",
        "title_color": "#2f6fb2",
    },
    "Doraemon Playroom": {
        "page_bg": "linear-gradient(135deg,#d9f0ff 0%,#bfe8ff 40%,#ffffff 100%)",
        "title_color": "#0b6fbf",
    }
}

# ---------------------------
# Session init
# ---------------------------
if "username" not in st.session_state:
    st.session_state.username = "Guest"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_tool" not in st.session_state:
    st.session_state.current_tool = "AI Doubt Solver"
if "ui_theme" not in st.session_state:
    st.session_state.ui_theme = "Pink K-Pop Glow"
if "ai_cache" not in st.session_state:
    st.session_state.ai_cache = {}
if "current_motivation" not in st.session_state:
    st.session_state.current_motivation = None

# ---------------------------
# Tools & descriptions
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
# History helpers
# ---------------------------
def get_user_tool_history(user: str, tool: str) -> List[dict]:
    return chat_history.get(user, {}).get(tool, [])

def add_user_tool_history(user: str, tool: str, role: str, message: str):
    if user not in chat_history:
        chat_history[user] = {}
    if tool not in chat_history[user]:
        chat_history[user][tool] = []
    chat_history[user][tool].append({"role": role, "message": message, "time": str(datetime.now())})
    save_json(CHAT_DB, chat_history)

# ---------------------------
# AI call with graceful fallback
# ---------------------------
def wiki_fallback_summary(query: str) -> str:
    try:
        r = requests.get("https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(query), timeout=6)
        if r.status_code == 200:
            j = r.json()
            return j.get("extract", "")
    except Exception:
        return ""
    return ""

def ask_ai_with_fallback(prompt: str, preferred_models=None, temp=0.5, max_tokens=300) -> str:
    # check cache
    if prompt in st.session_state.ai_cache:
        return st.session_state.ai_cache[prompt]
    key = st.secrets.get("OPENAI_API_KEY", "")
    if not key:
        demo = "(Demo) No OPENAI_API_KEY found. Add key in Streamlit Secrets to enable real AI."
        st.session_state.ai_cache[prompt] = demo
        return demo

    if preferred_models is None:
        preferred_models = ["gpt-4.1-mini", "gpt-4o-mini", "gpt-3.5-turbo"]

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    system = "You are StudyGenie — warm, concise, Gen-Z friendly. Reply in short crisp notes unless user asks for long."

    for model in preferred_models:
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temp,
                "max_tokens": max_tokens
            }
            resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=18)
            j = resp.json()
        except Exception:
            j = {}

        # handle errors
        if "error" in j:
            err = j.get("error", {}).get("message", "")
            low = err.lower()
            if "quota" in low or "rate limit" in low or resp.status_code in (429, 402):
                wiki = wiki_fallback_summary(prompt)
                if wiki:
                    ans = "(Fallback) Quick wiki summary:\n\n" + wiki
                else:
                    ans = "(Demo) AI unavailable due to quota or rate limits."
                st.session_state.ai_cache[prompt] = ans
                return ans
            # try next model otherwise
            continue

        choices = j.get("choices")
        if not choices:
            continue
        content = choices[0].get("message", {}).get("content", "").strip()
        if content:
            st.session_state.ai_cache[prompt] = content
            return content

    # final fallback
    wiki = wiki_fallback_summary(prompt)
    ans = "(Fallback) " + (wiki or "AI is unavailable right now. Try again later.")
    st.session_state.ai_cache[prompt] = ans
    return ans

# ---------------------------
# Prompt router for tools
# ---------------------------
def route_prompt_for_tool(toolname: str, user_text: str) -> str:
    mapping = {
        "AI Doubt Solver": f"Explain concisely in simple bullet points: {user_text}",
        "Notes Generator": f"Create crisp revision notes for: {user_text}",
        "Summary Maker": f"Summarize this text into 4–6 bullets: {user_text}",
        "Timetable Builder": f"Create a daily timetable given: {user_text}",
        "Motivation Booster": f"Write a 2–3 line encouraging message about: {user_text}",
        "Flashcards": f"Create 6 concise Q/A flashcards for: {user_text}",
        "Brain-Dump Cleaner": f"Organize the following messy notes into clear bullets: {user_text}",
        "Answer Checker": f"Grade and correct this student's answer: {user_text}",
        "AI Planner": f"Create a simple step-by-step plan to achieve: {user_text}",
        "Mindset Reset": f"Write a short mindset reset to re-energize: {user_text}",
        "Study Routine Designer": f"Design a daily study routine for: {user_text}",
        "Exam Strategy Maker": f"Create a high-impact exam strategy for: {user_text}",
        "Personal Study Coach": f"You are a study coach. Respond kindly with practical steps: {user_text}"
    }
    return mapping.get(toolname, user_text)

# ---------------------------
# Sidebar UI: login, theme, tools (sidebar-only access)
# ---------------------------
with st.sidebar:
    st.markdown("<div class='controls'>", unsafe_allow_html=True)
    st.header("StudyGenie • K-Edition")

    # login
    if not st.session_state.logged_in:
        name = st.text_input("Enter display name", value="")
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
    # theme selector
    st.subheader("Theme")
    theme_choice = st.radio("Choose theme:", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.ui_theme) if st.session_state.ui_theme in THEMES else 0)
    st.session_state.ui_theme = theme_choice

    st.markdown("---")
    # Tools (sidebar-only access)
    st.subheader("Tools")
    selected_tool = st.selectbox("Open tool:", TOOLS, index=TOOLS.index(st.session_state.current_tool) if st.session_state.current_tool in TOOLS else 0)
    if st.button("Open"):
        st.session_state.current_tool = selected_tool
        st.rerun()

    st.markdown("---")
    # Export / download
    if st.button("Export my data"):
        mem = io.BytesIO()
        with zipfile.ZipFile(mem, "w") as z:
            z.writestr(f"{st.session_state.username}_profile.json", json.dumps(profiles.get(st.session_state.username, {}), indent=2))
            z.writestr(f"{st.session_state.username}_chats.json", json.dumps(chat_history.get(st.session_state.username, {}), indent=2))
        mem.seek(0)
        st.download_button("Download ZIP", data=mem, file_name=f"{st.session_state.username}_studygenie.zip")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Apply selected theme CSS + header
# ---------------------------
theme = THEMES.get(st.session_state.ui_theme, THEMES["Pink K-Pop Glow"])
css = BASE_CSS + f"\nbody {{ background: {theme['page_bg']} !important; }}\n"
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.markdown("<div class='app-shell'>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align:center;color:{theme['title_color']};'>✨ StudyGenie — K-Edition ({st.session_state.ui_theme}) ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;opacity:0.85;'>Access tools only from the sidebar. Each tool keeps its own chat history and saved notes.</p>", unsafe_allow_html=True)

# ---------------------------
# Tiles view (visual only) — purely decorative; tools open only via sidebar
# ---------------------------
st.markdown("<div class='tools-grid'>", unsafe_allow_html=True)
for t in TOOLS:
    st.markdown(f"<div class='tile'><h3>{t}</h3><p>{TILE_DESCS.get(t,'')}</p></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"### 🔹 Active tool: **{st.session_state.current_tool}**")

# ---------------------------
# Tool UI renderer
# ---------------------------
def render_tool_ui(tool: str):
    # show history
    hist = get_user_tool_history(st.session_state.username, tool)
    if hist:
        st.markdown("**Conversation (this tool)**")
        for m in hist[-200:]:
            if m["role"] == "user":
                st.markdown(f"<div class='chat-box chat-user'><b>You</b><div>{html.escape(m['message'])}</div><div class='small'>{m['time']}</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-box chat-assistant'><b>Genie</b><div>{m['message']}</div><div class='small'>{m['time']}</div></div>", unsafe_allow_html=True)
    else:
        st.info("No conversation for this tool yet — open it from the sidebar and say hi!")

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

    # Tool-specific extras (Motivation, Flashcards, Notes, Summary, Timetable, Answer check etc.)
    if tool == "Motivation Booster":
        if st.button("New Motivation"):
            mot = random.choice([
                "Your effort today builds the life you want tomorrow.",
                "One focused hour counts more than a scattered day.",
                "You are allowed to rest — rest and return stronger."
            ])
            st.markdown(f"<div class='chat-box chat-assistant'>{mot}</div>", unsafe_allow_html=True)
        if st.button("Save Motivation to profile"):
            profiles.setdefault(st.session_state.username, {}).setdefault("motivations", []).append(st.session_state.get("current_motivation") or "")
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

# Render active tool
render_tool_ui(st.session_state.current_tool)

# Footer + snapshot export
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

# Persist DBs
save_json(USER_DB, users)
save_json(PROFILE_DB, profiles)
save_json(CHAT_DB, chat_history)

st.markdown("</div>", unsafe_allow_html=True)