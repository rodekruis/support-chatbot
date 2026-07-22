import json
import os
import re
import uuid

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv("../.env")
load_dotenv(".env")

API_BASE_URLS = {
    "prod": "https://support-chatbot.azurewebsites.net",
    "dev": "https://support-chatbot-dev.azurewebsites.net",
}

environment = os.getenv("ENVIRONMENT", "dev")
if environment not in API_BASE_URLS:
    raise ValueError(
        f"Unknown ENVIRONMENT {environment!r}; expected one of {sorted(API_BASE_URLS)}."
    )
API_BASE_URL = API_BASE_URLS[environment]

with st.sidebar:
    api_key = st.text_input(
        "support-chatbot API Key", key="chatbot_api_key", type="password"
    )
    manual_id = st.text_input("Manual", key="manual_id", value="121")


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

# One conversation id per browser session, so a user's turns share memory
# without colliding with other users.
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


def render_feedback(index: int, trace_id: str) -> None:
    """Render thumbs up/down controls for an assistant message."""
    selection = st.feedback("thumbs", key=f"feedback-{index}")
    if selection is not None:
        send_feedback(trace_id, positive=selection == 1)


def linkify_citations(text: str, sources: list[dict]) -> str:
    """Turn inline ``[n]`` citation markers into links to the n-th source.

    The engine numbers citations in the same order as ``sources``, so ``[n]``
    maps to ``sources[n-1]``. Markers whose number falls outside the source
    range (e.g. a year like ``[2024]``) are left untouched.
    """

    def _replace(match: re.Match[str]) -> str:
        index = int(match.group(1))
        if 1 <= index <= len(sources):
            url = sources[index - 1].get("url")
            if url:
                return f"[\\[{index}\\]]({url})"
        return match.group(0)

    return re.sub(r"\[(\d{1,2})\]", _replace, text)


# Display chat messages from history on app rerun
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(
                linkify_citations(message["content"], message.get("sources", []))
            )
            if message.get("trace_id"):
                render_feedback(index, message["trace_id"])
        else:
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

    # stream the answer from the chat API, rendering tokens as they arrive
    trace_id = None
    sources = []
    with st.chat_message("assistant"):
        placeholder = st.empty()
        accumulated = ""
        try:
            with requests.post(
                f"{API_BASE_URL}/ask/stream",
                headers={"Authorization": api_key},
                json={
                    "question": prompt,
                    "manual_id": manual_id,
                    "session_id": st.session_state.session_id,
                },
                stream=True,
                timeout=120,
            ) as stream:
                if stream.status_code != 200:
                    accumulated = f"Request failed: {stream.status_code}"
                else:
                    for line in stream.iter_lines():
                        if not line:
                            continue
                        event = json.loads(line)
                        if event["type"] == "token":
                            accumulated += event["text"]
                            placeholder.markdown(accumulated + "▌")
                        elif event["type"] == "done":
                            trace_id = event.get("trace_id")
                            sources = event.get("sources", [])
                        elif event["type"] == "error":
                            accumulated += "\n\n_Sorry, something went wrong._"
        except requests.RequestException as exc:
            accumulated = f"Request failed: {exc}"
        # final render with citations turned into links
        placeholder.markdown(linkify_citations(accumulated, sources))
    response = accumulated
    # Add assistant response to chat history
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
            "trace_id": trace_id,
            "sources": sources,
        }
    )
    if trace_id:
        render_feedback(len(st.session_state.messages) - 1, trace_id)
