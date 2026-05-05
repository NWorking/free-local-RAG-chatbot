# This is the frontend UI for the chatbot

# necessary package: pip install streamlit --break-system-packages
# command to run in terminal for local development: streamlit run app.py

import streamlit as st
from multi_turn_RAG_conversation import chat

# Page config
st.set_page_config(page_title="Chatbot Assistant", page_icon="💬")

# Title
st.title("Assistant 💬")
st.write("Ask me anything about the (website)!")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hi! I can help you answer questions. What would you like to know?"
    })

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat(prompt, session_id="web_user")
            st.write(response)

    # Add bot response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
