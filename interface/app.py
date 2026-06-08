import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv("../.env")
load_dotenv(".env")

with st.sidebar:
    api_key = st.text_input("support-chatbot API Key", key="chatbot_api_key", type="password")

st.title("💸 support-chatbot")
st.caption("Ask him questions about 121 and get answers from the user manual.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input():
    if not api_key:
        st.info("Please add the support-chatbot API key to continue.")
        st.stop()

    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # make a POST request to chat API
    answer = requests.post(
        # "http://127.0.0.1:8000/ask",
        "https://support-chatbot.azurewebsites.net/ask",
        headers={"Authorization": api_key},
        json={"question": prompt},
    )

    if answer.status_code != 200:
        response = f"Request failed: {answer.status_code}"
    else:
        response = answer.json()["answer"]
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
