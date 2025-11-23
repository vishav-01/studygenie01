import requests
import time
import html

def wiki_fallback_summary(query):
    """Quick Wikipedia summary fallback (no API key)."""
    try:
        q = requests.get("https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(query), timeout=8)
        if q.status_code == 200:
            j = q.json()
            return j.get("extract") or j.get("title") or ""
    except Exception:
        return ""
    return ""

def demo_fallback(query):
    """Canned demo answer if no external info available (short and sweet)."""
    return f"(Demo answer) I cannot reach the AI right now. Quick tip: {query[:120]} — try re-asking with more context or check your OpenAI billing."

def ask_ai_with_fallback(prompt, preferred_models=None, max_retries=2, temperature=0.45, max_tokens=350):
    """
    Robust call with graceful fallback:
      - returns AI text if ok
      - if quota/rate-limit or API error -> try Wikipedia summary -> else demo message
    """
    key = st.secrets.get("OPENAI_API_KEY", "")
    if not key:
        return "❌ No OpenAI key found. Add OPENAI_API_KEY to Streamlit Secrets or use demo mode."

    if preferred_models is None:
        preferred_models = ["gpt-5-mini", "gpt-4o-mini", "gpt-4.1-mini", "gpt-3.5-turbo"]

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload_base = {
        "messages": [
            {"role":"system","content":"You are StudyGenie — concise, helpful, Gen-Z friendly."},
            {"role":"user","content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    for model in preferred_models:
        attempt = 0
        while attempt <= max_retries:
            attempt += 1
            payload = dict(payload_base); payload["model"] = model
            try:
                resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=25)
            except Exception as e:
                if attempt > max_retries:
                    # network failure -> fallback
                    wiki = wiki_fallback_summary(prompt)
                    return wiki or demo_fallback(prompt)
                time.sleep(0.6 * attempt)
                continue

            # if response not JSON or error
            try:
                j = resp.json()
            except Exception:
                if attempt > max_retries:
                    wiki = wiki_fallback_summary(prompt)
                    return wiki or demo_fallback(prompt)
                time.sleep(0.4); continue

            # If API returned an error object
            if "error" in j:
                err_msg = j["error"].get("message", "")
                # detect common quota or rate-limit cases and fallback
                low = err_msg.lower()
                if "quota" in low or "insufficient_quota" in low or "rate limit" in low or resp.status_code in (429, 402):
                    # Friendly user-facing message + fallback
                    wiki = wiki_fallback_summary(prompt)
                    if wiki:
                        return "(Fallback) Quick wiki summary since AI quota limited:\n\n" + wiki
                    return "(AI unavailable due to quota or rate limits.) " + demo_fallback(prompt)
                # Other errors -> try again or break
                if attempt <= max_retries and resp.status_code >= 500:
                    time.sleep(1.0 * attempt); continue
                return f"❌ AI error: {err_msg}"

            # Successful choices
            choices = j.get("choices")
            if not choices:
                if attempt <= max_retries:
                    time.sleep(0.4); continue
                break
            message = choices[0].get("message") or {}
            content = message.get("content") or message.get("text") or ""
            if content:
                return content.strip()
            if attempt <= max_retries:
                time.sleep(0.3); continue

    # exhausted models -> fallback
    wiki = wiki_fallback_summary(prompt)
    return "(Fallback) " + (wiki or demo_fallback(prompt))