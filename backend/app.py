import streamlit as st
from query import get_answer
from db import register_user, login_user, save_chat, get_chats, save_knowledge

# ---------------- CONFIG ----------------
st.set_page_config(page_title="EV Assistant", layout="wide")

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# ---------------- THEME ----------------
if st.session_state.theme == "dark":
    st.markdown("""
        <style>
        body { background-color: #0E1117; color: white; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        body { background-color: #F7F7F8; color: black; }
        </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIN PAGE ----------------
if st.session_state.user is None:

    st.title("🔐 EV Assistant Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    with col2:
        if st.button("Sign Up"):
            success = register_user(username, password)
            if success:
                st.success("Account created! Now login")
            else:
                st.error("User already exists")

# ---------------- MAIN APP ----------------
else:

    # -------- TOP BAR --------
    col1, col2, col3, col4 = st.columns([8,1,1,1])

    with col1:
        st.title("⚡ EV Diagnostic Assistant")

    with col2:
        if st.button("🌙" if st.session_state.theme=="light" else "☀"):
            st.session_state.theme = "dark" if st.session_state.theme=="light" else "light"
            st.rerun()

    with col3:
        st.button("⚙")

    with col4:
        st.button("🔗")

    # -------- SIDEBAR --------
    with st.sidebar:
        st.header("📊 Dashboard")

        if st.button("➕ New Chat"):
            st.session_state.pending_question = None

        search = st.text_input("🔍 Search chats")

        st.subheader("📜 Chat History")
        chats = get_chats()

        for q, a in chats[::-1]:
            if search.lower() in q.lower():
                st.write("🧑", q[:30])

        st.markdown("---")
        st.write(f"👤 {st.session_state.user}")

        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

    # -------- CHAT AREA --------
    query = st.text_input("Ask your EV question...")

    if st.button("Ask"):
        if query:
            answer = get_answer(query)

            if answer == "NOT_FOUND":
                st.warning("I don't have info in manual.\nDo you want to teach me? 👇")
                st.session_state.pending_question = query
            else:
                st.success(answer)
                save_chat(query, answer)

    # -------- TEACH SYSTEM --------
    if st.session_state.pending_question:
        user_answer = st.text_area("Enter your answer:")

        if st.button("Save Knowledge"):
            save_knowledge(st.session_state.pending_question, user_answer)
            st.success("Learned successfully 🎉")
            st.session_state.pending_question = None

    # -------- CHAT DISPLAY --------
    st.subheader("💬 Conversation")

    chats = get_chats()

    for q, a in chats[::-1]:
        st.markdown(f"""
        <div style='background:#1E293B;padding:10px;border-radius:10px;margin:5px'>
        🧑 {q}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:#2563EB;padding:10px;border-radius:10px;margin:5px;color:white'>
        🤖 {a}
        </div>
        """, unsafe_allow_html=True)