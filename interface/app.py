import re

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
    environment = st.selectbox("Environment", ("prod", "dev"), key="environment", default="dev")

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


def render_sources(sources: list[dict]) -> None:
    """Render the manual pages that backed an answer as clickable links."""
    if not sources:
        return
    lines = ["**Sources**"]
    for source in sources:
        url = source.get("url")
        if not url:
            continue
        label = source.get("title") or url
        lines.append(f"- [{label}]({url})")
    st.markdown("\n".join(lines))


# Display chat messages from history on app rerun
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(
                linkify_citations(message["content"], message.get("sources", []))
            )
            render_sources(message.get("sources", []))
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

    # make a POST request to chat API
    answer = requests.post(
        f"{API_BASE_URL}/ask",
        headers={"Authorization": api_key},
        json={"question": prompt, "manual_id": manual_id},
    )

    trace_id = None
    sources = []
    if answer.status_code != 200:
        response = f"Request failed: {answer.status_code}"
    else:
        body = answer.json()
        response = body["answer"]
        trace_id = body.get("trace_id")
        sources = body.get("sources", [])
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(linkify_citations(response, sources))
        render_sources(sources)
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
