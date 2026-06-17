import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv("../.env")
load_dotenv(".env")

API_BASE_URLS = {
    "prod": "https://support-chatbot.azurewebsites.net",
    "dev": "https://support-chatbot-dev.azurewebsites.net",
}

with st.sidebar:
    api_key = st.text_input(
        "support-chatbot API Key", key="chatbot_api_key", type="password"
    )
    manual_id = st.text_input("Manual", key="manual_id", value="121")
    environment = st.selectbox("Environment", ("prod", "dev"), key="environment")

API_BASE_URL = API_BASE_URLS[environment]


def send_feedback(trace_id: str, positive: bool) -> None:
    """Send a thumbs up/down score for an answer to the feedback endpoint."""
    response = requests.post(
        f"{API_BASE_URL}/feedback",
        headers={"Authorization": api_key},
        json={"trace_id": trace_id, "positive": positive},
    )
    if response.status_code == 202:
        st.toast("Thanks for your feedback!")
    else:
        st.toast(f"Could not send feedback: {response.status_code}")


st.title("support-chatbot")
st.caption("Ask questions about 510's products and services.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


def render_feedback(index: int, trace_id: str) -> None:
    """Render thumbs up/down controls for an assistant message."""
    selection = st.feedback("thumbs", key=f"feedback-{index}")
    if selection is not None:
        send_feedback(trace_id, positive=selection == 1)


# Display chat messages from history on app rerun
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("trace_id"):
            render_feedback(index, message["trace_id"])

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
        f"{API_BASE_URL}/ask",
        headers={"Authorization": api_key},
        json={"question": prompt, "manual_id": manual_id},
    )

    trace_id = None
    if answer.status_code != 200:
        response = f"Request failed: {answer.status_code}"
    else:
        body = answer.json()
        response = body["answer"]
        trace_id = body.get("trace_id")
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response, "trace_id": trace_id}
    )
    if trace_id:
        render_feedback(len(st.session_state.messages) - 1, trace_id)
