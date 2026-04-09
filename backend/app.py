import streamlit as st
from db import register_user, login_user
from query import get_answer

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="EV Assistant", layout="wide")

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "home"

if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.main {
    background-color: #0f172a;
    color: white;
}
.box {
    background: white;
    padding: 30px;
    border-radius: 10px;
    width: 350px;
    margin: auto;
}
button {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HOME PAGE ----------------
if st.session_state.user is None:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.title("🚗 EV Diagnostic Assistant")

        if st.session_state.page == "home":
            if st.button("Login"):
                st.session_state.page = "login"
            if st.button("Signup"):
                st.session_state.page = "signup"

        # -------- LOGIN --------
        elif st.session_state.page == "login":
            st.subheader("Login Form")

            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Login Now"):
                user = login_user(email, password)
                if user:
                    st.session_state.user = email
                    st.success("Login Successful")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

            if st.button("Go to Signup"):
                st.session_state.page = "signup"
                st.rerun()

        # -------- SIGNUP --------
        elif st.session_state.page == "signup":
            st.subheader("Signup Form")

            email = st.text_input("New Email")
            password = st.text_input("New Password", type="password")

            if st.button("Create Account"):
                if len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    register_user(email, password)
                    st.success("Account Created! Go to Login")

            if st.button("Go to Login"):
                st.session_state.page = "login"
                st.rerun()

# ---------------- MAIN APP ----------------
else:
    st.sidebar.title("Dashboard")
    st.sidebar.write(f"👤 {st.session_state.user}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    st.title("🚗 EV Diagnostic Assistant")

    user_input = st.chat_input("Ask EV question...")
    if "last_question" not in st.session_state:
        st.session_state.last_question = ""

    if user_input:

    # If user says YES → use previous question
        if user_input.lower() == "yes":
            response = get_answer(st.session_state.last_question, use_ai=True)

        else:
        # Save current question
            st.session_state.last_question = user_input
            response = get_answer(user_input)

        st.write(response)

    # -------- CHAT DISPLAY --------
    for role, msg in st.session_state.chat:
        if role == "user":
            with st.chat_message("user"):
                st.write(msg)
        else:
            with st.chat_message("assistant"):
                st.write(msg)