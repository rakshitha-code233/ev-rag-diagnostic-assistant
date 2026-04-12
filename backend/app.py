import streamlit as st
from db import register_user, login_user
from query import get_answer
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="EV Assistant", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #0b1f4a, #132f6b, #1f4ed8);
}
header {visibility: hidden;}

/* TITLE */
.ev-title {
    background: linear-gradient(90deg, #60a5fa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 48px;
    font-weight: bold;
}

/* CARD */
.card-btn {
    position: relative;
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    border-radius: 18px;
    padding: 30px;
    text-align: center;
    color: white;
    cursor: pointer;
    border: 1px solid rgba(255,255,255,0.15);
    transition: all 0.35s ease;
    overflow: hidden;
}

/* GLOW BORDER */
.card-btn::before {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 18px;
    padding: 1px;
    background: linear-gradient(120deg, #60a5fa, transparent, #3b82f6);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
            mask-composite: exclude;
    opacity: 0.4;
}

/* SHINE */
.card-btn::after {
    content: "";
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(120deg, transparent, rgba(255,255,255,0.2), transparent);
    transform: rotate(25deg);
    opacity: 0;
}

/* HOVER */
.card-btn:hover {
    transform: translateY(-10px) scale(1.03);
    box-shadow: 0 0 30px rgba(96,165,250,0.6);
}
.card-btn:hover::after {
    opacity: 1;
    animation: shine 1.2s linear;
}

@keyframes shine {
    from { transform: translateX(-100%) rotate(25deg); }
    to { transform: translateX(100%) rotate(25deg); }
}

/* ICON */
.card-icon {
    font-size: 40px;
    margin-bottom: 10px;
}

/* CHAT */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.08);
    border-radius: 12px;
    color: white;
}

/* INPUT */
textarea, input {
    background-color: #1e3a8a !important;
    color: white !important;
}

/* HISTORY */
.history-box {
    background: rgba(255,255,255,0.08);
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
    color: white;
}
.history-box:hover {
    background: rgba(255,255,255,0.15);
    box-shadow: 0 0 10px rgba(96,165,250,0.4);
}

/* PROFILE */
.profile-card {
    background: rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 12px;
    color: white;
    width: 300px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state or not isinstance(st.session_state.history, list):
    st.session_state.history = []

# ---------------- LOGIN ----------------
if st.session_state.page == "login":

    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state.user = {
                "username": user[1],
                "email": user[2]
            }
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Create Account"):
        st.session_state.page = "signup"
        st.rerun()

# ---------------- SIGNUP ----------------
elif st.session_state.page == "signup":

    st.title("Create Account")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Register"):

        if password != confirm:
            st.error("Passwords do not match")

        elif len(password) < 6:
            st.error("Password must be at least 6 characters")

        else:
            result = register_user(username, email, password)

            if result == "success":
                st.success("Account created successfully")
                st.session_state.page = "login"
                st.rerun()

            elif result == "exists":
                st.error("Email already exists")

    if st.button("Back"):
        st.session_state.page = "login"
        st.rerun()

# ---------------- MAIN APP ----------------
else:

    # -------- TOP BAR --------
    col1, col2 = st.columns([1,10])

    # PROFILE LEFT
    with col1:
        if st.button("👤"):
            st.session_state.page = "profile"
            st.rerun()

    with col2:
        st.markdown("<h2 class='ev-title'>EV Diagnostic Assistant</h2>", unsafe_allow_html=True)

    # ---------------- PROFILE PAGE ----------------
    if st.session_state.page == "profile":

        st.header("My Profile")

        st.write("Name:", st.session_state.user["username"])
        st.write("Email:", st.session_state.user["email"])

        if st.button("Logout"):
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()

        if st.button("⬅ Back"):
            st.session_state.page = "dashboard"
            st.rerun()

    # ---------------- DASHBOARD ----------------
    elif st.session_state.page == "dashboard":

        # ✅ FIXED ORDER
        st.markdown("<h3>Welcome to</h3>", unsafe_allow_html=True)
        st.markdown("<h1 class='ev-title'>EV Diagnostic Assistant</h1>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        # ✅ CLICKABLE CARDS
        with col1:
            if st.button("🤖 EV Assistant", use_container_width=True):
                st.session_state.page = "chat"

        with col2:
            if st.button("📄 Upload Manuals", use_container_width=True):
                st.session_state.page = "upload"

        with col3:
            if st.button("🕘 Chat History", use_container_width=True):
                st.session_state.page = "history"

    # ---------------- CHAT ----------------
    elif st.session_state.page == "chat":

        st.header("EV Assistant")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("Ask question...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            response = get_answer(user_input)

            st.session_state.messages.append({"role": "assistant", "content": response})

            st.session_state.history.append({
                "time": datetime.now().strftime("%I:%M %p"),
                "question": user_input,
                "chat": st.session_state.messages.copy()
            })

            st.rerun()

    # ---------------- HISTORY ----------------
    elif st.session_state.page == "history":

        st.header("Chat History")

        for i, item in enumerate(st.session_state.history):

            if st.button(f"{item['time']} - {item['question']}", key=f"h{i}"):
                st.session_state.messages = item["chat"]
                st.session_state.page = "chat"
                st.rerun()

    # ---------------- UPLOAD ----------------
    elif st.session_state.page == "upload":

        st.header("Upload Manuals")

        file = st.file_uploader("Upload PDF", type=["pdf"])

        if file:
            with open("temp.pdf", "wb") as f:
                f.write(file.read())

            st.success("Uploaded successfully")

        if st.button("⬅ Back"):
            st.session_state.page = "dashboard"
            st.rerun()