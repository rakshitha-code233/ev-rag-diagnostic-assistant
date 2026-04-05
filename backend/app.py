import streamlit as st
from query import get_answer

st.set_page_config(page_title="EV Assistant", layout="centered")

# 🎨 PREMIUM CSS
st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #0b1120;
    color: #e5e7eb;
}

/* Title */
h1 {
    text-align: center;
    color: #3b82f6;
    font-weight: 600;
    margin-bottom: 20px;
}

/* Chat container spacing */
.block-container {
    padding-top: 2rem;
}

/* User message */
.user-msg {
    background: #3b82f6;
    color: white;
    padding: 12px;
    border-radius: 12px;
    margin: 8px 0;
    width: fit-content;
    max-width: 75%;
    margin-left: auto;
    font-size: 15px;
}

/* Bot message */
.bot-msg {
    background: #111827;
    border: 1px solid #1f2937;
    color: #e5e7eb;
    padding: 12px;
    border-radius: 12px;
    margin: 8px 0;
    width: fit-content;
    max-width: 75%;
    font-size: 15px;
}

/* Input box */
textarea {
    background-color: #111827 !important;
    color: #e5e7eb !important;
    border-radius: 10px !important;
    border: 1px solid #1f2937 !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #1f2937;
    border-radius: 10px;
}

/* Remove Streamlit footer */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# 🚗 Title
st.title("🚗 EV Diagnostic Assistant")

# 💬 Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-msg'>{msg['content']}</div>", unsafe_allow_html=True)

# Input
query = st.chat_input("Ask your EV question...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    answer = get_answer(query)

    st.session_state.messages.append({"role": "assistant", "content": answer})

    st.rerun()