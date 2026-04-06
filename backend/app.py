import streamlit as st
from db import register_user, login_user

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="EV Assistant", layout="centered")

# ---------------- CLEAN CSS ----------------
st.markdown("""
<style>

/* Remove top space */
.block-container {
    padding-top: 2rem !important;
}

/* Hide header/footer */
header {visibility: hidden;}
footer {visibility: hidden;}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}

/* Card */
.card {
    background: white;
    padding: 25px;
    border-radius: 12px;
    width: 380px;
    margin: auto;
    margin-top: 60px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
}

/* Title */
.title {
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 15px;
}

/* Buttons center fix */
.stButton>button {
    width: 100%;
    border-radius: 8px;
}

/* Input */
.stTextInput input {
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------------- CARD ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)

# -------- Toggle Buttons INSIDE CARD --------
col1, col2 = st.columns(2)

with col1:
    if st.button("Login"):
        st.session_state.page = "login"

with col2:
    if st.button("Signup"):
        st.session_state.page = "signup"

st.write("")

# ---------------- LOGIN ----------------
if st.session_state.page == "login":
    st.markdown('<div class="title">Login Form</div>', unsafe_allow_html=True)

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login Now"):
        user = login_user(email, password)
        if user:
            st.success("Login Successful ✅")
        else:
            st.error("Invalid Email or Password ❌")

# ---------------- SIGNUP ----------------
elif st.session_state.page == "signup":
    st.markdown('<div class="title">Signup Form</div>', unsafe_allow_html=True)

    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_pass")
    confirm = st.text_input("Confirm Password")

    if st.button("Signup Now"):
        if password != confirm:
            st.error("Passwords do not match ❌")
        elif len(password) < 6:
            st.warning("Password must be at least 6 characters")
        else:
            success = register_user(email, password)
            if success:
                st.success("Account created ✅")
                st.session_state.page = "login"
            else:
                st.error("User already exists ❌")

# ---------------- CLOSE CARD ----------------
st.markdown('</div>', unsafe_allow_html=True)