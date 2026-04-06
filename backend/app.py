import streamlit as st
from db import register_user, login_user

st.set_page_config(page_title="EV Assistant", layout="centered")

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- AFTER LOGIN → EV APP ----------------
if st.session_state.logged_in:

    st.title("⚡ EV Diagnostic Assistant")

    st.success("Welcome! You are logged in ✅")

    query = st.text_input("Ask your EV question:")

    if query:
        if query.lower() in ["hi", "hello"]:
            st.write("Hello! 👋")
        elif query.lower() in ["thanks", "thank you"]:
            st.write("You're welcome 😊")
        else:
            st.write("I don't have information in the manual.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"

    st.stop()   # 🔥 VERY IMPORTANT (stops login UI)

# ---------------- LOGIN / SIGNUP UI ----------------
st.markdown("## EV Assistant Login")

col1, col2 = st.columns(2)

with col1:
    if st.button("Login"):
        st.session_state.page = "login"

with col2:
    if st.button("Signup"):
        st.session_state.page = "signup"

# ---------------- LOGIN ----------------
if st.session_state.page == "login":

    st.subheader("Login Form")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login Now"):
        user = login_user(email, password)
        if user:
            st.session_state.logged_in = True   # ✅ KEY FIX
            st.success("Login successful")
            st.rerun()  # 🔥 reload app → go to EV page
        else:
            st.error("Invalid credentials")

# ---------------- SIGNUP ----------------
elif st.session_state.page == "signup":

    st.subheader("Signup Form")

    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_pass")
    confirm = st.text_input("Confirm Password")

    if st.button("Signup Now"):
        if password != confirm:
            st.error("Passwords do not match")
        else:
            success = register_user(email, password)
            if success:
                st.success("Account created! Please login")
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("User already exists")