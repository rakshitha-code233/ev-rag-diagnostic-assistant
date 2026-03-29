import streamlit as st
import sqlite3
from query import get_answer
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# go to project root → then database folder
db_path = os.path.join(BASE_DIR, "..", "database", "users.db")

conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")
conn.commit()

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------- SIGNUP ----------
def signup():
    st.title("📝 Create Account")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Signup"):
        try:
            c.execute("INSERT INTO users VALUES (?, ?)", (new_user, new_pass))
            conn.commit()
            st.success("Account created! Now login ✅")
            st.session_state.page = "login"
        except:
            st.error("Username already exists ❌")

    if st.button("Back to Login"):
        st.session_state.page = "login"

# ---------- LOGIN ----------
def login():
    st.title("🔐 Login")

    user = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, password))
        result = c.fetchone()

        if result:
            st.session_state.logged_in = True
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")

    if st.button("Create Account"):
        st.session_state.page = "signup"

# ---------- CHAT ----------
def chat():
    st.title("🚗 EV Assistant")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask your EV question...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_answer(user_input)
                st.write(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

# ---------- NAVIGATION ----------
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login()
    else:
        signup()
else:
    chat()