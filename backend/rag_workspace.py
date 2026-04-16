from datetime import datetime
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from groq import Groq

from db import create_table, init_db, login_user, register_user
from manual_query import get_answer
from rag import DATA_DIR, INDEX_FILE, METADATA_FILE, build_manual_index, list_manual_files


load_dotenv()

st.set_page_config(page_title="EV Diagnostic Assistant", layout="wide")

init_db()
create_table()

LOGO_PATH = Path(__file__).resolve().parent / "logo.png"


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-1: #050d1f;
            --bg-2: #091734;
            --bg-3: #0f2a5f;
            --panel: rgba(8, 20, 46, 0.92);
            --panel-soft: rgba(10, 24, 56, 0.78);
            --border: rgba(89, 154, 255, 0.18);
            --text: #f8fbff;
            --muted: #9cb6df;
            --sky: #58a6ff;
            --sky-soft: #7bc8ff;
        }
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(88, 166, 255, 0.12), transparent 24%),
                radial-gradient(circle at 20% 80%, rgba(62, 120, 255, 0.1), transparent 22%),
                linear-gradient(135deg, var(--bg-1) 0%, var(--bg-2) 46%, var(--bg-3) 100%);
            color: var(--text);
        }
        [data-testid="stSidebar"] {
            background: rgba(5, 14, 34, 0.97);
            border-right: 1px solid var(--border);
        }
        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.9rem;
            padding: 0.95rem 0.9rem;
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(8, 20, 46, 0.98), rgba(9, 27, 61, 0.92));
            border: 1px solid var(--border);
            margin-bottom: 1rem;
        }
        .sidebar-brandmark {
            width: 58px;
            height: 58px;
            border-radius: 999px;
            overflow: hidden;
            border: 2px solid rgba(123, 200, 255, 0.35);
            background: radial-gradient(circle at 30% 30%, rgba(123, 200, 255, 0.24), rgba(37, 99, 235, 0.22));
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .sidebar-brandmark img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .sidebar-brandtext {
            min-width: 0;
        }
        .sidebar-title {
            color: var(--text);
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.2;
        }
        .sidebar-subtitle {
            color: var(--muted);
            font-size: 0.82rem;
            margin-top: 0.25rem;
            line-height: 1.45;
        }
        .sidebar-caption {
            color: #6f89b8;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin: 0.35rem 0 0.6rem 0.15rem;
        }
        .page-shell {
            background: linear-gradient(180deg, rgba(6, 16, 38, 0.9), rgba(7, 18, 42, 0.82));
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1rem 1.1rem 1.2rem 1.1rem;
            box-shadow: 0 20px 60px rgba(1, 7, 20, 0.36);
        }
        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.1rem 0.1rem 0.9rem 0.1rem;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid rgba(88, 166, 255, 0.12);
        }
        .topbar-title {
            color: var(--text);
            font-size: 0.95rem;
            font-weight: 600;
        }
        .topbar-login {
            min-width: 90px;
            height: 34px;
            border-radius: 10px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(180deg, #2174ff, #1d57d8);
            border: 1px solid rgba(123, 200, 255, 0.32);
            color: white;
            font-size: 0.82rem;
            font-weight: 600;
            padding: 0 0.9rem;
        }
        .topbar-actions {
            display: flex;
            align-items: center;
            gap: 0.55rem;
        }
        .topbar-chip {
            min-width: 34px;
            height: 34px;
            border-radius: 999px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: rgba(12, 31, 69, 0.9);
            border: 1px solid rgba(88, 166, 255, 0.18);
            color: #cfe4ff;
            font-size: 0.9rem;
        }
        .hero-card, .panel-card, .nav-card, .composer-shell, .history-row, .upload-drop {
            background: linear-gradient(180deg, rgba(9, 22, 52, 0.94), rgba(11, 28, 63, 0.84));
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 1.2rem;
            box-shadow: 0 18px 50px rgba(2, 6, 23, 0.28);
            backdrop-filter: blur(10px);
        }
        .hero-card {
            padding: 1.6rem;
            min-height: 320px;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        .hero-card::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            height: 96px;
            background:
                radial-gradient(circle at 30% 50%, rgba(88, 166, 255, 0.8), transparent 30%),
                linear-gradient(90deg, transparent, rgba(88, 166, 255, 0.18), transparent);
            opacity: 0.6;
        }
        .welcome-line {
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1.1;
            color: #ffffff;
        }
        .brand-line {
            font-size: 2.8rem;
            font-weight: 800;
            line-height: 1.08;
            color: var(--sky-soft);
            margin-top: 0.2rem;
        }
        .hero-title {
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1.1;
            color: #f8fafc;
        }
        .hero-badge {
            display: inline-block;
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            background: rgba(88, 166, 255, 0.12);
            color: #d7ebff;
            border: 1px solid rgba(123, 200, 255, 0.22);
            font-size: 0.82rem;
            margin-bottom: 0.9rem;
        }
        .hero-subtitle {
            color: var(--muted);
            font-size: 1rem;
            margin-top: 0.75rem;
            line-height: 1.65;
            max-width: 480px;
            text-align: center;
        }
        .hero-illustration {
            width: min(440px, 94%);
            margin-top: 1.35rem;
            position: relative;
            z-index: 2;
        }
        .hero-illustration svg {
            width: 100%;
            height: auto;
            display: block;
            filter: drop-shadow(0 16px 34px rgba(41, 110, 255, 0.25));
        }
        .section-title {
            font-size: 1.08rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
            color: var(--text);
        }
        .feature-card {
            background: linear-gradient(180deg, rgba(9, 22, 52, 0.95), rgba(10, 27, 58, 0.84));
            border: 1px solid rgba(88, 166, 255, 0.14);
            border-radius: 16px;
            padding: 1rem;
            min-height: 172px;
        }
        .action-card {
            background: linear-gradient(180deg, rgba(9, 22, 52, 0.96), rgba(10, 27, 58, 0.88));
            border: 1px solid rgba(88, 166, 255, 0.14);
            border-radius: 18px;
            padding: 1rem;
            min-height: 120px;
        }
        .action-icon {
            width: 42px;
            height: 42px;
            border-radius: 14px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: rgba(88, 166, 255, 0.16);
            color: #cfe4ff;
            font-size: 1rem;
            margin-bottom: 0.8rem;
        }
        .feature-title, .nav-title {
            color: var(--text);
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .feature-copy {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.6;
        }
        .nav-step {
            color: var(--sky-soft);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.5rem;
        }
        .list-chip {
            padding: 0.45rem 0.7rem;
            border-radius: 999px;
            display: inline-block;
            margin: 0.25rem 0.35rem 0 0;
            background: rgba(88, 166, 255, 0.12);
            color: #e0f2fe;
            border: 1px solid rgba(123, 200, 255, 0.18);
            font-size: 0.84rem;
        }
        .metric-label {
            color: #9cc7ff;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.78rem;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: 0.2rem;
            color: var(--text);
        }
        .assistant-note {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.55;
        }
        .voice-card {
            background: linear-gradient(180deg, rgba(9, 22, 52, 0.96), rgba(10, 27, 58, 0.88));
            border: 1px solid rgba(123, 200, 255, 0.16);
            border-radius: 16px;
            padding: 0.7rem 0.75rem 0.5rem 0.75rem;
            min-height: 78px;
        }
        .voice-title {
            color: #d7ebff;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.45rem;
        }
        .chat-panel {
            background: linear-gradient(180deg, rgba(8, 19, 44, 0.94), rgba(10, 25, 54, 0.88));
            border: 1px solid rgba(88, 166, 255, 0.12);
            border-radius: 22px;
            padding: 1rem;
        }
        .history-row {
            padding: 0.9rem 1rem;
            border-radius: 16px;
            margin-bottom: 0.75rem;
            box-shadow: none;
        }
        .upload-drop {
            text-align: center;
            padding: 2rem 1.2rem;
            min-height: 240px;
        }
        .upload-icon {
            font-size: 2rem;
            color: var(--sky-soft);
            margin-bottom: 0.9rem;
        }
        .profile-shell {
            background: linear-gradient(145deg, rgba(14, 55, 116, 0.5), rgba(11, 28, 58, 0.9));
            border: 1px solid rgba(125, 211, 252, 0.14);
            border-radius: 22px;
            padding: 1.4rem;
            box-shadow: 0 18px 50px rgba(2, 6, 23, 0.28);
        }
        .profile-avatar {
            width: 68px;
            height: 68px;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            font-weight: 700;
            color: #eff6ff;
            background: linear-gradient(135deg, #0ea5e9, #2563eb);
            margin-bottom: 0.9rem;
        }
        .profile-name {
            font-size: 1.6rem;
            font-weight: 700;
            color: #f8fafc;
        }
        .profile-meta {
            color: var(--muted);
            margin-top: 0.3rem;
            line-height: 1.7;
        }
        div.stButton > button {
            border-radius: 999px;
            border: 1px solid rgba(88, 166, 255, 0.2);
            background: rgba(11, 28, 58, 0.82);
            color: var(--text);
        }
        div.stButton > button:hover {
            border-color: rgba(123, 200, 255, 0.7);
            color: #e0f2fe;
        }
        div.stButton > button[kind="primary"] {
            background: linear-gradient(180deg, #2174ff, #1d57d8);
            border-color: rgba(123, 200, 255, 0.32);
        }
        div[data-testid="stAudioInput"] {
            background: rgba(11, 28, 58, 0.72);
            border: 1px solid rgba(123, 200, 255, 0.16);
            border-radius: 16px;
            padding: 0.2rem 0.6rem;
        }
        div[data-testid="stAudioInput"] button {
            width: 100%;
        }
        div[data-testid="stChatMessage"] {
            background: transparent;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session() -> None:
    defaults = {
        "page": "login",
        "user": None,
        "messages": [],
        "history": [],
        "last_spoken_answer": "",
        "voice_autoplay": False,
        "last_audio_hash": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_brand_block(compact: bool = False) -> None:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=72 if compact else 120)


def render_sidebar_brand() -> None:
    logo_markup = "<div class='sidebar-brandmark'></div>"
    if LOGO_PATH.exists():
        encoded_logo = base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
        logo_markup = (
            "<div class='sidebar-brandmark'>"
            f"<img src='data:image/png;base64,{encoded_logo}' alt='EV Assistant logo' />"
            "</div>"
        )

    st.markdown(
        f"""
        <div class="sidebar-brand">
            {logo_markup}
            <div class="sidebar-brandtext">
                <div class="sidebar-title">EV Diagnostic Assistant</div>
                <div class="sidebar-subtitle">Manual-grounded EV technician workspace</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_shell(title: str) -> None:
    st.markdown(
        f"""
        <div class="page-shell">
            <div class="topbar">
                <div class="topbar-title">{title}</div>
                <div class="topbar-actions">
                    <span class="topbar-chip">☼</span>
                    <span class="topbar-chip">◐</span>
                    <span class="topbar-chip">⇄</span>
                    <span class="topbar-chip">⚙</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topbar(title: str, show_login: bool = False) -> None:
    login_markup = "<span class='topbar-login'>Login</span>" if show_login else ""
    st.markdown(
        f"""
        <div class="topbar">
            <div class="topbar-title">{title}</div>
            <div class="topbar-actions">
                <span class="topbar-chip">&#9728;</span>
                <span class="topbar-chip">&#9681;</span>
                <span class="topbar-chip">&#10227;</span>
                <span class="topbar-chip">&#9881;</span>
                {login_markup}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_user_initials() -> str:
    user = st.session_state.get("user") or {}
    username = (user.get("username") or "EV Technician").strip()
    parts = [part[0].upper() for part in username.split() if part]
    return "".join(parts[:2]) or "EV"


def get_groq_client() -> Groq | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def transcribe_audio_question(audio_file) -> str | None:
    client = get_groq_client()
    if client is None or audio_file is None:
        return None

    suffix = Path(audio_file.name).suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
        temp_audio.write(audio_file.getvalue())
        temp_path = temp_audio.name

    try:
        with open(temp_path, "rb") as handle:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=handle,
                language="en",
                response_format="text",
                temperature=0.0,
            )
        return transcript.strip() if transcript else None
    except Exception:
        return None
    finally:
        Path(temp_path).unlink(missing_ok=True)


def speak_text(text: str) -> None:
    if not text:
        return

    payload = json.dumps(text)
    components.html(
        f"""
        <script>
        const spokenText = {payload};
        const synth = window.speechSynthesis;
        if (synth) {{
            synth.cancel();
            const utterance = new SpeechSynthesisUtterance(spokenText);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            synth.speak(utterance);
        }}
        </script>
        <div style="font-size:0.85rem;color:#cbd5e1;padding:0.35rem 0;">
            Reading the latest answer aloud...
        </div>
        """,
        height=40,
    )


def handle_question_submission(question: str) -> None:
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching manuals and drafting a cited answer..."):
            try:
                response = get_answer(question)
            except Exception as exc:
                response = f"Error while retrieving manual guidance: {exc}"
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.last_spoken_answer = response
    st.session_state.history.append(
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "question": question,
            "chat": st.session_state.messages.copy(),
        }
    )

    if st.session_state.voice_autoplay:
        speak_text(response)


def render_sidebar() -> None:
    with st.sidebar:
        render_sidebar_brand()
        st.markdown("<div class='sidebar-caption'>Workspace</div>", unsafe_allow_html=True)

        if st.button("⌂  Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
        if st.button("⚙  EV Assistant", use_container_width=True):
            st.session_state.page = "chat"
        if st.button("🗎  Upload Manuals", use_container_width=True):
            st.session_state.page = "upload"
        if st.button("◷  Chat History", use_container_width=True):
            st.session_state.page = "history"
        if st.button("☺  Profile", use_container_width=True):
            st.session_state.page = "profile"

        st.markdown("---")
        manuals = list_manual_files()
        st.write(f"Indexed manuals ready: **{len(manuals)}**")

        if st.button("⏻  Logout", use_container_width=True):
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()


def save_uploaded_manual(uploaded_file):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    destination = DATA_DIR / uploaded_file.name
    destination.write_bytes(uploaded_file.getbuffer())
    return destination


def reset_manual_store() -> None:
    for pdf_file in list_manual_files():
        pdf_file.unlink(missing_ok=True)
    INDEX_FILE.unlink(missing_ok=True)
    METADATA_FILE.unlink(missing_ok=True)


def render_login() -> None:
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        user = login_user(email, password)
        if user:
            st.session_state.user = user
            st.session_state.page = "dashboard"
            st.rerun()
        st.error("Invalid credentials")

    if st.button("Create account", use_container_width=True):
        st.session_state.page = "signup"
        st.rerun()


def render_signup() -> None:
    st.title("Create Account")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Register", use_container_width=True):
        if password != confirm:
            st.error("Passwords do not match.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            result = register_user(username, email, password)
            if result == "success":
                st.success("Account created. Please log in.")
                st.session_state.page = "login"
                st.rerun()
            st.error("Email already exists.")

    if st.button("Back to login", use_container_width=True):
        st.session_state.page = "login"
        st.rerun()


def render_dashboard() -> None:
    manuals = list_manual_files()
    user = st.session_state.get("user") or {}
    st.markdown(
        """
        <div class="topbar">
            <div class="topbar-title">Dashboard</div>
            <div class="topbar-actions">
                <span class="topbar-chip">☼</span>
                <span class="topbar-chip">◐</span>
                <span class="topbar-chip">⇄</span>
                <span class="topbar-chip">⚙</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    hero_col, side_col = st.columns([1.7, 1])

    with hero_col:
        st.markdown(
            """
            <div class="hero-card">
                <div class="hero-badge">Workshop-ready assistant</div>
                <div class="welcome-line">Welcome to</div>
                <div class="brand-line">EV Diagnostic Assistant</div>
                <div class="hero-subtitle">
                    Keep manuals organized, search procedures faster, and get page-cited answers for
                    charging, symptoms, locations, warnings, and service checks.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with side_col:
        st.markdown(
            f"""
            <div class="panel-card">
                <div class="section-title">Workspace Summary</div>
                <div class="feature-copy">
                    Signed in as: <strong>{user.get('username', 'EV Technician')}</strong><br>
                    Manuals loaded: <strong>{len(manuals)}</strong><br>
                    Saved conversations: <strong>{len(st.session_state.history)}</strong><br>
                    Retrieval mode: <strong>Citation-first</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    metric1, metric2, metric3 = st.columns(3)
    metrics = [
        ("Manuals Loaded", str(len(manuals))),
        ("Chat Turns", str(len(st.session_state.history))),
        ("Voice Ready", "Yes" if get_groq_client() else "Setup needed"),
    ]
    for column, (label, value) in zip((metric1, metric2, metric3), metrics):
        with column:
            st.markdown(
                f"""
                <div class="panel-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    action1, action2, action3 = st.columns(3)
    with action1:
        st.markdown(
            """
            <div class="action-card">
                <div class="action-icon">🤖</div>
                <div class="feature-title">EV Assistant</div>
                <div class="feature-copy">Ask questions about your EV manuals and get cited answers.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open EV Assistant", use_container_width=True, type="primary"):
            st.session_state.page = "chat"
            st.rerun()
    with action2:
        st.markdown(
            """
            <div class="action-card">
                <div class="action-icon">📄</div>
                <div class="feature-title">Upload Manuals</div>
                <div class="feature-copy">Upload PDF manuals and refresh retrieval for better assistance.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Manual Library", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()
    with action3:
        st.markdown(
            """
            <div class="action-card">
                <div class="action-icon">🕘</div>
                <div class="feature-title">Chat History</div>
                <div class="feature-copy">Review previous conversations and resume technician workflows.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Chat History", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()

    st.write("")
    st.markdown("### Workflow")
    step1, step2, step3, step4 = st.columns(4)
    steps = [
        ("Step 1", "Manual Library", "Upload EV repair PDFs and keep the document base current."),
        ("Step 2", "Rebuild Index", "Refresh retrieval after adding or replacing manuals."),
        ("Step 3", "EV Assistant", "Ask for procedures, component locations, or charging guidance."),
        ("Step 4", "History Review", "Reopen earlier conversations for repeat workshop issues."),
    ]
    for column, (step, title, copy) in zip((step1, step2, step3, step4), steps):
        with column:
            st.markdown(
                f"""
                <div class="nav-card">
                    <div class="nav-step">{step}</div>
                    <div class="nav-title">{title}</div>
                    <div class="feature-copy">{copy}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    feature1, feature2, feature3 = st.columns(3)
    feature_cards = [
        (
            "Exact Manual Citations",
            "Every answer can point technicians back to the exact manual page before any repair action is taken.",
        ),
        (
            "Systematic Technician Flow",
            "The app keeps Home, EV Assistant, Manual Library, Profile, and History in a clear operational order.",
        ),
        (
            "Voice and Text Support",
            "Ask by typing or recording your question, then listen to the answer when hands-free support helps.",
        ),
    ]
    for column, (title, copy) in zip((feature1, feature2, feature3), feature_cards):
        with column:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-title">{title}</div>
                    <div class="feature-copy">{copy}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Recommended Questions</div>
                <div class="feature-copy">
                    - How do I open the charge port?<br>
                    - What checks should I perform when the vehicle will not start?<br>
                    - What does the manual say about charging alerts?<br>
                    - Where is the service disconnect located?
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        recent_manuals = "".join(
            f"<span class='list-chip'>{manual.name}</span>" for manual in manuals[:8]
        ) or "<div class='feature-copy'>No manuals uploaded yet.</div>"
        st.markdown(
            f"""
            <div class="panel-card">
                <div class="section-title">Loaded Manuals</div>
                {recent_manuals}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_dashboard_reference() -> None:
    manuals = list_manual_files()
    user = st.session_state.get("user") or {}
    render_topbar("Dashboard", show_login=True)

    hero_col, side_col = st.columns([1.72, 1])
    with hero_col:
        st.markdown(
            """
            <div class="hero-card">
                <div class="hero-badge">Smart EV Diagnostics</div>
                <div class="welcome-line">Welcome to</div>
                <div class="brand-line">EV Diagnostic Assistant</div>
                <div class="hero-subtitle">
                    Your intelligent companion for electric vehicle diagnostics.
                    Upload manuals, ask questions, and get expert solutions instantly.
                </div>
                <div class="hero-illustration">
                    <svg viewBox="0 0 780 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="EV charging illustration">
                        <defs>
                            <linearGradient id="carBodyRef" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#9cdcff"/>
                                <stop offset="55%" stop-color="#5b95ff"/>
                                <stop offset="100%" stop-color="#2259d8"/>
                            </linearGradient>
                            <linearGradient id="chargerBodyRef" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#1f4b98"/>
                                <stop offset="100%" stop-color="#153466"/>
                            </linearGradient>
                            <radialGradient id="groundGlowRef" cx="50%" cy="50%" r="50%">
                                <stop offset="0%" stop-color="#58a6ff" stop-opacity="0.92"/>
                                <stop offset="100%" stop-color="#58a6ff" stop-opacity="0"/>
                            </radialGradient>
                        </defs>
                        <ellipse cx="340" cy="236" rx="290" ry="26" fill="url(#groundGlowRef)" opacity="0.9"/>
                        <rect x="610" y="76" width="56" height="132" rx="14" fill="url(#chargerBodyRef)" stroke="#7bc8ff" stroke-opacity="0.35"/>
                        <rect x="624" y="98" width="28" height="46" rx="8" fill="#0a1b41" stroke="#7bc8ff" stroke-opacity="0.35"/>
                        <path d="M655 138 C700 130, 718 156, 695 193" stroke="#7bc8ff" stroke-width="5" fill="none"/>
                        <circle cx="690" cy="197" r="9" fill="#7bc8ff"/>
                        <path d="M631 108 L640 108 L633 124 L644 124 L628 146 L632 130 L622 130 Z" fill="#ffd76a"/>
                        <path d="M168 176 C204 125 279 106 390 116 C450 122 498 140 546 172 C557 180 560 197 544 203 L152 203 C139 201 135 188 144 181 C151 174 159 172 168 176 Z" fill="url(#carBodyRef)"/>
                        <path d="M250 124 C312 90 406 93 463 129 L492 164 L230 164 Z" fill="#8fd3ff" opacity="0.95"/>
                        <path d="M278 130 C325 108 393 109 437 131 L456 155 L258 155 Z" fill="#e7f6ff" opacity="0.88"/>
                        <circle cx="241" cy="202" r="29" fill="#0e1834" stroke="#8ed2ff" stroke-width="6"/>
                        <circle cx="485" cy="202" r="29" fill="#0e1834" stroke="#8ed2ff" stroke-width="6"/>
                        <circle cx="241" cy="202" r="11" fill="#7bc8ff"/>
                        <circle cx="485" cy="202" r="11" fill="#7bc8ff"/>
                        <path d="M167 178 L133 190 L150 198 L181 196 Z" fill="#4f8dff"/>
                        <path d="M520 177 L558 186 L541 194 L513 194 Z" fill="#4f8dff"/>
                        <path d="M213 154 L194 164" stroke="#f1fbff" stroke-width="5" stroke-linecap="round"/>
                        <path d="M478 151 L509 163" stroke="#f1fbff" stroke-width="5" stroke-linecap="round"/>
                    </svg>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with side_col:
        st.markdown(
            f"""
            <div class="panel-card" style="min-height:320px; display:flex; flex-direction:column; justify-content:center;">
                <div class="section-title">Welcome to</div>
                <div class="brand-line" style="font-size:2rem; margin-top:0;">EV Diagnostic Assistant</div>
                <div class="feature-copy" style="margin-top:1rem;">
                    Use the menu to get started with EV diagnostics, upload manuals,
                    or chat with your assistant.<br><br>
                    Signed in as: <strong>{user.get('username', 'EV Technician')}</strong><br>
                    Manuals loaded: <strong>{len(manuals)}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    action1, action2, action3 = st.columns(3)
    cards = [
        ("EV Assistant", "Ask questions about your EV manuals", "Open EV Assistant", "chat"),
        ("Upload Manuals", "Upload PDF manuals for better assistance", "Open Manual Library", "upload"),
        ("Chat History", "View your previous conversations", "Open Chat History", "history"),
    ]
    for index, (column, (title, copy, button_label, page_name)) in enumerate(zip((action1, action2, action3), cards), start=1):
        with column:
            st.markdown(
                f"""
                <div class="action-card">
                    <div class="feature-title">{title}</div>
                    <div class="feature-copy">{copy}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            button_type = "primary" if index == 1 else "secondary"
            if st.button(button_label, key=f"dashboard-ref-{page_name}", use_container_width=True, type=button_type):
                st.session_state.page = page_name
                st.rerun()

    st.markdown("<div class='quick-login-note'>Don't have an account? Sign up</div>", unsafe_allow_html=True)


def render_chat() -> None:
    st.markdown(
        """
        <div class="topbar">
            <div class="topbar-title">EV Assistant</div>
            <div class="topbar-actions">
                <span class="topbar-chip">☼</span>
                <span class="topbar-chip">◐</span>
                <span class="topbar-chip">⇄</span>
                <span class="topbar-chip">⚙</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.header("EV Assistant")
    st.caption("Ask manual-grounded EV questions with text or voice. Answers include citations when supported by indexed manuals.")

    manuals = list_manual_files()
    if not manuals:
        st.warning("No manuals are indexed yet. Upload one or more PDFs to start retrieval.")

    summary1, summary2, summary3 = st.columns(3)
    summary_data = [
        ("Manuals", str(len(manuals))),
        ("Conversations", str(len(st.session_state.history))),
        ("Voice Input", "Enabled" if get_groq_client() else "Need API key"),
    ]
    for column, (label, value) in zip((summary1, summary2, summary3), summary_data):
        with column:
            st.markdown(
                f"""
                <div class="panel-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown("<div class='chat-panel'>", unsafe_allow_html=True)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="composer-shell">
            <div class="section-title">Ask the EV Assistant</div>
            <div class="assistant-note">
                Keep your question, send button, and voice recorder together in one place for a cleaner technician workflow.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    option_left, option_right = st.columns([1.2, 1])
    with option_left:
        st.session_state.voice_autoplay = st.checkbox(
            "Read answers aloud automatically",
            value=st.session_state.voice_autoplay,
            help="Uses the browser's built-in voice to speak the latest assistant answer.",
        )
    with option_right:
        if st.button("Speak last answer", use_container_width=True):
            if st.session_state.last_spoken_answer:
                speak_text(st.session_state.last_spoken_answer)
            else:
                st.info("Ask a question first so there is an answer to read aloud.")

    client_ready = get_groq_client() is not None
    with st.form("assistant_form", clear_on_submit=True):
        input_col, voice_col, send_col = st.columns([5.3, 1.8, 1.15], vertical_alignment="bottom")
        with input_col:
            user_input = st.text_input(
                "Ask a question",
                label_visibility="collapsed",
                placeholder="Ask about a symptom, diagnostic procedure, charging issue, or DTC...",
            )
        with voice_col:
            st.markdown("<div class='voice-card'><div class='voice-title'>Voice Input</div>", unsafe_allow_html=True)
            audio_prompt = st.audio_input("Voice", label_visibility="collapsed") if client_ready else None
            st.markdown("</div>", unsafe_allow_html=True)
        with send_col:
            send_clicked = st.form_submit_button("Send", use_container_width=True, type="primary")

    if not client_ready:
        st.info("Add `GROQ_API_KEY` in `backend/.env` to enable voice input beside the send button.")

    if send_clicked and user_input.strip():
        handle_question_submission(user_input.strip())
        st.rerun()

    if client_ready and audio_prompt is not None:
        audio_hash = hashlib.sha256(audio_prompt.getvalue()).hexdigest()
        if audio_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = audio_hash
            with st.spinner("Transcribing your audio question..."):
                transcript = transcribe_audio_question(audio_prompt)
            if transcript:
                st.caption(f"Voice transcript: {transcript}")
                handle_question_submission(transcript)
                return
            st.warning("I could not transcribe that audio. Please try again or type your question.")


def render_history() -> None:
    st.markdown(
        """
        <div class="topbar">
            <div class="topbar-title">Chat History</div>
            <div class="topbar-actions">
                <span class="topbar-chip">☼</span>
                <span class="topbar-chip">◐</span>
                <span class="topbar-chip">⇄</span>
                <span class="topbar-chip">⚙</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.header("Chat History")
    if not st.session_state.history:
        st.info("No conversations yet.")
        return

    for index, item in enumerate(reversed(st.session_state.history), start=1):
        st.markdown("<div class='history-row'>", unsafe_allow_html=True)
        if st.button(f"{item['time']}  {item['question']}", key=f"history-{index}", use_container_width=True):
            st.session_state.messages = item["chat"]
            st.session_state.page = "chat"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_profile() -> None:
    st.markdown(
        """
        <div class="topbar">
            <div class="topbar-title">Profile</div>
            <div class="topbar-actions">
                <span class="topbar-chip">☼</span>
                <span class="topbar-chip">◐</span>
                <span class="topbar-chip">⇄</span>
                <span class="topbar-chip">⚙</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.header("Profile")
    user = st.session_state.get("user") or {}
    manuals = list_manual_files()
    initials = get_user_initials()
    st.markdown(
        f"""
        <div class="profile-shell">
            <div class="profile-avatar">{initials}</div>
            <div class="profile-name">{user.get('username', 'EV Technician')}</div>
            <div class="profile-meta">
                Email: {user.get('email', 'Not found')}<br>
                Role: Diagnostic assistant user<br>
                Manuals available: {len(manuals)}<br>
                Conversation count: {len(st.session_state.history)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    stat1, stat2, stat3 = st.columns(3)
    stats = [
        ("Profile Status", "Active"),
        ("Manual Library", str(len(manuals))),
        ("Saved Chats", str(len(st.session_state.history))),
    ]
    for column, (label, value) in zip((stat1, stat2, stat3), stats):
        with column:
            st.markdown(
                f"""
                <div class="panel-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_upload() -> None:
    manuals = list_manual_files()
    st.markdown(
        """
        <div class="topbar">
            <div class="topbar-title">Upload Manuals</div>
            <div class="topbar-actions">
                <span class="topbar-chip">☼</span>
                <span class="topbar-chip">◐</span>
                <span class="topbar-chip">⇄</span>
                <span class="topbar-chip">⚙</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.header("Manual Library")
    st.caption("Upload EV repair manuals, rebuild retrieval, and keep the indexed library ready for technician questions.")

    if manuals:
        st.markdown("### Current Manuals")
        for manual in manuals:
            st.write(f"- {manual.name}")
    else:
        st.info("No manuals uploaded yet.")

    st.markdown(
        """
        <div class="upload-drop">
            <div class="upload-icon">☁</div>
            <div class="section-title">Drag and drop your PDF files here</div>
            <div class="feature-copy">Upload EV repair manuals to build your technician knowledge base.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader("Upload a PDF manual", type=["pdf"])
    if uploaded_file is not None:
        with st.spinner("Saving manual and rebuilding the vector index..."):
            saved_path = save_uploaded_manual(uploaded_file)
            stats = build_manual_index()
        st.success(
            f"Indexed {saved_path.name}. Manuals: {stats['manuals_indexed']}, chunks: {stats['chunks_indexed']}."
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Rebuild Index", use_container_width=True):
            with st.spinner("Re-indexing manuals..."):
                stats = build_manual_index()
            st.success(f"Index rebuilt. Manuals: {stats['manuals_indexed']}, chunks: {stats['chunks_indexed']}.")
    with col2:
        if st.button("Clear All Manuals", use_container_width=True):
            reset_manual_store()
            st.success("Manual files and index cleared.")


def main() -> None:
    apply_styles()
    initialize_session()

    if st.session_state.page == "login":
        render_login()
        return

    if st.session_state.page == "signup":
        render_signup()
        return

    render_sidebar()

    page = st.session_state.page
    if page == "dashboard":
        render_dashboard_reference()
    elif page == "chat":
        render_chat()
    elif page == "history":
        render_history()
    elif page == "profile":
        render_profile()
    elif page == "upload":
        render_upload()
    else:
        st.session_state.page = "dashboard"
        st.rerun()


if __name__ == "__main__":
    main()
