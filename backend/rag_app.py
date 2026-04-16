from datetime import datetime
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
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(22, 163, 74, 0.18), transparent 28%),
                linear-gradient(135deg, #07111f 0%, #10233b 48%, #163a2d 100%);
            color: #f8fafc;
        }
        [data-testid="stSidebar"] {
            background: rgba(7, 17, 31, 0.86);
            border-right: 1px solid rgba(148, 163, 184, 0.18);
        }
        .hero-card, .panel-card {
            background: rgba(15, 23, 42, 0.78);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 18px;
            padding: 1.2rem;
            box-shadow: 0 18px 50px rgba(2, 6, 23, 0.28);
            backdrop-filter: blur(10px);
        }
        .hero-title {
            font-size: 2.4rem;
            font-weight: 700;
            line-height: 1.1;
        }
        .hero-badge {
            display: inline-block;
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            background: rgba(34, 197, 94, 0.14);
            color: #bbf7d0;
            border: 1px solid rgba(74, 222, 128, 0.28);
            font-size: 0.82rem;
            margin-bottom: 0.9rem;
        }
        .hero-subtitle {
            color: #cbd5e1;
            font-size: 1rem;
            margin-top: 0.75rem;
        }
        .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
        }
        .feature-card {
            background: rgba(15, 23, 42, 0.62);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 16px;
            padding: 1rem;
            min-height: 150px;
        }
        .feature-title {
            color: #f8fafc;
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .feature-copy {
            color: #cbd5e1;
            font-size: 0.92rem;
            line-height: 1.5;
        }
        .profile-shell {
            background: linear-gradient(145deg, rgba(22, 101, 52, 0.24), rgba(15, 23, 42, 0.86));
            border: 1px solid rgba(148, 163, 184, 0.14);
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
            color: #ecfdf5;
            background: linear-gradient(135deg, #16a34a, #0f766e);
            margin-bottom: 0.9rem;
        }
        .profile-name {
            font-size: 1.6rem;
            font-weight: 700;
            color: #f8fafc;
        }
        .profile-meta {
            color: #cbd5e1;
            margin-top: 0.3rem;
            line-height: 1.7;
        }
        .list-chip {
            padding: 0.45rem 0.7rem;
            border-radius: 999px;
            display: inline-block;
            margin: 0.25rem 0.35rem 0 0;
            background: rgba(34, 197, 94, 0.12);
            color: #dcfce7;
            border: 1px solid rgba(74, 222, 128, 0.18);
            font-size: 0.84rem;
        }
        .metric-label {
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.78rem;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: 0.2rem;
        }
        div.stButton > button {
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            background: rgba(15, 23, 42, 0.72);
            color: #f8fafc;
        }
        div.stButton > button:hover {
            border-color: rgba(74, 222, 128, 0.7);
            color: #dcfce7;
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
                # Place render_home definition here to ensure it's available before main()
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
        render_brand_block(compact=True)
        st.markdown("## EV Diagnostic Assistant")
        st.caption("Manual-grounded answers for service technicians")

        if st.button("Home", use_container_width=True):
            st.session_state.page = "home"
        if st.button("Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
        if st.button("Assistant", use_container_width=True):
            st.session_state.page = "chat"
        if st.button("Manuals", use_container_width=True):
            st.session_state.page = "upload"
        if st.button("History", use_container_width=True):
            st.session_state.page = "history"
        if st.button("Profile", use_container_width=True):
            st.session_state.page = "profile"

        st.markdown("---")
        manuals = list_manual_files()
        st.write(f"Indexed manuals ready: **{len(manuals)}**")

        if st.button("Log out", use_container_width=True):
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
    hero_col, side_col = st.columns([1.5, 1])

    with hero_col:
        render_brand_block()
        st.markdown(
            """
            <div class="hero-card">
                <div class="hero-badge">Technician-ready EV support</div>
                <div class="hero-title">Manual-grounded diagnostics with exact citations</div>
                <div class="hero-subtitle">
                    Ask about symptoms, charging issues, DTCs, or service procedures and get answers
                    traced back to the exact manual pages your team can verify.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with side_col:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Quick Start</div>
                <div class="feature-copy">
                    1. Upload EV repair PDFs<br>
                    2. Rebuild the manual index<br>
                    3. Ask the assistant for a cited procedure
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3)
    metrics = [
        ("Manuals loaded", str(len(manuals))),
        ("Chat turns", str(len(st.session_state.history))),
        ("Citations mode", "Enabled"),
    ]

    for column, (label, value) in zip((col1, col2, col3), metrics):
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
    action1, action2 = st.columns(2)
    with action1:
        if st.button("Open assistant", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()
    with action2:
        if st.button("Manage manuals", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()

    st.write("")
    feature1, feature2, feature3 = st.columns(3)
    feature_cards = [
        (
            "Exact Manual Citations",
            "Every useful answer is tied back to the manual and page so technicians can verify the guidance before acting.",
        ),
        (
            "Fast Fault Isolation",
            "Use the chat to search symptoms, charging behavior, warnings, or service steps without flipping through hundreds of pages.",
        ),
        (
            "Workshop Friendly",
            "The retrieval layer can still operate in locked-down environments, which helps in service bays with limited network access.",
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
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">What You Can Ask</div>
                <div class="feature-copy">
                    Try questions like:<br>
                    • How do I open the charge port?<br>
                    • What checks should I perform when the vehicle will not start?<br>
                    • What does the manual say about charging alerts?<br>
                    • Where is the service disconnect located?
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


def render_chat() -> None:
    st.header("Technician Assistant")
    st.caption("Answers are generated from indexed repair manuals and include page citations.")

    if not list_manual_files():
        st.warning("No manuals are indexed yet. Upload one or more PDFs to start retrieval.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    tools_col, audio_col = st.columns([1.2, 1])
    with tools_col:
        st.session_state.voice_autoplay = st.checkbox(
            "Read answers aloud automatically",
            value=st.session_state.voice_autoplay,
            help="Uses the browser's built-in voice to speak the latest assistant answer.",
        )
    with audio_col:
        if st.button("Speak last answer", use_container_width=True):
            if st.session_state.last_spoken_answer:
                speak_text(st.session_state.last_spoken_answer)
            else:
                st.info("Ask a question first so there is an answer to read aloud.")

    client_ready = get_groq_client() is not None
    if client_ready:
        audio_prompt = st.audio_input("Ask with your voice")
        if audio_prompt is not None:
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
    else:
        st.info("Add `GROQ_API_KEY` in `backend/.env` to enable microphone questions.")

    user_input = st.chat_input("Ask about a symptom, diagnostic procedure, or DTC...")
    if not user_input:
        return

    handle_question_submission(user_input)


def render_history() -> None:
    st.header("Chat History")
    if not st.session_state.history:
        st.info("No conversations yet.")
        return

    for index, item in enumerate(reversed(st.session_state.history), start=1):
        if st.button(f"{item['time']}  {item['question']}", key=f"history-{index}", use_container_width=True):
            st.session_state.messages = item["chat"]
            st.session_state.page = "chat"
            st.rerun()


def render_profile() -> None:
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
        ("Profile status", "Active"),
        ("Manual library", str(len(manuals))),
        ("Saved chats", str(len(st.session_state.history))),
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
    st.header("Manual Ingestion")
    st.caption("Upload EV repair manuals. Each PDF is chunked, embedded, and indexed with page metadata for citations.")

    if manuals:
        st.write("Current manuals:")
        for manual in manuals:
            st.write(f"- {manual.name}")
    else:
        st.info("No manuals uploaded yet.")

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
        if st.button("Rebuild index", use_container_width=True):
            with st.spinner("Re-indexing manuals..."):
                stats = build_manual_index()
            st.success(f"Index rebuilt. Manuals: {stats['manuals_indexed']}, chunks: {stats['chunks_indexed']}.")
    with col2:
        if st.button("Clear all manuals", use_container_width=True):
            reset_manual_store()
            st.success("Manual files and index cleared.")


def render_home() -> None:
    hero_col, side_col = st.columns([1.5, 1])
    with hero_col:
        render_brand_block()
        st.markdown(
            """
            <div class="hero-card">
                <div class="hero-badge">Welcome to the EV Diagnostic Assistant</div>
                <div class="hero-title">Your entry point for manual-grounded diagnostics</div>
                <div class="hero-subtitle">
                    Use the sidebar to access the dashboard, chat with the assistant, upload manuals, and more.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with side_col:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Quick Start</div>
                <div class="feature-copy">
                    1. Upload EV repair PDFs<br>
                    2. Rebuild the manual index<br>
                    3. Ask the assistant for a cited procedure
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.write("")
    st.info("Use the navigation on the left to get started.")


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
    if page == "home":
        render_home()
    elif page == "dashboard":
        render_dashboard()
    elif page == "chat":
        render_chat()
    elif page == "history":
        render_history()
    elif page == "profile":
        render_profile()
    elif page == "upload":
        render_upload()
    else:
        st.session_state.page = "home"
        st.rerun()


if __name__ == "__main__":
    main()
