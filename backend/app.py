import streamlit as st
from query import get_answer

st.set_page_config(page_title="EV Assistant", layout="wide")

# Styling (ChatGPT-like)
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🚗 EV Diagnostic Assistant")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input
query = st.chat_input("Ask your EV question...")

if query:
    # User message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    # AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = get_answer(query)
            st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})