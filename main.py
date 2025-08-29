"""
TalentScout — Streamlit frontend for AI Hiring Assistant
Refined version of the user's provided main.py with:
- improved validation and flow
- graceful fallback when API is not available
- simulated local storage (anonymized) for candidate records
- clearer prompts & modular structure
- safer OpenRouter handling
"""

import streamlit as st
import requests
import re
import json
import os
from datetime import datetime
from prompts import (
    build_greeting_prompt,
    build_tech_questions_prompt,
    build_fallback_prompt,
    build_context_prompt,
    build_validation_error_prompt,
    build_question_analysis_prompt,
    build_summary_prompt,
)

# ---------------------- Configuration ----------------------
STORAGE_FILE = "candidates_simulated.json"  # simulated local storage (anonymized)
API_TIMEOUT = 30
DEFAULT_MODEL = "meta-llama/llama-3.3-8b-instruct:free"

# ---------------------- UI CSS ----------------------
st.set_page_config(page_title="TalentScout AI Hiring Assistant", layout="centered")
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .chat-container {
        max-height: 360px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e1e5e9;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        margin-left: 20%;
        text-align: right;
    }
    .bot-message {
        background-color: #e9ecef;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        margin-right: 20%;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------- Utilities ----------------------
def load_api_key():
    """Load API key from Streamlit secrets if available."""
    try:
        return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        return None


def persist_candidate(candidate: dict):
    """
    Save anonymized candidate data to a local JSON file (simulated storage).
    Do NOT store sensitive raw data in production. This is only for assignment/demo.
    """
    record = candidate.copy()
    # Simple anonymization: mask phone partially and email domain
    if "phone" in record:
        digits = re.sub(r"\D", "", record["phone"])
        if len(digits) >= 6:
            record["phone"] = f"{digits[:3]}***{digits[-3:]}"
        else:
            record["phone"] = "masked"
    if "email" in record:
        parts = record["email"].split("@")
        if len(parts) == 2:
            local = parts[0]
            record["email"] = f"{local[:2]}***@{parts[1]}"
        else:
            record["email"] = "masked"
    record["timestamp"] = datetime.utcnow().isoformat() + "Z"

    # Prepare file
    if not os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "w") as f:
            json.dump([], f, indent=2)

    with open(STORAGE_FILE, "r+") as f:
        try:
            data = json.load(f)
        except Exception:
            data = []
        data.append(record)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()


def query_openrouter(prompt: str, system_message: str = None, api_key: str = None, model: str = DEFAULT_MODEL):
    """
    Query OpenRouter Chat Completions endpoint with simple error handling.
    Returns text response or raises Exception with message.
    """
    if api_key is None:
        raise RuntimeError("No API key provided for OpenRouter.")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": "TalentScout Hiring Assistant",
    }
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 900,
    }
    url = "https://openrouter.ai/api/v1/chat/completions"
    try:
        res = requests.post(url, headers=headers, json=body, timeout=API_TIMEOUT)
        if res.status_code == 200:
            j = res.json()
            # Defensive check
            return j["choices"][0]["message"]["content"]
        else:
            raise RuntimeError(f"API Error {res.status_code}: {res.text}")
    except requests.exceptions.Timeout:
        raise RuntimeError("Request timed out.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request error: {str(e)}")


def safe_generate_questions_local(techstack: str):
    """
    Local fallback to generate technical questions without calling an LLM.
    Produces 3-5 reasonable questions per major technology listed.
    """
    techs = [t.strip() for t in re.split(r"[,\n;]+", techstack) if t.strip()]
    questions = []
    for t in techs:
        # Basic heuristics for question generation
        if t.lower() in ("python", "py"):
            questions += [
                "1. Describe how Python's GIL affects multi-threaded programs and how you'd work around it.",
                "2. Explain list vs generator comprehension and when to use each.",
                "3. Given a large CSV (10GB), how would you process it efficiently in Python?",
            ]
        elif t.lower().startswith("django"):
            questions += [
                "1. How does Django's middleware work and how would you add a custom one?",
                "2. Explain Django ORM vs raw SQL and when to use each.",
                "3. How do you secure file uploads in a Django app?",
            ]
        elif t.lower() in ("javascript", "js"):
            questions += [
                "1. Explain closures in JavaScript and give an example use case.",
                "2. Describe event loop and how async/await fits into it.",
                "3. How do you handle cross-origin requests (CORS) in a web app?",
            ]
        elif t.lower() in ("react", "reactjs"):
            questions += [
                "1. Explain hooks (useState, useEffect) and when to create a custom hook.",
                "2. How would you optimize rendering performance in a large React app?",
                "3. Describe how props and state differ and where each should live.",
            ]
        else:
            # Generic practical questions for unknown tech
            questions += [
                f"1. Describe a common real-world use-case for {t} and how you'd implement it.",
                f"2. What are common pitfalls when working with {t} and how do you avoid them?",
                f"3. Give a small performance or security consideration specific to {t}.",
            ]
        # keep only up to 5 unique questions overall (avoid huge lists)
        if len(questions) >= 10:
            break

    # Reduce/format: return first 5 questions
    unique = []
    for q in questions:
        if q not in unique:
            unique.append(q)
        if len(unique) >= 5:
            break
    formatted = "\n".join(unique)
    return formatted or "No tech stack provided. Please add technologies."


