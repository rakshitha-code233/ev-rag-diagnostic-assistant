import streamlit as st
from db import register_user, login_user,create_table
from query import get_answer
from datetime import datetime
from db import init_db

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="EV Assistant", layout="wide")

# ---------------- CREATE TABLE ----------------
init_db()
create_table()

# ---------------- CSS (UPDATED ONLY THIS) ----------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0b1f4a, #132f6b, #1f4ed8);
    color: white;
}

/* Sidebar */
section{
    background: #081a3a !important;
}

/* Sidebar buttons */
section button {
    background: transparent;
    color: white;
    border-radius: 8px;
    padding: 6px;
}
section button:hover {
    background: rgba(255,255,255,0.1);
}

/* ✅ NORMAL SMALL GLOW BUTTONS */
div.stButton > button {
    height: 40px;
    font-size: 14px;
    border-radius: 8px;
    background: rgba(255,255,255,0.08);
    color: white;
    border: none;
    box-shadow: 0 0 8px rgba(0,200,255,0.3);
    transition: 0.2s;
}

div.stButton > button:hover {
    box-shadow: 0 0 15px rgba(0,255,255,0.6);
    transform: scale(1.03);
}

/* Title */
.title {
    font-size: 40px;
    font-weight: bold;
}
.blue {
    color: #60a5fa;
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

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- LOGIN ----------------
if st.session_state.page == "login":

    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)

        if user:
            st.session_state.user = user
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
                st.success("Account created")
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("Email already exists")

    if st.button("⬅ Back"):
        st.session_state.page = "login"
        st.rerun()

# ---------------- MAIN APP ----------------
else:

    # -------- SIDEBAR TOGGLE --------
    st.set_page_config (
        page_title="EV Assistant",layout="wide",
        initial_sidebar_state="expanded"  # ✅ always visible
    )
    with st.sidebar:

            st.markdown("## ⚡ EV Assistant")

            if st.button("🏠 Dashboard"):
                st.session_state.page = "dashboard"

            if st.button("🤖 EV Assistant"):
                st.session_state.page = "chat"

            if st.button("🕘 Chat History"):
                st.session_state.page = "history"

            if st.button("📄 Upload Manuals"):
                st.session_state.page = "upload"

            st.markdown("<br><br><br><br>", unsafe_allow_html=True)

        # Logout at bottom
            if st.button("🚪 Logout"):
                st.session_state.clear()
                st.session_state.page = "login"
                st.rerun()
    # -------- PROFILE ICON --------
    col1, col2 = st.columns([10,1])
    with col2:
        if st.button("👤"):
            st.session_state.page = "profile"
            st.rerun()

    # ---------------- PROFILE ----------------
    if st.session_state.page == "profile":

        if st.button("⬅"):
            st.session_state.page = "dashboard"
            st.rerun()

        user = st.session_state.get("user", {})
        st.title("My Profile")
        st.write("Username:", user.get("username"," Not found"))
        st.write("Email:",   user.get("email"," Not found"))

    # ---------------- DASHBOARD (UPDATED ONLY THIS) ----------------
    elif st.session_state.page == "dashboard":

        st.markdown("<div class='title'>Welcome to</div>", unsafe_allow_html=True)
        st.markdown("<div class='title blue'>EV Diagnostic Assistant</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🤖 EV Assistant", use_container_width=True):
                st.session_state.page = "chat"
                st.rerun()

        with col2:
            if st.button("📂 Upload Manuals", use_container_width=True):
                st.session_state.page = "upload"
                st.rerun()

        with col3:
            if st.button("📜 Chat History", use_container_width=True):
                st.session_state.page = "history"
                st.rerun()

    # ---------------- CHAT ----------------
    elif st.session_state.page == "chat":

        if st.button("⬅"):
            st.session_state.page = "dashboard"
            st.rerun()

        st.header("EV Assistant")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("Ask EV question...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            try:
                response = get_answer(user_input)
            except Exception as e:
                response = f"Error: {str(e)}"

            st.session_state.messages.append({"role": "assistant", "content": response})

            st.session_state.history.append({
                "time": datetime.now().strftime("%I:%M %p"),
                "question": user_input,
                "chat": st.session_state.messages.copy()
            })

            st.rerun()

    # ---------------- HISTORY ----------------
    elif st.session_state.page == "history":

        if st.button("⬅"):
            st.session_state.page = "dashboard"
            st.rerun()

        st.header("Chat History")

        for i, item in enumerate(st.session_state.history):
            if st.button(f"{item['time']} - {item['question']}", key=i):
                st.session_state.messages = item["chat"]
                st.session_state.page = "chat"
                st.rerun()

    # ---------------- UPLOAD ----------------
    elif st.session_state.page == "upload":

        if st.button("⬅"):
            st.session_state.page = "dashboard"
            st.rerun()

        st.header("Upload Manuals")

        file = st.file_uploader("Upload PDF", type=["pdf"])

        if file:
            with open("temp.pdf", "wb") as f:
                f.write(file.read())
    
            st.success("Uploaded successfully")
