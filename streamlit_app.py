import streamlit as st
import anthropic
import os

st.set_page_config(page_title="AWS Architecture Assistant", page_icon="☁️")

# Password protection
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 Login")
        password = st.text_input("Enter password", type="password")
        if st.button("Login"):
            if password == os.environ.get("APP_PASSWORD", "changeme"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Wrong password")
        st.stop()

check_password()

st.title("☁️ AWS Architecture Assistant")

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an expert AWS solutions architect. 
You help customers design scalable, cost-effective AWS architectures.
Be concise but thorough. Ask clarifying questions when needed."""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = {"input": 0, "output": 0}

with st.sidebar:
    st.header("📊 Session Stats")
    st.metric("Input Tokens", st.session_state.total_tokens["input"])
    st.metric("Output Tokens", st.session_state.total_tokens["output"])
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.total_tokens = {"input": 0, "output": 0}
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me about AWS architecture..."):

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    if len(st.session_state.messages) > 10:
        st.session_state.messages = st.session_state.messages[-10:]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=st.session_state.messages
            )
            assistant_message = response.content[0].text
            st.session_state.total_tokens["input"] += response.usage.input_tokens
            st.session_state.total_tokens["output"] += response.usage.output_tokens
            st.markdown(assistant_message)

    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_message
    })

    st.rerun()