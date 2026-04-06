import streamlit as st
import re

from query import get_answer
from db import register_user, login_user, save_chat, get_chats

# ---------------- CONFIG ----------------
st.set_page_config(page_title="EV Assistant", layout="wide")

# ---------------- PASSWORD VALIDATION ----------------
def is_valid_password(password):
    if len(password) < 6:
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    return True

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- SIDEBAR MENU ----------------
menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- AUTH ----------------
if st.session_state.user is None:

    if choice == "Sign Up":
        st.title("📝 Create Account")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Sign Up"):
            if not is_valid_password(password):
                st.error("Password must be 6+ chars, include 1 uppercase & 1 number")
            else:
                success = register_user(username, password)
                if success:
                    st.success("Account created! Please login.")
                else:
                    st.error("Username already exists")

    elif choice == "Login":
        st.title("🔐 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(username, password)

            if user:
                st.session_state.user = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid username or password")

# ---------------- MAIN APP ----------------
if st.session_state.user:

    st.sidebar.success(f"👤 {st.session_state.user}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    st.title("⚡ EV Diagnostic Assistant")

    query = st.text_input("Ask your EV question:")

    if st.button("Ask"):
        if query:
            answer = get_answer(query)

            st.markdown("### 🤖 Answer")
            st.write(answer)

            save_chat(query, answer)

    # ---------------- CHAT HISTORY ----------------
    st.subheader("📜 Chat History")

    chats = get_chats()
    for q, a in chats[::-1]:
        st.write(f"🧑 {q}")
        st.write(f"🤖 {a}")
        st.markdown("---")