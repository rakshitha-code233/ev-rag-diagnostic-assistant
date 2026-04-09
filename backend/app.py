import streamlit as st
from db import register_user, login_user
from query import get_answer

# ---------------- CONFIG ----------------
st.set_page_config(page_title="EV Assistant", layout="wide")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

if "last_question" not in st.session_state:
    st.session_state.last_question = ""

if "show_profile" not in st.session_state:
    st.session_state.show_profile = False

# ---------------- CSS ----------------
st.markdown("""
<style>
html, body {
    background-color: #0f172a;
    color: white;
}

/* Inputs */
.stTextInput input, .stChatInput input {
    color: white !important;
    background-color: #1e293b !important;
}

/* Chat bubbles */
.user-msg {
    background-color: #1e293b;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
    text-align: right;
}

.bot-msg {
    background-color: #020617;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
    text-align: left;
}

/* Buttons */
.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:

    st.title("🚗 EV Diagnostic Assistant")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Login Form")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_email = email  # SAVE USER
                st.rerun()
            else:
                st.error("Invalid credentials ❌")

    with tab2:
        st.subheader("Sign Up Form")
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")

        if st.button("Sign Up"):
            register_user(new_email, new_password)
            st.success("Account created ✅")

# ---------------- MAIN APP ----------------
else:

    # -------- SIDEBAR --------
    with st.sidebar:

        # LOGO + CLICK
        if st.button("🚗 EV Assistant"):
            st.session_state.show_profile = True

        st.image("logo.png", width=150)

        st.markdown("---")

        # NEW CHAT
        if st.button("➕ New Chat"):
            new_chat = f"Chat {len(st.session_state.chats) + 1}"
            st.session_state.chats[new_chat] = []
            st.session_state.current_chat = new_chat

        st.markdown("### 💬 Chats")

        # CHAT LIST + RENAME
        for chat in list(st.session_state.chats.keys()):

            col1, col2 = st.columns([3,1])

            with col1:
                if st.button(chat):
                    st.session_state.current_chat = chat

            with col2:
                if st.button("✏️", key=chat):
                    new_name = st.text_input("Rename:", key=f"rename_{chat}")
                    if new_name:
                        st.session_state.chats[new_name] = st.session_state.chats.pop(chat)
                        st.session_state.current_chat = new_name
                        st.rerun()

        st.markdown("---")

        # LOGOUT
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.chats = {"Chat 1": []}
            st.session_state.current_chat = "Chat 1"
            st.rerun()

    # -------- PROFILE PAGE --------
    if st.session_state.show_profile:

        st.title("👤 User Profile")

        st.markdown(f"""
        ### 📧 Email:
        {st.session_state.get("user_email")}

        ### 🚗 App:
        EV Diagnostic Assistant

        ### 💬 Total Chats:
        {len(st.session_state.chats)}
        """)

        if st.button("⬅ Back to Chat"):
            st.session_state.show_profile = False
            st.rerun()

        st.stop()

    # -------- MAIN HEADER --------
    st.title("🚗 EV Diagnostic Assistant")

    # -------- CHAT DISPLAY --------
    current_chat = st.session_state.current_chat
    messages = st.session_state.chats[current_chat]

    for msg in messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    # -------- INPUT --------
    user_input = st.chat_input("Ask your EV question...")

    if user_input:

        messages.append({"role": "user", "content": user_input})

        if user_input.lower() == "yes":
            response = get_answer(st.session_state.last_question, use_ai=True)
        else:
            st.session_state.last_question = user_input
            response = get_answer(user_input)

        messages.append({"role": "bot", "content": response})

        st.session_state.chats[current_chat] = messages
        st.rerun()