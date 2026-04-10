import streamlit as st
from db import register_user, login_user
from query import get_answer
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="EV Diagnostic Assistant", page_icon="🚗")

# ------------------ LOAD LOGO SAFELY ------------------
current_dir = os.path.dirname(__file__)
logo_path = os.path.join(current_dir, "logo.png")

if os.path.exists(logo_path):
    st.image(logo_path, width=150)
else:
    st.warning("Logo not found")

# ------------------ TITLE ------------------
st.title("🚗 EV Diagnostic Assistant")

# ------------------ SESSION STATE (CHAT HISTORY) ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ PDF UPLOAD ------------------
st.sidebar.header("📄 Upload EV Manual (PDF)")
uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())
    st.sidebar.success("PDF uploaded successfully!")

# ------------------ DISPLAY CHAT HISTORY ------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------ USER INPUT ------------------
user_input = st.chat_input("Ask your EV question...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get response (AUTO manual + AI fallback)
    response = get_answer(user_input)

    # Show bot response
    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})