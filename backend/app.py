import streamlit as st
from db import register_user, login_user
from query import get_answer

# ---------------- CONFIG ----------------
st.set_page_config(page_title="EV Assistant", layout="wide")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_question" not in st.session_state:
    st.session_state.last_question = ""

# ---------------- CSS ----------------
st.markdown("""
<style>
/* Background */
body {
    background-color: #0f172a;
    color: white;
}

/* Chat bubbles */
.user-msg {
    background-color: #1e293b;
    padding: 12px;
    border-radius: 10px;
    margin: 5px;
    text-align: right;
}

.bot-msg {
    background-color: #020617;
    padding: 12px;
    border-radius: 10px;
    margin: 5px;
    text-align: left;
}

/* Sidebar */
.sidebar .sidebar-content {
    background-color: #020617;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:

    st.title("🚗 EV Diagnostic Assistant")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(email, password)
            if user:
                st.session_state.logged_in = True
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Invalid credentials ❌")

    with col2:
        st.subheader("Sign Up")
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")

        if st.button("Sign Up"):
            register_user(new_email, new_password)
            st.success("Account created ✅")

# ---------------- MAIN APP ----------------
else:

    # -------- SIDEBAR --------
    with st.sidebar:
        st.title("📊 Dashboard")

        if st.button("➕ New Chat"):
            st.session_state.messages = []

        st.markdown("### 📜 History")

        for msg in st.session_state.messages[-10:]:
            if msg["role"] == "user":
                st.write("🧑 " + msg["content"][:30])

        st.markdown("---")

        st.write("👤 Profile")
        st.write("User logged in")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()

    # -------- HEADER --------
    st.title("🚗 EV Diagnostic Assistant")

    # -------- CHAT DISPLAY --------
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    # -------- INPUT --------
    user_input = st.chat_input("Ask your EV question...")

    if user_input:

        # Show user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Handle YES logic
        if user_input.lower() == "yes":
            response = get_answer(st.session_state.last_question, use_ai=True)
        else:
            st.session_state.last_question = user_input
            response = get_answer(user_input)

        # Save bot response
        st.session_state.messages.append({"role": "bot", "content": response})

        st.rerun()