# ---------------------- Validation ----------------------
def validate_email(email: str) -> bool:
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email.strip()) is not None


def validate_phone(phone: str) -> bool:
    digits = re.sub(r"\D", "", phone)
    return 7 <= len(digits) <= 15


def validate_experience(exp: str) -> bool:
    try:
        years = float(exp)
        return 0 <= years <= 60
    except Exception:
        return False


def check_exit_keywords(text: str) -> bool:
    exit_keywords = ["exit", "quit", "bye", "goodbye", "end", "stop", "cancel"]
    return any(k in text.lower() for k in exit_keywords)


# ---------------------- Session state helpers ----------------------
def init_session_state():
    if "candidate_info" not in st.session_state:
        st.session_state.candidate_info = {}
    if "step" not in st.session_state:
        st.session_state.step = "greeting"
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "done" not in st.session_state:
        st.session_state.done = False
    if "questions_generated" not in st.session_state:
        st.session_state.questions_generated = False
    if "session_start" not in st.session_state:
        st.session_state.session_start = datetime.now().isoformat()


def add_to_conversation(speaker: str, message: str):
    st.session_state.conversation_history.append(
        {"speaker": speaker, "message": message, "timestamp": datetime.now().isoformat()}
    )


def display_conversation():
    if st.session_state.conversation_history:
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        for entry in st.session_state.conversation_history:
            cls = "user-message" if entry["speaker"] == "user" else "bot-message"
            st.markdown(f"<div class='{cls}'>{entry['message']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def get_step_prompt(step: str) -> str:
    prompts = {
        "greeting": "👋 Welcome to TalentScout! I'm your AI Hiring Assistant.",
        "fullname": "Let's start with your full name:",
        "email": "What's your email address?",
        "phone": "Please provide your phone number (include country code if needed):",
        "experience": "How many years of professional experience do you have? (Enter a number)",
        "position": "What position(s) are you applying for?",
        "location": "What's your current location (city, state/country)?",
        "techstack": "Please list your technical skills (languages, frameworks, DBs, tools). Separate by commas:",
    }
    return prompts.get(step, "")


def get_next_step(current_step: str) -> str:
    steps_order = [
        "greeting",
        "fullname",
        "email",
        "phone",
        "experience",
        "position",
        "location",
        "techstack",
    ]
    try:
        idx = steps_order.index(current_step)
        return steps_order[idx + 1] if idx + 1 < len(steps_order) else "questions"
    except ValueError:
        return "done"


def generate_summary_text():
    info = st.session_state.candidate_info
    summary = f"""
**Candidate Summary:**
- **Name:** {info.get('fullname', 'Not provided')}
- **Email:** {info.get('email', 'Not provided')}
- **Phone:** {info.get('phone', 'Not provided')}
- **Experience:** {info.get('experience', 'Not provided')} years
- **Position:** {info.get('position', 'Not provided')}
- **Location:** {info.get('location', 'Not provided')}
- **Tech Stack:** {info.get('techstack', 'Not provided')}
"""
    return summary


# ---------------------- Main app ----------------------
def main():
    init_session_state()
    api_key = load_api_key()

    st.markdown(
        """
    <div class="main-header">
        <h1>🤖 TalentScout AI Hiring Assistant</h1>
        <p>Your intelligent partner for technical recruitment screening</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    display_conversation()

    # Initial greeting step (one-time)
    if st.session_state.step == "greeting":
        greeting = build_greeting_prompt().strip()
        add_to_conversation("bot", greeting)
        st.session_state.step = "fullname"

    # Completed (after questions generated)
    if st.session_state.step == "questions" and not st.session_state.questions_generated:
        # Show summary & generate questions
        st.markdown(generate_summary_text())
        st.write("🎯 Generating personalized technical questions based on your tech stack...")
        techstack = st.session_state.candidate_info.get("techstack", "")
        if techstack:
            with st.spinner("Creating tailored questions..."):
                prompt = build_tech_questions_prompt(techstack)
                system_msg = "You are an expert technical recruiter. Generate 3-5 relevant technical interview questions based on candidate's tech stack. Format as numbered list."
                # Try API, fallback to local generator
                try:
                    if api_key:
                        questions = query_openrouter(prompt, system_msg, api_key=api_key)
                    else:
                        raise RuntimeError("No API key configured — using local fallback.")
                except Exception as e:
                    # fallback
                    questions = safe_generate_questions_local(techstack)
                    add_to_conversation("bot", f"(Fallback used) {str(e)}")
                st.markdown("### 🚀 Your Technical Interview Questions:")
                st.markdown(questions)
                add_to_conversation("bot", f"Technical questions based on your tech stack:\n{questions}")
        else:
            st.warning("No tech stack information available. Please provide your tech stack above to generate questions.")
        st.session_state.questions_generated = True
        st.session_state.step = "completed"

    # Completed screen
    if st.session_state.step == "completed":
        st.markdown(
            """
        <div class="success-box">
        <h3>✅ Screening Complete!</h3>
        <p>Thank you for completing the initial screening. Here's what happens next:</p>
        <ul>
        <li>Your information has been recorded (simulated)</li>
        <li>A recruiter will review your profile within 2-3 business days</li>
        <li>You'll receive an email with further instructions</li>
        </ul>
        <p><strong>Good luck with your application! 🍀</strong></p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.session_state.done = True
        # Persist the anonymized candidate info for simulated backend
        try:
            persist_candidate(st.session_state.candidate_info)
        except Exception:
            # Non-fatal; just warn in UI
            st.warning("Warning: Could not persist simulated record locally.")
        st.stop()

    # Normal step-by-step input collection
    if not st.session_state.done:
        current_step = st.session_state.step
        prompt_text = get_step_prompt(current_step)
        st.markdown(f"### {prompt_text}")

        with st.form(key=f"form_{current_step}"):
            user_input = st.text_input("Your answer:", key=f"input_{current_step}")
            submitted = st.form_submit_button("Submit")

        if submitted:
            # exit handling
            if check_exit_keywords(user_input or ""):
                st.markdown(
                    """
                <div class="success-box">
                <h3>👋 Session Ended</h3>
                <p>Thank you for your time! Feel free to return anytime to complete your application.</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                add_to_conversation("user", user_input or "[user ended session]")
                add_to_conversation("bot", "Session ended by user. Thank you!")
                st.session_state.done = True
                st.stop()

            # validate
            is_valid = True
            error_msg = ""
            if current_step == "email":
                is_valid = validate_email(user_input)
                if not is_valid:
                    error_msg = "Please enter a valid email address (e.g., user@example.com)"
            elif current_step == "phone":
                is_valid = validate_phone(user_input)
                if not is_valid:
                    error_msg = "Please enter a valid phone number (7-15 digits)"
            elif current_step == "experience":
                is_valid = validate_experience(user_input)
                if not is_valid:
                    error_msg = "Please enter years of experience as a number (0-60)"
            elif current_step in ["fullname", "position", "location", "techstack"]:
                is_valid = len((user_input or "").strip()) >= 2
                if not is_valid:
                    error_msg = f"Please provide a valid {current_step}"

            if is_valid:
                cleaned = user_input.strip()
                st.session_state.candidate_info[current_step] = cleaned
                add_to_conversation("user", cleaned)

                # For a few steps, call the LLM for small encouraging contextual reply if API exists
                if current_step in ["fullname", "experience", "position"]:
                    context_prompt = build_context_prompt(current_step, cleaned)
                    system_msg = "You are a friendly AI hiring assistant. Provide brief encouragement (1-2 sentences)."
                    try:
                        if api_key:
                            bot_resp = query_openrouter(context_prompt, system_msg, api_key=api_key)
                        else:
                            # local fallback happy path
                            bot_resp = f"Thanks, {st.session_state.candidate_info.get('fullname','candidate')} — noted."
                    except Exception as e:
                        bot_resp = f"(Fallback) {build_fallback_prompt(cleaned, current_step).strip()}"
                        add_to_conversation("bot", f"(Note: LLM fallback used) {str(e)}")
                    add_to_conversation("bot", bot_resp)

                # move to next step
                st.session_state.step = get_next_step(current_step)
                # Streamlit will rerun
                st.rerun()
            else:
                st.error(f"❌ {error_msg}")
                add_to_conversation("user", user_input or "")
                add_to_conversation("bot", f"I need to clarify that: {error_msg}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("🚨 An unexpected error occurred. Please refresh and try again.")
        st.write(f"Error details: {str(e)}")

    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🔒 Your information is secure for this demo and will be used only for recruitment purposes.</p>
        <p>Built with ❤️ by TalentScout AI Team | Powered by Advanced Language Models</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
