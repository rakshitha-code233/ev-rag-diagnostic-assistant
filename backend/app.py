import streamlit as st
from db import register_user, login_user, get_knowledge, save_knowledge
from query import ask_ai

st.set_page_config(page_title="EV Assistant", layout="wide")

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- LOGIN SYSTEM ----------
if not st.session_state.logged_in:

    st.title("🔐 EV Assistant Login System")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            st.session_state.page = "login"

    with col2:
        if st.button("Signup"):
            st.session_state.page = "signup"

    # -------- LOGIN --------
    if st.session_state.page == "login":
        st.subheader("Login Form")

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login Now"):
            user = login_user(email, password)
            if user:
                st.session_state.logged_in = True
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Invalid credentials ❌")

    # -------- SIGNUP --------
    elif st.session_state.page == "signup":
        st.subheader("Signup Form")

        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")
        confirm = st.text_input("Confirm Password")

        if st.button("Signup Now"):
            if password != confirm:
                st.error("Passwords do not match ❌")
            else:
                success = register_user(email, password)
                if success:
                    st.success("Account created ✅ Please login")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error("User already exists ❌")

    st.stop()

# ---------- MAIN EV CHAT ----------
st.title("⚡ EV Diagnostic Assistant")

# -------- CHAT HISTORY --------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------- INPUT --------
query = st.chat_input("Ask your EV question...")

if query:

    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    # -------- GREETINGS --------
    if query.lower() in ["hi", "hello"]:
        answer = "Hello! 👋 Ask me about EV diagnostics."

    elif query.lower() in ["thanks", "thank you"]:
        answer = "You're welcome 😊"

    else:
        stored = get_knowledge(query)

        if stored:
            answer = f"📘 From manual:\n{stored}"
        else:
            answer = "❌ Not found in manual.\n\nDo you want AI answer?"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)

    # -------- AI OPTION --------
    if "Not found" in answer:

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Yes (Use AI)"):
                ai_answer = ask_ai(query)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_answer
                })

                with st.chat_message("assistant"):
                    st.write(ai_answer)

                if st.button("Save this answer"):
                    save_knowledge(query, ai_answer)
                    st.success("Saved ✅")

        with col2:
            if st.button("No"):
                st.info("Okay 👍")

# -------- LOGOUT --------
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()